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
        combat_logger.debug("Combat Engine initialized with RNG and lock")

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
        weapon_name = getattr(weapon, 'name', 'Unarmed')
        combat_logger.debug(f"Attacker {attacker.name} using {weapon_name}")
        
        # Validate weapon exists OR attacker has pending spell/ability
        has_spell = (hasattr(attacker, 'pending_spell') or
                     hasattr(attacker, 'casting_spell') or
                     self._is_casting_spell(attacker))
        
        if not weapon and not has_spell:
            return CombatOutcome(
                False, [], description="No valid weapon or spell available"
            )
            
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
                print(f"  -> VALID TARGET")
            else:
                print(f"  -> INVALID TARGET")

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

        # Calculate hit chance for the attack event
        hit_chance = 0.1  # Start with guaranteed hit for debugging
        print("DEBUG: Initial hit_chance = 1.0")
        
        try:
            calculated_hit = ScalingManager.calculate_hit_chance(
                attacker, defender)
            print(f"DEBUG: ScalingManager returned hit_chance = {calculated_hit}")
            hit_chance = calculated_hit
        except (TypeError, AttributeError) as e:
            # Fallback for spells or missing weapon data
            print(f"DEBUG: Exception in hit_chance calculation: {e}")
            hit_chance = 1.0  # Force hit for debugging
            
        print(f"DEBUG: Final hit_chance = {hit_chance}")
        
        # Note: base_damage calculation removed to avoid divergent maths
        # Real damage comes from ScalingManager.compute_damage()
        # Future: pass base_damage via DamagePacket to ScalingManager

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

        # miss?
        rng_value = self._rng.random()
        print(f"DEBUG: Hit check - RNG={rng_value}, hit_chance={hit_chance}")
        if rng_value > hit_chance:
            attack_event.was_hit = False
            attack_event.final_damage = 0.0  # No damage on miss
            out.add_event(CombatEvent(
                CombatEventType.ATTACK_MISSED, attacker, defender))
            # Set a descriptive outcome for miss
            miss_desc = f"{attacker.name}'s attack missed {defender.name}"
            out.description = miss_desc
            return out

        # dodge?
        if def_cp.can_dodge():
            print("DEBUG: Attack was DODGED!")
            attack_event.was_hit = False
            attack_event.final_damage = 0.0  # No damage on dodge
            out.add_event(DefenseEvent(
                CombatEventType.ATTACK_DODGED, attacker, defender,
                was_dodged=True))
            # Set a descriptive outcome for dodge
            dodge_desc = f"{defender.name} dodged {attacker.name}'s attack"
            out.description = dodge_desc
            return out

        # block?
        print(f"DEBUG: Checking if {defender.name} can block...")
        has_offhand = hasattr(defender, 'offhand') and defender.offhand is not None
        offhand_name = getattr(defender.offhand, 'name', 'None') if has_offhand else 'None'
        block_chance_stat = defender.get_stat('block_chance')
        
        print(f"DEBUG: Has offhand: {has_offhand}, Offhand: {offhand_name}")
        print(f"DEBUG: Block chance stat: {block_chance_stat}")
        
        if has_offhand and hasattr(defender.offhand, 'block_chance'):
            print(f"DEBUG: Offhand block chance: {defender.offhand.block_chance}")
        
        if def_cp.can_block():
            print("DEBUG: Attack was BLOCKED!")
            attack_event.was_hit = False
            attack_event.final_damage = 0.0  # No damage on block
            out.add_event(DefenseEvent(
                CombatEventType.ATTACK_BLOCKED, attacker, defender,
                was_blocked=True))
            # Set a descriptive outcome for block
            block_desc = f"{defender.name} blocked {attacker.name}'s attack"
            out.description = block_desc
            combat_logger.info(block_desc)
            return out

        # Hit successful!
        combat_logger.info(f"{attacker.name}'s attack hit {defender.name}")
        attack_event.was_hit = True

        # damage maths
        # Create DamagePacket to eliminate getattr() reflection
        
        # Check actor attributes for spell state
        combat_logger.debug(f"Checking attacker {attacker.name} for spell attributes")
        has_spell_state = hasattr(attacker, '_spell_state')
        spell_state_value = getattr(attacker, '_spell_state', False)
        has_pending_spell = hasattr(attacker, 'pending_spell')
        pending_spell_value = getattr(attacker, 'pending_spell', None)
        has_job_id = hasattr(attacker, 'job_id')
        job_id_value = getattr(attacker, 'job_id', None)
        
        combat_logger.debug(
            f"{attacker.name} spell state: {has_spell_state}={spell_state_value}, "
            f"pending: {has_pending_spell}={pending_spell_value}"
        )
        
        # Calculate intellect bonus
        intellect_value = attacker.get_stat('intellect')
        intellect_multiplier = intellect_value / 10.0
        combat_logger.debug(
            f"{attacker.name} intellect: {intellect_value} "
            f"(multiplier: {intellect_multiplier:.2f})"
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
        should_use_spell_path = is_spell_state or has_spell or (not is_weapon_attack and is_mage)
        
        print(f"DEBUG: Combat path decision:")
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
            print(f"DEBUG: Using SPELL DAMAGE PATH")
            
            # Get the spell_id from the actor's pending_spell
            spell_id = getattr(attacker, 'pending_spell', 'fireball')  # Default to fireball
            print(f"DEBUG: Spell ID from actor: {spell_id}")
            
            # Load the actual spell to get its base_power
            base_power = 50  # Default if we can't load the spell
            try:
                from game_sys.magic.spell_loader import load_spell
                spell = load_spell(spell_id)
                if spell:
                    # Get the actual base_power from the spell
                    base_power = spell.base_power
                    print(f"DEBUG: Loaded spell {spell_id} with base_power: {base_power}")
            except Exception as e:
                print(f"DEBUG: Error loading spell: {e}")
            
            # Apply intellect enhancement formula: base_power * (1 + intellect/10)
            enhanced_power = base_power * (1.0 + intellect_multiplier)
            
            print(f"DEBUG: Intellect enhancement formula:")
            print(f"  Base power: {base_power}")
            print(f"  Intellect: {intellect_value}")
            print(f"  Multiplier: {intellect_multiplier}")
            print(f"  Enhanced power: {enhanced_power}")
            
            # Create spell packet
            spell_packet = DamagePacket.from_spell_cast(
                attacker, defender, enhanced_power, spell_id
            )
            print(f"DEBUG: Created spell packet with enhanced_power={enhanced_power}")
            
            # Apply modifiers
            spell_packet.apply_modifier("spell_bonus", 2.0)
            print(f"DEBUG: Applied spell_bonus=2.0 to packet")
            print(f"DEBUG: Final packet base_damage: {spell_packet.base_damage}")
            print(f"DEBUG: Final effective damage: {spell_packet.get_effective_damage()}")
            
            damage_packet = spell_packet
        elif weapon:
            print(f"DEBUG: Using WEAPON DAMAGE PATH")
            damage_packet = DamagePacket.from_weapon_attack(
                attacker, defender, weapon
            )
        else:
            # Fallback to old calculation
            print(f"DEBUG: Using FALLBACK INTELLECT DAMAGE")
            spell_power = intellect_value * 5.0
            
            spell_packet = DamagePacket.from_spell_cast(
                attacker, defender, spell_power
            )
            spell_packet.apply_modifier("spell_bonus", 2.0)
            
            damage_packet = spell_packet
        
        base_dmg = ScalingManager.compute_damage_from_packet(damage_packet)
        print(f"DEBUG: ScalingManager returned base damage: {base_dmg}")
        
        critical = atk_cp.is_critical_hit()
        if critical:
            final_dmg = atk_cp.apply_critical_damage(base_dmg)
            print(f"DEBUG: Critical hit! Damage increased to {final_dmg}")
        else:
            final_dmg = base_dmg
            print(f"DEBUG: Normal hit, damage remains {final_dmg}")

        # Apply status flag damage modifiers
        if hasattr(attacker, 'status_flags'):
            outgoing_multiplier = attacker.status_flags.get_damage_multiplier(outgoing=True)
            final_dmg *= outgoing_multiplier
            print(f"DEBUG: Applied outgoing damage multiplier: {outgoing_multiplier}")
        
        if hasattr(defender, 'status_flags'):
            incoming_multiplier = defender.status_flags.get_damage_multiplier(outgoing=False)
            final_dmg *= incoming_multiplier
            print(f"DEBUG: Applied incoming damage multiplier: {incoming_multiplier}")

        # Determine damage type for resistance/weakness calculations
        damage_type = None
        if weapon and hasattr(weapon, 'damage_type'):
            damage_type = weapon.damage_type
        elif hasattr(attacker, 'pending_spell') and attacker.pending_spell:
            # For spells, try to get damage type from spell data
            try:
                from game_sys.magic.spell_loader import load_spell
                spell_data = load_spell(attacker.pending_spell)
                if spell_data and hasattr(spell_data, 'damage_type'):
                    spell_damage_type = spell_data.damage_type
                    
                    # Convert string to DamageType enum if necessary
                    if isinstance(spell_damage_type, str):
                        from game_sys.core.damage_type_utils import (
                            get_damage_type_by_name
                        )
                        damage_type = get_damage_type_by_name(spell_damage_type)
                    else:
                        damage_type = spell_damage_type
                elif 'fire' in str(attacker.pending_spell).lower():
                    from game_sys.core.damage_type_utils import (
                        get_damage_type_by_name
                    )
                    damage_type = get_damage_type_by_name("FIRE")
                elif 'ice' in str(attacker.pending_spell).lower():
                    from game_sys.core.damage_type_utils import (
                        get_damage_type_by_name
                    )
                    damage_type = get_damage_type_by_name("ICE")
                elif 'lightning' in str(attacker.pending_spell).lower():
                    from game_sys.core.damage_type_utils import (
                        get_damage_type_by_name
                    )
                    damage_type = get_damage_type_by_name("LIGHTNING")
            except Exception as e:
                print(f"DEBUG: Error getting spell damage type: {e}")
        
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
