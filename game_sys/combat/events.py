# game_sys/combat/events.py
"""
Combat event definitions and data structures.

This module defines structured events emitted during combat operations,
providing a clean interface for UI, logging, and other systems to
respond to combat outcomes.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from game_sys.character.actor import Actor
    from game_sys.core.damage_types import DamageType


class CombatEventType(Enum):
    """Types of combat events."""
    ATTACK_STARTED = "attack_started"
    ATTACK_MISSED = "attack_missed"
    ATTACK_BLOCKED = "attack_blocked"
    ATTACK_DODGED = "attack_dodged"
    CRITICAL_HIT = "critical_hit"
    DAMAGE_DEALT = "damage_dealt"
    HEALING_APPLIED = "healing_applied"
    DEATH = "death"


@dataclass
class CombatEvent:
    """Base combat event with common fields."""
    event_type: CombatEventType
    attacker: Optional[Actor] = None
    defender: Optional[Actor] = None
    damage: float = 0.0
    healing: float = 0.0
    damage_type: Optional[DamageType] = None
    weapon: Optional[Any] = None
    was_critical: bool = False
    was_blocked: bool = False
    was_dodged: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackEvent(CombatEvent):
    """Event for attack attempts."""
    hit_chance: float = 1.0
    base_damage: float = 0.0
    final_damage: float = 0.0
    was_hit: bool = False


@dataclass
class DefenseEvent(CombatEvent):
    """Event for defensive actions."""
    defense_value: float = 0.0
    damage_reduced: float = 0.0
    block_chance: float = 0.0


@dataclass
class CombatOutcome:
    """Result of a complete combat action."""
    success: bool
    events: list[CombatEvent]
    total_damage: float = 0.0
    total_healing: float = 0.0
    description: str = ""

    def add_event(self, event: CombatEvent):
        """Add an event to this outcome."""
        self.events.append(event)
        if event.damage > 0:
            self.total_damage += event.damage
        if event.healing > 0:
            self.total_healing += event.healing

    def merge(self, other: 'CombatOutcome'):
        """Merge another outcome's events and totals into this one."""
        self.events.extend(other.events)
        self.total_damage += other.total_damage
        self.total_healing += other.total_healing
        # Success should be false if either outcome failed
        self.success = self.success and other.success
        if other.description and not self.description:
            self.description = other.description
