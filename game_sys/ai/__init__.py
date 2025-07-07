"""
AI System Package
================

Provides intelligent behavior for NPCs, enemies, and combat scenarios.
"""

from .ai_service import AIService
from .combat_ai import CombatAI
from .behavior_tree import BehaviorTree, BehaviorNode
from .difficulty_scaling import DifficultyScaler

__all__ = [
    'AIService',
    'CombatAI', 
    'BehaviorTree',
    'BehaviorNode',
    'DifficultyScaler'
]
