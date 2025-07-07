"""
AI Service - Main AI Coordination
=================================

Central AI service that coordinates all AI subsystems and provides
a unified interface for AI behavior in the game.
"""

from typing import Any, Dict, Optional, List
import logging
import random
import time

from .combat_ai import CombatAI, CombatStrategy
from .behavior_tree import BehaviorTree, CombatBehaviorBuilder
from .difficulty_scaling import DifficultyScaler, DifficultyLevel


class AIService:
    """Main AI service that coordinates all AI systems."""
    
    def __init__(self, combat_service=None):
        self.logger = logging.getLogger("ai_service")
        self.combat_ai = CombatAI(combat_service)
        self.difficulty_scaler = DifficultyScaler()
        
        # Pre-built behavior trees
        self.behavior_trees = {
            "basic_enemy": CombatBehaviorBuilder.build_basic_enemy(),
            "aggressive_enemy": CombatBehaviorBuilder.build_aggressive_enemy(),
            "defensive_enemy": CombatBehaviorBuilder.build_defensive_enemy()
        }
        
        # AI actor registry
        self.ai_actors: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("AI Service initialized")
        
    def register_ai_actor(self, actor: Any, behavior_type: str = "basic_enemy", 
                         custom_config: Optional[Dict[str, Any]] = None):
        """Register an actor for AI control."""
        actor_id = str(id(actor))
        
        # Apply difficulty scaling
        self.difficulty_scaler.apply_modifiers_to_enemy(actor)
        
        # Set up AI configuration
        config = {
            'actor': actor,
            'behavior_type': behavior_type,
            'behavior_tree': self.behavior_trees.get(behavior_type),
            'last_action_time': 0.0,
            'action_cooldown': 1.0,  # 1 second between actions
            'combat_strategy': None,
            'target': None,
            'active': True
        }
        
        # Apply custom configuration
        if custom_config:
            config.update(custom_config)
            
        # Give AI actors some basic spells if they don't have any
        self._ensure_ai_spells(actor)
        
        self.ai_actors[actor_id] = config
        
        self.logger.info(f"Registered AI actor: {getattr(actor, 'name', 'Unknown')} "
                        f"with behavior: {behavior_type}")
        
    def unregister_ai_actor(self, actor: Any):
        """Unregister an actor from AI control."""
        actor_id = str(id(actor))
        if actor_id in self.ai_actors:
            del self.ai_actors[actor_id]
            self.logger.info(f"Unregistered AI actor: {getattr(actor, 'name', 'Unknown')}")
            
    def _ensure_ai_spells(self, actor: Any):
        """Ensure AI actors have some spells to use."""
        if not hasattr(actor, 'known_spells') or not actor.known_spells:
            # Give basic spells based on actor type/level
            basic_spells = ["magic_missile"]
            
            # Add more spells based on level or type
            if hasattr(actor, 'level') and actor.level >= 3:
                basic_spells.append("fireball")
                
            if hasattr(actor, 'level') and actor.level >= 2:
                basic_spells.append("heal")
                
            if hasattr(actor, 'name') and 'dragon' in actor.name.lower():
                basic_spells.extend(["fireball", "lightning_bolt"])
                
            actor.known_spells = basic_spells
            self.logger.debug(f"Gave {getattr(actor, 'name', 'actor')} spells: {basic_spells}")
            
    def set_target_for_actor(self, actor: Any, target: Any):
        """Set combat target for an AI actor."""
        actor_id = str(id(actor))
        if actor_id in self.ai_actors:
            self.ai_actors[actor_id]['target'] = target
            self.logger.debug(f"Set target for {getattr(actor, 'name', 'actor')}: "
                            f"{getattr(target, 'name', 'target') if target else 'None'}")
            
    def get_ai_actor_info(self, actor: Any) -> Optional[Dict[str, Any]]:
        """Get AI configuration for an actor."""
        actor_id = str(id(actor))
        return self.ai_actors.get(actor_id)
        
    def update_ai_actors(self, delta_time: float = 1.0):
        """Update all AI actors."""
        current_time = time.time()
        actions_performed = 0
        
        for actor_id, config in self.ai_actors.items():
            if not config['active']:
                continue
                
            actor = config['actor']
            
            # Check if actor is still alive
            if hasattr(actor, 'current_health') and actor.current_health <= 0:
                config['active'] = False
                continue
                
            # Check action cooldown
            if current_time - config['last_action_time'] < config['action_cooldown']:
                continue
                
            # Perform AI action
            if self._perform_ai_action(config):
                config['last_action_time'] = current_time
                actions_performed += 1
                
        if actions_performed > 0:
            self.logger.debug(f"Performed {actions_performed} AI actions")
            
    def _perform_ai_action(self, config: Dict[str, Any]) -> bool:
        """Perform an AI action for a specific actor."""
        actor = config['actor']
        target = config['target']
        behavior_tree = config['behavior_tree']
        
        if not target:
            return False
            
        try:
            # Create context for behavior tree
            context = {
                'target': target,
                'ai_service': self,
                'combat_ai': self.combat_ai,
                'difficulty_modifiers': self.difficulty_scaler.get_current_modifiers()
            }
            
            # Execute behavior tree
            if behavior_tree:
                from .behavior_tree import NodeStatus
                status = behavior_tree.execute(actor, context)
                return status != NodeStatus.FAILURE
            else:
                # Fallback: Direct combat AI decision
                decision = self.combat_ai.make_combat_decision(actor, target)
                action_data = decision['action_data']
                status = self.combat_ai.execute_action(actor, action_data)
                return status != NodeStatus.FAILURE
                
        except Exception as e:
            self.logger.error(f"Error performing AI action for {getattr(actor, 'name', 'actor')}: {e}")
            return False
            
    def force_ai_action(self, actor: Any, target: Any) -> bool:
        """Force an immediate AI action (for testing/manual triggers)."""
        actor_id = str(id(actor))
        config = self.ai_actors.get(actor_id)
        
        if not config:
            self.logger.warning(f"Actor {getattr(actor, 'name', 'Unknown')} not registered for AI")
            return False
            
        # Temporarily set target and perform action
        old_target = config['target']
        config['target'] = target
        
        result = self._perform_ai_action(config)
        
        # Restore original target
        config['target'] = old_target
        
        return result
        
    def get_ai_behavior_types(self) -> List[str]:
        """Get list of available AI behavior types."""
        return list(self.behavior_trees.keys())
        
    def change_actor_behavior(self, actor: Any, behavior_type: str):
        """Change an actor's behavior type."""
        actor_id = str(id(actor))
        if actor_id in self.ai_actors and behavior_type in self.behavior_trees:
            self.ai_actors[actor_id]['behavior_type'] = behavior_type
            self.ai_actors[actor_id]['behavior_tree'] = self.behavior_trees[behavior_type]
            self.logger.info(f"Changed {getattr(actor, 'name', 'actor')} behavior to {behavior_type}")
            
    def set_actor_active(self, actor: Any, active: bool):
        """Enable or disable AI for an actor."""
        actor_id = str(id(actor))
        if actor_id in self.ai_actors:
            self.ai_actors[actor_id]['active'] = active
            status = "enabled" if active else "disabled"
            self.logger.info(f"AI {status} for {getattr(actor, 'name', 'actor')}")
            
    def record_battle_result(self, player_won: bool, battle_duration: float = 0.0,
                           damage_dealt: float = 0.0, damage_received: float = 0.0):
        """Record battle result for difficulty scaling."""
        self.difficulty_scaler.record_battle_result(
            player_won, battle_duration, damage_dealt, damage_received
        )
        
    def record_battle_start(self):
        """Record battle start for metrics."""
        self.difficulty_scaler.record_battle_start()
        
    def get_difficulty_info(self) -> Dict[str, Any]:
        """Get current difficulty information."""
        return self.difficulty_scaler.get_performance_summary()
        
    def force_difficulty(self, difficulty: str):
        """Force a specific difficulty level."""
        try:
            difficulty_level = DifficultyLevel(difficulty)
            self.difficulty_scaler.force_difficulty_level(difficulty_level)
            self.logger.info(f"Difficulty manually set to {difficulty}")
        except ValueError:
            valid_levels = [level.value for level in DifficultyLevel]
            self.logger.error(f"Invalid difficulty: {difficulty}. Valid: {valid_levels}")
            
    def get_active_ai_actors(self) -> List[Any]:
        """Get list of currently active AI actors."""
        return [config['actor'] for config in self.ai_actors.values() 
                if config['active'] and config['actor']]
                
    def clear_all_ai_actors(self):
        """Clear all AI actors (useful for resetting game state)."""
        self.ai_actors.clear()
        self.logger.info("Cleared all AI actors")
        
    def get_ai_status_summary(self) -> Dict[str, Any]:
        """Get summary of AI system status."""
        active_actors = sum(1 for config in self.ai_actors.values() if config['active'])
        total_actors = len(self.ai_actors)
        
        behavior_counts = {}
        for config in self.ai_actors.values():
            behavior_type = config['behavior_type']
            behavior_counts[behavior_type] = behavior_counts.get(behavior_type, 0) + 1
            
        return {
            'total_ai_actors': total_actors,
            'active_ai_actors': active_actors,
            'behavior_type_counts': behavior_counts,
            'available_behaviors': self.get_ai_behavior_types(),
            'difficulty_info': self.get_difficulty_info()
        }
        
    def create_custom_behavior_tree(self, name: str, root_node) -> BehaviorTree:
        """Create and register a custom behavior tree."""
        tree = BehaviorTree(name, root_node)
        self.behavior_trees[name] = tree
        self.logger.info(f"Created custom behavior tree: {name}")
        return tree
        
    def simulate_ai_vs_ai_battle(self, actor1: Any, actor2: Any, max_rounds: int = 20) -> Dict[str, Any]:
        """Simulate a battle between two AI actors (for testing)."""
        self.logger.info(f"Starting AI vs AI battle: {getattr(actor1, 'name', 'Actor1')} vs {getattr(actor2, 'name', 'Actor2')}")
        
        # Register both actors if needed
        if str(id(actor1)) not in self.ai_actors:
            self.register_ai_actor(actor1, "aggressive_enemy")
        if str(id(actor2)) not in self.ai_actors:
            self.register_ai_actor(actor2, "defensive_enemy")
            
        # Set targets
        self.set_target_for_actor(actor1, actor2)
        self.set_target_for_actor(actor2, actor1)
        
        # Battle loop
        rounds = 0
        battle_log = []
        
        while rounds < max_rounds:
            rounds += 1
            
            # Check for battle end
            if (hasattr(actor1, 'current_health') and actor1.current_health <= 0) or \
               (hasattr(actor2, 'current_health') and actor2.current_health <= 0):
                break
                
            # Perform AI actions
            self.update_ai_actors()
            
            # Log round state
            round_info = {
                'round': rounds,
                'actor1_health': getattr(actor1, 'current_health', 0),
                'actor2_health': getattr(actor2, 'current_health', 0)
            }
            battle_log.append(round_info)
            
        # Determine winner
        actor1_alive = getattr(actor1, 'current_health', 0) > 0
        actor2_alive = getattr(actor2, 'current_health', 0) > 0
        
        if actor1_alive and not actor2_alive:
            winner = actor1
        elif actor2_alive and not actor1_alive:
            winner = actor2
        else:
            winner = None  # Draw or both alive
            
        result = {
            'winner': getattr(winner, 'name', 'Draw') if winner else 'Draw',
            'rounds': rounds,
            'battle_log': battle_log,
            'final_health': {
                'actor1': getattr(actor1, 'current_health', 0),
                'actor2': getattr(actor2, 'current_health', 0)
            }
        }
        
        self.logger.info(f"AI battle completed: {result['winner']} wins in {rounds} rounds")
        return result
