# game_sys/character/status_flags.py
"""
Status Flags System

Defines standardized status effect flags that can be applied to characters.
These flags control behavior, stat modifications, and interaction restrictions.
"""

from enum import Enum, auto
from typing import Set, Dict, Any, Optional
from dataclasses import dataclass


class StatusFlag(Enum):
    """
    Enumeration of all possible status flags that can affect a character.
    """
    # Movement and Action Control
    STUNNED = auto()           # Cannot take any actions
    PARALYZED = auto()         # Cannot move or take physical actions
    FROZEN = auto()            # Cannot move, take reduced damage from physical
    ROOTED = auto()            # Cannot move but can take other actions
    SLOWED = auto()            # Movement and action speed reduced
    HASTED = auto()            # Movement and action speed increased
    
    # Combat State
    BURNING = auto()           # Taking fire damage over time
    POISONED = auto()          # Taking poison damage over time
    BLEEDING = auto()          # Taking physical damage over time
    REGENERATING = auto()      # Healing over time
    
    # Mental/Psychological Effects
    FEARED = auto()            # Cannot attack, may flee randomly
    CHARMED = auto()           # Controlled by another character
    CONFUSED = auto()          # Actions may target random entities
    SLEEPING = auto()          # Cannot take actions, vulnerable to attacks
    
    # Defensive States
    INVULNERABLE = auto()      # Cannot take damage
    INVISIBLE = auto()         # Cannot be targeted by most attacks
    PROTECTED = auto()         # Reduced incoming damage
    SHIELDED = auto()          # Absorbs damage before health
    
    # Offensive States
    BERSERKING = auto()        # Increased damage, reduced defense
    ENRAGED = auto()           # Increased attack, cannot retreat
    WEAKENED = auto()          # Reduced physical damage output
    SILENCED = auto()          # Cannot cast spells
    
    # Resource Effects
    MANA_BURN = auto()         # Losing mana over time
    MANA_SHIELD = auto()       # Damage affects mana before health
    STAMINA_DRAIN = auto()     # Losing stamina over time
    
    # Special States
    TIME_STOPPED = auto()      # Frozen in time, cannot act
    BANISHED = auto()          # Removed from combat temporarily
    TRANSFORMED = auto()       # Changed form with different stats
    MARKED = auto()            # Takes increased damage from specific source


