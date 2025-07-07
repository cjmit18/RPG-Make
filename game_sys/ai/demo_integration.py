"""
AI Integration Module
====================

Integration module that connects the AI system with the demo and game engine.
Shows how to implement responsive enemy AI using the existing service layer.
"""

import logging
import random
import time
from typing import Any, Dict, Optional

from game_sys.ai.ai_service import AIService
from game_sys.ai.difficulty_scaling import DifficultyScaler, DifficultyLevel
from game_sys.combat.combat_service import CombatService


class AIIntegrationManager:
    """Manages AI integration with the game demo."""
    
    def __init__(self, combat_service: CombatService):
        self.logger = logging.getLogger("ai_integration")
        self.combat_service = combat_service
        self.ai_service = AIService(combat_service)
        self.difficulty_scaler = self.ai_service.difficulty_scaler
        
        # Track AI-controlled actors
        self.ai_actors: Dict[str, Dict[str, Any]] = {}
        
        # AI update timing
        self.last_ai_update = time.time()
        self.ai_update_interval = 2.0  # AI acts every 2 seconds
        
        self.logger.info("AI Integration Manager initialized")
        
    def register_enemy_for_ai(self, enemy: Any, behavior_type: str = "basic_enemy"):
        """Register an enemy for AI control with difficulty scaling."""
        try:
            # Apply difficulty scaling first
            scaled_enemy = self.difficulty_scaler.apply_modifiers_to_enemy(enemy)
            
            # Register with AI service
            self.ai_service.register_ai_actor(scaled_enemy, behavior_type)
            
            # Track in our local registry
            actor_id = str(id(scaled_enemy))
            self.ai_actors[actor_id] = {
                'actor': scaled_enemy,
                'behavior_type': behavior_type,
                'last_action_time': time.time(),
                'action_cooldown': 1.5,  # Minimum time between actions
                'registered_time': time.time()
            }
            
            self.logger.info(
                f"Registered {scaled_enemy.name} for AI control "
                f"(behavior: {behavior_type}, "
                f"difficulty: {self.difficulty_scaler.current_difficulty.value})"
            )
            
            return scaled_enemy
            
        except Exception as e:
            self.logger.error(f"Failed to register enemy for AI: {e}")
            return enemy
            
    def update_ai(self, player: Any, current_time: Optional[float] = None):
        """Update AI for all registered actors."""
        if current_time is None:
            current_time = time.time()
            
        # Check if it's time for AI update
        if current_time - self.last_ai_update < self.ai_update_interval:
            return []
            
        self.last_ai_update = current_time
        ai_actions = []
        
        try:
            for actor_id, actor_data in list(self.ai_actors.items()):
                enemy = actor_data['actor']
                
                # Skip if enemy is dead
                if not hasattr(enemy, 'current_health') or enemy.current_health <= 0:
                    # Remove from AI control
                    del self.ai_actors[actor_id]
                    continue
                    
                # Check action cooldown
                if (current_time - actor_data['last_action_time'] < 
                        actor_data['action_cooldown']):
                    continue
                    
                # Get AI decision
                action = self.ai_service.get_ai_action(enemy, player)
                
                if action:
                    # Execute the action
                    result = self._execute_ai_action(enemy, player, action)
                    if result:
                        ai_actions.append({
                            'enemy': enemy,
                            'action': action,
                            'result': result
                        })
                        
                    # Update action timing
                    actor_data['last_action_time'] = current_time
                    
        except Exception as e:
            self.logger.error(f"Error in AI update: {e}")
            
        return ai_actions
        
    def _execute_ai_action(self, enemy: Any, player: Any, action: Dict[str, Any]):
        """Execute an AI action and return the result."""
        try:
            action_type = action.get('type', 'unknown')
            
            if action_type == 'attack':
                # AI enemy attacks player
                weapon = getattr(enemy, 'weapon', None)
                result = self.combat_service.perform_attack(enemy, player, weapon)
                
                if result['success']:
                    self.logger.info(
                        f"AI {enemy.name} attacks {player.name} for "
                        f"{result['damage']:.1f} damage"
                    )
                    return {
                        'type': 'attack',
                        'damage': result['damage'],
                        'success': True,
                        'message': f"{enemy.name} attacks for {result['damage']:.1f} damage!"
                    }
                else:
                    self.logger.debug(f"AI {enemy.name} attack missed {player.name}")
                    return {
                        'type': 'attack',
                        'success': False,
                        'message': f"{enemy.name}'s attack missed!"
                    }
                    
            elif action_type == 'cast_spell':
                # AI enemy casts spell
                spell_id = action.get('spell_id', 'fireball')
                result = self.combat_service.cast_spell_at_target(
                    enemy, spell_id, player
                )
                
                if result['success']:
                    self.logger.info(
                        f"AI {enemy.name} casts {spell_id} for "
                        f"{result['damage']:.1f} damage"
                    )
                    return {
                        'type': 'cast_spell',
                        'spell_id': spell_id,
                        'damage': result['damage'],
                        'success': True,
                        'message': f"{enemy.name} casts {spell_id} for {result['damage']:.1f} damage!"
                    }
                else:
                    return {
                        'type': 'cast_spell',
                        'spell_id': spell_id,
                        'success': False,
                        'message': f"{enemy.name}'s {spell_id} failed!"
                    }
                    
            elif action_type == 'heal':
                # AI enemy heals itself
                heal_amount = action.get('amount', 20)
                result = self.combat_service.apply_healing(enemy, enemy, heal_amount)
                
                if result['success']:
                    self.logger.info(f"AI {enemy.name} heals for {result['healing']:.1f}")
                    return {
                        'type': 'heal',
                        'healing': result['healing'],
                        'success': True,
                        'message': f"{enemy.name} heals for {result['healing']:.1f}!"
                    }
                    
            elif action_type == 'defend':
                # AI enemy takes defensive stance
                self.logger.debug(f"AI {enemy.name} takes defensive stance")
                return {
                    'type': 'defend',
                    'success': True,
                    'message': f"{enemy.name} takes a defensive stance!"
                }
                
            else:
                self.logger.warning(f"Unknown AI action type: {action_type}")
                
        except Exception as e:
            self.logger.error(f"Error executing AI action: {e}")
            
        return None
        
    def record_battle_result(self, player_won: bool, battle_duration: float = 0.0,
                           damage_dealt: float = 0.0, damage_received: float = 0.0):
        """Record battle results for difficulty scaling."""
        self.difficulty_scaler.record_battle_result(
            player_won, battle_duration, damage_dealt, damage_received
        )
        
    def get_difficulty_info(self) -> Dict[str, Any]:
        """Get current difficulty information."""
        return {
            'current_level': self.difficulty_scaler.current_difficulty.value,
            'performance': self.difficulty_scaler.get_performance_summary(),
            'modifiers': self.difficulty_scaler.get_current_modifiers().__dict__
        }
        
    def force_difficulty(self, difficulty: str):
        """Force a specific difficulty level (for testing)."""
        try:
            difficulty_level = DifficultyLevel(difficulty)
            self.difficulty_scaler.force_difficulty_level(difficulty_level)
            self.logger.info(f"Forced difficulty to {difficulty}")
        except ValueError:
            self.logger.error(f"Invalid difficulty level: {difficulty}")
            
    def clear_ai_actors(self):
        """Clear all AI-controlled actors."""
        count = len(self.ai_actors)
        self.ai_actors.clear()
        self.logger.info(f"Cleared {count} AI actors")


