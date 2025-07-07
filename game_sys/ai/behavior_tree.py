"""
Behavior Tree System
===================

Implements a flexible behavior tree system for AI decision making.
Behavior trees provide a structured way to define complex AI behaviors
through composable nodes.
"""

from enum import Enum
from typing import Any, List, Optional, Callable
import random
import time


class NodeStatus(Enum):
    """Status returned by behavior tree nodes."""
    SUCCESS = "success"
    FAILURE = "failure" 
    RUNNING = "running"


class BehaviorNode:
    """Base class for all behavior tree nodes."""
    
    def __init__(self, name: str = "Node"):
        self.name = name
        self.parent: Optional['BehaviorNode'] = None
        self.children: List['BehaviorNode'] = []
        self.status = NodeStatus.FAILURE
        
    def add_child(self, child: 'BehaviorNode') -> 'BehaviorNode':
        """Add a child node."""
        child.parent = self
        self.children.append(child)
        return self
        
    def execute(self, actor: Any, context: dict) -> NodeStatus:
        """Execute this node and return status."""
        raise NotImplementedError("Subclasses must implement execute()")
        
    def reset(self):
        """Reset node state."""
        self.status = NodeStatus.FAILURE
        for child in self.children:
            child.reset()


class SequenceNode(BehaviorNode):
    """Executes children in order until one fails."""
    
    def __init__(self, name: str = "Sequence"):
        super().__init__(name)
        self.current_child = 0
        
    def execute(self, actor: Any, context: dict) -> NodeStatus:
        """Execute children in sequence."""
        while self.current_child < len(self.children):
            child = self.children[self.current_child]
            status = child.execute(actor, context)
            
            if status == NodeStatus.FAILURE:
                self.reset()
                return NodeStatus.FAILURE
            elif status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            elif status == NodeStatus.SUCCESS:
                self.current_child += 1
                
        # All children succeeded
        self.reset()
        return NodeStatus.SUCCESS
        
    def reset(self):
        """Reset sequence state."""
        super().reset()
        self.current_child = 0


class SelectorNode(BehaviorNode):
    """Executes children until one succeeds."""
    
    def __init__(self, name: str = "Selector"):
        super().__init__(name)
        self.current_child = 0
        
    def execute(self, actor: Any, context: dict) -> NodeStatus:
        """Execute children until one succeeds."""
        while self.current_child < len(self.children):
            child = self.children[self.current_child]
            status = child.execute(actor, context)
            
            if status == NodeStatus.SUCCESS:
                self.reset()
                return NodeStatus.SUCCESS
            elif status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            elif status == NodeStatus.FAILURE:
                self.current_child += 1
                
        # All children failed
        self.reset()
        return NodeStatus.FAILURE
        
    def reset(self):
        """Reset selector state."""
        super().reset()
        self.current_child = 0


class ParallelNode(BehaviorNode):
    """Executes all children simultaneously."""
    
    def __init__(self, name: str = "Parallel", success_threshold: int = 1):
        super().__init__(name)
        self.success_threshold = success_threshold
        
    def execute(self, actor: Any, context: dict) -> NodeStatus:
        """Execute all children in parallel."""
        success_count = 0
        failure_count = 0
        running_count = 0
        
        for child in self.children:
            status = child.execute(actor, context)
            
            if status == NodeStatus.SUCCESS:
                success_count += 1
            elif status == NodeStatus.FAILURE:
                failure_count += 1
            elif status == NodeStatus.RUNNING:
                running_count += 1
                
        # Check success condition
        if success_count >= self.success_threshold:
            return NodeStatus.SUCCESS
            
        # Check if enough children have failed to make success impossible
        remaining = len(self.children) - (success_count + failure_count)
        if success_count + remaining < self.success_threshold:
            return NodeStatus.FAILURE
            
        # Still running
        return NodeStatus.RUNNING