@dataclass
class StatusFlagData:
    """
    Data associated with a status flag application.
    """
    flag: StatusFlag
    duration: float
    intensity: float = 1.0     # Multiplier for effect strength
    source: Optional[str] = None  # What caused this status
    tick_damage: float = 0.0   # Damage per second (for DoT effects)
    tick_heal: float = 0.0     # Healing per second (for HoT effects)
    metadata: Dict[str, Any] = None  # Additional effect-specific data
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class StatusFlagManager:
    """
    Manages status flags for a character.
    """
    
    def __init__(self, owner):
        self.owner = owner
        self.active_flags: Dict[StatusFlag, StatusFlagData] = {}
        self._flag_immunity: Set[StatusFlag] = set()
        self._flag_resistance: Dict[StatusFlag, float] = {}
    
    def add_flag(self, flag_data: StatusFlagData) -> bool:
        """
        Add a status flag. Returns True if successfully applied.
        """
        flag = flag_data.flag
        
        # Check immunity
        if flag in self._flag_immunity:
            return False
        
        # Apply resistance
        if flag in self._flag_resistance:
            resistance = self._flag_resistance[flag]
            flag_data.duration *= (1.0 - resistance)
            flag_data.intensity *= (1.0 - resistance)
            
            # If resistance negates the effect completely
            if flag_data.duration <= 0 or flag_data.intensity <= 0:
                return False
        
        # Check for conflicts and overrides
        self._handle_flag_conflicts(flag_data)
        
        # Apply the flag
        self.active_flags[flag] = flag_data
        self._on_flag_applied(flag_data)
        return True
    
    def remove_flag(self, flag: StatusFlag) -> bool:
        """
        Remove a status flag. Returns True if it was present.
        """
        if flag in self.active_flags:
            flag_data = self.active_flags.pop(flag)
            self._on_flag_removed(flag_data)
            return True
        return False
    
    def has_flag(self, flag: StatusFlag) -> bool:
        """Check if a specific flag is active."""
        return flag in self.active_flags
    
    def get_flag_data(self, flag: StatusFlag) -> Optional[StatusFlagData]:
        """Get the data for an active flag."""
        return self.active_flags.get(flag)
    
    def update(self, dt: float):
        """
        Update all active flags, handling duration and tick effects.
        """
        expired_flags = []
        
        for flag, flag_data in self.active_flags.items():
            # Handle tick effects
            if flag_data.tick_damage > 0:
                damage = flag_data.tick_damage * flag_data.intensity * dt
                self.owner.take_damage(damage)
            
            if flag_data.tick_heal > 0:
                heal = flag_data.tick_heal * flag_data.intensity * dt
                self.owner.current_health = min(
                    self.owner.current_health + heal,
                    self.owner.max_health
                )
            
            # Update duration
            flag_data.duration -= dt
            if flag_data.duration <= 0:
                expired_flags.append(flag)
        
        # Remove expired flags
        for flag in expired_flags:
            self.remove_flag(flag)
    
    def add_immunity(self, flag: StatusFlag):
        """Grant immunity to a specific status flag."""
        self._flag_immunity.add(flag)
        # Remove the flag if currently active
        self.remove_flag(flag)
    
    def remove_immunity(self, flag: StatusFlag):
        """Remove immunity to a specific status flag."""
        self._flag_immunity.discard(flag)
    
    def set_resistance(self, flag: StatusFlag, resistance: float):
        """Set resistance to a status flag (0.0 = no resistance, 1.0 = immunity)."""
        self._flag_resistance[flag] = max(0.0, min(1.0, resistance))
    
    def can_take_action(self) -> bool:
        """Check if the character can take normal actions."""
        blocking_flags = {
            StatusFlag.STUNNED, StatusFlag.PARALYZED, StatusFlag.FROZEN,
            StatusFlag.SLEEPING, StatusFlag.TIME_STOPPED, StatusFlag.BANISHED
        }
        return not any(flag in self.active_flags for flag in blocking_flags)
    
    def can_move(self) -> bool:
        """Check if the character can move."""
        movement_blocking = {
            StatusFlag.STUNNED, StatusFlag.PARALYZED, StatusFlag.FROZEN,
            StatusFlag.ROOTED, StatusFlag.SLEEPING, StatusFlag.TIME_STOPPED,
            StatusFlag.BANISHED
        }
        return not any(flag in self.active_flags for flag in movement_blocking)
    
    def can_cast_spells(self) -> bool:
        """Check if the character can cast spells."""
        casting_blocking = {
            StatusFlag.STUNNED, StatusFlag.PARALYZED, StatusFlag.SILENCED,
            StatusFlag.SLEEPING, StatusFlag.TIME_STOPPED, StatusFlag.BANISHED
        }
        return not any(flag in self.active_flags for flag in casting_blocking)
    
    def can_attack(self) -> bool:
        """Check if the character can attack."""
        attack_blocking = {
            StatusFlag.STUNNED, StatusFlag.PARALYZED, StatusFlag.FEARED,
            StatusFlag.SLEEPING, StatusFlag.TIME_STOPPED, StatusFlag.BANISHED
        }
        return not any(flag in self.active_flags for flag in attack_blocking)
    
    def get_movement_multiplier(self) -> float:
        """Get the movement speed multiplier based on active flags."""
        multiplier = 1.0
        
        if self.has_flag(StatusFlag.SLOWED):
            slowed_data = self.get_flag_data(StatusFlag.SLOWED)
            multiplier *= (1.0 - 0.5 * slowed_data.intensity)
        
        if self.has_flag(StatusFlag.HASTED):
            hasted_data = self.get_flag_data(StatusFlag.HASTED)
            multiplier *= (1.0 + 0.5 * hasted_data.intensity)
        
        return max(0.1, multiplier)  # Minimum 10% speed
    
    def get_damage_multiplier(self, outgoing: bool = True) -> float:
        """Get damage multiplier for outgoing or incoming damage."""
        multiplier = 1.0
        
        if outgoing:
            # Outgoing damage modifiers
            if self.has_flag(StatusFlag.BERSERKING):
                berserk_data = self.get_flag_data(StatusFlag.BERSERKING)
                multiplier *= (1.0 + 0.5 * berserk_data.intensity)
            
            if self.has_flag(StatusFlag.ENRAGED):
                enraged_data = self.get_flag_data(StatusFlag.ENRAGED)
                multiplier *= (1.0 + 0.3 * enraged_data.intensity)
            
            if self.has_flag(StatusFlag.WEAKENED):
                weakened_data = self.get_flag_data(StatusFlag.WEAKENED)
                multiplier *= (1.0 - 0.4 * weakened_data.intensity)
        else:
            # Incoming damage modifiers
            if self.has_flag(StatusFlag.PROTECTED):
                protected_data = self.get_flag_data(StatusFlag.PROTECTED)
                multiplier *= (1.0 - 0.3 * protected_data.intensity)
            
            if self.has_flag(StatusFlag.BERSERKING):
                berserk_data = self.get_flag_data(StatusFlag.BERSERKING)
                multiplier *= (1.0 + 0.3 * berserk_data.intensity)  # Take more damage
            
            if self.has_flag(StatusFlag.INVULNERABLE):
                multiplier = 0.0
        
        return max(0.0, multiplier)
    
    def _handle_flag_conflicts(self, new_flag_data: StatusFlagData):
        """Handle conflicting status flags."""
        flag = new_flag_data.flag
        
        # Define mutually exclusive flags
        conflicts = {
            StatusFlag.SLOWED: [StatusFlag.HASTED],
            StatusFlag.HASTED: [StatusFlag.SLOWED],
            StatusFlag.FROZEN: [StatusFlag.BURNING, StatusFlag.HASTED],
            StatusFlag.BURNING: [StatusFlag.FROZEN],
            StatusFlag.SLEEPING: [StatusFlag.ENRAGED, StatusFlag.BERSERKING],
            StatusFlag.FEARED: [StatusFlag.ENRAGED, StatusFlag.BERSERKING],
        }
        
        if flag in conflicts:
            for conflicting_flag in conflicts[flag]:
                if conflicting_flag in self.active_flags:
                    # Remove the conflicting flag
                    self.remove_flag(conflicting_flag)
    
    def _on_flag_applied(self, flag_data: StatusFlagData):
        """Handle side effects when a flag is applied."""
        flag = flag_data.flag
        
        # Special handling for certain flags
        if flag == StatusFlag.SLEEPING:
            # Sleeping characters can't defend as effectively
            pass
        elif flag == StatusFlag.INVISIBLE:
            # Handle visibility changes
            pass
        elif flag == StatusFlag.TRANSFORMED:
            # Handle form changes
            pass
    
    def _on_flag_removed(self, flag_data: StatusFlagData):
        """Handle side effects when a flag is removed."""
        flag = flag_data.flag
        
        # Clean up any effects
        if flag == StatusFlag.TRANSFORMED:
            # Restore original form
            pass
    
    def get_all_active_flags(self) -> Dict[StatusFlag, StatusFlagData]:
        """Get all currently active status flags."""
        return self.active_flags.copy()
    
    def clear_all_flags(self):
        """Remove all active status flags."""
        for flag in list(self.active_flags.keys()):
            self.remove_flag(flag)