# Demo integration functions for easy use in demo.py
def create_ai_integration(combat_service: CombatService) -> AIIntegrationManager:
    """Create an AI integration manager for the demo."""
    return AIIntegrationManager(combat_service)


def setup_enemy_ai(ai_manager: AIIntegrationManager, enemy: Any, 
                  behavior_type: str = "basic_enemy") -> Any:
    """Set up AI control for an enemy."""
    return ai_manager.register_enemy_for_ai(enemy, behavior_type)


def update_enemy_ai(ai_manager: AIIntegrationManager, player: Any):
    """Update AI for all enemies and return actions taken."""
    return ai_manager.update_ai(player)


def get_ai_status(ai_manager: AIIntegrationManager) -> str:
    """Get a formatted string showing AI status."""
    difficulty_info = ai_manager.get_difficulty_info()
    performance = difficulty_info['performance']
    
    status = f"AI Status:\n"
    status += f"  Difficulty: {difficulty_info['current_level'].upper()}\n"
    status += f"  Battles: {performance['total_battles']} "
    status += f"(Win Rate: {performance['win_rate']:.1%})\n"
    status += f"  AI Actors: {len(ai_manager.ai_actors)}\n"
    
    if performance['win_streak'] > 0:
        status += f"  Win Streak: {performance['win_streak']}\n"
    elif performance['loss_streak'] > 0:
        status += f"  Loss Streak: {performance['loss_streak']}\n"
        
    return status
