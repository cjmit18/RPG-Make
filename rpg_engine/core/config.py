"""
Game Configuration System - Centralized configuration management

Loads and manages game settings from default_settings.json
with proper validation and type safety.
"""
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum, auto

logger = logging.getLogger(__name__)


class Rarity(Enum):
    """Character and item rarity levels"""
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"
    MYTHIC = "MYTHIC"
    DIVINE = "DIVINE"


class Grade(Enum):
    """Character grade levels"""
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    SIX = "SIX"
    SEVEN = "SEVEN"


class DamageType(Enum):
    """Damage types for combat"""
    NONE = "NONE"
    PHYSICAL = "PHYSICAL"
    FIRE = "FIRE"
    ICE = "ICE"
    LIGHTNING = "LIGHTNING"
    POISON = "POISON"
    ARCANE = "ARCANE"
    HOLY = "HOLY"
    DARK = "DARK"
    MAGIC = "MAGIC"


@dataclass
class StatMultipliers:
    """Combat stat multipliers"""
    strength: float = 2.0
    dexterity: float = 1.5
    vitality: float = 2.0
    intelligence: float = 2.0
    wisdom: float = 1.5
    constitution: float = 2.0
    luck: float = 1.0
    agility: float = 1.5
    charisma: float = 1.2


@dataclass
class DerivedStatFormulas:
    """Formulas for calculating derived stats"""
    # Core derived stats
    health: float = 10.0          # constitution * health
    mana: float = 10.0            # intelligence * mana
    stamina: float = 10.0         # vitality * stamina
    
    # Combat stats
    attack: float = 1.5           # strength * attack
    defense: float = 1.0          # constitution * defense
    speed: float = 1.2            # dexterity * speed
    magic_power: float = 1.5      # intelligence * magic_power
    
    # Chance-based stats (as percentages)
    critical_chance: float = 0.005      # luck * critical_chance
    dodge_chance: float = 0.006         # agility * dodge_chance
    block_chance: float = 0.006         # strength * block_chance
    parry_chance: float = 0.006         # dexterity * parry_chance
    accuracy: float = 0.007             # dexterity * accuracy
    evasion: float = 0.006              # agility * evasion
    
    # Resistance stats
    magic_resistance: float = 0.15      # wisdom * magic_resistance
    damage_reduction: float = 0.15      # constitution * damage_reduction
    
    # Regeneration stats
    health_regeneration: float = 0.05   # constitution * health_regen
    mana_regeneration: float = 0.08     # wisdom * mana_regen
    stamina_regeneration: float = 0.1   # vitality * stamina_regen
    
    # Social stats
    leadership: float = 1.0             # charisma * leadership
    social_influence: float = 0.5       # charisma * social_influence
    negotiation_bonus: float = 0.02     # charisma * negotiation


@dataclass
class LevelingConfig:
    """Leveling system configuration"""
    max_level: int = 100
    formula_type: str = "exponential_smooth"
    xp_base: int = 100
    xp_exponent: float = 2.0
    stat_points_per_level: int = 3
    growth_factor: float = 1.15
    level_modifier: float = 0.05


@dataclass
class BaseStats:
    """Base character statistics"""
    strength: int = 10
    dexterity: int = 10
    vitality: int = 10
    intelligence: int = 10
    wisdom: int = 10
    constitution: int = 10
    luck: int = 10
    agility: int = 10
    charisma: int = 10


