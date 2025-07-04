# game_sys/character/actor.py
"""
Module: game_sys.character.actor

Defines the core Actor hierarchy, encapsulating character state,
stats, pools, progression, inventory, action scheduling, combat interactions,
status effects, item usage, abilities, interactions, serialization, and metadata.
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Tuple
from game_sys.managers.collision_manager import collision_manager
from game_sys.effects.status_manager import status_manager
from game_sys.config.config_manager import ConfigManager
from game_sys.config.feature_flags import FeatureFlags
from game_sys.core.scaling_manager import ScalingManager
from game_sys.core.damage_types import DamageType
from game_sys.effects.base import Effect
from game_sys.logging import character_logger, log_exception
from game_sys.hooks.hooks_setup import (
    emit,
    ON_DEATH,
    ON_LEVEL_UP,
    ON_STATUS_APPLIED,
    ON_STATUS_EXPIRED,
    ON_ITEM_USED,
    ON_ABILITY_CAST,
    ON_INTERACT,
    ON_SPAWN
)
from game_sys.managers.factories import get_action_queue, get_inventory_manager
from game_sys.managers.time_manager import time_manager
from game_sys.skills.skill_loader import load_skill
from game_sys.magic.spell_loader import load_spell
flags = FeatureFlags()


def _fmt(val: float) -> str:
    """
    Format a float with up to two decimals,
    but drop the decimal part if it’s a whole number.
    """
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return f"{val:.2f}"
    return str(val)


class Actor:
    """
    Base class for all characters.
    """

    def __init__(
        self,
        name: str,
        base_stats: Dict[str, float],
        **overrides
    ):
        character_logger.info(f"Creating actor: {name}")
        self.name = name
        cfg = ConfigManager()

        # Initialize base stats
        defaults = cfg.get('constants.stats_defaults', {})
        self.base_stats: Dict[str, float] = {
            s: defaults.get(s, 0.0) for s in defaults
        }
        self.base_stats.update(base_stats)
        for k, v in overrides.items():
            self.base_stats[k] = v
            
        character_logger.debug(f"Actor {name} base stats: {self.base_stats}")

        # Progression
        self.level: int = 1
        self.xp: float = 0.0
        self.max_level: int = cfg.get('constants.leveling.max_level', 100)

        # Pools
        self.max_health: float = self.get_stat('health')
        self.current_health: float = self.max_health
        self.max_mana: float = self.get_stat('mana')
        self.current_mana: float = self.max_mana
        self.max_stamina: float = self.get_stat('stamina')
        self.current_stamina: float = self.max_stamina
        self.skill_cooldowns: Dict[str, float] = {}
        self.spell_cooldowns: Dict[str, float] = {}

        # Quality & economy
        self.grade: Optional[int] = None
        self.rarity: Optional[str] = None
        self.gold: int = 0

        # Resistances/weaknesses
        self.weaknesses: Dict[DamageType, float] = {}
        self.resistances: Dict[DamageType, float] = {}

        # Combat metadata
        self.last_hit_by: Optional[Actor] = None
        self.last_hit_damage: float = 0.0
        self.killed_by: Optional[Actor] = None
        self.kills: List[Actor] = []
        self.team = 'neutral'  # 'player', 'enemy', 'neutral'
        
        # Spell and skill tracking
        self.pending_spell: Optional[str] = None  # Track currently casting spell
        self._spell_state: bool = False  # Flag for spell execution

        # Status effects
        self.active_statuses: Dict[str, Tuple[Effect, float]] = {}

        # Systems
        self.inventory = get_inventory_manager(self)
        self.action_queue = get_action_queue()
        self.action_queue.register_actor(self)

        # Combat engine integration
        from game_sys.combat.engine import CombatEngine
        from game_sys.combat.turn_manager import turn_manager
        self._combat_engine = CombatEngine()

        # Register for ticks and collision checks
        time_manager.register(self)
        time_manager.register(self.action_queue)
        turn_manager.register(self)                                    # NEW
        collision_manager.register(self)
        status_manager.register_actor(self)
        # Note: PassiveManager.register_actor moved to CharacterFactory
        # Combat/effects hooks
        self.weapon: Any = None
        self.offhand: Any = None  # For dual wielding
        self.stat_bonus_ids: List[str] = []
        self.passive_ids: List[str] = []
        self.skill_effect_ids: List[str] = []

        # Coordinates & facing
        self.position: Tuple[float, float] = (0.0, 0.0)
        self.facing_vector: Tuple[float, float] = (1.0, 0.0)

        # Emit spawn event
        emit(ON_SPAWN, actor=self)
    # --- Stat & progression ---

    def get_stat(self, stat_name: str) -> float:
        """Return effective stat (base or derived) including bonuses."""
        return ScalingManager.compute_stat(self, stat_name)

    def gain_xp(self, amount: float):
        """Award XP and handle level-ups."""
        character_logger.debug(f"{self.name} gained {amount} XP")
        self.xp += amount
        while self.xp >= self._xp_for_next() and self.level < self.max_level:
            self.xp -= self._xp_for_next()
            old_level = self.level
            self.level += 1
            character_logger.info(f"{self.name} leveled up from {old_level} to {self.level}")
            emit(ON_LEVEL_UP, actor=self, new_level=self.level)
            self.on_level_up()

    def _xp_for_next(self) -> float:
        """Calculate XP threshold from config formula: base * level^exponent."""
        cfg = ConfigManager()
        base = cfg.get('constants.leveling.xp_base', 100)
        exp = cfg.get('constants.leveling.xp_exponent', 1.0)
        return base * (self.level ** exp)

    def on_level_up(self):
        """Hook called after leveling up."""
        self.update_stats()
        self.restore_all()

    @log_exception
    def update_stats(self):
        """Recompute pools and clamp current values."""
        character_logger.debug(f"Updating stats for {self.name}")
        self.max_health = self.get_stat('health')
        self.max_mana = self.get_stat('mana')
        self.max_stamina = self.get_stat('stamina')
        self.current_health = min(self.current_health, self.max_health)
        self.current_mana = min(self.current_mana, self.max_mana)
        self.current_stamina = min(self.current_stamina, self.max_stamina)

    def restore_all(self):
        """Restore health, mana, and stamina, but respect active drain effects."""
        # Check for active resource drain effects by effect ID pattern
        active_drains = set()
        for eff_id in self.active_statuses.keys():
            if 'resource_drain_' in eff_id:
                # Extract resource from effect ID (e.g., 'resource_drain_mana_2_9999')
                parts = eff_id.split('_')
                if len(parts) >= 3:
                    resource = parts[2]  # 'mana', 'health', or 'stamina'
                    active_drains.add(resource)
        
        # Only restore resources that aren't being drained
        if 'health' not in active_drains:
            self.current_health = self.max_health
        if 'mana' not in active_drains:
            self.current_mana = self.max_mana
        if 'stamina' not in active_drains:
            self.current_stamina = self.max_stamina

    # --- Regeneration ---

    @log_exception
    def regenerate(self, dt: float):
        """Apply passive regeneration if enabled."""
        if self.current_health <= 0:
            return
        
        old_health = self.current_health
        old_mana = self.current_mana
        old_stamina = self.current_stamina
        
        self.current_health = min(
            self.max_health,
            self.current_health + self.get_stat('health_regeneration') * dt
        )
        self.current_mana = min(
            self.max_mana,
            self.current_mana + self.get_stat('mana_regeneration') * dt
        )
        self.current_stamina = min(
            self.max_stamina,
            self.current_stamina + self.get_stat('stamina_regeneration') * dt
        )
        
        # Only log if there was a significant change
        if (abs(self.current_health - old_health) > 0.1 or
                abs(self.current_mana - old_mana) > 0.1 or
                abs(self.current_stamina - old_stamina) > 0.1):
            character_logger.debug(
                f"{self.name} regenerated: "
                f"HP: {_fmt(old_health)} → {_fmt(self.current_health)}, "
                f"MP: {_fmt(old_mana)} → {_fmt(self.current_mana)}, "
                f"SP: {_fmt(old_stamina)} → {_fmt(self.current_stamina)}"
            )

    # --- Status effects ---

    @log_exception
    def apply_status(self, effect: Effect):
        """Add or refresh a status effect."""
        character_logger.info(
            f"Applying status effect {effect.id} to {self.name}"
        )
        emit(ON_STATUS_APPLIED, actor=self, effect=effect.id)
        self.active_statuses[effect.id] = (effect, effect.duration)
        # ensure status effects are ticked
        from game_sys.effects.status_manager import status_manager
        status_manager.register_actor(self)

    # --- Actions & combat ---

    @log_exception
    def attack_targets(self, targets):
        """
        Schedule an attack; actual resolution happens when the cooldown
        expires (TurnManager → CombatEngine).  Returns `True` if enqueued.
        """
        cd = self.get_stat("attack_cooldown")
        character_logger.debug(
            f"{self.name} scheduled attack with {len(targets)} targets, cooldown: {cd}"
        )
        return self.action_queue.schedule(
            self, "attack", cd, targets=targets)

    @log_exception
    def schedule_action(self, action_name: str, **params) -> bool:
        cooldown = self.get_stat('attack_cooldown')
        character_logger.debug(
            f"{self.name} scheduling action '{action_name}' with cooldown {cooldown}"
        )
        return self.action_queue.schedule(
            self, action_name, cooldown, **params)

    @log_exception
    def consume_ready_actions(self) -> List[Tuple[str, Dict]]:
        actions = self.action_queue.consume(self)
        if actions:
            character_logger.debug(
                f"{self.name} consumed {len(actions)} ready actions"
            )
        return actions

    @log_exception
    def take_damage(self, amount: float, attacker: Any = None) -> float:
        """
        Apply incoming damage, track metadata, clamp at zero,
        and emit death exactly once when crossing below zero.
        Shield blocking is now handled by the combat engine.
        """
        # If already dead, nothing to do
        if self.current_health <= 0:
            return 0.0
        
        self.last_hit_by = attacker
        self.last_hit_damage = amount

        prev_hp = self.current_health
        self.current_health = max(0.0, self.current_health - amount)

        attacker_name = attacker.name if attacker else 'environment'
        character_logger.debug(
            f"{self.name} takes {amount} damage from {attacker_name} "
            f"(HP: {_fmt(prev_hp)} → {_fmt(self.current_health)})"
        )

        # Trigger death once
        if prev_hp > 0 and self.current_health == 0:
            self.killed_by = attacker
            if attacker:
                attacker.kills.append(self)
            emit(ON_DEATH, victim=self, killer=attacker)
            
            character_logger.info(f"{self.name} has died.")
            
            # Remove from turn manager to stop processing actions
            from game_sys.combat.turn_manager import turn_manager
            turn_manager.unregister(self)

        return self.current_health

    @log_exception
    async def use_skill(self, skill_id: str, target: Any) -> bool:
        skill = load_skill(skill_id)
        if self.current_stamina < skill.stamina_cost:
            character_logger.info(
                f"{self.name} tried to use skill {skill_id}, but not enough stamina."
            )
            return False
        if self.skill_cooldowns.get(skill_id, 0) > 0:
            character_logger.info(
                f"{self.name} tried to use skill {skill_id}, but it's on cooldown."
            )
            return False
        self.current_stamina -= skill.stamina_cost
        dmg = skill.execute(self, target)
        self.skill_cooldowns[skill_id] = skill.cooldown
        emit(ON_ABILITY_CAST, actor=self, ability=skill_id, damage=dmg, target=target)
        character_logger.info(
            f"{self.name} used skill {skill_id} on {target.name}, dealing {dmg} damage."
        )
        return True

    @log_exception
    async def cast_spell(self, spell_id: str, target: Any) -> bool:
        spell = load_spell(spell_id)
        if self.spell_cooldowns.get(spell_id, 0) > 0:
            character_logger.info(
                f"{self.name} tried to cast spell {spell_id}, but it's on cooldown."
            )
            return False
        result = await spell.cast(self, target)
        character_logger.info(
            f"{self.name} cast spell {spell_id} on {target.name}."
        )
        return result

    @log_exception
    def tick(self, dt: float):
        """Called every frame by TimeManager to update regen and cooldowns."""
        self.regenerate(dt)
        
        # Update cooldowns
        for cd_map in (self.skill_cooldowns, self.spell_cooldowns):
            expired_cooldowns = []
            for key in list(cd_map):
                cd_map[key] -= dt
                if cd_map[key] <= 0:
                    expired_cooldowns.append(key)
                    del cd_map[key]
            
            if expired_cooldowns:
                is_skill = cd_map is self.skill_cooldowns
                type_name = "skill" if is_skill else "spell"
                character_logger.debug(
                    f"{self.name} cooldowns expired: "
                    f"{type_name}s {expired_cooldowns}"
                )

    def is_alive(self) -> bool:
        if self.current_health <= 0 and hasattr(self, 'name'):
            character_logger.debug(
                f"{self.name} is dead (health: {self.current_health})"
            )
        return self.current_health > 0

    def die(self):
        """Force death by removing all health."""
        character_logger.info(f"{self.name} has died")
        self.take_damage(self.current_health)

    # --- Item usage & abilities ---

    @log_exception
    def use_item(self, item_id: str) -> bool:
        item = self.inventory.find(item_id)
        if not item:
            character_logger.info(
                f"{self.name} tried to use item {item_id}, but it was not found."
            )
            return False
        item.apply(self)
        self.inventory.remove_item(item)
        emit(ON_ITEM_USED, actor=self, item=item_id)
        character_logger.info(f"{self.name} used item {item_id}.")
        return True

    @log_exception
    def start_ability(self, ability_id: str, target: Any = None):
        target_name = target.name if target else 'no target'
        character_logger.info(
            f"{self.name} started using ability {ability_id} on {target_name}."
        )
        emit(ON_ABILITY_CAST, actor=self, ability=ability_id, target=target)

    # --- Equipment ---

    @log_exception
    def equip_weapon(self, weapon: Any):
        """Equip the given weapon on this actor."""
        # Unequip current weapon first
        if self.weapon:
            self._unequip_weapon()
        
        # Merge weapon stats into base_stats
        if hasattr(weapon, 'stats'):
            for stat_name, bonus in weapon.stats.items():
                current_value = self.base_stats.get(stat_name, 0.0)
                self.base_stats[stat_name] = current_value + bonus
        
        # Add weapon effect IDs
        if hasattr(weapon, 'effect_ids'):
            self.skill_effect_ids.extend(weapon.effect_ids)
        
        self.weapon = weapon
        
        character_logger.info(f"{self.name} equipped weapon {weapon.id}.")
        
        # If it's a two-handed weapon, unequip offhand
        if hasattr(weapon, 'two_handed') and weapon.two_handed:
            self.unequip_offhand()

    def _unequip_weapon(self):
        """Helper to unequip current weapon and remove its bonuses."""
        unequipped_weapon = self.weapon
        
        if self.weapon and hasattr(self.weapon, 'stats'):
            # Remove weapon stat bonuses
            for stat_name, bonus in self.weapon.stats.items():
                current_value = self.base_stats.get(stat_name, 0.0)
                self.base_stats[stat_name] = max(0.0, current_value - bonus)
            
            # Remove weapon effect IDs
            if hasattr(self.weapon, 'effect_ids'):
                for effect_id in self.weapon.effect_ids:
                    if effect_id in self.skill_effect_ids:
                        self.skill_effect_ids.remove(effect_id)
        
        character_logger.info(f"{self.name} unequipped their weapon.")
        
        self.weapon = None
        # Re-compute pools after unequipping
        self.update_stats()
        
        return unequipped_weapon

    @log_exception
    def equip_offhand(self, item: Any):
        """Equip an offhand item (shield, dagger, etc.) for dual wielding."""
        # Can't dual wield with two-handed weapons
        if (self.weapon and hasattr(self.weapon, 'two_handed') and
                self.weapon.two_handed):
            character_logger.info(
                f"{self.name} can't equip offhand with two-handed weapon."
            )
            return False
            
        # Only allow items specifically designed for offhand use
        if (hasattr(item, 'slot') and item.slot == 'offhand' and
                hasattr(item, 'dual_wield') and item.dual_wield):
            # Unequip current offhand first
            if self.offhand:
                self._unequip_offhand()
            
            # Merge offhand stats into base_stats
            if hasattr(item, 'stats'):
                for stat_name, bonus in item.stats.items():
                    current_value = self.base_stats.get(stat_name, 0.0)
                    self.base_stats[stat_name] = current_value + bonus
            
            # Add offhand effect IDs
            if hasattr(item, 'effect_ids'):
                self.skill_effect_ids.extend(item.effect_ids)
            
            self.offhand = item
            character_logger.info(
                f"{self.name} equipped offhand item {item.id}."
            )
            return True
        else:
            # Item is not suitable for offhand slot
            character_logger.info(
                f"{self.name} can't equip {item.id} in offhand slot."
            )
            return False

    def _unequip_offhand(self):
        """Helper to unequip current offhand and remove its bonuses."""
        unequipped_offhand = self.offhand
        
        if not self.offhand:
            return None

        if hasattr(self.offhand, 'stats'):
            # Remove offhand stat bonuses
            for stat_name, bonus in self.offhand.stats.items():
                current_value = self.base_stats.get(stat_name, 0.0)
                self.base_stats[stat_name] = max(0.0, current_value - bonus)
            
            # Remove offhand effect IDs
            if hasattr(self.offhand, 'effect_ids'):
                for effect_id in self.offhand.effect_ids:
                    if effect_id in self.skill_effect_ids:
                        self.skill_effect_ids.remove(effect_id)
        
        character_logger.debug(f"{self.name} removed offhand bonuses")
        self.offhand = None
        # Re-compute pools after unequipping
        self.update_stats()
        
        return unequipped_offhand

    def unequip_weapon(self):
        """Remove the main weapon."""
        return self._unequip_weapon()

    def unequip_offhand(self):
        """Remove the offhand item."""
        character_logger.info(f"{self.name} unequipped their offhand item.")
        return self._unequip_offhand()

    @log_exception
    def unequip_armor(self, slot: str):
        """Unequip armor from the specified slot."""
        slot_attr = f"equipped_{slot}"
        equipped_item = getattr(self, slot_attr, None)
        
        if equipped_item:
            # Remove armor stat bonuses
            if hasattr(equipped_item, 'stats'):
                for stat_name, bonus in equipped_item.stats.items():
                    current_value = self.base_stats.get(stat_name, 0.0)
                    new_value = max(0.0, current_value - bonus)
                    self.base_stats[stat_name] = new_value
            
            # Remove armor effect IDs
            if hasattr(equipped_item, 'effect_ids'):
                for effect_id in equipped_item.effect_ids:
                    if effect_id in self.skill_effect_ids:
                        self.skill_effect_ids.remove(effect_id)
            
            # Clear the slot
            setattr(self, slot_attr, None)
            
            item_name = equipped_item.name
            msg = f"{self.name} unequipped {slot} armor: {item_name}"
            character_logger.info(msg)
            
            # Re-compute pools after unequipping
            self.update_stats()
            
            return equipped_item
        else:
            character_logger.debug(f"{self.name} has no {slot} armor equipped")
            return None

    def get_total_damage(self) -> float:
        """Calculate total damage from main weapon and offhand weapon."""
        total_damage = 0.0
        
        # Main weapon damage
        if self.weapon and hasattr(self.weapon, 'base_damage'):
            total_damage += self.weapon.base_damage
            
        # Offhand weapon damage (only for actual OffhandWeapon instances)
        if (self.offhand and
                hasattr(self.offhand, 'get_effective_damage')):
            # Use the effective damage calculation for offhand weapons
            total_damage += self.offhand.get_effective_damage()
            
        return total_damage

    def get_total_defense(self) -> float:
        """Calculate total defense from base stats, armor and shields."""
        total_defense = self.get_stat('defense')
        
        # Add offhand shield defense (already included in base_stats via Equipment.apply)
        # This method now just returns the computed defense stat
        return total_defense

    # --- Interaction & serialization ---

    @log_exception
    def interact_with(self, target: Any):
        emit(ON_INTERACT, actor=self, target=target)
        character_logger.info(f"{self.name} interacted with {target.name}.")

    @log_exception
    def serialize(self) -> str:
        """Return JSON representing actor state."""
        data = {
            'name': self.name,
            'base_stats': self.base_stats,
            'level': self.level,
            'xp': self.xp,
            'current_health': self.current_health,
            'current_mana': self.current_mana,
            'current_stamina': self.current_stamina,
            'grade': self.grade,
            'rarity': self.rarity,
            'gold': self.gold,
            'statuses': [eid for eid in self.active_statuses],
            'skills': self.skill_effect_ids,
            'inventory': self.inventory.list_items()
        }
        character_logger.debug(f"Serializing actor {self.name}")
        return json.dumps(data)

    @log_exception
    def deserialize(self, data_str: str):
        """Restore actor state from JSON string."""
        character_logger.debug(f"Deserializing actor {self.name}")
        data = json.loads(data_str)
        self.base_stats.update(data.get('base_stats', {}))
        self.level = data.get('level', self.level)
        self.xp = data.get('xp', self.xp)
        self.current_health = data.get('current_health', self.current_health)
        self.current_mana = data.get('current_mana', self.current_mana)
        
        # Split long line to avoid lint error
        self.current_stamina = data.get(
            'current_stamina', self.current_stamina
        )
        
        self.grade = data.get('grade', self.grade)
        self.rarity = data.get('rarity', self.rarity)
        self.gold = data.get('gold', self.gold)
        character_logger.info(
            f"Actor {self.name} state restored from saved data"
        )

    def __str__(self) -> str:
        # Format base_stats
        stats_str = ", ".join(
            f"{k}: {_fmt(v)}" for k, v in self.base_stats.items()
        )

        # Inventory list
        inv = self.inventory.list_items()
        inv_str = ", ".join(item.id for item in inv) if inv else "None"

        character_logger.debug(
            f"Generating string representation for {self.name}"
        )
        
        return (
            f"{self.name} (Level {self.level})\n"
            f"Health: {_fmt(self.current_health)}/{_fmt(self.max_health)}, "
            f"Mana: {_fmt(self.current_mana)}/{_fmt(self.max_mana)}, "
            f"Stamina: {_fmt(self.current_stamina)}/{_fmt(self.max_stamina)}\n"
            f"XP: {_fmt(self.xp)}/{_fmt(self._xp_for_next())}\n"
            f"Stats: {stats_str}\n"
            f"Inventory: {inv_str}\n"
            f"Job: {getattr(self, 'job_name', 'None')} "
            f"(Grade: {getattr(self, 'grade', 'N/A')}, "
            f"Rarity: {getattr(self, 'rarity', 'N/A')})\n"
            f"Team: {self.team}\n"
            f"Facing: ({_fmt(self.facing_vector[0])}, "
            f"{_fmt(self.facing_vector[1])})  "
            f"Position: ({_fmt(self.position[0])}, {_fmt(self.position[1])})"
        )

    # --- Compatibility properties for tests ---
    
    @property
    def health(self) -> float:
        """Compatibility property for current health."""
        character_logger.debug(
            f"Deprecated health property accessed for {self.name}"
        )
        return self.current_health
    
    @health.setter
    def health(self, value: float):
        """Compatibility setter for current health."""
        character_logger.debug(
            f"Deprecated health setter used for {self.name}: {value}"
        )
        self.current_health = value
    
    @property
    def stats(self):
        """Compatibility property for stats interface."""
        character_logger.debug(
            f"Deprecated stats property accessed for {self.name}"
        )
        from game_sys.combat.capabilities import StatsWrapper
        return StatsWrapper(self)
    
    @property
    def defending(self) -> bool:
        """Compatibility property for defending state."""
        character_logger.debug(
            f"Deprecated defending property accessed for {self.name}"
        )
        return getattr(self, '_defending', False)
    
    @defending.setter
    def defending(self, value: bool):
        """Compatibility setter for defending state."""
        character_logger.debug(
            f"Deprecated defending setter used for {self.name}: {value}"
        )
        self._defending = value


class Player(Actor):
    """Player-controlled actor with learning capabilities."""

    def __init__(self, name: str, base_stats: Dict[str, float], **overrides):
        super().__init__(name, base_stats, **overrides)
        from game_sys.skills.learning_system import LearningSystem
        self.learning = LearningSystem(self)
        from game_sys.character.leveling_manager import LevelingManager
        self.leveling_manager = LevelingManager()
        from game_sys.character.job_manager import JobManager
        JobManager.assign(self, 'commoner')
        character_logger.info(f"Initialized Player {name} with systems")


class NPC(Actor):
    """Non-player character (dialogue, quests)."""
    pass


class Enemy(Actor):
    """Enemy actor with AI behaviors."""
    def set_behavior(self, state: str):
        character_logger.debug(
            f"Enemy {self.name} behavior changed to {state}"
        )
        self.behavior_state = state
