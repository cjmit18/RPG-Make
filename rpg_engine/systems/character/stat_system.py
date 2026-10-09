"""
Character Stat System - Configuration-driven stat calculation and progression

Handles character statistics, derived stats calculation,
and stat-based progression mechanics using the game configuration system.
"""
import asyncio
from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from enum import Enum
import logging

from ...core.service_container import ServiceContainer, AsyncInitializable
from ...core.event_bus import EventBus, GameEvent
from ...core.config import get_config, Rarity, Grade
from .character_system import Character

logger = logging.getLogger(__name__)


# Stat-related events
@dataclass(frozen=True)
class StatChangedEvent(GameEvent):
    character_id: str = ""
    stat_name: str = ""
    old_value: int = 0
    new_value: int = 0
    change_reason: str = ""


@dataclass(frozen=True)
class DerivedStatsCalculatedEvent(GameEvent):
    character_id: str = ""
    derived_stats: Dict[str, int] = field(default_factory=dict)


@dataclass
class CharacterStats:
    """Character statistics data structure with configuration-driven calculations"""
    # Base Stats
    strength: int = 10
    dexterity: int = 10
    vitality: int = 10
    intelligence: int = 10
    wisdom: int = 10
    constitution: int = 10
    luck: int = 10
    agility: int = 10
    charisma: int = 10
    
    # Character properties
    level: int = 1
    rarity: Rarity = Rarity.COMMON
    grade: Grade = Grade.ONE
    
    # Derived Stats (calculated)
    health: int = field(default=0, init=False)
    max_health: int = field(default=0, init=False)
    mana: int = field(default=0, init=False)
    max_mana: int = field(default=0, init=False)
    stamina: int = field(default=0, init=False)
    max_stamina: int = field(default=0, init=False)
    
    # Combat Stats
    attack_power: int = field(default=0, init=False)
    defense: int = field(default=0, init=False)
    speed: int = field(default=0, init=False)
    magic_power: int = field(default=0, init=False)
    
    # Chance-based stats (percentages 0-100)
    critical_chance: float = field(default=0.0, init=False)
    dodge_chance: float = field(default=0.0, init=False)
    block_chance: float = field(default=0.0, init=False)
    parry_chance: float = field(default=0.0, init=False)
    accuracy: float = field(default=0.0, init=False)
    evasion: float = field(default=0.0, init=False)
    
    # Resistances (percentages 0-100)
    magic_resistance: float = field(default=0.0, init=False)
    damage_reduction: float = field(default=0.0, init=False)
    
    # Regeneration rates (per second)
    health_regeneration: float = field(default=0.0, init=False)
    mana_regeneration: float = field(default=0.0, init=False)
    stamina_regeneration: float = field(default=0.0, init=False)
    
    # Social stats
    leadership: int = field(default=0, init=False)
    social_influence: float = field(default=0.0, init=False)
    negotiation_bonus: float = field(default=0.0, init=False)
    
    # Critical damage multiplier
    critical_damage: float = field(default=1.5, init=False)
    
    def __post_init__(self):
        """Calculate derived stats after initialization"""
        self.calculate_derived_stats()
    
    def calculate_derived_stats(self):
        """Calculate all derived stats based on base stats using configuration"""
        config = get_config()
        multipliers = config.stat_multipliers
        formulas = config.derived_formulas
        
        # Apply rarity and grade multipliers to base stats
        rarity_multiplier = 1.0 + config.get_rarity_multiplier(self.rarity)
        grade_multiplier = 1.0 + config.get_grade_multiplier(self.grade)
        total_multiplier = rarity_multiplier * grade_multiplier
        
        # Effective stats with multipliers
        effective_str = int(self.strength * total_multiplier)
        effective_dex = int(self.dexterity * total_multiplier)
        effective_vit = int(self.vitality * total_multiplier)
        effective_int = int(self.intelligence * total_multiplier)
        effective_wis = int(self.wisdom * total_multiplier)
        effective_con = int(self.constitution * total_multiplier)
        effective_luck = int(self.luck * total_multiplier)
        effective_agi = int(self.agility * total_multiplier)
        effective_cha = int(self.charisma * total_multiplier)
        
        # Core derived stats
        self.max_health = int(effective_vit * formulas.health)
        self.max_mana = int(effective_int * formulas.mana)
        self.max_stamina = int(effective_con * formulas.stamina)
        
        # Set current values if not already set
        if self.health == 0:
            self.health = self.max_health
        if self.mana == 0:
            self.mana = self.max_mana
        if self.stamina == 0:
            self.stamina = self.max_stamina
        
        # Combat stats
        self.attack_power = int(effective_str * formulas.attack)
        self.defense = int(effective_con * formulas.defense)
        self.speed = int(effective_agi * formulas.speed)
        self.magic_power = int(effective_int * formulas.magic_power)
        
        # Chance-based stats (convert to percentages)
        self.critical_chance = min(95.0, effective_luck * formulas.critical_chance * 100)
        self.dodge_chance = min(95.0, effective_agi * formulas.dodge_chance * 100)
        self.block_chance = min(95.0, effective_str * formulas.block_chance * 100)
        self.parry_chance = min(95.0, effective_dex * formulas.parry_chance * 100)
        self.accuracy = min(99.0, effective_dex * formulas.accuracy * 100)
        self.evasion = min(95.0, effective_agi * formulas.evasion * 100)
        
        # Resistance stats (convert to percentages)
        self.magic_resistance = min(90.0, effective_wis * formulas.magic_resistance * 100)
        self.damage_reduction = min(90.0, effective_con * formulas.damage_reduction * 100)
        
        # Regeneration rates
        self.health_regeneration = effective_vit * formulas.health_regeneration
        self.mana_regeneration = effective_wis * formulas.mana_regeneration
        self.stamina_regeneration = effective_con * formulas.stamina_regeneration

        # Social stats
        self.leadership = int(effective_cha * formulas.leadership)
        self.social_influence = effective_cha * formulas.social_influence
        self.negotiation_bonus = min(50.0, effective_cha * formulas.negotiation_bonus * 100)
        
        logger.debug(f"Calculated stats for level {self.level} {self.rarity.value} {self.grade.value} character")
    
    def get_effective_stat(self, stat_name: str) -> int:
        """Get effective stat value with all modifiers applied"""
        base_value = getattr(self, stat_name, 0)
        if not isinstance(base_value, (int, float)):
            return 0
            
        config = get_config()
        rarity_multiplier = 1.0 + config.get_rarity_multiplier(self.rarity)
        grade_multiplier = 1.0 + config.get_grade_multiplier(self.grade)
        
        return int(base_value * rarity_multiplier * grade_multiplier)


