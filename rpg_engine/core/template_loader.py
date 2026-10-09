"""
JSON Template Loading System - Data-driven content management

This system loads and manages all game content from JSON files,
including character templates, achievements, items, and skills.
Everything is data-driven for maximum flexibility and moddability.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, TypeVar
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

T = TypeVar('T')

class TemplateValidationError(Exception):
    """Raised when template validation fails"""
    pass

class TemplateLoader(ABC):
    """Abstract base class for template loaders"""
    
    @abstractmethod
    def load_templates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Load templates from JSON data"""
        pass
    
    @abstractmethod
    def validate_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Validate a single template"""
        pass

@dataclass
class CharacterTemplate:
    """Character template loaded from JSON"""
    id: str
    name: str
    description: str
    character_class: str
    rarity: str
    grade: str
    base_stats: Dict[str, int]
    growth_rates: Dict[str, float]
    starting_equipment: List[str]
    starting_skills: List[str]
    background: str
    appearance: Dict[str, str]
    
    def calculate_stat_at_level(self, stat_name: str, level: int) -> float:
        """Calculate a stat value at a specific level"""
        base_value = self.base_stats.get(stat_name, 0)
        growth_rate = self.growth_rates.get(stat_name, 1.0)
        
        # Level 1 = base stats, each additional level adds growth_rate
        return base_value + (growth_rate * (level - 1))
    
    def calculate_derived_stat(self, stat_name: str, level: int, formulas: Dict[str, float]) -> float:
        """Calculate derived stat using formula from config"""
        # Map derived stats to their base stat sources
        stat_mapping = {
            'health': 'constitution',
            'mana': 'intelligence', 
            'stamina': 'vitality',
            'attack': 'strength',
            'defense': 'constitution',
            'speed': 'dexterity',
            'magic_power': 'intelligence',
            'critical_chance': 'luck',
            'dodge_chance': 'agility',
            'block_chance': 'strength',
            'parry_chance': 'dexterity',
            'accuracy': 'dexterity',
            'evasion': 'agility',
            'magic_resistance': 'wisdom',
            'physical_damage': 'strength',
            'damage_reduction': 'constitution',
            'health_regeneration': 'constitution',
            'mana_regeneration': 'wisdom',
            'stamina_regeneration': 'vitality',
            'luck_factor': 'luck'
        }
        
        base_stat_name = stat_mapping.get(stat_name)
        if not base_stat_name:
            logger.warning(f"Unknown derived stat: {stat_name}")
            return 0.0
        
        formula_multiplier = formulas.get(stat_name, 1.0)
        base_stat_value = self.calculate_stat_at_level(base_stat_name, level)
        
        return base_stat_value * formula_multiplier

@dataclass 
class AchievementTemplate:
    """Achievement template loaded from JSON"""
    id: str
    name: str
    description: str
    points: int
    category: str
    icon: Optional[str] = None
    hidden: bool = False
    requirements: Dict[str, Any] = None
    rewards: Dict[str, Any] = None

class CharacterTemplateLoader(TemplateLoader):
    """Loads character templates from JSON"""
    
    def load_templates(self, data: Dict[str, Any]) -> Dict[str, CharacterTemplate]:
        """Load character templates from JSON data"""
        templates = {}
        character_data = data.get('character_templates', {})
        
        for template_id, template_info in character_data.items():
            try:
                if self.validate_template(template_id, template_info):
                    template = self._create_template(template_id, template_info)
                    templates[template_id] = template
                    logger.debug(f"Loaded character template: {template_id}")
            except Exception as e:
                logger.error(f"Failed to load character template {template_id}: {e}")
        
        logger.info(f"Loaded {len(templates)} character templates")
        return templates
    
    def validate_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Validate character template structure"""
        required_fields = [
            'id', 'name', 'description', 'character_class', 
            'rarity', 'grade', 'base_stats', 'growth_rates'
        ]
        
        for field in required_fields:
            if field not in template_data:
                raise TemplateValidationError(f"Missing required field '{field}' in template {template_id}")
        
        # Validate base_stats structure
        required_stats = [
            'strength', 'dexterity', 'vitality', 'intelligence',
            'wisdom', 'constitution', 'luck', 'agility', 'charisma'
        ]
        
        base_stats = template_data.get('base_stats', {})
        for stat in required_stats:
            if stat not in base_stats:
                raise TemplateValidationError(f"Missing base stat '{stat}' in template {template_id}")
            if not isinstance(base_stats[stat], (int, float)):
                raise TemplateValidationError(f"Base stat '{stat}' must be a number in template {template_id}")
        
        # Validate growth_rates structure
        growth_rates = template_data.get('growth_rates', {})
        for stat in required_stats:
            if stat not in growth_rates:
                raise TemplateValidationError(f"Missing growth rate '{stat}' in template {template_id}")
            if not isinstance(growth_rates[stat], (int, float)):
                raise TemplateValidationError(f"Growth rate '{stat}' must be a number in template {template_id}")
        
        # Validate rarity and grade
        valid_rarities = ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE']
        valid_grades = ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN']
        
        if template_data['rarity'] not in valid_rarities:
            raise TemplateValidationError(f"Invalid rarity '{template_data['rarity']}' in template {template_id}")
        
        if template_data['grade'] not in valid_grades:
            raise TemplateValidationError(f"Invalid grade '{template_data['grade']}' in template {template_id}")
        
        return True
    
    def _create_template(self, template_id: str, data: Dict[str, Any]) -> CharacterTemplate:
        """Create CharacterTemplate object from JSON data"""
        return CharacterTemplate(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            character_class=data['character_class'],
            rarity=data['rarity'],
            grade=data['grade'],
            base_stats=data['base_stats'],
            growth_rates=data['growth_rates'],
            starting_equipment=data.get('starting_equipment', []),
            starting_skills=data.get('starting_skills', []),
            background=data.get('background', 'unknown'),
            appearance=data.get('appearance', {})
        )

