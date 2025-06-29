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
import random
from typing import Any, Dict, List, Optional, Tuple
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
        self.max_health: float     = self.get_stat('health')
        self.current_health: float = self.max_health
        self.max_mana: float       = self.get_stat('mana')
        self.current_mana: float   = self.max_mana
        self.max_stamina: float    = self.get_stat('stamina')
        self.current_stamina: float= self.max_stamina

        # Quality & economy
        self.grade: Optional[int] = None
        self.rarity: Optional[str]= None
        self.gold: int            = 0

        # Resistances/weaknesses
        self.weaknesses: Dict[DamageType, float]  = {}
        self.resistances: Dict[DamageType, float] = {}

        # Combat metadata
        self.last_hit_by: Optional[Actor] = None
        self.last_hit_damage: float       = 0.0
        self.killed_by: Optional[Actor]   = None
        self.kills: List[Actor]           = []

        # Status effects
        self.active_statuses: Dict[str, Tuple[Effect, float]] = {}

        # Systems
        self.inventory = get_inventory_manager(self)
        self.action_queue = get_action_queue()
        self.action_queue.register_actor(self)

        # Register for ticks (regen & status)
        time_manager.register(self)
        time_manager.register(self.action_queue)

        # Combat/effects hooks
        self.weapon: Any               = None
        self.stat_bonus_ids: List[str]   = []
        self.passive_ids: List[str]      = []
        self.skill_effect_ids: List[str] = []

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
        exp  = cfg.get('constants.leveling.xp_exponent', 1.0)
        return base * (self.level ** exp)

    def on_level_up(self):
        """Hook called after leveling up."""
        self.update_stats()
        self.restore_all()

    def update_stats(self):
        """Recompute pools and clamp current values."""
        self.max_health     = self.get_stat('health')
        self.max_mana       = self.get_stat('mana')
        self.max_stamina    = self.get_stat('stamina')
        self.current_health = min(self.current_health, self.max_health)
        self.current_mana   = min(self.current_mana, self.max_mana)
        self.current_stamina= min(self.current_stamina, self.max_stamina)

    def restore_all(self):
        """Fully restore health, mana, and stamina."""
        self.current_health  = self.max_health
        self.current_mana    = self.max_mana
        self.current_stamina = self.max_stamina

    # --- Regeneration ---
    def regenerate(self, dt: float):
        """Apply passive regeneration if enabled."""
        self.current_health  = min(self.max_health,  self.current_health  + self.get_stat('health_regeneration')  * dt)
        self.current_mana    = min(self.max_mana,    self.current_mana    + self.get_stat('mana_regeneration')    * dt)
        self.current_stamina = min(self.max_stamina, self.current_stamina + self.get_stat('stamina_regeneration') * dt)

    # --- Status effects ---
    def apply_status(self, effect: Effect):
        """Add or refresh a status effect."""
        self.active_statuses[effect.id] = (effect, effect.duration)

    def tick_statuses(self, dt: float):
        """Reduce durations and remove expired statuses."""
        # Handled by StatusEffectManager

    # --- Actions & combat ---
    async def attack_targets(self, targets: List[Any]):
        """
        Deals damage up to max_targets and emits ON_ATTACK_HIT asynchronously.
        """
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
        """Apply incoming damage, track metadata, and handle death."""
        self.last_hit_by     = attacker
        self.last_hit_damage = amount
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            self.killed_by = attacker
            if attacker:
                attacker.kills.append(self)
            emit(ON_DEATH, victim=self, killer=attacker)
        return self.current_health

    def is_alive(self) -> bool:
        return self.current_health > 0

    def die(self):
        """Force death."""
        self.take_damage(self.current_health)

    # --- Item usage & abilities ---
    def use_item(self, item_id: str) -> bool:
        """Consume an item and apply its effects."""
        item = self.inventory.find(item_id)
        if not item:
            return False
        item.apply(self)
        self.inventory.remove_item(item)
        emit(ON_ITEM_USED, actor=self, item=item_id)
        return True

    def start_ability(self, ability_id: str, target: Any = None):
        """Trigger an ability cast event."""
        emit(ON_ABILITY_CAST, actor=self, ability=ability_id, target=target)

    def cancel_action(self):
        """Interrupt all queued actions."""
        _ = self.consume_ready_actions()
    # --- Equipment ---
    def equip_weapon(self, weapon: Any):
        """
        Equip the given weapon on this actor.
        Weapons should have at least a `base_damage` attribute
        and optionally `effect_ids`.
        """
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
            'statuses': self.statuses,
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
        self.statuses = data.get('statuses', self.statuses)
        self.skill_effect_ids = data.get('skills', self.skill_effect_ids)

# Subclasses
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
