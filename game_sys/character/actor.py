# game_sys/character/actor.py
"""
Module: game_sys.character.actor

Defines the core Actor hierarchy, encapsulating character state,
stats, pools, progression, inventory, action scheduling, combat interactions,
status effects, item usage, abilities, interactions, serialization, and metadata.
"""

from __future__ import annotations
import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple
from game_sys.managers.collision_manager import collision_manager
from game_sys.config.config_manager import ConfigManager
from game_sys.config.feature_flags import FeatureFlags
from game_sys.core.scaling_manager import ScalingManager
from game_sys.core.damage_types import DamageType
from game_sys.effects.base import Effect
from game_sys.hooks.hooks_setup import (
    emit,
    ON_ATTACK_HIT,
    ON_DEATH,
    ON_LEVEL_UP,
    ON_STATUS_APPLIED,
    ON_STATUS_EXPIRED,
    ON_ITEM_USED,
    ON_ABILITY_CAST,
    ON_INTERACT
)
from game_sys.managers.factories import get_action_queue, get_inventory_manager
from game_sys.managers.time_manager import time_manager
from game_sys.skills.skill_loader import load_skill
from game_sys.magic.spell_loader import load_spell

flags = FeatureFlags()


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
        self.name = name
        cfg = ConfigManager()

        # Initialize base stats
        defaults = cfg.get('constants.stats_defaults', {})
        self.base_stats: Dict[str, float] = {s: defaults.get(s, 0.0) for s in defaults}
        self.base_stats.update(base_stats)
        for k, v in overrides.items():
            self.base_stats[k] = v

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
        self.stamina = self.max_stamina
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

        # Status effects
        self.active_statuses: Dict[str, Tuple[Effect, float]] = {}

        # Systems
        self.inventory = get_inventory_manager(self)
        self.action_queue = get_action_queue()
        self.action_queue.register_actor(self)

        # Register for ticks and collision checks
        time_manager.register(self)
        time_manager.register(self.action_queue)
        collision_manager.register(self)

        # Combat/effects hooks
        self.weapon: Any = None
        self.stat_bonus_ids: List[str] = []
        self.passive_ids: List[str] = []
        self.skill_effect_ids: List[str] = []

        # Coordinates & facing
        self.position: Tuple[float, float] = (0.0, 0.0)
        self.facing_vector: Tuple[float, float] = (1.0, 0.0)

    # --- Stat & progression ---

    def get_stat(self, stat_name: str) -> float:
        """Return effective stat (base or derived) including bonuses."""
        return ScalingManager.compute_stat(self, stat_name)

    def gain_xp(self, amount: float):
        """Award XP and handle level-ups."""
        self.xp += amount
        while self.xp >= self._xp_for_next() and self.level < self.max_level:
            self.xp -= self._xp_for_next()
            self.level += 1
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

    def update_stats(self):
        """Recompute pools and clamp current values."""
        self.max_health = self.get_stat('health')
        self.max_mana = self.get_stat('mana')
        self.max_stamina = self.get_stat('stamina')
        self.current_health = min(self.current_health, self.max_health)
        self.current_mana = min(self.current_mana, self.max_mana)
        self.current_stamina = min(self.current_stamina, self.max_stamina)

    def restore_all(self):
        """Fully restore health, mana, and stamina."""
        self.current_health = self.max_health
        self.current_mana = self.max_mana
        self.current_stamina = self.max_stamina

    # --- Regeneration ---

    def regenerate(self, dt: float):
        """Apply passive regeneration if enabled."""
        if self.current_health <= 0:
            return
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

    # --- Status effects ---

    def apply_status(self, effect: Effect):
        """Add or refresh a status effect."""
        emit(ON_STATUS_APPLIED, actor=self, effect=effect.id)
        self.active_statuses[effect.id] = (effect, effect.duration)

    # --- Actions & combat ---

    async def attack_targets(self, targets: List[Any]):
        """Deals damage up to max_targets and emits ON_ATTACK_HIT asynchronously."""
        max_t = int(self.get_stat('max_targets'))
        for tgt in targets[:max_t]:
            dmg = ScalingManager.compute_damage(self, tgt, self.weapon)
            await self._process_attack(dmg, tgt)
            emit(ON_ATTACK_HIT, source=self, target=tgt, damage=dmg)

    async def _process_attack(self, damage: float, target: Any):
        """Simulate attack processing with cooldown delay."""
        cooldown = self.get_stat('attack_cooldown')
        await asyncio.sleep(cooldown)
        target.take_damage(damage, self)

    def schedule_action(self, action_name: str, **params) -> bool:
        cooldown = self.get_stat('attack_cooldown')
        return self.action_queue.schedule(self, action_name, cooldown, **params)

    def consume_ready_actions(self) -> List[Tuple[str, Dict]]:
        return self.action_queue.consume(self)

    def take_damage(self, amount: float, attacker: Any = None) -> float:
        """
        Apply incoming damage, track metadata, clamp at zero,
        and emit death exactly once when crossing below zero.
        """
        self.last_hit_by     = attacker
        self.last_hit_damage = amount

        # If already dead, nothing to do
        if self.current_health <= 0:
            return 0.0

        prev_hp = self.current_health
        self.current_health = max(0.0, self.current_health - amount)

        # Trigger death once
        if prev_hp > 0 and self.current_health == 0:
            self.killed_by = attacker
            if attacker:
                attacker.kills.append(self)
            emit(ON_DEATH, victim=self, killer=attacker)
            print(f"{self.name} has been defeated!")

        return self.current_health

    async def use_skill(self, skill_id: str, target: Any) -> bool:
        skill = load_skill(skill_id)
        if self.stamina < skill.stamina_cost:
            return False
        if self.skill_cooldowns.get(skill_id, 0) > 0:
            return False
        self.stamina -= skill.stamina_cost
        dmg = skill.execute(self, target)
        self.skill_cooldowns[skill_id] = skill.cooldown
        emit(ON_ABILITY_CAST, actor=self, ability=skill_id, damage=dmg, target=target)
        return True

    async def cast_spell(self, spell_id: str, target: Any) -> bool:
        spell = load_spell(spell_id)
        if self.spell_cooldowns.get(spell_id, 0) > 0:
            return False
        return await spell.cast(self, target)

    def tick(self, dt: float):
        """Called every frame by TimeManager to update regen and cooldowns."""
        self.regenerate(dt)
        for cd_map in (self.skill_cooldowns, self.spell_cooldowns):
            for key in list(cd_map):
                cd_map[key] -= dt
                if cd_map[key] <= 0:
                    del cd_map[key]

    def is_alive(self) -> bool:
        return self.current_health > 0

    def die(self):
        """Force death by removing all health."""
        self.take_damage(self.current_health)

    # --- Item usage & abilities ---

    def use_item(self, item_id: str) -> bool:
        item = self.inventory.find(item_id)
        if not item:
            return False
        item.apply(self)
        self.inventory.remove_item(item)
        emit(ON_ITEM_USED, actor=self, item=item_id)
        return True

    def start_ability(self, ability_id: str, target: Any = None):
        emit(ON_ABILITY_CAST, actor=self, ability=ability_id, target=target)

    def cancel_action(self):
        """Interrupt all queued actions."""
        _ = self.consume_ready_actions()

    # --- Equipment ---

    def equip_weapon(self, weapon: Any):
        """Equip the given weapon on this actor."""
        self.weapon = weapon

    # --- Interaction & serialization ---

    def interact_with(self, target: Any):
        emit(ON_INTERACT, actor=self, target=target)

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
        return json.dumps(data)

    def deserialize(self, data_str: str):
        """Restore actor state from JSON string."""
        data = json.loads(data_str)
        self.base_stats.update(data.get('base_stats', {}))
        self.level = data.get('level', self.level)
        self.xp = data.get('xp', self.xp)
        self.current_health = data.get('current_health', self.current_health)
        self.current_mana = data.get('current_mana', self.current_mana)
        self.current_stamina = data.get('current_stamina', self.current_stamina)
        self.grade = data.get('grade', self.grade)
        self.rarity = data.get('rarity', self.rarity)
        self.gold = data.get('gold', self.gold)

    def __str__(self) -> str:
        return (
            f"{self.name} (Level {self.level})\n"
            f"Health: {self.current_health}/{self.max_health}, "
            f"Mana: {self.current_mana}/{self.max_mana}, "
            f"Stamina: {self.current_stamina}/{self.max_stamina}\n"
            f"XP: {self.xp}/{self._xp_for_next()}\n"
            f"Stats: {', '.join(f'{k}: {v}' for k, v in self.base_stats.items())}\n"
            f"Inventory: {', '.join(item.id for item in self.inventory.list_items())}\n"
            f"Weapon: {self.weapon.name if self.weapon else 'None'}\n"
            f"Active Statuses: {', '.join(self.active_statuses.keys()) or 'None'}"
        )


class Player(Actor):
    """Player-controlled actor with learning capabilities."""

    def __init__(self, name: str, base_stats: Dict[str, float], **overrides):
        super().__init__(name, base_stats, **overrides)
        from game_sys.skills.learning_system import LearningSystem
        self.learning = LearningSystem(self)
        from game_sys.character.job_manager import JobManager
        JobManager.assign(self, 'commoner')


class NPC(Actor):
    """Non-player character (dialogue, quests)."""
    pass


class Enemy(Actor):
    """Enemy actor with AI behaviors."""
    def set_behavior(self, state: str):
        self.behavior_state = state