class GameConfig:
    """Central game configuration manager"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/default_settings.json")
        self._config_data: Dict[str, Any] = {}
        self._stat_multipliers: Optional[StatMultipliers] = None
        self._derived_formulas: Optional[DerivedStatFormulas] = None
        self._leveling_config: Optional[LevelingConfig] = None
        self._base_stats: Optional[BaseStats] = None
        
        # Auto-load configuration on initialization
        self.load_config()
        
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                self._create_default_config()
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
            
            self._initialize_typed_configs()
            logger.info(f"Configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._create_default_config()
            return False
    
    def _initialize_typed_configs(self):
        """Initialize typed configuration objects"""
        # Stat multipliers
        combat_config = self._config_data.get("constants", {}).get("combat", {})
        self._stat_multipliers = StatMultipliers(
            strength=combat_config.get("strength_multiplier", 2.0),
            dexterity=combat_config.get("dexterity_multiplier", 1.5),
            vitality=combat_config.get("vitality_multiplier", 2.0),
            intelligence=combat_config.get("intelligence_multiplier", 2.0),
            wisdom=combat_config.get("wisdom_multiplier", 1.5),
            constitution=combat_config.get("constitution_multiplier", 2.0),
            luck=combat_config.get("luck_multiplier", 1.0),
            agility=combat_config.get("agility_multiplier", 1.5),
            charisma=combat_config.get("charisma_multiplier", 1.2)
        )
        
        # Derived stat formulas
        derived_config = self._config_data.get("constants", {}).get("derived_stats", {})
        self._derived_formulas = DerivedStatFormulas(
            health=derived_config.get("health", 10.0),
            mana=derived_config.get("mana", 10.0),
            stamina=derived_config.get("stamina", 10.0),
            attack=derived_config.get("attack", 1.5),
            defense=derived_config.get("defense", 1.0),
            speed=derived_config.get("speed", 1.2),
            magic_power=derived_config.get("magic_power", 1.5),
            critical_chance=derived_config.get("critical_chance", 0.005),
            dodge_chance=derived_config.get("dodge_chance", 0.006),
            block_chance=derived_config.get("block_chance", 0.006),
            parry_chance=derived_config.get("parry_chance", 0.006),
            accuracy=derived_config.get("accuracy", 0.007),
            evasion=derived_config.get("evasion", 0.006),
            magic_resistance=derived_config.get("magic_resistance", 0.15),
            damage_reduction=derived_config.get("damage_reduction", 0.15),
            health_regeneration=derived_config.get("health_regeneration", 0.05),
            mana_regeneration=derived_config.get("mana_regeneration", 0.08),
            stamina_regeneration=derived_config.get("stamina_regeneration", 0.1),
            leadership=derived_config.get("leadership", 1.0),
            social_influence=derived_config.get("social_influence", 0.5),
            negotiation_bonus=derived_config.get("negotiation_bonus", 0.02)
        )
        
        # Leveling configuration
        leveling_config = self._config_data.get("constants", {}).get("leveling", {})
        self._leveling_config = LevelingConfig(
            max_level=leveling_config.get("max_level", 100),
            formula_type=leveling_config.get("formula_type", "exponential_smooth"),
            xp_base=leveling_config.get("xp_base", 100),
            xp_exponent=leveling_config.get("xp_exponent", 2.0),
            stat_points_per_level=leveling_config.get("stat_points_per_level", 3),
            growth_factor=leveling_config.get("growth_factor", 1.15),
            level_modifier=leveling_config.get("level_modifier", 0.05)
        )
        
        # Base stats
        base_stats_config = self._config_data.get("leveling", {}).get("base_stats", {})
        self._base_stats = BaseStats(
            strength=base_stats_config.get("strength", 10),
            dexterity=base_stats_config.get("dexterity", 10),
            vitality=base_stats_config.get("vitality", 10),
            intelligence=base_stats_config.get("intelligence", 10),
            wisdom=base_stats_config.get("wisdom", 10),
            constitution=base_stats_config.get("constitution", 10),
            luck=base_stats_config.get("luck", 10),
            agility=base_stats_config.get("agility", 10),
            charisma=base_stats_config.get("charisma", 9)  # Default from old system
        )
    
    def _create_default_config(self):
        """Create default configuration"""
        self._stat_multipliers = StatMultipliers()
        self._derived_formulas = DerivedStatFormulas()
        self._leveling_config = LevelingConfig()
        self._base_stats = BaseStats()
    
    @property
    def stat_multipliers(self) -> StatMultipliers:
        """Get stat multipliers configuration"""
        return self._stat_multipliers or StatMultipliers()
    
    @property
    def derived_formulas(self) -> DerivedStatFormulas:
        """Get derived stat formulas"""
        return self._derived_formulas or DerivedStatFormulas()
    
    @property
    def leveling_config(self) -> LevelingConfig:
        """Get leveling configuration"""
        return self._leveling_config or LevelingConfig()
    
    @property
    def base_stats(self) -> BaseStats:
        """Get base stats configuration"""
        return self._base_stats or BaseStats()
    
    def get_rarity_multiplier(self, rarity: Rarity) -> float:
        """Get stat multiplier for character rarity"""
        rarity_config = self._config_data.get("constants", {}).get("rarity", {}).get("stat_multiplier", {})
        return rarity_config.get(rarity.value, 0.0)
    
    def get_grade_multiplier(self, grade: Grade) -> float:
        """Get stat multiplier for character grade"""
        grade_config = self._config_data.get("constants", {}).get("grade", {}).get("stat_multiplier", {})
        return grade_config.get(grade.value, 0.0)
    
    def get_rarity_weights(self) -> Dict[str, float]:
        """Get rarity probability weights"""
        return self._config_data.get("randomness", {}).get("rarity_weights", {
            "COMMON": 0.6,
            "UNCOMMON": 0.2,
            "RARE": 0.1,
            "EPIC": 0.05,
            "LEGENDARY": 0.03,
            "MYTHIC": 0.015,
            "DIVINE": 0.005
        })
    
    def get_grade_weights(self) -> Dict[str, float]:
        """Get grade probability weights"""
        return self._config_data.get("randomness", {}).get("grade_weights", {
            "ONE": 0.4,
            "TWO": 0.25,
            "THREE": 0.15,
            "FOUR": 0.1,
            "FIVE": 0.06,
            "SIX": 0.03,
            "SEVEN": 0.01
        })
    
    def get_stamina_costs(self) -> Dict[str, int]:
        """Get stamina costs for combat actions"""
        return self._config_data.get("constants", {}).get("combat", {}).get("stamina_costs", {
            "attack": 5,
            "dodge": 8,
            "parry": 6,
            "evade": 7,
            "block": 4
        })
    
    def calculate_experience_for_level(self, level: int) -> int:
        """Calculate experience required for a given level"""
        config = self.leveling_config
        
        if config.formula_type == "exponential_smooth":
            # Use exponential formula with smoothing
            return int(config.xp_base * (level ** config.xp_exponent) * config.growth_factor)
        elif config.formula_type == "linear":
            # Simple linear progression
            return config.xp_base * level
        else:
            # Default exponential
            return int(config.xp_base * (level ** config.xp_exponent))
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self._config_data.get("toggles", {}).get(feature, False)
    
    def get_inventory_max_size(self) -> int:
        """Get maximum inventory size"""
        return self._config_data.get("constants", {}).get("inventory", {}).get("max_size", 20)
    
    def get_ui_colors(self) -> Dict[str, str]:
        """Get UI color configuration"""
        return self._config_data.get("ui", {}).get("colors", {
            "background": "black",
            "text": "white",
            "highlight": "yellow",
            "error": "red",
            "success": "green"
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (for compatibility with dict-like access)"""
        return self._config_data.get(key, default)
    
    def get_raw_config(self) -> Dict[str, Any]:
        """Get the raw configuration data"""
        return self._config_data.copy()


# Global configuration instance
_config_instance: Optional[GameConfig] = None


def get_config() -> GameConfig:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = GameConfig()
        _config_instance.load_config()
    return _config_instance


def reload_config() -> bool:
    """Reload configuration from file"""
    global _config_instance
    if _config_instance is not None:
        return _config_instance.load_config()
    return False
