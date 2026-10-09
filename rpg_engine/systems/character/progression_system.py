"""
Character Progression System - Configuration-driven leveling and skill advancement

Handles character experience, leveling, skill learning,
and progression mechanics using the game configuration system.
"""
import asyncio
import math
from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from enum import Enum
import logging

from ...core.service_container import ServiceContainer, AsyncInitializable
from ...core.event_bus import EventBus, GameEvent
from ...core.config import get_config
from .character_system import Character, CharacterLevelUpEvent

logger = logging.getLogger(__name__)


# Progression events
@dataclass(frozen=True)
class ExperienceGainedEvent(GameEvent):
    character_id: str = ""
    experience_gained: int = 0
    source: str = ""
    total_experience: int = 0


@dataclass(frozen=True)
class SkillLearnedEvent(GameEvent):
    character_id: str = ""
    skill_id: str = ""
    skill_name: str = ""
    skill_level: int = 1


@dataclass(frozen=True)
class SkillPointsAllocatedEvent(GameEvent):
    character_id: str = ""
    allocations: Dict[str, int] = field(default_factory=dict)
    total_points_spent: int = 0


# Skill data structure
@dataclass
class Skill:
    """Skill definition"""
    id: str
    name: str
    description: str
    category: str
    max_level: int = 10
    prerequisites: List[str] = None
    cost_per_level: int = 1
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


# Character skill entry
@dataclass
class CharacterSkill:
    """Character's skill with level"""
    skill: Skill
    level: int = 1
    experience: int = 0


