# game_sys/effects/status_effects.py
"""
Status Effects Implementation

Implements concrete status effects using the status flag system.
"""

from typing import Any, Dict, Optional
from game_sys.effects.base import Effect
from game_sys.character.status_flags import (
    StatusFlag, StatusFlagData, StatusFlagManager,
    create_burn_effect, create_poison_effect, create_stun_effect,
    create_fear_effect, create_slow_effect, create_freeze_effect,
    create_regeneration_effect
)
from game_sys.logging import effects_logger


class StatusEffect(Effect):
    """
    Base class for status effects that use the flag system.
    """
    
    def __init__(self, flag: StatusFlag, duration: float, intensity: float = 1.0, 
                 tick_damage: float = 0.0, tick_heal: float = 0.0, **kwargs):
        super().__init__(id=f"status_{flag.name.lower()}")
        self.flag = flag
        self.duration = duration
        self.intensity = intensity
        self.tick_damage = tick_damage
        self.tick_heal = tick_heal
        self.metadata = kwargs
    
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        """Apply the status effect to the target."""
        if not hasattr(target, 'status_flags'):
            # Initialize status flag manager if not present
            target.status_flags = StatusFlagManager(target)
        
        flag_data = StatusFlagData(
            flag=self.flag,
            duration=self.duration,
            intensity=self.intensity,
            tick_damage=self.tick_damage,
            tick_heal=self.tick_heal,
            source=getattr(caster, 'name', 'Unknown'),
            metadata=self.metadata
        )
        
        success = target.status_flags.add_flag(flag_data)
        
        # Also add to active_statuses for the status manager to tick
        if not hasattr(target, 'active_statuses'):
            target.active_statuses = {}
        
        # Create a unique status ID
        status_id = f"{self.flag.name.lower()}_{id(self)}"
        target.active_statuses[status_id] = (self, self.duration)
        
        if success:
            effects_logger.info(f"Applied {self.flag.name} to {target.name}")
            return f"{target.name} is affected by {self.flag.name.lower()}"
        else:
            effects_logger.info(f"Failed to apply {self.flag.name} to {target.name} (immune/resistant)")
            return f"{target.name} resists {self.flag.name.lower()}"
    
    def tick(self, target: Any, dt: float) -> None:
        """
        Handle periodic ticking of the status effect.
        
        Args:
            target: The actor affected by this status effect
            dt: Time delta in seconds since last tick
        """
        # Apply tick damage if any
        if self.tick_damage > 0:
            damage = self.tick_damage * dt
            if hasattr(target, 'take_damage'):
                target.take_damage(damage)
                effects_logger.info(
                    f"{target.name} takes {damage:.1f} {self.flag.name.lower()} damage"
                )
            elif hasattr(target, 'current_health'):
                # Fallback: directly reduce health
                target.current_health = max(0, target.current_health - damage)
                effects_logger.info(
                    f"{target.name} takes {damage:.1f} {self.flag.name.lower()} damage"
                )
        
        # Apply tick healing if any
        if self.tick_heal > 0:
            healing = self.tick_heal * dt
            if hasattr(target, 'heal'):
                target.heal(healing)
                effects_logger.info(
                    f"{target.name} heals {healing:.1f} health from {self.flag.name.lower()}"
                )
            elif hasattr(target, 'current_health') and hasattr(target, 'max_health'):
                # Fallback: directly increase health
                target.current_health = min(
                    target.max_health, 
                    target.current_health + healing
                )
                effects_logger.info(
                    f"{target.name} heals {healing:.1f} health from {self.flag.name.lower()}"
                )


class BurnEffect(StatusEffect):
    """Fire damage over time effect."""
    
    def __init__(self, duration: float = 5.0, tick_damage: float = 2.0, **kwargs):
        super().__init__(
            flag=StatusFlag.BURNING,
            duration=duration,
            tick_damage=tick_damage,
            **kwargs
        )
    
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        result = super().apply(caster, target, combat_engine)
        
        # Additional fire-specific logic
        if hasattr(target, 'status_flags') and target.status_flags.has_flag(StatusFlag.FROZEN):
            # Burning removes frozen status
            target.status_flags.remove_flag(StatusFlag.FROZEN)
            return result + " (thawed from burning)"
        
        return result


class PoisonEffect(StatusEffect):
    """Poison damage over time effect."""
    
    def __init__(self, duration: float = 8.0, tick_damage: float = 1.5, **kwargs):
        super().__init__(
            flag=StatusFlag.POISONED,
            duration=duration,
            tick_damage=tick_damage,
            **kwargs
        )