class AchievementTemplateLoader(TemplateLoader):
    """Loads achievement templates from JSON"""
    
    def load_templates(self, data: Dict[str, Any]) -> Dict[str, AchievementTemplate]:
        """Load achievement templates from JSON data"""
        templates = {}
        achievement_data = data.get('achievements', {})
        
        for category_name, category_data in achievement_data.items():
            for achievement_id, achievement_info in category_data.items():
                try:
                    full_id = f"{category_name}.{achievement_id}"
                    if self.validate_template(full_id, achievement_info):
                        template = self._create_template(full_id, achievement_info, category_name)
                        templates[full_id] = template
                        logger.debug(f"Loaded achievement template: {full_id}")
                except Exception as e:
                    logger.error(f"Failed to load achievement template {full_id}: {e}")
        
        logger.info(f"Loaded {len(templates)} achievement templates")
        return templates
    
    def validate_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Validate achievement template structure"""
        required_fields = ['name', 'description', 'points']
        
        for field in required_fields:
            if field not in template_data:
                raise TemplateValidationError(f"Missing required field '{field}' in achievement {template_id}")
        
        if not isinstance(template_data['points'], int) or template_data['points'] < 0:
            raise TemplateValidationError(f"Points must be a non-negative integer in achievement {template_id}")
        
        return True
    
    def _create_template(self, template_id: str, data: Dict[str, Any], category: str) -> AchievementTemplate:
        """Create AchievementTemplate object from JSON data"""
        return AchievementTemplate(
            id=template_id,
            name=data['name'],
            description=data['description'],
            points=data['points'],
            category=category,
            icon=data.get('icon'),
            hidden=data.get('hidden', False),
            requirements=data.get('requirements', {}),
            rewards=data.get('rewards', {})
        )

class TemplateManager:
    """Central manager for all template loading and caching"""
    
    def __init__(self, data_directory: Path = None):
        self.data_directory = data_directory or Path("data")
        self.character_templates: Dict[str, CharacterTemplate] = {}
        self.achievement_templates: Dict[str, AchievementTemplate] = {}
        
        # Template loaders
        self.character_loader = CharacterTemplateLoader()
        self.achievement_loader = AchievementTemplateLoader()
        
        logger.info(f"Template manager initialized with data directory: {self.data_directory}")
    
    def load_all_templates(self) -> None:
        """Load all templates from JSON files"""
        try:
            # Load character templates
            character_file = self.data_directory / "character_templates.json"
            if character_file.exists():
                with open(character_file, 'r', encoding='utf-8') as f:
                    character_data = json.load(f)
                self.character_templates = self.character_loader.load_templates(character_data)
            
            # Load achievement templates  
            achievement_file = self.data_directory / "achievements.json"
            if achievement_file.exists():
                with open(achievement_file, 'r', encoding='utf-8') as f:
                    achievement_data = json.load(f)
                self.achievement_templates = self.achievement_loader.load_templates(achievement_data)
            
            logger.info("All templates loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            raise
    
    def get_character_template(self, template_id: str) -> Optional[CharacterTemplate]:
        """Get a character template by ID"""
        return self.character_templates.get(template_id)
    
    def get_achievement_template(self, template_id: str) -> Optional[AchievementTemplate]:
        """Get an achievement template by ID"""
        return self.achievement_templates.get(template_id)
    
    def list_character_templates(self) -> List[CharacterTemplate]:
        """Get all character templates"""
        return list(self.character_templates.values())
    
    def list_achievement_templates(self) -> List[AchievementTemplate]:
        """Get all achievement templates"""
        return list(self.achievement_templates.values())
    
    def validate_all_templates(self) -> Dict[str, List[str]]:
        """Validate all loaded templates and return any errors"""
        errors = {
            'character_templates': [],
            'achievement_templates': []
        }
        
        # Validate character templates
        for template_id, template in self.character_templates.items():
            try:
                self.character_loader.validate_template(template_id, template.__dict__)
            except TemplateValidationError as e:
                errors['character_templates'].append(f"{template_id}: {e}")
        
        # Validate achievement templates
        for template_id, template in self.achievement_templates.items():
            try:
                self.achievement_loader.validate_template(template_id, template.__dict__)
            except TemplateValidationError as e:
                errors['achievement_templates'].append(f"{template_id}: {e}")
        
        return errors
    
    def reload_templates(self) -> None:
        """Reload all templates from files (for development)"""
        logger.info("Reloading all templates...")
        self.character_templates.clear()
        self.achievement_templates.clear()
        self.load_all_templates()
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded templates"""
        return {
            'character_templates': len(self.character_templates),
            'achievement_templates': len(self.achievement_templates),
            'total_templates': len(self.character_templates) + len(self.achievement_templates)
        }

# Global template manager instance
_template_manager: Optional[TemplateManager] = None

def get_template_manager() -> TemplateManager:
    """Get the global template manager instance"""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
        _template_manager.load_all_templates()
    return _template_manager

def reload_templates() -> None:
    """Reload all templates (for development)"""
    global _template_manager
    if _template_manager is not None:
        _template_manager.reload_templates()

# Export main classes and functions
__all__ = [
    'TemplateManager', 'CharacterTemplate', 'AchievementTemplate',
    'TemplateValidationError', 'get_template_manager', 'reload_templates'
]
