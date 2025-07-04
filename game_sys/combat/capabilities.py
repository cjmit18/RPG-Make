# game_sys/combat/capabilities.py
"""
Combat capabilities and derived stats calculation.

This module provides the CombatCapabilities class which wraps an Actor
and exposes computed combat-related stats like attack, defense, crit chance,
block chance, etc. This serves as the interface expected by tests and
provides a clean abstraction over the raw Actor stats.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional
from dataclasses import dataclass

if TYPE_CHECKING:
    from game_sys.character.actor import Actor

from game_sys.core.scaling_manager import ScalingManager
from game_sys.logging import combat_logger, log_exception


@dataclass
class CombatStats:
    """Computed combat statistics for an actor."""
    attack: float
    defense: float
    max_health: float
    current_health: float
    crit_chance: float
    crit_multiplier: float
    block_chance: float
    dodge_chance: float
    accuracy: float
    max_targets: int
    attack_cooldown: float
    

class CombatCapabilities:
    """
    Wrapper around an Actor that exposes combat-related capabilities.
    
    This class serves as the interface between the combat system and actors,
    providing computed stats and combat methods while keeping the core
    Actor class focused on state management.
    """
    
    def __init__(self, character: Actor, enemy: Optional[Actor] = None,
                 rng: Any = None):
        """
        Initialize combat capabilities for a character.
        
        Args:
            character: The actor to wrap
            enemy: Optional enemy for context-dependent calculations
            rng: Optional RNG instance for deterministic testing
        """
        self.character = character
        self.enemy = enemy
        self.rng = rng or __import__('random')
        combat_logger.debug(
            f"Initialized CombatCapabilities for {character.name}"
            f"{' against ' + enemy.name if enemy else ''}"
        )
    
    def get_combat_stats(self) -> CombatStats:
        """Get computed combat statistics for this actor."""
        stats = CombatStats(
            attack=self.character.get_stat('attack'),
            defense=self.character.get_stat('defense'),
            max_health=self.character.max_health,
            current_health=self.character.current_health,
            crit_chance=self.character.get_stat('crit_chance'),
            crit_multiplier=self.character.get_stat('crit_multiplier'),
            block_chance=self.character.get_stat('block_chance'),
            dodge_chance=self.character.get_stat('dodge_chance'),
            accuracy=self.character.get_stat('accuracy'),
            max_targets=int(self.character.get_stat('max_targets')),
            attack_cooldown=self.character.get_stat('attack_cooldown')
        )
        combat_logger.debug(f"Combat stats for {self.character.name}: {vars(stats)}")
        return stats
    
    def can_attack(self) -> bool:
        """Check if this actor can perform an attack."""
        can_atk = (
            self.character.is_alive() and
            self.character.weapon is not None and
            self.character.current_stamina > 0
        )
        combat_logger.debug(
            f"{self.character.name} can_attack check: {can_atk} "
            f"(alive={self.character.is_alive()}, "
            f"has_weapon={self.character.weapon is not None}, "
            f"stamina={self.character.current_stamina})"
        )
        return can_atk
    
    def can_block(self) -> bool:
        """Check if this actor can block incoming attacks."""
        # Start with zero block chance
        total_block_chance = 0.0
        
        # First, check if the character has an offhand item with block chance
        if self.character.offhand:
            # Handle both block_chance and block_percent (convert % to decimal)
            shield_block_chance = getattr(
                self.character.offhand, 'block_chance',
                getattr(self.character.offhand, 'block_percent', 0) / 100.0
            )
            if shield_block_chance > 0:
                # Shield block chance takes priority
                total_block_chance = shield_block_chance
                combat_logger.debug(
                    f"{self.character.name} has shield block chance: "
                    f"{shield_block_chance}"
                )
        
        # If no shield block chance found, check character's block_chance stat
        if total_block_chance <= 0:
            try:
                stat_block_chance = self.character.get_stat('block_chance')
                if stat_block_chance > 0:
                    total_block_chance = stat_block_chance
                    combat_logger.debug(
                        f"{self.character.name} has stat block chance: "
                        f"{stat_block_chance}"
                    )
            except (AttributeError, KeyError):
                # If stat doesn't exist or there's an error, leave at 0
                combat_logger.debug(
                    f"{self.character.name} has no block_chance stat"
                )
                pass
                
        # Log the total block chance for debugging
        combat_logger.debug(
            f"{self.character.name} total block chance: {total_block_chance:.2f}"
        )
            
        # Check if we have any block chance at all
        if total_block_chance <= 0:
            combat_logger.debug(f"{self.character.name} cannot block (no chance)")
            return False
            
        # Optimization: if block_chance >= 100%, guarantee block
        if total_block_chance >= 1.0:
            combat_logger.debug(
                f"{self.character.name} guaranteed block (chance >= 100%)"
            )
            return True
            
        # Roll for block
        roll = self.rng.random()
        blocked = roll < total_block_chance
        combat_logger.debug(
            f"{self.character.name} block roll: {roll:.3f} vs "
            f"{total_block_chance:.2f} -> {blocked}"
        )
        return blocked
    
    def can_dodge(self) -> bool:
        """Check if this actor successfully dodges an attack."""
        dodge_chance = self.character.get_stat('dodge_chance')
        roll = self.rng.random()
        dodged = roll < dodge_chance
        combat_logger.debug(
            f"{self.character.name} dodge roll: {roll:.3f} vs "
            f"{dodge_chance:.2f} -> {dodged}"
        )
        return dodged
    
    def calculate_base_damage(self) -> float:
        """Calculate base damage before modifiers."""
        if not self.character.weapon:
            # Unarmed damage based on attack stat
            return self.character.get_stat('attack') * 0.1
        
        return getattr(self.character.weapon, 'base_damage', 0.0)
    
    def calculate_damage(self, attacker: Actor, defender: Actor) -> str:
        """
        Calculate damage and apply it to the defender.
        Returns a description string of the outcome.
        
        This method implements the legacy damage calculation for test compatibility:
        1. Base damage = attacker.attack - (defender.defense * 0.05)
        2. Apply damage variance using uniform()
        3. Check for critical hit using random() < 0.1
        4. Apply defending modifier (halve damage if defending)
        5. Round and apply damage
        """
        # Get base stats
        attacker_attack = attacker.get_stat('attack')
        defender_defense = defender.get_stat('defense')
        
        # Calculate base damage: attack - (defense * 0.05)
        base_damage = attacker_attack - (defender_defense * 0.05)
        
        # Apply variance using uniform() - legacy tests expect uniform(0.8, 1.2)
        # but tests pass 1.0 for deterministic results
        variance = self.rng.uniform(0.8, 1.2)
        damage = base_damage * variance
        
        # Check for critical hit (legacy uses 0.1 threshold)
        is_critical = self.rng.random() < 0.1
        if is_critical:
            damage *= 2.0
        
        # Apply defending modifier
        if getattr(defender, 'defending', False):
            damage *= 0.5
        
        # Round damage
        final_damage = round(damage)
        
        # Apply the damage using the current_health property
        defender.current_health -= final_damage
        if defender.current_health < 0:
            defender.current_health = 0
        
        # Format outcome description
        if is_critical:
            return (f"{attacker.name} deals {final_damage} damage. "
                    "Critical Hit!")
        else:
            return f"{attacker.name} deals {final_damage} damage"
    
    def get_weapon_damage_type(self):
        """Get the damage type of the equipped weapon."""
        from game_sys.core.damage_types import DamageType
        if not self.character.weapon:
            return DamageType.PHYSICAL
        return getattr(
            self.character.weapon, 'damage_type', DamageType.PHYSICAL)
    
    def get_effective_armor(self) -> float:
        """Get effective armor/defense rating."""
        return self.character.get_stat('defense')
    
    def is_critical_hit(self) -> bool:
        """Determine if an attack results in a critical hit."""
        crit_chance = self.character.get_stat('crit_chance')
        return self.rng.random() < crit_chance
    
    def apply_critical_damage(self, base_damage: float) -> float:
        """Apply critical hit multiplier to damage."""
        crit_multiplier = self.character.get_stat('crit_multiplier')
        return base_damage * crit_multiplier
    
    # Compatibility methods for existing tests
    @property
    def stats(self):
        """Compatibility property for tests that access .stats."""
        return StatsWrapper(self.character)


class StatsWrapper:
    """Wrapper to provide stats interface expected by tests."""
    
    def __init__(self, actor: Actor):
        self.actor = actor
    
    def effective(self) -> Dict[str, float]:
        """Return effective stats dictionary."""
        return {
            'health': self.actor.max_health,
            'attack': self.actor.get_stat('attack'),
            'defense': self.actor.get_stat('defense'),
            'mana': self.actor.max_mana,
            'stamina': self.actor.max_stamina,
        }
    
    def set_base(self, stat_name: str, value: float):
        """Set base stat value."""
        self.actor.base_stats[stat_name] = value
        # Update derived pools if needed
        if stat_name == 'health':
            self.actor.max_health = self.actor.get_stat('health')
            self.actor.current_health = self.actor.max_health
        elif stat_name == 'mana':
            self.actor.max_mana = self.actor.get_stat('mana')
            self.actor.current_mana = self.actor.max_mana
        elif stat_name == 'stamina':
            self.actor.max_stamina = self.actor.get_stat('stamina')
            self.actor.current_stamina = self.actor.max_stamina