class StunEffect(StatusEffect):
    """Prevents all actions."""
    
    def __init__(self, duration: float = 2.0, **kwargs):
        super().__init__(
            flag=StatusFlag.STUNNED,
            duration=duration,
            **kwargs
        )


class FearEffect(StatusEffect):
    """Prevents attacks and may cause fleeing."""
    
    def __init__(self, duration: float = 3.0, **kwargs):
        super().__init__(
            flag=StatusFlag.FEARED,
            duration=duration,
            **kwargs
        )


class SlowEffect(StatusEffect):
    """Reduces movement and action speed."""
    
    def __init__(self, duration: float = 5.0, intensity: float = 1.0, **kwargs):
        super().__init__(
            flag=StatusFlag.SLOWED,
            duration=duration,
            intensity=intensity,
            **kwargs
        )


class FreezeEffect(StatusEffect):
    """Prevents movement and reduces physical damage taken."""
    
    def __init__(self, duration: float = 3.0, **kwargs):
        super().__init__(
            flag=StatusFlag.FROZEN,
            duration=duration,
            **kwargs
        )


class HasteEffect(StatusEffect):
    """Increases movement and action speed."""
    
    def __init__(self, duration: float = 10.0, intensity: float = 1.0, **kwargs):
        super().__init__(
            flag=StatusFlag.HASTED,
            duration=duration,
            intensity=intensity,
            **kwargs
        )


class RegenerationEffect(StatusEffect):
    """Healing over time effect."""
    
    def __init__(self, duration: float = 10.0, tick_heal: float = 2.0, **kwargs):
        super().__init__(
            flag=StatusFlag.REGENERATING,
            duration=duration,
            tick_heal=tick_heal,
            **kwargs
        )


class SilenceEffect(StatusEffect):
    """Prevents spellcasting."""
    
    def __init__(self, duration: float = 4.0, **kwargs):
        super().__init__(
            flag=StatusFlag.SILENCED,
            duration=duration,
            **kwargs
        )


class WeakenEffect(StatusEffect):
    """Reduces physical damage output."""
    
    def __init__(self, duration: float = 6.0, intensity: float = 1.0, **kwargs):
        super().__init__(
            flag=StatusFlag.WEAKENED,
            duration=duration,
            intensity=intensity,
            **kwargs
        )


class BerserkEffect(StatusEffect):
    """Increases damage output but also damage taken."""
    
    def __init__(self, duration: float = 8.0, intensity: float = 1.0, **kwargs):
        super().__init__(
            flag=StatusFlag.BERSERKING,
            duration=duration,
            intensity=intensity,
            **kwargs
        )


class ProtectionEffect(StatusEffect):
    """Reduces incoming damage."""
    
    def __init__(self, duration: float = 12.0, intensity: float = 1.0, **kwargs):
        super().__init__(
            flag=StatusFlag.PROTECTED,
            duration=duration,
            intensity=intensity,
            **kwargs
        )


class InvisibilityEffect(StatusEffect):
    """Makes the target untargetable by most attacks."""
    
    def __init__(self, duration: float = 6.0, **kwargs):
        super().__init__(
            flag=StatusFlag.INVISIBLE,
            duration=duration,
            **kwargs
        )


class ParalyzeEffect(StatusEffect):
    """Prevents movement and physical actions."""
    
    def __init__(self, duration: float = 3.0, **kwargs):
        super().__init__(
            flag=StatusFlag.PARALYZED,
            duration=duration,
            **kwargs
        )


class SleepEffect(StatusEffect):
    """Prevents all actions and makes vulnerable."""
    
    def __init__(self, duration: float = 5.0, **kwargs):
        super().__init__(
            flag=StatusFlag.SLEEPING,
            duration=duration,
            **kwargs
        )


# Factory function for creating status effects from names
def create_status_effect(name: str, **params) -> StatusEffect:
    """
    Create a status effect by name with optional parameters.
    """
    effect_map = {
        'burn': BurnEffect,
        'poison': PoisonEffect,
        'stun': StunEffect,
        'fear': FearEffect,
        'slow': SlowEffect,
        'freeze': FreezeEffect,
        'haste': HasteEffect,
        'regeneration': RegenerationEffect,
        'silence': SilenceEffect,
        'weaken': WeakenEffect,
        'berserk': BerserkEffect,
        'protection': ProtectionEffect,
        'invisibility': InvisibilityEffect,
        'paralyze': ParalyzeEffect,
        'sleep': SleepEffect,
    }
    
    effect_class = effect_map.get(name.lower())
    if effect_class:
        return effect_class(**params)
    else:
        effects_logger.warning(f"Unknown status effect: {name}")
        return StatusEffect(StatusFlag.STUNNED, 1.0)  # Fallback