"""
Achievement System Module

This module provides event-driven achievement tracking for the RPG engine.
It demonstrates proper observer pattern implementation by reacting to
character system events and awarding achievements based on progression.
"""

from .achievement_system import AchievementSystem, Achievement, AchievementUnlockedEvent

__all__ = ['AchievementSystem', 'Achievement', 'AchievementUnlockedEvent']