class ConditionNode(BehaviorNode):
    """Node that checks a condition."""
    
    def __init__(self, name: str, condition_func: Callable[[Any, dict], bool]):
        super().__init__(name)
        self.condition_func = condition_func
        
    def execute(self, actor: Any, context: dict) -> NodeStatus:
        """Check condition and return status."""
        if self.condition_func(actor, context):
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE


class ActionNode(BehaviorNode):
    """Node that performs an action."""
    
    def __init__(self, name: str, action_func: Callable[[Any, dict], NodeStatus]):
        super().__init__(name)
        self.action_func = action_func
        
    def execute(self, actor: Any, context: dict) -> NodeStatus:
        """Execute action and return status."""
        return self.action_func(actor, context)


class WaitNode(BehaviorNode):
    """Node that waits for a specified duration."""
    
    def __init__(self, name: str = "Wait", duration: float = 1.0):
        super().__init__(name)
        self.duration = duration
        self.start_time: Optional[float] = None
        
    def execute(self, actor: Any, context: dict) -> NodeStatus:
        """Wait for specified duration."""
        current_time = time.time()
        
        if self.start_time is None:
            self.start_time = current_time
            
        if current_time - self.start_time >= self.duration:
            self.reset()
            return NodeStatus.SUCCESS
            
        return NodeStatus.RUNNING
        
    def reset(self):
        """Reset wait timer."""
        super().reset()
        self.start_time = None


class RandomSelectorNode(BehaviorNode):
    """Selector that randomly chooses a child to execute."""
    
    def __init__(self, name: str = "RandomSelector"):
        super().__init__(name)
        self.selected_child: Optional[int] = None
        
    def execute(self, actor: Any, context: dict) -> NodeStatus:
        """Execute a randomly selected child."""
        if not self.children:
            return NodeStatus.FAILURE
            
        if self.selected_child is None:
            self.selected_child = random.randint(0, len(self.children) - 1)
            
        child = self.children[self.selected_child]
        status = child.execute(actor, context)
        
        if status != NodeStatus.RUNNING:
            self.reset()
            
        return status
        
    def reset(self):
        """Reset random selection."""
        super().reset()
        self.selected_child = None


class BehaviorTree:
    """Main behavior tree class that manages execution."""
    
    def __init__(self, name: str = "BehaviorTree", root: Optional[BehaviorNode] = None):
        self.name = name
        self.root = root
        self.last_status = NodeStatus.FAILURE
        self.execution_count = 0
        
    def set_root(self, root: BehaviorNode):
        """Set the root node of the tree."""
        self.root = root
        
    def execute(self, actor: Any, context: Optional[dict] = None) -> NodeStatus:
        """Execute the behavior tree."""
        if self.root is None:
            return NodeStatus.FAILURE
            
        if context is None:
            context = {}
            
        self.execution_count += 1
        context['execution_count'] = self.execution_count
        context['tree_name'] = self.name
        
        self.last_status = self.root.execute(actor, context)
        return self.last_status
        
    def reset(self):
        """Reset the entire tree."""
        if self.root:
            self.root.reset()
        self.last_status = NodeStatus.FAILURE
        self.execution_count = 0


# Pre-built behavior tree builders for common patterns