# Character Progression Service
class CharacterProgressionService(AsyncInitializable):
    """
    Character progression and skill management system
    
    Handles experience gain, leveling, skill learning,
    and skill point allocation with async patterns.
    """
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.event_bus: Optional[EventBus] = None
        self.config = get_config()
        
        # Character skills (character_id -> skill_id -> CharacterSkill)
        self.character_skills: Dict[str, Dict[str, CharacterSkill]] = {}
        
        # Character skill points (character_id -> available_points)
        self.character_skill_points: Dict[str, int] = {}
        
        # Skill database
        self.skill_database: Dict[str, Skill] = {}
        
        # Use configuration for experience curve settings
        leveling_config = self.config.leveling_config
        self.base_experience_per_level = leveling_config.xp_base
        self.experience_multiplier = leveling_config.growth_factor
    
    async def initialize_async(self) -> None:
        """Initialize the progression system"""
        self.event_bus = await self.service_container.get_service(EventBus)
        
        # Load default skills
        await self._load_default_skills()
    
    async def _load_default_skills(self) -> None:
        """Load default skills into the database"""
        default_skills = [
            Skill(
                id="sword_mastery",
                name="Sword Mastery",
                description="Improves sword combat effectiveness",
                category="combat",
                max_level=10
            ),
            Skill(
                id="magic_missile",
                name="Magic Missile",
                description="Basic offensive spell",
                category="magic",
                max_level=5
            ),
            Skill(
                id="stealth",
                name="Stealth",
                description="Ability to move unseen",
                category="utility",
                max_level=8
            ),
            Skill(
                id="healing",
                name="Healing",
                description="Restore health to self or others",
                category="magic",
                max_level=7
            ),
            Skill(
                id="lockpicking",
                name="Lockpicking",
                description="Open locked containers and doors",
                category="utility",
                max_level=6,
                prerequisites=["stealth"]
            )
        ]
        
        for skill in default_skills:
            self.skill_database[skill.id] = skill
    
    async def gain_experience_async(self, 
                                  character: Character, 
                                  amount: int,
                                  source: str = "combat") -> Optional[CharacterLevelUpEvent]:
        """
        Add experience to character and handle level ups
        
        Args:
            character: Character to gain experience
            amount: Amount of experience to gain
            source: Source of experience (combat, quest, etc.)
            
        Returns:
            LevelUpEvent if character leveled up, None otherwise
        """
        old_experience = character.experience
        old_level = character.level
        
        character.experience += amount
        
        # Check for level up
        required_exp = await self._calculate_experience_for_level_async(character.level + 1)
        level_up_event = None
        
        if character.experience >= required_exp:
            new_level = await self._calculate_level_from_experience_async(character.experience)
            levels_gained = new_level - old_level
            
            if levels_gained > 0:
                character.level = new_level
                
                # Award skill points
                skill_points_gained = levels_gained * 2  # 2 skill points per level
                current_points = self.character_skill_points.get(character.id, 0)
                self.character_skill_points[character.id] = current_points + skill_points_gained
                
                # Create level up event
                level_up_event = CharacterLevelUpEvent(
                    character_id=character.id,
                    old_level=old_level,
                    new_level=new_level,
                    stat_increases={},  # Could add automatic stat increases here
                    timestamp=asyncio.get_event_loop().time()
                )
                
                # Publish level up event
                if self.event_bus:
                    await self.event_bus.publish(level_up_event)
        
        # Publish experience gain event
        if self.event_bus:
            await self.event_bus.publish(ExperienceGainedEvent(
                character_id=character.id,
                experience_gained=amount,
                source=source,
                total_experience=character.experience,
                timestamp=asyncio.get_event_loop().time()
            ))
        
        return level_up_event
    
    async def _calculate_experience_for_level_async(self, level: int) -> int:
        """Calculate total experience required for a given level using configuration"""
        return self.config.calculate_experience_for_level(level)
    
    async def _calculate_level_from_experience_async(self, experience: int) -> int:
        """Calculate character level from total experience using configuration"""
        level = 1
        max_level = self.config.leveling_config.max_level
        
        while level < max_level:
            next_level_exp = await self._calculate_experience_for_level_async(level + 1)
            if experience < next_level_exp:
                break
            level += 1
        
        return level
    
    async def learn_skill_async(self, 
                              character_id: str, 
                              skill_id: str) -> bool:
        """
        Learn a new skill
        
        Args:
            character_id: Character learning the skill
            skill_id: ID of skill to learn
            
        Returns:
            True if successful, False if requirements not met
        """
        if skill_id not in self.skill_database:
            return False
        
        skill = self.skill_database[skill_id]
        
        # Check if character already has this skill
        if character_id in self.character_skills:
            if skill_id in self.character_skills[character_id]:
                return False  # Already knows this skill
        
        # Check prerequisites
        if skill.prerequisites:
            character_skills = self.character_skills.get(character_id, {})
            for prereq_id in skill.prerequisites:
                if prereq_id not in character_skills:
                    return False  # Missing prerequisite
        
        # Check skill points
        available_points = self.character_skill_points.get(character_id, 0)
        if available_points < skill.cost_per_level:
            return False  # Not enough skill points
        
        # Learn the skill
        if character_id not in self.character_skills:
            self.character_skills[character_id] = {}
        
        character_skill = CharacterSkill(skill=skill, level=1, experience=0)
        self.character_skills[character_id][skill_id] = character_skill
        
        # Deduct skill points
        self.character_skill_points[character_id] -= skill.cost_per_level
        
        # Publish event
        if self.event_bus:
            await self.event_bus.publish(SkillLearnedEvent(
                character_id=character_id,
                skill_id=skill_id,
                skill_name=skill.name,
                skill_level=1,
                timestamp=asyncio.get_event_loop().time()
            ))
        
        return True
    
    async def get_character_skills_async(self, character_id: str) -> Dict[str, CharacterSkill]:
        """Get all skills for a character"""
        return self.character_skills.get(character_id, {}).copy()
    
    async def get_available_skill_points_async(self, character_id: str) -> int:
        """Get available skill points for a character"""
        return self.character_skill_points.get(character_id, 0)
    
    async def get_learnable_skills_async(self, character_id: str) -> List[Skill]:
        """Get list of skills a character can learn"""
        character_skills = self.character_skills.get(character_id, {})
        available_points = self.character_skill_points.get(character_id, 0)
        learnable = []
        
        for skill_id, skill in self.skill_database.items():
            # Skip if already known
            if skill_id in character_skills:
                continue
            
            # Check skill points
            if available_points < skill.cost_per_level:
                continue
            
            # Check prerequisites
            can_learn = True
            for prereq_id in skill.prerequisites:
                if prereq_id not in character_skills:
                    can_learn = False
                    break
            
            if can_learn:
                learnable.append(skill)
        
        return learnable
    
    async def allocate_skill_points_async(self, 
                                        character_id: str, 
                                        allocations: Dict[str, int]) -> bool:
        """
        Allocate skill points to improve existing skills
        
        Args:
            character_id: Character to allocate points for
            allocations: Dict of skill_id -> points to allocate
            
        Returns:
            True if successful, False if insufficient points or invalid allocation
        """
        character_skills = self.character_skills.get(character_id, {})
        available_points = self.character_skill_points.get(character_id, 0)
        
        # Calculate total points needed
        total_points_needed = sum(allocations.values())
        
        if total_points_needed > available_points:
            return False
        
        # Validate all allocations first
        for skill_id, points in allocations.items():
            if skill_id not in character_skills:
                return False  # Don't know this skill
            
            character_skill = character_skills[skill_id]
            if character_skill.level + points > character_skill.skill.max_level:
                return False  # Would exceed max level
        
        # Apply allocations
        for skill_id, points in allocations.items():
            character_skills[skill_id].level += points
        
        # Deduct skill points
        self.character_skill_points[character_id] -= total_points_needed
        
        # Publish event
        if self.event_bus:
            await self.event_bus.publish(SkillPointsAllocatedEvent(
                character_id=character_id,
                allocations=allocations.copy(),
                total_points_spent=total_points_needed,
                timestamp=asyncio.get_event_loop().time()
            ))
        
        return True
    
    async def shutdown_async(self) -> None:
        """Cleanup progression system"""
        self.character_skills.clear()
        self.character_skill_points.clear()
