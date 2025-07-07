"""
Combat AI System
===============

Provides intelligent combat behavior for enemies and NPCs.
Integrates with the existing combat service to perform actions.
"""

from typing import Any, Optional, List, Dict
import random
import logging
from enum import Enum

from ..combat.combat_service import CombatService
from .behavior_tree import NodeStatus


class CombatStrategy(Enum):
    """Different combat strategies for AI actors."""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    OPPORTUNISTIC = "opportunistic"


class ThreatLevel(Enum):
    """Threat assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CombatAI:
    """AI system for combat decision making."""
    
    def __init__(self, combat_service: Optional[CombatService] = None):
        self.combat_service = combat_service or CombatService()
        self.logger = logging.getLogger("combat_ai")
        
    def assess_threat(self, actor: Any, target: Any) -> ThreatLevel:
        """Assess the threat level of a target."""
        if not target or not hasattr(target, 'current_health'):
            return ThreatLevel.LOW
            
        # Calculate relative health percentages
        actor_health_pct = getattr(actor, 'current_health', 0) / max(getattr(actor, 'max_health', 1), 1)
        target_health_pct = getattr(target, 'current_health', 0) / max(getattr(target, 'max_health', 1), 1)
        
        # Calculate relative damage potential
        actor_attack = getattr(actor, 'attack', 0) if hasattr(actor, 'get_stat') else getattr(actor, 'attack', 0)
        target_attack = getattr(target, 'attack', 0) if hasattr(target, 'get_stat') else getattr(target, 'attack', 0)
        
        # Simple threat assessment based on multiple factors
        threat_score = 0
        
        # Target's offensive capability
        if target_attack > actor_attack * 1.5:
            threat_score += 2
        elif target_attack > actor_attack:
            threat_score += 1
            
        # Target's health (healthy targets are more threatening)
        if target_health_pct > 0.8:
            threat_score += 1
        elif target_health_pct > 0.5:
            threat_score += 0.5
            
        # Actor's own health (when low, everything is more threatening)
        if actor_health_pct < 0.3:
            threat_score += 2
        elif actor_health_pct < 0.6:
            threat_score += 1
            
        # Convert score to threat level
        if threat_score >= 4:
            return ThreatLevel.CRITICAL
        elif threat_score >= 2.5:
            return ThreatLevel.HIGH
        elif threat_score >= 1:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
            
    def choose_combat_strategy(self, actor: Any, target: Any) -> CombatStrategy:
        """Choose the best combat strategy based on current situation."""
        threat = self.assess_threat(actor, target)
        
        actor_health_pct = getattr(actor, 'current_health', 0) / max(getattr(actor, 'max_health', 1), 1)
        actor_mana_pct = getattr(actor, 'current_mana', 0) / max(getattr(actor, 'max_mana', 1), 1)
        
        # Critical situation - go defensive
        if threat == ThreatLevel.CRITICAL or actor_health_pct < 0.25:
            return CombatStrategy.DEFENSIVE
            
        # Low health but not critical - be opportunistic
        if actor_health_pct < 0.5:
            return CombatStrategy.OPPORTUNISTIC
            
        # High mana and healthy - be aggressive
        if actor_health_pct > 0.7 and actor_mana_pct > 0.6:
            return CombatStrategy.AGGRESSIVE
            
        # Default to balanced
        return CombatStrategy.BALANCED
        
    def get_available_actions(self, actor: Any) -> List[str]:
        """Get list of actions available to the actor."""
        actions = []
        
        # Basic attack is always available
        actions.append("attack")
        
        # Check for spells/abilities
        if hasattr(actor, 'known_spells') and actor.known_spells:
            for spell in actor.known_spells:
                # Check if actor has enough mana for spell
                mana_cost = self._get_spell_mana_cost(spell)
                if getattr(actor, 'current_mana', 0) >= mana_cost:
                    actions.append(f"spell_{spell}")
                    
        # Check for special abilities
        if hasattr(actor, 'special_abilities'):
            for ability in actor.special_abilities:
                actions.append(f"ability_{ability}")
                
        # Defensive actions
        if hasattr(actor, 'can_block') and actor.can_block:
            actions.append("block")
            
        return actions
        
    def _get_spell_mana_cost(self, spell_id: str) -> int:
        """Get mana cost for a spell."""
        # Simple mana cost mapping
        spell_costs = {
            "fireball": 15,
            "ice_shard": 12,
            "lightning_bolt": 18,
            "heal": 10,
            "magic_missile": 8,
            "shield": 6
        }
        return spell_costs.get(spell_id, 10)
        
    def select_best_action(self, actor: Any, target: Any, strategy: CombatStrategy) -> Dict[str, Any]:
        """Select the best action based on strategy and situation."""
        available_actions = self.get_available_actions(actor)
        
        if not available_actions:
            return {"action": "wait", "target": None}
            
        threat = self.assess_threat(actor, target)
        actor_health_pct = getattr(actor, 'current_health', 0) / max(getattr(actor, 'max_health', 1), 1)
        
        # Strategy-based action selection
        if strategy == CombatStrategy.DEFENSIVE:
            return self._select_defensive_action(actor, target, available_actions, actor_health_pct)
        elif strategy == CombatStrategy.AGGRESSIVE:
            return self._select_aggressive_action(actor, target, available_actions)
        elif strategy == CombatStrategy.OPPORTUNISTIC:
            return self._select_opportunistic_action(actor, target, available_actions, threat)
        else:  # BALANCED
            return self._select_balanced_action(actor, target, available_actions, actor_health_pct)
            
    def _select_defensive_action(self, actor: Any, target: Any, actions: List[str], health_pct: float) -> Dict[str, Any]:
        """Select defensive action."""
        # Prioritize healing if health is low
        if health_pct < 0.4:
            heal_spells = [a for a in actions if "spell_heal" in a]
            if heal_spells:
                return {"action": heal_spells[0], "target": actor}
                
        # Try to block if available
        if "block" in actions and random.random() < 0.3:
            return {"action": "block", "target": None}
            
        # Otherwise attack with weakest available option
        attack_actions = [a for a in actions if a.startswith("spell_") or a == "attack"]
        if attack_actions:
            # Prefer lower-cost spells
            if "spell_magic_missile" in attack_actions:
                return {"action": "spell_magic_missile", "target": target}
            elif "attack" in attack_actions:
                return {"action": "attack", "target": target}
                
        return {"action": "wait", "target": None}
        
    def _select_aggressive_action(self, actor: Any, target: Any, actions: List[str]) -> Dict[str, Any]:
        """Select aggressive action."""
        # Prioritize high-damage spells
        high_damage_spells = [a for a in actions if any(spell in a for spell in ["fireball", "lightning_bolt"])]
        if high_damage_spells:
            return {"action": random.choice(high_damage_spells), "target": target}
            
        # Medium damage spells
        medium_damage_spells = [a for a in actions if "spell_ice_shard" in a]
        if medium_damage_spells:
            return {"action": medium_damage_spells[0], "target": target}
            
        # Fall back to basic attack
        if "attack" in actions:
            return {"action": "attack", "target": target}
            
        return {"action": "wait", "target": None}
        
    def _select_opportunistic_action(self, actor: Any, target: Any, actions: List[str], threat: ThreatLevel) -> Dict[str, Any]:
        """Select opportunistic action based on threat level."""
        target_health_pct = getattr(target, 'current_health', 0) / max(getattr(target, 'max_health', 1), 1)
        
        # If target is low on health, go for the kill
        if target_health_pct < 0.3:
            return self._select_aggressive_action(actor, target, actions)
            
        # If we're in immediate danger, defend
        if threat in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            return self._select_defensive_action(actor, target, actions, 
                                               getattr(actor, 'current_health', 0) / max(getattr(actor, 'max_health', 1), 1))
            
        # Otherwise be balanced
        return self._select_balanced_action(actor, target, actions, 
                                          getattr(actor, 'current_health', 0) / max(getattr(actor, 'max_health', 1), 1))
        
    def _select_balanced_action(self, actor: Any, target: Any, actions: List[str], health_pct: float) -> Dict[str, Any]:
        """Select balanced action."""
        # Heal if health is getting low
        if health_pct < 0.5:
            heal_spells = [a for a in actions if "spell_heal" in a]
            if heal_spells and random.random() < 0.4:
                return {"action": heal_spells[0], "target": actor}
                
        # Mix of spells and attacks
        spell_actions = [a for a in actions if a.startswith("spell_") and "heal" not in a]
        if spell_actions and random.random() < 0.6:
            return {"action": random.choice(spell_actions), "target": target}
            
        # Basic attack
        if "attack" in actions:
            return {"action": "attack", "target": target}
            
        return {"action": "wait", "target": None}
        
    def execute_action(self, actor: Any, action_data: Dict[str, Any]) -> NodeStatus:
        """Execute the selected action."""
        action = action_data.get("action", "wait")
        target = action_data.get("target")
        
        try:
            if action == "attack":
                return self._execute_attack(actor, target)
            elif action.startswith("spell_"):
                spell_id = action.replace("spell_", "")
                return self._execute_spell(actor, spell_id, target)
            elif action == "block":
                return self._execute_block(actor)
            elif action == "wait":
                return NodeStatus.SUCCESS
            else:
                self.logger.warning(f"Unknown action: {action}")
                return NodeStatus.FAILURE
                
        except Exception as e:
            self.logger.error(f"Error executing action {action}: {e}")
            return NodeStatus.FAILURE
            
    def _execute_attack(self, actor: Any, target: Any) -> NodeStatus:
        """Execute basic attack."""
        if not target:
            return NodeStatus.FAILURE
            
        weapon = getattr(actor, 'weapon', None)
        result = self.combat_service.perform_attack(actor, target, weapon)
        
        return NodeStatus.SUCCESS if result.get('success', False) else NodeStatus.FAILURE
        
    def _execute_spell(self, actor: Any, spell_id: str, target: Any) -> NodeStatus:
        """Execute spell casting."""
        if not target:
            target = actor if spell_id == "heal" else None
            
        if not target:
            return NodeStatus.FAILURE
            
        result = self.combat_service.cast_spell_at_target(actor, spell_id, target)
        
        return NodeStatus.SUCCESS if result.get('success', False) else NodeStatus.FAILURE
        
    def _execute_block(self, actor: Any) -> NodeStatus:
        """Execute blocking action."""
        # Set blocking flag if actor supports it
        if hasattr(actor, 'is_blocking'):
            actor.is_blocking = True
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
        
    def make_combat_decision(self, actor: Any, target: Any) -> Dict[str, Any]:
        """Make a complete combat decision for an actor."""
        strategy = self.choose_combat_strategy(actor, target)
        action_data = self.select_best_action(actor, target, strategy)
        
        self.logger.info(f"{getattr(actor, 'name', 'Actor')} chose {strategy.value} strategy, action: {action_data['action']}")
        
        return {
            'strategy': strategy,
            'action_data': action_data,
            'threat_level': self.assess_threat(actor, target)
        }
        
    # Static methods for behavior tree integration
    @staticmethod
    def has_available_spells(actor: Any) -> bool:
        """Check if actor has any usable spells."""
        if not hasattr(actor, 'known_spells') or not actor.known_spells:
            return False
            
        current_mana = getattr(actor, 'current_mana', 0)
        ai = CombatAI()
        
        for spell in actor.known_spells:
            mana_cost = ai._get_spell_mana_cost(spell)
            if current_mana >= mana_cost:
                return True
                
        return False
        
    @staticmethod
    def has_offensive_spells(actor: Any) -> bool:
        """Check if actor has offensive spells available."""
        if not hasattr(actor, 'known_spells'):
            return False
            
        offensive_spells = ["fireball", "ice_shard", "lightning_bolt", "magic_missile"]
        current_mana = getattr(actor, 'current_mana', 0)
        ai = CombatAI()
        
        for spell in actor.known_spells:
            if spell in offensive_spells:
                mana_cost = ai._get_spell_mana_cost(spell)
                if current_mana >= mana_cost:
                    return True
                    
        return False
        
    @staticmethod
    def has_heal_spells(actor: Any) -> bool:
        """Check if actor has healing spells available."""
        if not hasattr(actor, 'known_spells'):
            return False
            
        heal_spells = ["heal"]
        current_mana = getattr(actor, 'current_mana', 0)
        ai = CombatAI()
        
        for spell in actor.known_spells:
            if spell in heal_spells:
                mana_cost = ai._get_spell_mana_cost(spell)
                if current_mana >= mana_cost:
                    return True
                    
        return False
        
    @staticmethod
    def has_defensive_spells(actor: Any) -> bool:
        """Check if actor has defensive spells available."""
        if not hasattr(actor, 'known_spells'):
            return False
            
        defensive_spells = ["shield", "protection"]
        current_mana = getattr(actor, 'current_mana', 0)
        ai = CombatAI()
        
        for spell in actor.known_spells:
            if spell in defensive_spells:
                mana_cost = ai._get_spell_mana_cost(spell)
                if current_mana >= mana_cost:
                    return True
                    
        return False
        
    @staticmethod
    def attack_target(actor: Any, target: Any) -> NodeStatus:
        """Attack action for behavior trees."""
        if not target:
            return NodeStatus.FAILURE
            
        ai = CombatAI()
        return ai._execute_attack(actor, target)
        
    @staticmethod
    def cast_best_spell(actor: Any, target: Any) -> NodeStatus:
        """Cast the best available spell."""
        if not target:
            return NodeStatus.FAILURE
            
        ai = CombatAI()
        strategy = ai.choose_combat_strategy(actor, target)
        action_data = ai.select_best_action(actor, target, strategy)
        
        if action_data['action'].startswith('spell_'):
            spell_id = action_data['action'].replace('spell_', '')
            return ai._execute_spell(actor, spell_id, action_data['target'])
            
        return NodeStatus.FAILURE
        
    @staticmethod
    def cast_offensive_spell(actor: Any, target: Any) -> NodeStatus:
        """Cast an offensive spell."""
        if not target or not CombatAI.has_offensive_spells(actor):
            return NodeStatus.FAILURE
            
        ai = CombatAI()
        offensive_spells = ["fireball", "lightning_bolt", "ice_shard", "magic_missile"]
        available_spells = [s for s in actor.known_spells if s in offensive_spells]
        
        if available_spells:
            spell = random.choice(available_spells)
            return ai._execute_spell(actor, spell, target)
            
        return NodeStatus.FAILURE
        
    @staticmethod
    def cast_heal_spell(actor: Any, target: Any) -> NodeStatus:
        """Cast a healing spell."""
        if not target or not CombatAI.has_heal_spells(actor):
            return NodeStatus.FAILURE
            
        ai = CombatAI()
        return ai._execute_spell(actor, "heal", target)
        
    @staticmethod
    def cast_defensive_spell(actor: Any, target: Any) -> NodeStatus:
        """Cast a defensive spell."""
        if not target or not CombatAI.has_defensive_spells(actor):
            return NodeStatus.FAILURE
            
        ai = CombatAI()
        defensive_spells = ["shield", "protection"]
        available_spells = [s for s in actor.known_spells if s in defensive_spells]
        
        if available_spells:
            spell = random.choice(available_spells)
            return ai._execute_spell(actor, spell, target)
            
        return NodeStatus.FAILURE
