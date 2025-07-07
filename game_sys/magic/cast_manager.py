# game_sys/magic/cast_manager.py
"""
Spell Casting Manager
====================

Handles spell casting, resource management, and result tracking.
"""

from typing import List, Any
from dataclasses import dataclass

from game_sys.character.actor import Actor
from game_sys.utils.profiler import profiler


@dataclass
class SpellCastResult:
    """Result of a spell cast operation."""
    success: bool
    message: str
    damage: float = 0.0
    mana_cost: float = 0.0
    effects_applied: List[str] = None
    
    def __post_init__(self):
        if self.effects_applied is None:
            self.effects_applied = []


def cast_spell(
    caster: Actor, spell: Any, targets: List[Actor]
) -> SpellCastResult:
    """
    Cast a spell from a caster to one or more targets.
    
    Args:
        caster: The actor casting the spell
        spell: The spell to cast
        targets: List of target actors for the spell
        
    Returns:
        SpellCastResult with information about the cast
    """
    with profiler.span("cast_spell"):
        return _cast_spell_internal(caster, spell, targets)


def _cast_spell_internal(
    caster: Actor, spell: Any, targets: List[Actor]
) -> SpellCastResult:
    """Internal implementation of spell casting."""
    # Validate inputs
    if not caster:
        return SpellCastResult(False, "No caster provided")
        
    if not spell:
        return SpellCastResult(False, "No spell provided")
        
    if not targets:
        return SpellCastResult(False, "No targets provided")
    
    # Check if caster has enough mana
    mana_cost = getattr(spell, 'mana_cost', 0)
    if hasattr(caster, 'current_mana') and caster.current_mana < mana_cost:
        return SpellCastResult(
            False,
            f"Not enough mana ({caster.current_mana}/{mana_cost})",
            mana_cost=mana_cost
        )
    
    # Apply mana cost
    if hasattr(caster, 'current_mana'):
        caster.current_mana -= mana_cost
    
    # Calculate damage based on spell and caster stats
    base_damage = getattr(spell, 'base_power', 0)
    int_bonus = 0
    
    if hasattr(caster, 'get_stat'):
        int_bonus = caster.get_stat('intelligence') * 0.5
    
    damage = base_damage + int_bonus
    
    # Apply damage to all targets
    damage_dealt = 0
    effects_applied = []
    
    for target in targets:
        if hasattr(target, 'take_damage'):
            # Pass the spell's damage type for resistance/weakness calculations
            damage_type = getattr(spell, 'damage_type', None)
            target.take_damage(damage, caster, damage_type)
            damage_dealt += damage
            
        # Apply effects if available
        if hasattr(spell, 'effects') and spell.effects:
            for effect in spell.effects:
                effect_name = "unknown effect"
                
                if hasattr(effect, 'apply'):
                    effect.apply(caster, target)
                    
                    # Get effect name based on type - prioritize status flags
                    if (hasattr(effect, 'flag') and
                            hasattr(effect.flag, 'name')):
                        # Status effect with flag (most common case)
                        effect_name = effect.flag.name.lower()
                    elif hasattr(effect, '__class__'):
                        # Extract from class name (BurnEffect -> "burning")
                        class_name = effect.__class__.__name__
                        if class_name.endswith('Effect'):
                            base_name = class_name[:-6]  # Remove 'Effect'
                            # Special mappings for better names
                            name_mapping = {
                                'Burn': 'burning',
                                'Slow': 'slowing',
                                'Stun': 'stunned',
                                'Fear': 'feared',
                                'Freeze': 'frozen',
                                'Poison': 'poisoned',
                                'Haste': 'hasted',
                                'Silence': 'silenced',
                                'Weaken': 'weakened'
                            }
                            effect_name = name_mapping.get(
                                base_name, base_name.lower()
                            )
                        else:
                            effect_name = class_name.lower()
                    elif hasattr(effect, 'name'):
                        # Effect with direct name attribute
                        effect_name = effect.name
                    elif hasattr(effect, 'id'):
                        # Effect with ID attribute
                        effect_name = effect.id.replace('_', ' ')
                    
                    effects_applied.append(effect_name)
                    
                # Check if it's a status effect dictionary
                elif isinstance(effect, dict):
                    if effect.get('type') == 'status':
                        params = effect.get('params', {})
                        effect_name = params.get('name', 'unknown')
                        effects_applied.append(effect_name)
    
    # Return successful result
    return SpellCastResult(
        True,
        f"Spell {spell.name} cast successfully",
        damage=damage_dealt,
        mana_cost=mana_cost,
        effects_applied=effects_applied
    )
