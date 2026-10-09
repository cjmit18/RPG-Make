"""
Achievement System - Event-driven achievement tracking

This system demonstrates proper observer pattern implementation by
listening to character system events and awarding achievements
based on character progression and milestones.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from rpg_engine.core.event_bus import EventBus, GameEvent, EventHandler
from rpg_engine.core.config import GameConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AchievementUnlockedEvent(GameEvent):
    """Event fired when a player unlocks an achievement"""
    achievement_id: str = ""
    achievement_name: str = ""
    achievement_description: str = ""
    points_awarded: int = 0
    character_id: str = ""


@dataclass
class Achievement:
    """Represents a single achievement"""
    id: str
    name: str
    description: str
    points: int
    category: str
    unlocked: bool = False
    unlock_timestamp: Optional[float] = None
    progress: Dict[str, Any] = field(default_factory=dict)
    
    def unlock(self) -> None:
        """Mark achievement as unlocked"""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_timestamp = time.time()
            logger.info(f"Achievement unlocked: {self.name} ({self.points} points)")


class AchievementSystem(EventHandler):
    """
    Event-driven achievement system that demonstrates proper observer pattern.
    
    This system listens to various character events and awards achievements
    based on predefined criteria, showcasing how to implement reactive
    business logic using the event bus.
    """
    
    def __init__(self, event_bus: EventBus, config: GameConfig):
        self.event_bus = event_bus
        self.config = config
        self.achievements: Dict[str, Achievement] = {}
        self.character_stats: Dict[str, Dict[str, Any]] = {}
        self.total_points = 0
        
        # Initialize achievements from config
        self._load_achievements()
        
        # Subscribe to relevant events - this is the key observer pattern implementation
        self._setup_event_subscriptions()
        
        logger.info(f"Achievement system initialized with {len(self.achievements)} achievements")
    
    def _load_achievements(self) -> None:
        """Load achievements from configuration"""
        achievement_config = self.config.get('achievement_system', {})
        if not achievement_config.get('enabled', False):
            logger.warning("Achievement system disabled in configuration")
            return
            
        categories = achievement_config.get('categories', {})
        
        for category_name, category_data in categories.items():
            for achievement_id, achievement_data in category_data.items():
                if isinstance(achievement_data, dict):
                    achievement = Achievement(
                        id=f"{category_name}.{achievement_id}",
                        name=achievement_data.get('name', 'Unknown Achievement'),
                        description=achievement_data.get('description', 'No description'),
                        points=achievement_data.get('points', 0),
                        category=category_name
                    )
                    self.achievements[achievement.id] = achievement
    
    def _setup_event_subscriptions(self) -> None:
        """Subscribe to events - demonstrates observer pattern"""
        from rpg_engine.systems.character.character_system import CharacterCreatedEvent
        from rpg_engine.systems.character.progression_system import CharacterLevelUpEvent, ExperienceGainedEvent
        from rpg_engine.systems.character.stat_system import StatChangedEvent
        
        # Character creation events
        self.event_bus.subscribe(CharacterCreatedEvent, self)
        
        # Progression events  
        self.event_bus.subscribe(CharacterLevelUpEvent, self)
        self.event_bus.subscribe(ExperienceGainedEvent, self)
        
        # Stat change events
        self.event_bus.subscribe(StatChangedEvent, self)
        
        logger.info("Achievement system subscribed to character events")
    
    async def handle(self, event: GameEvent) -> None:
        """
        Main event handler - demonstrates reactive programming
        
        This method shows how to implement proper event-driven business logic
        by reacting to different types of events and checking achievement criteria.
        """
        try:
            # Import here to avoid circular imports
            from rpg_engine.systems.character.character_system import CharacterCreatedEvent
            from rpg_engine.systems.character.progression_system import CharacterLevelUpEvent, ExperienceGainedEvent
            from rpg_engine.systems.character.stat_system import StatChangedEvent
            
            if isinstance(event, CharacterCreatedEvent):
                await self._handle_character_created(event)
            elif isinstance(event, CharacterLevelUpEvent):
                await self._handle_level_up(event)
            elif isinstance(event, ExperienceGainedEvent):
                await self._handle_experience_gained(event)
            elif isinstance(event, StatChangedEvent):
                await self._handle_stat_changed(event)
                
        except Exception as e:
            logger.error(f"Error handling achievement event {event.__class__.__name__}: {e}")
    
    async def _handle_character_created(self, event) -> None:
        """Handle character creation achievements"""
        character_id = getattr(event, 'character_id', '')
        
        # Track character creation
        if character_id not in self.character_stats:
            self.character_stats[character_id] = {
                'created': True,
                'level': 1,
                'stats': {},
                'total_characters_created': len(self.character_stats) + 1
            }
        
        # Check first character achievement
        await self._check_achievement_criteria('character_creation.first_character', {
            'characters_created': len(self.character_stats)
        }, character_id)
        
        # Check character variety achievement (5 characters)
        await self._check_achievement_criteria('character_creation.character_variety', {
            'characters_created': len(self.character_stats)
        }, character_id)
    
    async def _handle_level_up(self, event) -> None:
        """Handle level up achievements"""
        character_id = getattr(event, 'character_id', '')
        new_level = getattr(event, 'new_level', 1)
        
        # Update character tracking
        if character_id not in self.character_stats:
            self.character_stats[character_id] = {}
        self.character_stats[character_id]['level'] = new_level
        
        # Check level milestone achievements
        level_achievements = [
            ('progression.level_milestones.level_10', 10),
            ('progression.level_milestones.level_25', 25),
            ('progression.level_milestones.level_50', 50),
            ('progression.level_milestones.max_level', self.config.get('character_mechanics', {}).get('progression', {}).get('max_level', 100))
        ]
        
        for achievement_id, required_level in level_achievements:
            if new_level >= required_level:
                await self._check_achievement_criteria(achievement_id, {
                    'level': new_level,
                    'required_level': required_level
                }, character_id)
    
    async def _handle_experience_gained(self, event) -> None:
        """Handle experience-related achievements"""
        # Could add experience-based achievements here
        pass
    
    async def _handle_stat_changed(self, event) -> None:
        """Handle stat-based achievements"""
        character_id = getattr(event, 'character_id', '')
        stat_name = getattr(event, 'stat_name', '')
        new_value = getattr(event, 'new_value', 0)
        
        # Update character stat tracking
        if character_id not in self.character_stats:
            self.character_stats[character_id] = {'stats': {}}
        if 'stats' not in self.character_stats[character_id]:
            self.character_stats[character_id]['stats'] = {}
            
        self.character_stats[character_id]['stats'][stat_name] = new_value
        
        # Check stat threshold achievements
        stat_achievements = [
            ('stats.stat_thresholds.strength_100', 'strength', 100),
            ('stats.stat_thresholds.intelligence_100', 'intelligence', 100)
        ]
        
        for achievement_id, required_stat, required_value in stat_achievements:
            if stat_name == required_stat and new_value >= required_value:
                await self._check_achievement_criteria(achievement_id, {
                    'stat_name': stat_name,
                    'stat_value': new_value,
                    'required_value': required_value
                }, character_id)
        
        # Check balanced stats achievement (all stats above 50)
        character_stats = self.character_stats[character_id]['stats']
        main_stats = ['strength', 'dexterity', 'vitality', 'intelligence', 'wisdom', 'constitution']
        
        if all(character_stats.get(stat, 0) >= 50 for stat in main_stats):
            await self._check_achievement_criteria('stats.stat_thresholds.balanced_stats', {
                'all_stats_above_50': True,
                'stats': character_stats
            }, character_id)
    
    async def _check_achievement_criteria(self, achievement_id: str, criteria: Dict[str, Any], character_id: str) -> None:
        """Check if achievement criteria are met and unlock if necessary"""
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            logger.warning(f"Achievement not found: {achievement_id}")
            return
            
        if achievement.unlocked:
            return  # Already unlocked
        
        # Determine if criteria are met based on achievement type
        criteria_met = False
        
        if 'first_character' in achievement_id:
            criteria_met = criteria.get('characters_created', 0) >= 1
        elif 'character_variety' in achievement_id:
            criteria_met = criteria.get('characters_created', 0) >= 5
        elif 'level_' in achievement_id:
            required_level = criteria.get('required_level', 999)
            criteria_met = criteria.get('level', 0) >= required_level
        elif 'strength_100' in achievement_id or 'intelligence_100' in achievement_id:
            required_value = criteria.get('required_value', 999)
            criteria_met = criteria.get('stat_value', 0) >= required_value
        elif 'balanced_stats' in achievement_id:
            criteria_met = criteria.get('all_stats_above_50', False)
        
        if criteria_met:
            await self._unlock_achievement(achievement, character_id)
    
    async def _unlock_achievement(self, achievement: Achievement, character_id: str) -> None:
        """Unlock an achievement and fire the appropriate event"""
        achievement.unlock()
        self.total_points += achievement.points
        
        # Fire achievement unlocked event - more observer pattern!
        unlock_event = AchievementUnlockedEvent(
            achievement_id=achievement.id,
            achievement_name=achievement.name,
            achievement_description=achievement.description,
            points_awarded=achievement.points,
            character_id=character_id,
            timestamp=time.time()
        )
        
        await self.event_bus.publish(unlock_event)
        logger.info(f"🏆 Achievement Unlocked: {achievement.name} (+{achievement.points} points)")
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements"""
        return [achievement for achievement in self.achievements.values() if achievement.unlocked]
    
    def get_achievement_progress(self) -> Dict[str, Any]:
        """Get achievement progress summary"""
        total_achievements = len(self.achievements)
        unlocked_count = len(self.get_unlocked_achievements())
        
        return {
            'total_achievements': total_achievements,
            'unlocked_count': unlocked_count,
            'completion_percentage': (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0,
            'total_points': self.total_points,
            'achievements_by_category': self._get_achievements_by_category()
        }
    
    def _get_achievements_by_category(self) -> Dict[str, Dict[str, Any]]:
        """Get achievements organized by category"""
        categories = {}
        
        for achievement in self.achievements.values():
            if achievement.category not in categories:
                categories[achievement.category] = {
                    'total': 0,
                    'unlocked': 0,
                    'points': 0
                }
            
            categories[achievement.category]['total'] += 1
            if achievement.unlocked:
                categories[achievement.category]['unlocked'] += 1
                categories[achievement.category]['points'] += achievement.points
        
        return categories
    
    async def reset_achievements(self) -> None:
        """Reset all achievements (for testing)"""
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.unlock_timestamp = None
        
        self.character_stats.clear()
        self.total_points = 0
        logger.info("All achievements reset")


# Export for easier importing
__all__ = ['AchievementSystem', 'Achievement', 'AchievementUnlockedEvent']
