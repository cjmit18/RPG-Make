# game_sys/combat/engine.py
"""
CombatEngine
============
Handles immediate attack resolution.  Scheduling is now external:
Actor schedules an `"attack"` into ActionQueue, TurnManager calls
`execute_attack_sync()` when the cooldown expires.
"""

from __future__ import annotations
import random
import threading
from typing import List, Union, Protocol, TYPE_CHECKING, Any

from game_sys.utils.profiler import profiler
from game_sys.core.scaling_manager import ScalingManager
from game_sys.hooks.hooks_setup import emit, ON_ATTACK_HIT
from game_sys.logging import combat_logger
from .capabilities import CombatCapabilities
from .damage_packet import DamagePacket
from .events import (
    CombatOutcome, CombatEvent, CombatEventType, AttackEvent, DefenseEvent
)

if TYPE_CHECKING:
    from game_sys.character.actor import Actor


class RandomProtocol(Protocol):
    """Protocol for random number generators."""
    def random(self) -> float: ...
    def seed(self, seed: int) -> None: ...



class CombatEngine:
    # --- ASYNC HOOKS: These can be extended or monkey-patched as needed --- #
    async def on_pre_attack(self, attacker, targets, weapon):
        """Async hook: called before attack is resolved. Override for effects, logging, etc."""
        pass

    async def on_post_attack(self, attacker, targets, outcome):
        """Async hook: called after attack is resolved. Override for effects, logging, etc."""
        pass

    async def on_attack_hit(self, attacker, defender, damage, outcome):
        """Async hook: called when an attack hits. Override for effects, animations, etc."""
        pass

    async def on_attack_miss(self, attacker, defender, outcome):
        """Async hook: called when an attack misses. Override for effects, animations, etc."""
        pass

    # --- ASYNC AI HOOKS --- #
    async def on_ai_turn_start(self, ai_actor, player, outcome):
        """Async hook: called before an AI actor takes its turn. Override for effects, logging, etc."""
        pass

    async def on_ai_turn_end(self, ai_actor, player, outcome):
        """Async hook: called after an AI actor takes its turn. Override for effects, logging, etc."""
        pass

    async def process_ai_responses_async(self, attacker, targets, outcome):
        """
        Async version of AI response processing. Calls async AI controller if available, else falls back to sync.
        """
        if not self._ai_controller:
            return
        ai_actors = []
        for target in targets:
            if (target and hasattr(target, 'is_alive') and target.is_alive() and hasattr(target, 'ai_enabled') and target.ai_enabled):
                ai_actors.append(target)
        player = None
        for t in [attacker] + targets:
            if hasattr(t, 'is_player') and t.is_player:
                player = t
                break
        if not player:
            for t in [attacker] + targets:
                if not (hasattr(t, 'ai_enabled') and t.ai_enabled):
                    player = t
                    break
        for ai_actor in ai_actors:
            try:
                await self.on_ai_turn_start(ai_actor, player, outcome)
                # Prefer async AI controller if available
                ai_ctrl = self._ai_controller
                if hasattr(ai_ctrl, 'process_ai_turn_async') and callable(getattr(ai_ctrl, 'process_ai_turn_async')):
                    await ai_ctrl.process_ai_turn_async(ai_actor, player, 0.0)
                elif hasattr(ai_ctrl, 'process_ai_turn') and callable(getattr(ai_ctrl, 'process_ai_turn')):
                    ai_ctrl.process_ai_turn(ai_actor, player, 0.0)
                await self.on_ai_turn_end(ai_actor, player, outcome)
            except Exception as e:
                combat_logger.warning(f"Error processing async AI responses: {e}")

    async def execute_attack_async(
        self, attacker: "Actor", targets: List["Actor"], weapon: Any | None = None
    ) -> "CombatOutcome":
        """
        Async version of execute_attack_sync. Use this in async game loops.
        Mirrors execute_attack_sync, but allows for awaitable hooks or delays in the future.
        """
        # Practical async hooks: pre-attack, post-attack, on-hit, on-miss
        await self.on_pre_attack(attacker, targets, weapon)
        # Call the sync version for now, but process events for async hooks
        outcome = self.execute_attack_sync(attacker, targets, weapon)
        # For each event, call appropriate async hooks
        for event in getattr(outcome, 'events', []):
            if hasattr(event, 'event_type'):
                et = event.event_type.name if hasattr(event.event_type, 'name') else str(event.event_type)
                if et == 'DAMAGE_DEALT' and getattr(event, 'was_critical', False) is not None:
                    await self.on_attack_hit(event.attacker, event.defender, getattr(event, 'damage', 0), outcome)
                elif et in ('ATTACK_MISSED', 'ATTACK_DODGED'):
                    await self.on_attack_miss(event.attacker, event.defender, outcome)
        await self.on_post_attack(attacker, targets, outcome)
        return outcome

    async def execute_spell_attack_async(
        self, actor: "Actor", targets: list, spell_info: dict
    ) -> "CombatOutcome":
        """
        Async version of spell attack execution for compatibility with async TurnManager.
        Mirrors the sync pathway, but allows for awaitable hooks or delays in the future.
        """
        # Set up spell state as in the sync pathway if needed
        actor_id = getattr(actor, 'id', str(id(actor)))
        if not hasattr(self, '_casting_states'):
            self._casting_states = {}
        if actor_id not in self._casting_states:
            self._casting_states[actor_id] = {}
        self._casting_states[actor_id]['executing'] = True
        actor._spell_state = True
        spell_id = spell_info.get('id')
        if spell_id:
            actor.pending_spell = spell_id
        try:
            # Call the sync attack for now
            return self.execute_attack_sync(actor, targets, weapon=None)
        finally:
            if hasattr(actor, '_spell_state'):
                delattr(actor, '_spell_state')
            if hasattr(actor, 'pending_spell'):
                delattr(actor, 'pending_spell')
            if (actor_id in self._casting_states and
                    'executing' in self._casting_states[actor_id]):
                del self._casting_states[actor_id]['executing']
    """
    Core combat engine that processes attacks, defenses, and outcomes.
    
    Thread Safety Notes:
    - Each TurnManager gets its own CombatEngine instance for thread safety
    - If multithread access is needed, protect self._rng with a lock
    
    Future Improvements:
    - Implement DamagePacket struct for ScalingManager.compute_damage()
    - Add hit resolution middleware for evasion, parry, reflection
    - Consider local random.Random instances per attack for full isolation
    """

    def __init__(
        self, rng: Union[random.Random, RandomProtocol, None] = None
    ) -> None:
        combat_logger.info("Initializing Combat Engine")
        self._rng = rng or random.Random()
        self._rng_lock = threading.Lock()  # For future multithread safety
        self._ai_controller = None  # Optional AI controller
        combat_logger.debug("Combat Engine initialized with RNG and lock")

    def set_ai_controller(self, ai_controller) -> None:
        """Set the AI controller for automatic enemy responses."""
        self._ai_controller = ai_controller
        combat_logger.debug("AI controller set for combat engine")

    @property
    def rng(self) -> Union[random.Random, RandomProtocol]:
        """Access the random number generator."""
        return self._rng

    @rng.setter
    def rng(self, value: Union[random.Random, RandomProtocol]) -> None:
        """Set the random number generator."""
        combat_logger.debug("Setting new RNG for Combat Engine")
        self._rng = value

    def set_rng_seed(self, seed: int) -> None:
        """Set RNG seed for deterministic testing."""
        combat_logger.debug(f"Setting RNG seed: {seed}")
        if hasattr(self._rng, 'seed'):
            self._rng.seed(seed)
        else:
            # Fallback for custom RNG objects
            self._rng = random.Random(seed)
            combat_logger.debug("Created new Random with seed")

    def _is_casting_spell(self, actor: "Actor") -> bool:
        """
        Check if an actor is currently casting a spell.
        
        Args:
            actor: The actor to check
            
        Returns:
            True if the actor is casting a spell, False otherwise
        """
        # Check if actor has any spell-related state
        return (hasattr(actor, 'pending_spell') or
                hasattr(actor, 'casting_spell') or
                hasattr(actor, '_spell_state'))

    # ------------------------------------------------------------------ #
    #  entry-point called by TurnManager                                 #
    # ------------------------------------------------------------------ #
    def execute_attack_sync(
        self, attacker: "Actor", targets: List["Actor"],
        weapon: Any | None = None
    ) -> CombatOutcome:
        """
        Resolves an already-scheduled attack **synchronously** (no awaits).
        
        Args:
            attacker: The attacking actor
            targets: List of target actors
            weapon: Optional weapon override (uses attacker's weapon if None)
            
        Returns:
            CombatOutcome with success status and events
        """
        attacker_name = getattr(attacker, 'name', 'Unknown')
        target_names = [getattr(t, 'name', 'Unknown') for t in targets]
        combat_logger.info(
            f"Executing attack: {attacker_name} -> {', '.join(target_names)}"
        )
        
        with profiler.span("combat"):
            return self._execute_attack_internal(attacker, targets, weapon)
    
    def _execute_attack_internal(
        self, attacker: "Actor", targets: List["Actor"],
        weapon: Any | None = None
    ) -> CombatOutcome:
        # --- Stamina enforcement for attacks ---
        from game_sys.config.config_manager import ConfigManager
        cfg = ConfigManager()
        stamina_cost = cfg.get("constants.combat.stamina_costs.attack", 5)
        # Only operate if attacker has a numeric current_stamina attribute
        current_stamina = getattr(attacker, 'current_stamina', None)
        # Defensive: ensure both are numbers
        if not (isinstance(current_stamina, (int, float)) and isinstance(stamina_cost, (int, float))):
            return CombatOutcome(False, [], description=f"{getattr(attacker, 'name', 'Attacker')} has no usable stamina stat!")
        if float(current_stamina) < float(stamina_cost):
            return CombatOutcome(
                False, [],
                description=f"{getattr(attacker, 'name', 'Attacker')} is too exhausted to attack! (Needs {stamina_cost} stamina)"
            )
        # Deduct stamina immediately
        attacker.current_stamina = float(current_stamina) - float(stamina_cost)
        if attacker.current_stamina < 0:
            attacker.current_stamina = 0
        # Input validation
        if not attacker:
            combat_logger.warning("Attack failed: Invalid attacker")
            return CombatOutcome(False, [], description="Invalid attacker")
        
        if not hasattr(attacker, 'is_alive') or not attacker.is_alive():
            combat_logger.warning(f"Attack failed: {attacker.name} is not alive")
            return CombatOutcome(
                False, [], description="Attacker is not alive"
            )
            
        # Check if attacker can perform actions due to status effects
        if hasattr(attacker, 'status_flags') and not attacker.status_flags.can_attack():
            return CombatOutcome(
                False, [], description=f"{attacker.name} cannot attack due to status effects"
            )
        
        weapon = weapon or getattr(attacker, 'weapon', None)
        # If no weapon and not casting a spell, assign 'empty_hands' weapon
        has_spell = (hasattr(attacker, 'pending_spell') or
                     hasattr(attacker, 'casting_spell') or
                     self._is_casting_spell(attacker))
        if not weapon and not has_spell:
            try:
                from game_sys.items.factory import ItemFactory
                weapon = ItemFactory.create('empty_hands')
                combat_logger.debug(
                    f"Assigned 'empty_hands' weapon to {attacker.name}"
                )
            except Exception as e:
                combat_logger.warning(
                    f"Could not assign 'empty_hands' weapon: {e}"
                )
                return CombatOutcome(
                    False, [], description="No valid weapon or spell available"
                )
        weapon_name = getattr(weapon, 'name', 'Unarmed')
        combat_logger.debug(f"Attacker {attacker.name} using {weapon_name}")
            
        # For weapons, validate required attributes
        if weapon and not (
            hasattr(weapon, 'damage_type') or
            hasattr(weapon, 'damage_map') or
            hasattr(weapon, 'base_damage')
        ):
            return CombatOutcome(
                False, [], description="No valid weapon available"
            )
            
        # Get max_targets with fallback to 1
        try:
            max_targets = int(attacker.get_stat("max_targets"))
            print(f"DEBUG: Got max_targets={max_targets} for {attacker.name}")
        except (AttributeError, KeyError, ValueError):
            max_targets = 1
            print(f"DEBUG: Using fallback max_targets=1 for {attacker.name}")
        
        # Ensure max_targets is at least 1 (critical fix for targeting)
        max_targets = max(1, max_targets)
        print(f"DEBUG: Final max_targets={max_targets} for {attacker.name}")
        valid_targets = []
        
        # Filter targets more robustly
        print(f"DEBUG: Filtering {len(targets)} targets with max {max_targets}")
        for target in targets[:max_targets]:
            print(f"DEBUG: Checking target: {target.name if target else 'None'}")
            print(f"  target exists: {target is not None}")
            print(f"  has is_alive: {hasattr(target, 'is_alive') if target else False}")
            print(f"  is alive: {target.is_alive() if target and hasattr(target, 'is_alive') else 'N/A'}")
            print(f"  not attacker: {target != attacker if target else 'N/A'}")
            
            if (target and
                    hasattr(target, 'is_alive') and
                    target.is_alive() and
                    target != attacker):  # Don't allow self-attack
                valid_targets.append(target)
                print("  -> VALID TARGET")
            else:
                print("  -> INVALID TARGET")

        if not valid_targets:
            return CombatOutcome(
                False, [],
                description="No valid targets available"
            )

        # Create outcome after all validation passes
        outcome = CombatOutcome(True, [])
        
        # Process each target individually with specific error handling
        for tgt in valid_targets:
            try:
                single_outcome = self._attack_vs_single(attacker, tgt, weapon)
                outcome.merge(single_outcome)
            except (ValueError, AttributeError, TypeError) as e:
                # Narrow exception handling with target context
                target_name = getattr(tgt, 'name', 'unknown target')
                return CombatOutcome(
                    False, [],
                    description=f"Combat error against {target_name}: {str(e)}"
                )
            except Exception as e:
                # Fallback for unexpected errors
                target_name = getattr(tgt, 'name', 'unknown target')
                return CombatOutcome(
                    False, [],
                    description=f"Unexpected error against {target_name}: {e}"
                )

        # Process AI responses after combat if available
        self._process_ai_responses(attacker, valid_targets, outcome)
        
        # Always format full outcome description for multi-target scenarios
        formatted_desc = self._format_outcome_description(outcome)
        if outcome.description:
            outcome.description += "; " + formatted_desc
        else:
            outcome.description = formatted_desc
        return outcome

    # ------------------------------------------------------------------ #
    #  internal helpers                                                  #
    # ------------------------------------------------------------------ #
    def _attack_vs_single(
        self, attacker: "Actor", defender: "Actor", weapon: Any
    ) -> CombatOutcome:
        with profiler.span("single_attack"):
            return self._attack_vs_single_internal(attacker, defender, weapon)
    
    def _attack_vs_single_internal(
        self, attacker: "Actor", defender: "Actor", weapon: Any
    ) -> CombatOutcome:
        out = CombatOutcome(True, [])
        atk_cp = CombatCapabilities(attacker, defender, self._rng)
        def_cp = CombatCapabilities(defender, attacker, self._rng)


        # --- Modern hit, evade, block, parry logic using stat ranges ---
        import random
        # Add some randomness to accuracy and evasion for each attack
        accuracy_base = attacker.get_stat('accuracy')
        evasion_base = defender.get_stat('evasion')
        dodge_base = defender.get_stat('dodge_chance')
        parry_base = defender.get_stat('parry_chance')
        block_base = defender.get_stat('block_chance')
        resilience_base = defender.get_stat('resilience')
        focus_base = attacker.get_stat('focus')  # noqa: F841
        

        # Define a range (e.g., ±10%) for each stat
        def stat_with_variance(base, variance=0.1):
            spread = base * variance
            return random.uniform(base - spread, base + spread)

        attacker_accuracy = stat_with_variance(accuracy_base, 0.1)
        defender_evasion = stat_with_variance(evasion_base, 0.1)
        defender_dodge = stat_with_variance(dodge_base, 0.1)
        defender_parry = stat_with_variance(parry_base, 0.1)
        defender_block = stat_with_variance(block_base, 0.1)
        defender_resilience = stat_with_variance(resilience_base, 0.1)

        print(
            f"DEBUG: Modern hit_chance = (accuracy={attacker_accuracy:.3f}, "
            f"dodge={defender_dodge:.3f})"
        )
        # Clamp: min 0.05, max 0.95, base 0.85 offset for typical RPG feel
        hit_chance = max(
            0.05,
            min(0.95, attacker_accuracy - defender_dodge + 0.85)
        )

        # Evasion: attacker_accuracy vs defender_evasion (with variance)
        print(f"DEBUG: Evasion check - accuracy={attacker_accuracy:.3f}, evasion={defender_evasion:.3f}")
        if attacker_accuracy < defender_evasion:
            attack_event = AttackEvent(
                event_type=CombatEventType.ATTACK_DODGED,
                attacker=attacker,
                defender=defender,
                weapon=weapon,
                hit_chance=hit_chance,
                base_damage=0.0
            )
            attack_event.was_hit = False
            attack_event.final_damage = 0.0
            out.add_event(attack_event)
            out.description = (
                f"{defender.name} dodged {attacker.name}'s attack! (No damage dealt)"
            )
            combat_logger.info(out.description)
            return out

        # --- start event
        attack_event = AttackEvent(
            event_type=CombatEventType.ATTACK_STARTED,
            attacker=attacker,
            defender=defender,
            weapon=weapon,
            hit_chance=hit_chance,
            base_damage=0.0  # Will be set later
        )
        out.add_event(attack_event)

        # miss? (accuracy vs dodge)
        print(f"DEBUG: Hit check - accuracy={attacker_accuracy}, dodge={defender_dodge}, hit_chance={hit_chance}")
        if attacker_accuracy < defender_dodge:
            attack_event.was_hit = False
            attack_event.final_damage = 0.0  # No damage on miss
            miss_event = CombatEvent(
                CombatEventType.ATTACK_MISSED, attacker, defender)
            out.add_event(miss_event)
            # Set a descriptive outcome for miss
            miss_desc = f"{attacker.name}'s attack missed {defender.name}! (No damage dealt)"
            out.description = miss_desc
            combat_logger.info(miss_desc)
            return out

        # block? (accuracy vs block)
        print(f"DEBUG: Checking if {defender.name} can block... accuracy={attacker_accuracy}, block={defender_block}")
        has_offhand = (
            hasattr(defender, 'offhand') and defender.offhand is not None
        )
        offhand_name = (
            getattr(defender.offhand, 'name', 'None')
            if has_offhand else 'None'
        )
        block_chance_stat = defender_block
        print(f"DEBUG: Has offhand: {has_offhand}, Offhand: {offhand_name}")
        print(f"DEBUG: Block chance stat: {block_chance_stat}")
        if has_offhand and hasattr(defender.offhand, 'block_chance'):
            print(
                f"DEBUG: Offhand block chance: "
                f"{defender.offhand.block_chance}"
            )
        if def_cp.can_block() and attacker_accuracy < defender_block:
            print("DEBUG: Attack was BLOCKED!")
            # Parry check after block triggers (accuracy vs parry)
            print(f"DEBUG: Parry check - accuracy={attacker_accuracy}, parry={defender_parry}")
            if attacker_accuracy < defender_parry:
                # Parry successful
                parry_event = CombatEvent(
                    CombatEventType.ATTACK_PARRIED, attacker, defender)
                out.add_event(parry_event)
                out.description = f"{defender.name} parried {attacker.name}'s attack! (No damage dealt)"
                combat_logger.info(out.description)
                return out
            else:
                block_event = CombatEvent(
                    CombatEventType.ATTACK_BLOCKED, attacker, defender)
                out.add_event(block_event)
                out.description = f"{defender.name} blocked {attacker.name}'s attack! (No damage dealt)"
                combat_logger.info(out.description)
                return out

        # Hit successful!
        combat_logger.info(f"{attacker.name}'s attack hit {defender.name}")
        attack_event.was_hit = True

        # damage maths
        # Create DamagePacket to eliminate getattr() reflection
        
        # Check actor attributes for spell state
        combat_logger.debug(
            f"Checking attacker {attacker.name} for spell attributes"
        )
        has_spell_state = hasattr(attacker, '_spell_state')
        spell_state_value = getattr(attacker, '_spell_state', False)
        has_pending_spell = hasattr(attacker, 'pending_spell')
        pending_spell_value = getattr(attacker, 'pending_spell', None)
        has_job_id = hasattr(attacker, 'job_id')
        job_id_value = getattr(attacker, 'job_id', None)
        
        combat_logger.debug(
            f"{attacker.name} spell state: {has_spell_state}="
            f"{spell_state_value}, pending: {has_pending_spell}="
            f"{pending_spell_value}"
        )
        
        # Calculate intelligence bonus (use correct stat name)
        intelligence_value = attacker.get_stat('intelligence')
        intelligence_multiplier = intelligence_value / 10.0
        # Crit chance base value from config or stat
        from game_sys.config.config_manager import ConfigManager
        cfg = ConfigManager()
        # Use derived_stats.critical_chance as the config default
        base_crit_chance = cfg.get('constants.derived_stats.critical_chance', 0.01)
        # Ensure base_crit_chance is a float
        if not isinstance(base_crit_chance, (int, float)):
            base_crit_chance = 0.01
        # Allow override from character stat if present
        stat_crit_chance = attacker.get_stat('critical_chance')
        if isinstance(stat_crit_chance, (int, float)):
            base_crit_chance = stat_crit_chance
        # Physical crit chance: increased by dexterity
        dexterity_value = attacker.get_stat('dexterity')
        if not isinstance(dexterity_value, (int, float)):
            dexterity_value = 0.0
        physical_crit_chance = base_crit_chance + (dexterity_value / 100.0)
        # Spell crit chance: increased by focus
        focus_value = attacker.get_stat('focus')
        if not isinstance(focus_value, (int, float)):
            focus_value = 0.0
        spell_crit_chance = base_crit_chance + (focus_value / 100.0)
        combat_logger.debug(
            f"{attacker.name} intelligence: {intelligence_value} "
            f"(multiplier: {intelligence_multiplier:.2f}), focus: {focus_value} (spell crit+{spell_crit_chance:.2%}), dexterity: {dexterity_value} (phys crit+{physical_crit_chance:.2%}), base_crit_chance: {base_crit_chance:.2%}"
        )
        
        # Determine if we should use spell path
        is_spell_state = has_spell_state and spell_state_value
        has_spell = has_pending_spell and pending_spell_value is not None
        is_mage = has_job_id and job_id_value == 'mage'
        is_weapon_attack = weapon is not None
        
        # Use spell path if ANY of these are true:
        # 1. Actor has _spell_state = True
        # 2. Actor has pending_spell set
        # 3. No weapon AND actor is a mage
        should_use_spell_path = (
            is_spell_state or has_spell or (not is_weapon_attack and is_mage)
        )

        # --- PATCH: If not is_weapon_attack and not should_use_spell_path, force empty_hands weapon ---
        if not is_weapon_attack and not should_use_spell_path:
            try:
                from game_sys.items.factory import ItemFactory
                weapon = ItemFactory.create('empty_hands')
                is_weapon_attack = True
                combat_logger.debug(f"Forced 'empty_hands' weapon for {attacker.name} (no fallback)")
            except Exception as e:
                combat_logger.warning(f"Could not assign 'empty_hands' weapon in _attack_vs_single_internal: {e}")
        
        print("DEBUG: Combat path decision:")
        print(f"  has_spell_state: {has_spell_state}")
        print(f"  spell_state_value: {spell_state_value}")
        print(f"  has_pending_spell: {has_pending_spell}")
        print(f"  pending_spell_value: {pending_spell_value}")
        print(f"  has_job_id: {has_job_id}")
        print(f"  job_id_value: {job_id_value}")
        print(f"  is_mage: {is_mage}")
        print(f"  is_weapon_attack: {is_weapon_attack}")
        print(f"  USING SPELL PATH: {should_use_spell_path}")
        
        if should_use_spell_path:
            print("DEBUG: Using SPELL DAMAGE PATH")
            # Get the spell_id from the actor's pending_spell
            spell_id = getattr(attacker, 'pending_spell', 'fireball')
            print(f"DEBUG: Spell ID from actor: {spell_id}")
            # Load the actual spell to get its base_power and damage_type
            base_power = 50  # Default if we can't load the spell
            spell_damage_type = None
            try:
                from game_sys.magic.spell_loader import load_spell
                spell = load_spell(spell_id)
                if spell:
                    base_power = spell.base_power
                    spell_damage_type = getattr(spell, 'damage_type', None)
                    print(f"DEBUG: Loaded spell {spell_id} with base_power: {base_power} and damage_type: {spell_damage_type}")
            except Exception as e:
                print(f"DEBUG: Error loading spell: {e}")
            # Apply intelligence and magic power enhancement formula:
            magic_power = attacker.get_stat('magic_power') or 1.0
            enhanced_power = base_power * (1.0 + intelligence_multiplier) * magic_power
            print("DEBUG: Intelligence & magic power enhancement formula:")
            print(f"  Base power: {base_power}")
            print(f"  Intelligence: {intelligence_value}")
            print(f"  Multiplier: {intelligence_multiplier}")
            print(f"  Magic Power: {magic_power}")
            print(f"  Enhanced power: {enhanced_power}")
            # Always use the spell's damage_type if available, else fallback to MAGIC
            if spell_damage_type is None:
                from game_sys.core.damage_types import DamageType
                spell_damage_type = DamageType.MAGIC
            spell_packet = DamagePacket.from_spell_cast(
                attacker, defender, enhanced_power, spell_id, damage_type=spell_damage_type
            )
            # Use logger for debug output instead of print
            combat_logger.debug(
                f"Created spell packet with enhanced_power={enhanced_power} and damage_type={spell_damage_type}"
            )
            # Get spell bonus from config
            spell_bonus = cfg.get('constants.combat.spell_bonus', 2.0)
            if not isinstance(spell_bonus, (int, float)):
                spell_bonus = 2.0
            spell_packet.apply_modifier("spell_bonus", float(spell_bonus))
            combat_logger.debug(f"Applied spell_bonus={spell_bonus} to packet")
            combat_logger.debug(f"Final packet base_damage: {spell_packet.base_damage}")
            combat_logger.debug(f"Final effective damage: {spell_packet.get_effective_damage()}")
            # --- Spell Crit Calculation ---
            import random
            spell_crit_roll = random.random()
            is_spell_crit = spell_crit_roll < spell_crit_chance
            combat_logger.debug(f"Spell crit roll: {spell_crit_roll:.3f} vs chance: {spell_crit_chance:.3f}")
            damage_packet = spell_packet
        elif weapon:
            print("DEBUG: Using WEAPON DAMAGE PATH")
            damage_packet = DamagePacket.from_weapon_attack(
                attacker, defender, weapon
            )
        else:
            # Fallback to old calculation
            print("DEBUG: Using FALLBACK INTELLIGENCE DAMAGE")
            # Fallback: use a flat, low base damage (not based on intelligence)
            fallback_base_damage = 8.0  # You can tune this value for balance
            spell_packet = DamagePacket.from_spell_cast(
                attacker, defender, fallback_base_damage, damage_type=None
            )
            # No luck or stat-based bonus for fallback
            damage_packet = spell_packet
        
        base_dmg = ScalingManager.compute_damage_from_packet(damage_packet)
        print(f"DEBUG: ScalingManager returned base damage: {base_dmg}")

        # Focus: increases spell crit chance (now handled above)
        # Resilience: reduces critical hit multiplier
        if should_use_spell_path:
            critical = is_spell_crit
            crit_chance_used = spell_crit_chance
        else:
            # Use physical crit chance for weapon attacks
            import random
            phys_crit_roll = random.random()
            critical = phys_crit_roll < physical_crit_chance
            crit_chance_used = physical_crit_chance
            combat_logger.debug(f"Physical crit roll: {phys_crit_roll:.3f} vs chance: {physical_crit_chance:.3f}")

        # Apply magic resistance for spells, physical for weapon
        if should_use_spell_path:
            magic_resistance = defender.get_stat('magic_resistance') or 0.0
            final_dmg = base_dmg * (1.0 - magic_resistance)
        else:
            final_dmg = base_dmg

        if critical:
            # Reduce crit multiplier by defender's resilience (up to 50% reduction)
            crit_multiplier = 2.0 - min(defender_resilience, 0.5)
            final_dmg = final_dmg * crit_multiplier
            combat_logger.info(f"CRITICAL HIT! {attacker.name} crit {defender.name} for {final_dmg:.2f} (crit chance used: {crit_chance_used:.2%})")

        # Apply status flag damage modifiers
        if hasattr(attacker, 'status_flags'):
            outgoing_multiplier = attacker.status_flags.get_damage_multiplier(
                outgoing=True
            )
            final_dmg *= outgoing_multiplier
            print(
                f"DEBUG: Applied outgoing damage multiplier: "
                f"{outgoing_multiplier}"
            )
        
        if hasattr(defender, 'status_flags'):
            incoming_multiplier = defender.status_flags.get_damage_multiplier(
                outgoing=False
            )
            final_dmg *= incoming_multiplier
            print(
                f"DEBUG: Applied incoming damage multiplier: "
                f"{incoming_multiplier}"
            )

        # Determine damage type for resistance/weakness calculations
        # Always use the damage_type from the DamagePacket if present
        damage_type = getattr(damage_packet, 'damage_type', None)
        debug_msg = (f"DEBUG: Applying {final_dmg} damage to {defender.name} "
                     f"with damage type: {damage_type}")
        print(debug_msg)
        hp_left = defender.take_damage(final_dmg, attacker, damage_type)
        print(f"DEBUG: {defender.name} has {hp_left} HP remaining")
        
        # Update the attack event with base and final damage
        attack_event.base_damage = base_dmg  # Pre-crit damage
        attack_event.final_damage = final_dmg  # Post-crit damage
        
        # Create damage event with critical info and resistance/weakness data
        event_metadata = {}
        
        # Add resistance/weakness info to metadata
        if damage_type:
            if (hasattr(defender, 'resistances') and
                    damage_type in defender.resistances):
                resistance_value = defender.resistances[damage_type]
                event_metadata['resistance'] = {
                    'type': damage_type.name,
                    'value': resistance_value,
                    'message': (f"{defender.name} resists "
                                f"{resistance_value:.1%} of the "
                                f"{damage_type.name.lower()} damage!")
                }
                
            if (hasattr(defender, 'weaknesses') and
                    damage_type in defender.weaknesses):
                weakness_value = defender.weaknesses[damage_type]
                event_metadata['weakness'] = {
                    'type': damage_type.name,
                    'value': weakness_value,
                    'message': (f"{defender.name} is vulnerable to "
                                f"{damage_type.name.lower()} "
                                f"(+{weakness_value:.1%} damage)!")
                }
        
        damage_event = CombatEvent(
            CombatEventType.DAMAGE_DEALT, attacker, defender,
            damage=final_dmg, was_critical=critical,
            damage_type=damage_type,
            metadata=event_metadata
        )
        out.add_event(damage_event)
        
        # Note: CRITICAL_HIT event removed to avoid duplication
        # All critical info is included in DAMAGE_DEALT event
        
        emit(ON_ATTACK_HIT, source=attacker, target=defender, damage=final_dmg)

        if hp_left <= 0:
            out.add_event(CombatEvent(
                CombatEventType.DEATH, attacker, defender))

        return out

    def apply_healing(
        self, healer: "Actor", target: "Actor", amount: float,
        into: CombatOutcome | None = None
    ) -> CombatOutcome:
        """
        Apply healing to a target.
        
        Args:
            healer: The actor performing the healing
            target: The target to heal
            amount: Amount of healing to apply
            into: Optional outcome to merge into instead of returning new one
            
        Returns:
            CombatOutcome describing the healing (or the merged outcome)
        """
        # Input validation
        if not healer:
            return CombatOutcome(
                False, [], description="Invalid healer"
            )
        
        if not target:
            return CombatOutcome(
                False, [], description="Invalid target"
            )
        
        if amount <= 0:
            failure_outcome = CombatOutcome(
                False, [], description="Healing amount must be positive"
            )
            if into:
                into.merge(failure_outcome)
                return into
            return failure_outcome
        
        # Use provided outcome or create a new one
        outcome = into or CombatOutcome(success=True, events=[])
        
        if not hasattr(target, 'is_alive') or not target.is_alive():
            failure_outcome = CombatOutcome(
                False, [],
                description=f"{target.name} is dead and cannot be healed"
            )
            if into:
                into.merge(failure_outcome)
                return into
            return failure_outcome

        # Validate target has required attributes
        if (not hasattr(target, 'current_health') or
                not hasattr(target, 'max_health')):
            failure_outcome = CombatOutcome(
                False, [], description="Target has invalid health attributes"
            )
            if into:
                into.merge(failure_outcome)
                return into
            return failure_outcome

        try:
            # Calculate actual healing (can't exceed max health)
            max_heal = target.max_health - target.current_health
            actual_heal = min(amount, max_heal)
            
            # Apply healing
            target.current_health += actual_heal
            
            # Create healing event
            heal_event = CombatEvent(
                event_type=CombatEventType.HEALING_APPLIED,
                attacker=healer,
                defender=target,
                healing=actual_heal
            )
            outcome.add_event(heal_event)
            # Note: total_healing is automatically updated by add_event()
            
            # Append to description if it already exists, otherwise set it
            heal_desc = (f"{healer.name} heals {target.name} "
                         f"for {actual_heal} health")
            if outcome.description:
                outcome.description += f"; {heal_desc}"
            else:
                outcome.description = heal_desc
        except Exception as e:
            failure_outcome = CombatOutcome(
                False, [], description=f"Healing error: {str(e)}"
            )
            if into:
                into.merge(failure_outcome)
                return into
            return failure_outcome
        
        return outcome

    def _format_outcome_description(self, outcome: CombatOutcome) -> str:
        """
        Format a human-readable description of the combat outcome.
        
        Note: This builds the description once to preserve event order,
        which is important for complex multi-target/multi-effect scenarios.
        """
        if not outcome.events:
            return "No combat events occurred"
        
        # Build descriptions in event order to preserve narrative flow
        descriptions = []
        for event in outcome.events:
            desc = self._format_single_event(event)
            if desc:
                descriptions.append(desc)
        
        return "; ".join(descriptions)
    
    def _format_single_event(self, event: CombatEvent) -> str:
        """Format a single combat event into a description string."""
        attacker_name = getattr(event.attacker, 'name', 'Unknown')
        defender_name = getattr(event.defender, 'name', 'Unknown')
        
        if event.event_type == CombatEventType.DAMAGE_DEALT:
            desc = f"{attacker_name} deals {event.damage} damage"
            if event.was_critical:
                desc += " (CRITICAL!)"
            desc += f" to {defender_name}"
            return desc
        elif event.event_type == CombatEventType.ATTACK_BLOCKED:
            return f"{defender_name} blocked {attacker_name}'s attack"
        elif event.event_type == CombatEventType.ATTACK_DODGED:
            return f"{defender_name} dodged {attacker_name}'s attack"
        elif event.event_type == CombatEventType.ATTACK_MISSED:
            return f"{attacker_name}'s attack missed {defender_name}"
        elif event.event_type == CombatEventType.DEATH:
            return f"{defender_name} was defeated!"
        elif event.event_type == CombatEventType.HEALING_APPLIED:
            return (f"{attacker_name} healed {defender_name} "
                    f"for {event.healing} health")
        elif event.event_type == CombatEventType.CRITICAL_HIT:
            # Skip description - critical info already in DAMAGE_DEALT event
            return ""
        
        # Default for unhandled event types
        return f"{event.event_type.name} occurred"

    def _process_ai_responses(
        self, attacker: "Actor", targets: List["Actor"], 
        outcome: CombatOutcome
    ) -> None:
        """
        Legacy sync AI response for backward compatibility. Prefer process_ai_responses_async in async flows.
        """
        import asyncio
        try:
            # Try to run the async version if in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.process_ai_responses_async(attacker, targets, outcome))
            else:
                loop.run_until_complete(self.process_ai_responses_async(attacker, targets, outcome))
        except Exception:
            # Fallback to old sync logic if async fails
            if not self._ai_controller:
                return
            ai_actors = []
            for target in targets:
                if (target and hasattr(target, 'is_alive') and target.is_alive() and hasattr(target, 'ai_enabled') and target.ai_enabled):
                    ai_actors.append(target)
            player = None
            for t in [attacker] + targets:
                if hasattr(t, 'is_player') and t.is_player:
                    player = t
                    break
            if not player:
                for t in [attacker] + targets:
                    if not (hasattr(t, 'ai_enabled') and t.ai_enabled):
                        player = t
                        break
            for ai_actor in ai_actors:
                try:
                    combat_logger.debug(f"Processing AI turn for {ai_actor.name}")
                    if hasattr(self._ai_controller, 'process_ai_turn'):
                        self._ai_controller.process_ai_turn(ai_actor, player, 0.0)
                except Exception as e:
                    combat_logger.warning(f"Error processing AI responses: {e}")