class CombatBehaviorBuilder:
    """Builder for common combat behavior trees."""
    
    @staticmethod
    def build_basic_enemy() -> BehaviorTree:
        """Build a basic enemy behavior tree."""
        from .combat_ai import CombatAI  # Import here to avoid circular dependency
        
        root = SelectorNode("EnemyRoot")
        
        # High priority: Cast spells if available and low health
        spell_sequence = SequenceNode("SpellCasting")
        spell_sequence.add_child(ConditionNode("LowHealth", 
            lambda actor, ctx: getattr(actor, 'current_health', 0) < getattr(actor, 'max_health', 1) * 0.3))
        spell_sequence.add_child(ConditionNode("HasSpells", 
            lambda actor, ctx: CombatAI.has_available_spells(actor)))
        spell_sequence.add_child(ActionNode("CastSpell", 
            lambda actor, ctx: CombatAI.cast_best_spell(actor, ctx.get('target'))))
        
        # Medium priority: Attack if enemy is close
        attack_sequence = SequenceNode("Attack")
        attack_sequence.add_child(ConditionNode("HasTarget", 
            lambda actor, ctx: ctx.get('target') is not None))
        attack_sequence.add_child(ActionNode("AttackTarget", 
            lambda actor, ctx: CombatAI.attack_target(actor, ctx.get('target'))))
        
        # Low priority: Wait/idle
        wait_action = ActionNode("Wait", 
            lambda actor, ctx: NodeStatus.SUCCESS)
        
        root.add_child(spell_sequence)
        root.add_child(attack_sequence)
        root.add_child(wait_action)
        
        tree = BehaviorTree("BasicEnemy", root)
        return tree
        
    @staticmethod
    def build_aggressive_enemy() -> BehaviorTree:
        """Build an aggressive enemy behavior tree."""
        from .combat_ai import CombatAI
        
        root = SelectorNode("AggressiveRoot")
        
        # Always attack if target is available
        attack_sequence = SequenceNode("AggressiveAttack")
        attack_sequence.add_child(ConditionNode("HasTarget", 
            lambda actor, ctx: ctx.get('target') is not None))
        attack_sequence.add_child(ActionNode("AttackTarget", 
            lambda actor, ctx: CombatAI.attack_target(actor, ctx.get('target'))))
        
        # Cast offensive spells
        spell_sequence = SequenceNode("OffensiveSpells")
        spell_sequence.add_child(ConditionNode("HasOffensiveSpells", 
            lambda actor, ctx: CombatAI.has_offensive_spells(actor)))
        spell_sequence.add_child(ActionNode("CastOffensiveSpell", 
            lambda actor, ctx: CombatAI.cast_offensive_spell(actor, ctx.get('target'))))
        
        root.add_child(attack_sequence)
        root.add_child(spell_sequence)
        
        tree = BehaviorTree("AggressiveEnemy", root)
        return tree
        
    @staticmethod
    def build_defensive_enemy() -> BehaviorTree:
        """Build a defensive enemy behavior tree."""
        from .combat_ai import CombatAI
        
        root = SelectorNode("DefensiveRoot")
        
        # High priority: Heal if health is low
        heal_sequence = SequenceNode("SelfHeal")
        heal_sequence.add_child(ConditionNode("LowHealth", 
            lambda actor, ctx: getattr(actor, 'current_health', 0) < getattr(actor, 'max_health', 1) * 0.4))
        heal_sequence.add_child(ConditionNode("HasHealSpells", 
            lambda actor, ctx: CombatAI.has_heal_spells(actor)))
        heal_sequence.add_child(ActionNode("CastHeal", 
            lambda actor, ctx: CombatAI.cast_heal_spell(actor, actor)))
        
        # Medium priority: Attack if healthy
        attack_sequence = SequenceNode("CautiousAttack")
        attack_sequence.add_child(ConditionNode("HealthyEnough", 
            lambda actor, ctx: getattr(actor, 'current_health', 0) > getattr(actor, 'max_health', 1) * 0.5))
        attack_sequence.add_child(ConditionNode("HasTarget", 
            lambda actor, ctx: ctx.get('target') is not None))
        attack_sequence.add_child(ActionNode("AttackTarget", 
            lambda actor, ctx: CombatAI.attack_target(actor, ctx.get('target'))))
        
        # Low priority: Defensive spells
        defense_sequence = SequenceNode("DefensiveSpells")
        defense_sequence.add_child(ConditionNode("HasDefensiveSpells", 
            lambda actor, ctx: CombatAI.has_defensive_spells(actor)))
        defense_sequence.add_child(ActionNode("CastDefensiveSpell", 
            lambda actor, ctx: CombatAI.cast_defensive_spell(actor, actor)))
        
        root.add_child(heal_sequence)
        root.add_child(attack_sequence)
        root.add_child(defense_sequence)
        
        tree = BehaviorTree("DefensiveEnemy", root)
        return tree