# Character Stat Service
class CharacterStatService(AsyncInitializable):
    """
    Service for character stat management and calculation using configuration system
    
    Handles base stats, derived stats, and stat progression
    with async calculation and event publishing.
    """
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.event_bus: Optional[EventBus] = None
        self.config = get_config()
    
    async def initialize_async(self) -> None:
        """Initialize the stat service"""
        self.event_bus = await self.service_container.get_service(EventBus)
    
    async def create_character_stats_async(self, 
                                         base_stats: Optional[Dict[str, int]] = None,
                                         level: int = 1,
                                         rarity: Rarity = Rarity.COMMON,
                                         grade: Grade = Grade.ONE) -> CharacterStats:
        """
        Create a new CharacterStats instance with configuration-based defaults
        
        Args:
            base_stats: Optional base stat overrides
            level: Character level
            rarity: Character rarity
            grade: Character grade
            
        Returns:
            New CharacterStats instance
        """
        # Start with configuration defaults
        config_base_stats = self.config.base_stats
        
        stats = CharacterStats(
            strength=base_stats.get('strength', config_base_stats.strength) if base_stats else config_base_stats.strength,
            dexterity=base_stats.get('dexterity', config_base_stats.dexterity) if base_stats else config_base_stats.dexterity,
            vitality=base_stats.get('vitality', config_base_stats.vitality) if base_stats else config_base_stats.vitality,
            intelligence=base_stats.get('intelligence', config_base_stats.intelligence) if base_stats else config_base_stats.intelligence,
            wisdom=base_stats.get('wisdom', config_base_stats.wisdom) if base_stats else config_base_stats.wisdom,
            constitution=base_stats.get('constitution', config_base_stats.constitution) if base_stats else config_base_stats.constitution,
            luck=base_stats.get('luck', config_base_stats.luck) if base_stats else config_base_stats.luck,
            agility=base_stats.get('agility', config_base_stats.agility) if base_stats else config_base_stats.agility,
            charisma=base_stats.get('charisma', config_base_stats.charisma) if base_stats else config_base_stats.charisma,
            level=level,
            rarity=rarity,
            grade=grade
        )
        
        return stats
    
    async def calculate_derived_stats_async(self, character: Character) -> Dict[str, int]:
        """
        Calculate all derived stats for a character
        
        Args:
            character: Character to calculate stats for
            
        Returns:
            Dictionary of derived stat values
        """
        # Create CharacterStats instance for calculation
        stats = await self.create_character_stats_async(
            base_stats=character.base_stats,
            level=character.level,
            rarity=getattr(character, 'rarity', Rarity.COMMON),
            grade=getattr(character, 'grade', Grade.ONE)
        )
        
        # Extract derived stats as dictionary
        derived_stats = {
            'health': stats.health,
            'max_health': stats.max_health,
            'mana': stats.mana,
            'max_mana': stats.max_mana,
            'stamina': stats.stamina,
            'max_stamina': stats.max_stamina,
            'attack_power': stats.attack_power,
            'defense': stats.defense,
            'speed': stats.speed,
            'magic_power': stats.magic_power,
            'critical_chance': stats.critical_chance,
            'dodge_chance': stats.dodge_chance,
            'block_chance': stats.block_chance,
            'parry_chance': stats.parry_chance,
            'accuracy': stats.accuracy,
            'evasion': stats.evasion,
            'magic_resistance': stats.magic_resistance,
            'damage_reduction': stats.damage_reduction,
            'health_regeneration': stats.health_regeneration,
            'mana_regeneration': stats.mana_regeneration,
            'stamina_regeneration': stats.stamina_regeneration,
            'leadership': stats.leadership,
            'social_influence': stats.social_influence,
            'negotiation_bonus': stats.negotiation_bonus
        }
        
        # Publish calculation event
        if self.event_bus:
            await self.event_bus.publish(DerivedStatsCalculatedEvent(
                character_id=character.id,
                derived_stats=derived_stats.copy(),
                timestamp=asyncio.get_event_loop().time()
            ))
        
        return derived_stats
    
    async def apply_stat_changes_async(self, 
                                     character: Character, 
                                     stat_changes: Dict[str, int],
                                     reason: str = "manual_change") -> None:
        """
        Apply stat changes to a character
        
        Args:
            character: Character to modify
            stat_changes: Dictionary of stat name -> change amount
            reason: Reason for the stat change (for events)
        """
        for stat_name, change_amount in stat_changes.items():
            if stat_name in character.base_stats:
                old_value = character.base_stats[stat_name]
                new_value = old_value + change_amount
                character.base_stats[stat_name] = max(0, new_value)  # Minimum 0
                
                # Publish change event
                if self.event_bus:
                    await self.event_bus.publish(StatChangedEvent(
                        character_id=character.id,
                        stat_name=stat_name,
                        old_value=old_value,
                        new_value=character.base_stats[stat_name],
                        change_reason=reason,
                        timestamp=asyncio.get_event_loop().time()
                    ))
        
        # Recalculate derived stats
        character.derived_stats = await self.calculate_derived_stats_async(character)
    
    async def validate_stat_allocation_async(self, 
                                           stat_allocation: Dict[str, int],
                                           total_points: Optional[int] = None) -> tuple[bool, str]:
        """
        Validate a stat point allocation using configuration-based rules
        
        Args:
            stat_allocation: Proposed stat allocation
            total_points: Total points allowed (defaults to config-based calculation)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Use configuration-based total points if not specified
        if total_points is None:
            leveling_config = self.config.leveling_config
            total_points = leveling_config.stat_points_per_level * 1  # For level 1 character
        
        # Check total points
        total_used = sum(stat_allocation.values())
        if total_used > total_points:
            return False, f"Allocated {total_used} points, but only {total_points} available"
        
        # Check minimum values (use config base stats as minimums)
        base_stats_config = self.config.base_stats
        min_stats = {
            'strength': 1,
            'dexterity': 1, 
            'vitality': 1,
            'intelligence': 1,
            'wisdom': 1,
            'constitution': 1,
            'luck': 1,
            'agility': 1,
            'charisma': 1
        }
        
        for stat_name, value in stat_allocation.items():
            min_value = min_stats.get(stat_name, 1)
            if value < min_value:
                return False, f"Stat '{stat_name}' must be at least {min_value}"
        
        # Check for required stats
        required_stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom']
        for required_stat in required_stats:
            if required_stat not in stat_allocation:
                return False, f"Missing required stat: {required_stat}"
        
        return True, "Valid allocation"
    
    async def get_stat_recommendations_async(self, 
                                           character_class: str) -> Dict[str, int]:
        """
        Get recommended stat allocation for a character class based on configuration
        
        Args:
            character_class: Class to get recommendations for
            
        Returns:
            Dictionary of recommended stat allocations
        """
        base_stats = self.config.base_stats
        
        # Enhanced recommendations using configuration values
        class_recommendations = {
            'warrior': {
                'strength': base_stats.strength + 4,
                'dexterity': base_stats.dexterity + 1,
                'vitality': base_stats.vitality + 3,
                'constitution': base_stats.constitution + 4,
                'intelligence': base_stats.intelligence,
                'wisdom': base_stats.wisdom,
                'luck': base_stats.luck + 1,
                'agility': base_stats.agility + 1,
                'charisma': base_stats.charisma
            },
            'mage': {
                'strength': base_stats.strength,
                'dexterity': base_stats.dexterity + 1,
                'vitality': base_stats.vitality + 1,
                'constitution': base_stats.constitution + 1,
                'intelligence': base_stats.intelligence + 5,
                'wisdom': base_stats.wisdom + 4,
                'luck': base_stats.luck + 1,
                'agility': base_stats.agility + 1,
                'charisma': base_stats.charisma + 1
            },
            'rogue': {
                'strength': base_stats.strength + 2,
                'dexterity': base_stats.dexterity + 5,
                'vitality': base_stats.vitality + 2,
                'constitution': base_stats.constitution + 2,
                'intelligence': base_stats.intelligence + 1,
                'wisdom': base_stats.wisdom + 1,
                'luck': base_stats.luck + 3,
                'agility': base_stats.agility + 5,
                'charisma': base_stats.charisma + 1
            },
            'cleric': {
                'strength': base_stats.strength + 1,
                'dexterity': base_stats.dexterity,
                'vitality': base_stats.vitality + 2,
                'constitution': base_stats.constitution + 3,
                'intelligence': base_stats.intelligence + 2,
                'wisdom': base_stats.wisdom + 5,
                'luck': base_stats.luck + 2,
                'agility': base_stats.agility,
                'charisma': base_stats.charisma + 3
            }
        }
        
        # Default balanced allocation
        default_allocation = {
            'strength': base_stats.strength + 1,
            'dexterity': base_stats.dexterity + 1,
            'vitality': base_stats.vitality + 1,
            'constitution': base_stats.constitution + 1,
            'intelligence': base_stats.intelligence + 1,
            'wisdom': base_stats.wisdom + 1,
            'luck': base_stats.luck + 1,
            'agility': base_stats.agility + 1,
            'charisma': base_stats.charisma + 1
        }
        
        return class_recommendations.get(character_class.lower(), default_allocation)
    
    async def calculate_experience_for_level_async(self, level: int) -> int:
        """Calculate experience required for a given level using configuration formulas"""
        return self.config.calculate_experience_for_level(level)
    
    async def get_stamina_cost_async(self, action: str) -> int:
        """Get stamina cost for an action from configuration"""
        stamina_costs = self.config.get_stamina_costs()
        return stamina_costs.get(action, 5)  # Default 5 stamina
    
    async def shutdown_async(self) -> None:
        """Cleanup stat service"""
        pass
