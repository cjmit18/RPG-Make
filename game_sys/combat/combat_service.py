# game_sys/combat/combat_service.py
"""
Combat Service
==============

High-level combat service that integrates combat engine, magic casting, and loot generation.
Provides simple methods for UI/demo usage.
"""

from typing import List, Optional, Dict, Any
from game_sys.combat.engine import CombatEngine
from game_sys.magic.spell_loader import load_spell
from game_sys.loot.loot_table import LootTable
from game_sys.logging import combat_logger


class CombatService:
    """High-level service for combat operations."""
    
    def __init__(self, ai_controller=None):
        """Initialize the combat service.
        
        Args:
            ai_controller: Optional AI controller for enemy responses
        """
        self.engine = CombatEngine()
        self.loot_table = LootTable()
        self.ai_controller = ai_controller
        
        # Set AI controller in the engine if provided
        if ai_controller:
            self.engine.set_ai_controller(ai_controller)
    
    def perform_attack(self, attacker, target, weapon=None) -> Dict[str, Any]:
        """
        Perform a basic attack between two actors.
        
        Args:
            attacker: The attacking actor
            target: The target actor
            weapon: Optional weapon override
            
        Returns:
            Dictionary with attack results
        """
        if not attacker or not target:
            return {
                'success': False,
                'message': 'Invalid attacker or target',
                'damage': 0,
                'defeated': False
            }
        
        # Store initial health for damage calculation
        initial_health = getattr(target, 'current_health', 0)
        
        # Execute attack through combat engine
        outcome = self.engine.execute_attack_sync(attacker, [target], weapon)
        
        # Calculate actual damage dealt
        final_health = getattr(target, 'current_health', 0)
        damage_dealt = initial_health - final_health
        
        # Check if target was defeated
        defeated = final_health <= 0
        
        # Extract resistance/weakness messages from combat events
        resistance_messages = []
        for event in outcome.events:
            if hasattr(event, 'metadata') and event.metadata:
                if 'resistance' in event.metadata:
                    message = event.metadata['resistance']['message']
                    resistance_messages.append(message)
                if 'weakness' in event.metadata:
                    message = event.metadata['weakness']['message']
                    resistance_messages.append(message)
        
        # Generate loot if target was defeated
        loot_items = []
        if defeated:
            loot_items = self.generate_defeat_loot(target, attacker)
        
        return {
            'success': outcome.success,
            'message': outcome.description,
            'damage': damage_dealt,
            'defeated': defeated,
            'loot': loot_items,
            'events': outcome.events,
            'resistance_messages': resistance_messages
        }
    
    def cast_spell_at_target(
        self, caster, spell_id: str, target
    ) -> Dict[str, Any]:
        """
        Cast a spell at a target through the combat engine.
        
        Args:
            caster: The actor casting the spell
            spell_id: ID of the spell to cast
            target: The target actor
            
        Returns:
            Dictionary with spell cast results
        """
        try:
            # Load the spell to validate it exists and get mana cost
            spell = load_spell(spell_id)
            if not spell:
                return {
                    'success': False,
                    'message': f'Failed to load spell: {spell_id}',
                    'damage': 0,
                    'defeated': False,
                    'loot': [],
                    'resistance_messages': []
                }
            
            # Check if caster has enough mana
            mana_cost = getattr(spell, 'mana_cost', 0)
            if (hasattr(caster, 'current_mana') and
                    caster.current_mana < mana_cost):
                return {
                    'success': False,
                    'message': (f'Not enough mana '
                                f'({caster.current_mana}/{mana_cost})'),
                    'damage': 0,
                    'defeated': False,
                    'loot': [],
                    'mana_cost': mana_cost,
                    'resistance_messages': []
                }
            
            # Apply mana cost
            if hasattr(caster, 'current_mana'):
                caster.current_mana -= mana_cost
            
            # Store initial health for damage calculation
            initial_health = getattr(target, 'current_health', 0)
            
            # Set up the caster for spell casting - tells the combat engine
            # to use the spell path for damage calculation
            caster.pending_spell = spell_id
            caster._spell_state = True
            
            # Execute spell damage through combat engine (no weapon = spell)
            outcome = self.engine.execute_attack_sync(
                caster, [target], weapon=None
            )
            
            # Clean up spell state
            if hasattr(caster, 'pending_spell'):
                delattr(caster, 'pending_spell')
            if hasattr(caster, '_spell_state'):
                delattr(caster, '_spell_state')
            
            # Calculate actual damage dealt
            final_health = getattr(target, 'current_health', 0)
            damage_dealt = initial_health - final_health
            
            # Check if target was defeated
            defeated = final_health <= 0
            
            # Extract resistance/weakness messages from combat events
            resistance_messages = []
            for event in outcome.events:
                if hasattr(event, 'metadata') and event.metadata:
                    if 'resistance' in event.metadata:
                        message = event.metadata['resistance']['message']
                        resistance_messages.append(message)
                    if 'weakness' in event.metadata:
                        message = event.metadata['weakness']['message']
                        resistance_messages.append(message)
            
            # Apply spell effects (buffs, debuffs, etc.) - not via engine
            effects_applied = []
            if hasattr(spell, 'effects') and spell.effects:
                for effect in spell.effects:
                    effect_name = "unknown effect"
                    
                    if hasattr(effect, 'apply'):
                        effect.apply(caster, target)
                        
                        # Get effect name based on type - prioritize flags
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
            
            # Generate loot if target was defeated
            loot_items = []
            if defeated:
                loot_items = self.generate_defeat_loot(target, caster)
            
            return {
                'success': outcome.success,
                'message': outcome.description,
                'damage': damage_dealt,
                'defeated': defeated,
                'loot': loot_items,
                'events': outcome.events,
                'mana_cost': mana_cost,
                'effects_applied': effects_applied,
                'resistance_messages': resistance_messages
            }
            
        except Exception as e:
            combat_logger.error(f"Error casting spell {spell_id}: {e}")
            return {
                'success': False,
                'message': f'Error casting {spell_id}: {str(e)}',
                'damage': 0,
                'defeated': False,
                'loot': [],
                'resistance_messages': []
            }
    
    def generate_defeat_loot(self, defeated_enemy, victor) -> List[Any]:
        """
        Generate loot when an enemy is defeated.
        
        Args:
            defeated_enemy: The defeated enemy actor
            victor: The victorious actor
            
        Returns:
            List of loot items
        """
        try:
            # Get enemy properties
            enemy_level = getattr(defeated_enemy, 'level', 1)
            enemy_type = getattr(defeated_enemy, 'template_id', 'unknown')
            enemy_grade = getattr(defeated_enemy, 'grade', 'ONE')
            enemy_rarity = getattr(defeated_enemy, 'rarity', 'COMMON')
            
            # Get player luck for loot calculations
            player_luck = 10  # Default luck
            if hasattr(victor, 'get_stat'):
                player_luck = victor.get_stat('luck')
            elif hasattr(victor, 'base_stats'):
                player_luck = victor.base_stats.get('luck', 10)
            
            # Generate loot
            loot_result = self.loot_table.generate_loot(
                enemy_level=enemy_level,
                enemy_type=enemy_type,
                player_luck=player_luck
            )
            
            # Add items to victor's inventory if they have one
            if hasattr(victor, 'inventory') and loot_result.get('items'):
                for item in loot_result['items']:
                    try:
                        victor.inventory.add_item(item)
                        combat_logger.info(f"Added {item.name} to {victor.name}'s inventory")
                    except Exception as e:
                        combat_logger.warning(f"Failed to add {item.name} to inventory: {e}")
            
            # Award experience if victor has a leveling manager
            experience = loot_result.get('experience', 0)
            if experience > 0 and hasattr(victor, 'leveling_manager'):
                try:
                    victor.leveling_manager.gain_experience(victor, experience)
                    combat_logger.info(f"Awarded {experience} XP to {victor.name}")
                except Exception as e:
                    combat_logger.warning(f"Failed to award XP: {e}")
            
            return loot_result.get('items', [])
            
        except Exception as e:
            combat_logger.error(f"Error generating loot: {e}")
            return []
    
    def apply_healing(self, healer, target, amount: float) -> Dict[str, Any]:
        """
        Apply healing to a target.
        
        Args:
            healer: The actor performing the healing
            target: The target to heal
            amount: Amount of healing
            
        Returns:
            Dictionary with healing results
        """
        if not target:
            return {
                'success': False,
                'message': 'No target to heal',
                'healing': 0
            }
        
        # Store initial health
        initial_health = getattr(target, 'current_health', 0)
        max_health = getattr(target, 'max_health', initial_health)
        
        # Apply healing
        if hasattr(target, 'current_health'):
            target.current_health = min(target.current_health + amount, max_health)
            actual_healing = target.current_health - initial_health
        else:
            actual_healing = 0
        
        return {
            'success': True,
            'message': f'Healed {target.name} for {actual_healing} health',
            'healing': actual_healing
        }