# Convenience functions for creating common status effects
def create_burn_effect(duration: float, tick_damage: float, source: str = None) -> StatusFlagData:
    """Create a burning status effect."""
    return StatusFlagData(
        flag=StatusFlag.BURNING,
        duration=duration,
        tick_damage=tick_damage,
        source=source
    )

def create_poison_effect(duration: float, tick_damage: float, source: str = None) -> StatusFlagData:
    """Create a poison status effect."""
    return StatusFlagData(
        flag=StatusFlag.POISONED,
        duration=duration,
        tick_damage=tick_damage,
        source=source
    )

def create_stun_effect(duration: float, source: str = None) -> StatusFlagData:
    """Create a stun status effect."""
    return StatusFlagData(
        flag=StatusFlag.STUNNED,
        duration=duration,
        source=source
    )

def create_fear_effect(duration: float, source: str = None) -> StatusFlagData:
    """Create a fear status effect."""
    return StatusFlagData(
        flag=StatusFlag.FEARED,
        duration=duration,
        source=source
    )

def create_slow_effect(duration: float, intensity: float = 1.0, source: str = None) -> StatusFlagData:
    """Create a slow status effect."""
    return StatusFlagData(
        flag=StatusFlag.SLOWED,
        duration=duration,
        intensity=intensity,
        source=source
    )

def create_freeze_effect(duration: float, source: str = None) -> StatusFlagData:
    """Create a freeze status effect."""
    return StatusFlagData(
        flag=StatusFlag.FROZEN,
        duration=duration,
        source=source
    )

def create_regeneration_effect(duration: float, tick_heal: float, source: str = None) -> StatusFlagData:
    """Create a regeneration status effect."""
    return StatusFlagData(
        flag=StatusFlag.REGENERATING,
        duration=duration,
        tick_heal=tick_heal,
        source=source
    )
