# game_sys/combat/damage_packet.py
"""
DamagePacket
============
Encapsulates damage-related data for clean transfer to ScalingManager,
eliminating the need for getattr() reflection.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Any, Dict

if TYPE_CHECKING:
    from game_sys.character.actor import Actor
    from game_sys.core.damage_types import DamageType

from game_sys.logging import combat_logger, log_exception


@dataclass
class DamagePacket:
    """
    Encapsulates all damage-related data for ScalingManager calculations.
    
    This struct eliminates the need for getattr() reflection by providing
    a clean interface between combat systems and damage calculation.
    """
    
    # Core damage data
    base_damage: float = 0.0
    damage_type: Optional["DamageType"] = None
    
    # Actor references
    attacker: Optional["Actor"] = None
    defender: Optional["Actor"] = None
    weapon: Optional[Any] = None
    
    # Effect and modifier data
    effect_ids: list[str] = field(default_factory=list)
    damage_modifiers: Dict[str, float] = field(default_factory=dict)
    
    # Additional weapon/spell data
    weapon_type: Optional[str] = None
    damage_variance: tuple[float, float] = (1.0, 1.0)  # min, max multipliers
    penetration: float = 0.0
    
    @classmethod
    def from_weapon_attack(
        cls, attacker: "Actor", defender: "Actor", weapon: Any
    ) -> "DamagePacket":
        """
        Create a DamagePacket from a weapon-based attack.
        
        Args:
            attacker: The attacking actor
            defender: The defending actor
            weapon: The weapon being used
            
        Returns:
            DamagePacket with weapon data populated
        """
        from game_sys.core.damage_types import DamageType
        
        combat_logger.debug(f"Creating DamagePacket for weapon attack: {attacker.name} -> {defender.name}")
        
        # Extract weapon data safely
        base_damage = getattr(weapon, 'base_damage', 0.0)
        damage_type = getattr(weapon, 'damage_type', DamageType.PHYSICAL)
        weapon_type = getattr(weapon, 'weapon_type', 'melee')
        penetration = getattr(weapon, 'armor_penetration', 0.0)
        
        combat_logger.debug(
            f"Weapon data - damage: {base_damage}, type: {damage_type}, "
            f"weapon type: {weapon_type}, penetration: {penetration}"
        )
        
        # Apply attacker's attack stat to boost damage
        attack_stat = attacker.get_stat('attack')
        if attack_stat > 0:
            # Enhance base damage using the same formula as spell power:
            # base_damage * (1 + attack/10)
            attack_multiplier = attack_stat / 10.0
            enhanced_damage = base_damage * (1.0 + attack_multiplier)
            combat_logger.debug(
                f"Enhanced weapon damage: base={base_damage}, attack={attack_stat}, "
                f"multiplier={attack_multiplier}, enhanced={enhanced_damage}"
            )
            base_damage = enhanced_damage
        
        # Get damage variance from weapon
        min_var = getattr(weapon, 'damage_variance_min', 0.8)
        max_var = getattr(weapon, 'damage_variance_max', 1.2)
        combat_logger.debug(f"Damage variance: min={min_var}, max={max_var}")
        
        # Get effect_ids from weapon
        effect_ids = getattr(weapon, 'effect_ids', [])
        combat_logger.debug(f"Weapon effect_ids: {effect_ids}")
        
        return cls(
            base_damage=base_damage,
            damage_type=damage_type,
            attacker=attacker,
            defender=defender,
            weapon=weapon,
            weapon_type=weapon_type,
            damage_variance=(min_var, max_var),
            penetration=penetration,
            effect_ids=effect_ids
        )
    
    @classmethod
    def from_spell_cast(
        cls, attacker: "Actor", defender: "Actor",
        spell_damage: float, spell_id: str = "magic", damage_type=None
    ) -> "DamagePacket":
        """
        Create a DamagePacket from a spell cast.
        
        Args:
            attacker: The casting actor
            defender: The target actor
            spell_damage: Base spell damage
            spell_id: ID of the spell being cast
            damage_type: The elemental type of the spell (FIRE, ICE, etc)
            
        Returns:
            DamagePacket with spell data populated
        """
        from game_sys.core.damage_types import DamageType
        
        combat_logger.debug(
            f"Creating DamagePacket for spell cast: {attacker.name} -> {defender.name}, "
            f"spell: {spell_id}, damage: {spell_damage}"
        )
        
        # Add the spell ID to the effect_ids for tracking
        effect_ids = [spell_id] if spell_id else []
        # Use provided damage_type if available, else default to MAGIC
        if damage_type is None:
            damage_type = DamageType.MAGIC
        return cls(
            base_damage=spell_damage,
            damage_type=damage_type,
            attacker=attacker,
            defender=defender,
            weapon=None,
            # Use spell_id as weapon_type for better identification
            weapon_type=spell_id,
            damage_variance=(1.0, 1.0),  # Spells typically consistent
            penetration=0.0,
            effect_ids=effect_ids  # Include spell ID in effect IDs
        )
    
    def apply_modifier(self, modifier_name: str, multiplier: float) -> None:
        """
        Apply a damage modifier to this packet.
        
        Args:
            modifier_name: Name of the modifier (e.g., "strength_bonus")
            multiplier: Damage multiplier to apply
        """
        combat_logger.debug(
            f"Applying damage modifier: {modifier_name}={multiplier} "
            f"to damage packet for {self.attacker.name if self.attacker else 'unknown'}"
        )
        self.damage_modifiers[modifier_name] = multiplier
    
    def get_total_multiplier(self) -> float:
        """
        Calculate the total damage multiplier from all modifiers.
        
        Returns:
            Combined multiplier from all damage modifiers
        """
        if not self.damage_modifiers:
            combat_logger.debug("No damage modifiers present, using default multiplier of 1.0")
            return 1.0
        
        total = 1.0
        for name, multiplier in self.damage_modifiers.items():
            combat_logger.debug(f"Applying modifier: {name}={multiplier}")
            total *= multiplier
        
        combat_logger.debug(f"Total damage multiplier: {total}")
        return total
    
    def get_effective_damage(self) -> float:
        """
        Calculate effective damage including all modifiers.
        
        Returns:
            Base damage multiplied by total modifier
        """
        return self.base_damage * self.get_total_multiplier()
    
    def apply_variance(self, rng) -> float:
        """
        Apply damage variance to the base damage.
        
        Args:
            rng: Random number generator for variance calculation
            
        Returns:
            Damage with variance applied
        """
        if self.damage_variance == (1.0, 1.0):
            return self.base_damage
        
        min_mult, max_mult = self.damage_variance
        variance_mult = rng.uniform(min_mult, max_mult)
        return self.base_damage * variance_mult
    
    def get_effective_damage_with_variance(self, rng) -> float:
        """
        Calculate effective damage including modifiers and variance.
        
        Args:
            rng: Random number generator for variance
            
        Returns:
            Final damage with all modifiers and variance applied
        """
        base_with_variance = self.apply_variance(rng)
        return base_with_variance * self.get_total_multiplier()
