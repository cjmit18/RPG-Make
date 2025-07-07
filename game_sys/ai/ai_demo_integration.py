"""
AI Demo Integration
==================

Demonstrates how to integrate the AI system with the demo and combat.
Shows real-time AI decision making and responsive enemy behavior.
"""

import logging
from typing import Optional, Dict, Any
import random

from game_sys.ai.ai_service import AIService
from game_sys.ai.difficulty_scaling import DifficultyScaler, DifficultyLevel
from game_sys.combat.combat_service import CombatService

logger = logging.getLogger("ai_demo_integration")


class AIDemoController:
    """Controls AI behavior in the demo environment."""
    
    def __init__(self, combat_service: CombatService):
        """Initialize the AI demo controller.
        
        Args:
            combat_service: The combat service instance from the demo
        """
        self.combat_service = combat_service
        self.ai_service = AIService()
        self.difficulty_scaler = DifficultyScaler()
        
        # Demo-specific settings
        self.auto_ai_enabled = True
        self.ai_response_delay = 1.0  # Seconds between AI actions
        self.last_ai_action_time = 0.0
        
        logger.info("AI Demo Controller initialized")
    
    def enable_ai_for_enemy(self, enemy):
        """Enable AI control for an enemy.
        
        Args:
            enemy: The enemy actor to control with AI
        """
        if not enemy:
            logger.warning("Cannot enable AI for None enemy")
            return False
            
        # Apply difficulty modifiers to the enemy
        self._apply_difficulty_to_enemy(enemy)
        
        # Register the enemy with AI service
        try:
            self.ai_service.register_ai_actor(enemy)
            logger.info(f"AI enabled for {enemy.name}")
            # Set the enemy's team to ensure proper targeting
            enemy.team = 'enemy'
            return True
        except Exception as e:
            logger.warning(f"Failed to enable AI for {enemy.name}: {e}")
            return False
    
    def disable_ai_for_enemy(self, enemy):
        """Disable AI control for an enemy.
        
        Args:
            enemy: The enemy actor to remove from AI control
        """
        if not enemy:
            return
            
        self.ai_service.unregister_ai_actor(enemy)
        logger.info(f"AI disabled for {enemy.name}")
    
    def process_ai_turn(self, enemy, player, dt: float):
        """Process a single AI turn for an enemy.
        
        Args:
            enemy: The AI-controlled enemy
            player: The player character (target)
            dt: Delta time since last update
        
        Returns:
            Dict with action information or None if no action taken
        """
        if not enemy or not player:
            return None
            
        if not enemy.is_alive() or not player.is_alive():
            return None
            
        # Check if enough time has passed for AI action
        import time
        current_time = time.time()
        if current_time - self.last_ai_action_time < self.ai_response_delay:
            return None
            
        # Get AI decision
        action = self.ai_service.get_action_for_actor(enemy, [player])
        
        if action:
            self.last_ai_action_time = current_time
            result = self._execute_ai_action(enemy, player, action)
            
            # Record performance for difficulty scaling
            if result and result.get('success'):
                self._record_ai_performance(enemy, player, action, result)
                
            return result
            
        return None
    
    def _execute_ai_action(self, enemy, player, action: Dict[str, Any]) -> Optional[Dict]:
        """Execute an AI action.
        
        Args:
            enemy: The AI actor performing the action
            player: The target player
            action: The action dictionary from AI service
            
        Returns:
            Result dictionary from the action execution
        """
        action_type = action.get('type')
        
        try:
            if action_type == 'attack':
                return self.combat_service.perform_attack(enemy, player, enemy.weapon)
                
            elif action_type == 'cast_spell':
                spell_id = action.get('spell_id', 'fireball')
                return self.combat_service.cast_spell_at_target(enemy, spell_id, player)
                
            elif action_type == 'defend':
                # Set defending state
                enemy.defending = True
                logger.info(f"{enemy.name} takes a defensive stance")
                return {
                    'success': True,
                    'action': 'defend',
                    'message': f"{enemy.name} defends"
                }
                
            elif action_type == 'use_item':
                item_id = action.get('item_id')
                if item_id and hasattr(enemy, 'use_item'):
                    success = enemy.use_item(item_id)
                    return {
                        'success': success,
                        'action': 'use_item',
                        'item': item_id
                    }
                    
            elif action_type == 'wait':
                logger.debug(f"{enemy.name} waits")
                return {
                    'success': True,
                    'action': 'wait',
                    'message': f"{enemy.name} waits"
                }
                
            else:
                logger.warning(f"Unknown AI action type: {action_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing AI action {action_type}: {e}")
            return None
    
    def _apply_difficulty_to_enemy(self, enemy):
        """Apply difficulty modifiers to an enemy.
        
        Args:
            enemy: The enemy to modify
        """
        try:
            modifiers = self.difficulty_scaler.get_current_modifiers()
            
            # Apply health multiplier
            if hasattr(enemy, 'base_stats') and 'health' in enemy.base_stats:
                original_health = enemy.base_stats['health']
                enemy.base_stats['health'] *= modifiers.enemy_health_multiplier
                enemy.max_health = enemy.get_stat('health')
                enemy.current_health = enemy.max_health
                
                logger.debug(
                    f"Applied health multiplier {modifiers.enemy_health_multiplier} "
                    f"to {enemy.name}: {original_health} -> {enemy.max_health}"
                )
            
            # Apply damage multiplier
            if hasattr(enemy, 'base_stats') and 'attack' in enemy.base_stats:
                enemy.base_stats['attack'] *= modifiers.enemy_damage_multiplier
                
            # Apply speed multiplier
            if hasattr(enemy, 'base_stats') and 'speed' in enemy.base_stats:
                enemy.base_stats['speed'] *= modifiers.enemy_speed_multiplier
                
            # Apply mana multiplier
            if hasattr(enemy, 'base_stats') and 'mana' in enemy.base_stats:
                enemy.base_stats['mana'] *= modifiers.enemy_mana_multiplier
                enemy.max_mana = enemy.get_stat('mana')
                enemy.current_mana = enemy.max_mana
                
            # Apply defense multiplier
            if hasattr(enemy, 'base_stats') and 'defense' in enemy.base_stats:
                enemy.base_stats['defense'] *= modifiers.enemy_defense_multiplier
                
            # Update stats to reflect changes
            if hasattr(enemy, 'update_stats'):
                enemy.update_stats()
                
            logger.info(f"Applied difficulty modifiers to {enemy.name}")
            
        except Exception as e:
            logger.error(f"Error applying difficulty to {enemy.name}: {e}")
    
    def _record_ai_performance(self, enemy, player, action: Dict, result: Dict):
        """Record AI performance for difficulty scaling.
        
        Args:
            enemy: The AI actor
            player: The player
            action: The action taken
            result: The result of the action
        """
        try:
            # Record damage dealt
            damage = result.get('damage', 0)
            if damage > 0:
                self.difficulty_scaler.record_damage_dealt(damage)
                
            # Check if player was defeated
            if not player.is_alive():
                self.difficulty_scaler.record_battle_result(False, enemy.level)
                logger.info("AI defeated player - recording loss")
                
        except Exception as e:
            logger.error(f"Error recording AI performance: {e}")
    
    def record_player_victory(self, player, enemy):
        """Record when the player defeats an AI enemy.
        
        Args:
            player: The victorious player
            enemy: The defeated AI enemy
        """
        try:
            self.difficulty_scaler.record_battle_result(True, enemy.level)
            logger.info("Player defeated AI enemy - recording win")
            
            # Check if difficulty should be adjusted
            if self.difficulty_scaler.should_adjust_difficulty():
                old_difficulty = self.difficulty_scaler.current_difficulty
                self.difficulty_scaler.adjust_difficulty()
                new_difficulty = self.difficulty_scaler.current_difficulty
                
                if old_difficulty != new_difficulty:
                    logger.info(
                        f"Difficulty adjusted: {old_difficulty.value} -> {new_difficulty.value}"
                    )
                    
        except Exception as e:
            logger.error(f"Error recording player victory: {e}")
    
    def get_ai_status(self, enemy) -> Dict[str, Any]:
        """Get current AI status for an enemy.
        
        Args:
            enemy: The AI-controlled enemy
            
        Returns:
            Dictionary with AI status information
        """
        if not enemy:
            return {'ai_enabled': False}
            
        is_registered = self.ai_service.is_actor_registered(enemy)
        
        status = {
            'ai_enabled': is_registered,
            'difficulty_level': self.difficulty_scaler.current_difficulty.value,
            'win_rate': self.difficulty_scaler.metrics.win_rate,
            'battles_fought': (
                self.difficulty_scaler.metrics.battles_won + 
                self.difficulty_scaler.metrics.battles_lost
            )
        }
        
        if is_registered:
            # Get current AI state
            behavior = getattr(enemy, 'behavior_state', 'unknown')
            status['behavior'] = behavior
            
            # Get last action info
            last_action = getattr(enemy, '_last_ai_action', None)
            if last_action:
                status['last_action'] = last_action
                
        return status
    
    def set_difficulty_level(self, level: DifficultyLevel):
        """Manually set the difficulty level.
        
        Args:
            level: The difficulty level to set
        """
        self.difficulty_scaler.current_difficulty = level
        logger.info(f"Difficulty manually set to {level.value}")
    
    def toggle_auto_ai(self):
        """Toggle automatic AI processing on/off."""
        self.auto_ai_enabled = not self.auto_ai_enabled
        status = "enabled" if self.auto_ai_enabled else "disabled"
        logger.info(f"Auto AI {status}")
        return self.auto_ai_enabled
