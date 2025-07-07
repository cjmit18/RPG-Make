"""
Difficulty Scaling System
========================

Dynamically adjusts game difficulty based on player performance.
Provides adaptive challenge scaling for AI opponents.
Integrates with the main config system for consistent difficulty settings.
"""

from typing import Any, Dict, List
import time
import logging
from enum import Enum
from dataclasses import dataclass, field

# Import config system for integration
from game_sys.config.config_manager import ConfigManager


class DifficultyLevel(Enum):
    """Difficulty levels for scaling."""
    VERY_EASY = "very_easy"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    VERY_HARD = "very_hard"
    EXTREME = "extreme"


@dataclass
class PerformanceMetrics:
    """Tracks player performance metrics."""
    battles_won: int = 0
    battles_lost: int = 0
    total_damage_dealt: float = 0.0
    total_damage_received: float = 0.0
    average_battle_duration: float = 0.0
    spells_cast: int = 0
    items_used: int = 0
    deaths: int = 0
    level_ups: int = 0
    last_battle_time: float = field(default_factory=time.time)
    win_streak: int = 0
    loss_streak: int = 0
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        total_battles = self.battles_won + self.battles_lost
        if total_battles == 0:
            return 0.0
        return self.battles_won / total_battles
        
    @property
    def damage_ratio(self) -> float:
        """Calculate damage dealt vs received ratio."""
        if self.total_damage_received == 0:
            return float('inf') if self.total_damage_dealt > 0 else 1.0
        return self.total_damage_dealt / self.total_damage_received


@dataclass
class DifficultyModifiers:
    """Modifiers applied based on difficulty level."""
    enemy_health_multiplier: float = 1.0
    enemy_damage_multiplier: float = 1.0
    enemy_speed_multiplier: float = 1.0
    enemy_mana_multiplier: float = 1.0
    enemy_defense_multiplier: float = 1.0
    enemy_spell_frequency: float = 1.0
    loot_quality_multiplier: float = 1.0
    experience_multiplier: float = 1.0
    enemy_ai_aggression: float = 1.0
    status_effect_resistance: float = 0.0


class DifficultyScaler:
    """Manages dynamic difficulty scaling with config system integration."""
    
    def __init__(self, config_manager=None):
        self.logger = logging.getLogger("difficulty_scaler")
        self.metrics = PerformanceMetrics()
        self.current_difficulty = DifficultyLevel.NORMAL
        self.target_win_rate = 0.65  # Target 65% win rate
        self.adjustment_threshold = 5  # Battles before considering adjustment
        self.last_adjustment_time = time.time()
        self.adjustment_cooldown = 300  # 5 minutes between adjustments
        
        # Initialize config manager
        try:
            self.config_manager = config_manager or ConfigManager()
        except Exception as e:
            self.logger.warning(f"Could not initialize config manager: {e}")
            self.config_manager = None
        
        # Load difficulty settings from config, with fallbacks
        self._load_difficulty_config()
        
    def _load_difficulty_config(self):
        """Load difficulty configuration from config system."""
        try:
            if self.config_manager is None:
                self.logger.warning("No config manager available")
                self._create_default_modifiers()
                return
                
            # Get difficulty settings from config
            config_difficulty = self.config_manager.get(
                'defaults.difficulty', {}
            )
            
            # Convert config format to our modifiers format
            self.difficulty_modifiers = {}
            
            # Define extended difficulty levels with config integration
            for level in DifficultyLevel:
                level_name = level.value
                
                # Get base config values or use defaults
                if (isinstance(config_difficulty, dict) and 
                        level_name in config_difficulty):
                    config_data = config_difficulty[level_name]
                    enemy_mult = config_data.get('enemy_multiplier', 1.0)
                    loot_mult = config_data.get('loot_multiplier', 1.0)
                else:
                    # Use our predefined values as fallback
                    enemy_mult, loot_mult = self._get_default_multipliers(
                        level
                    )
                
                # Create comprehensive modifiers based on level
                modifiers = self._create_modifiers_for_level(
                    level, enemy_mult, loot_mult
                )
                self.difficulty_modifiers[level] = modifiers
                
            self.logger.info(
                f"Loaded difficulty config with "
                f"{len(self.difficulty_modifiers)} levels"
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to load difficulty config: {e}")
            self._create_default_modifiers()
            
    def _get_default_multipliers(self, level: DifficultyLevel):
        """Get default multipliers for a difficulty level."""
        defaults = {
            DifficultyLevel.VERY_EASY: (0.6, 1.3),
            DifficultyLevel.EASY: (0.8, 1.15), 
            DifficultyLevel.NORMAL: (1.0, 1.0),
            DifficultyLevel.HARD: (1.3, 0.9),
            DifficultyLevel.VERY_HARD: (1.6, 0.8),
            DifficultyLevel.EXTREME: (2.0, 0.7)
        }
        return defaults.get(level, (1.0, 1.0))
        
    def _create_modifiers_for_level(self, level: DifficultyLevel, 
                                   enemy_mult: float, loot_mult: float):
        """Create comprehensive modifiers for a difficulty level."""
        # Base scaling factors based on enemy multiplier
        if enemy_mult <= 0.7:  # Very Easy
            return DifficultyModifiers(
                enemy_health_multiplier=enemy_mult,
                enemy_damage_multiplier=enemy_mult * 1.1,
                enemy_speed_multiplier=0.8,
                enemy_mana_multiplier=0.8,
                enemy_defense_multiplier=enemy_mult * 0.9,
                enemy_spell_frequency=0.5,
                loot_quality_multiplier=loot_mult,
                experience_multiplier=1.2,
                enemy_ai_aggression=0.6,
                status_effect_resistance=0.0
            )
        elif enemy_mult <= 0.9:  # Easy  
            return DifficultyModifiers(
                enemy_health_multiplier=enemy_mult,
                enemy_damage_multiplier=enemy_mult * 1.05,
                enemy_speed_multiplier=0.9,
                enemy_mana_multiplier=0.9,
                enemy_defense_multiplier=enemy_mult * 0.95,
                enemy_spell_frequency=0.7,
                loot_quality_multiplier=loot_mult,
                experience_multiplier=1.1,
                enemy_ai_aggression=0.8,
                status_effect_resistance=0.1
            )
        elif enemy_mult <= 1.1:  # Normal
            return DifficultyModifiers(
                enemy_health_multiplier=enemy_mult,
                enemy_damage_multiplier=enemy_mult,
                enemy_speed_multiplier=1.0,
                enemy_mana_multiplier=1.0,
                enemy_defense_multiplier=enemy_mult,
                enemy_spell_frequency=1.0,
                loot_quality_multiplier=loot_mult,
                experience_multiplier=1.0,
                enemy_ai_aggression=1.0,
                status_effect_resistance=0.2
            )
        elif enemy_mult <= 1.4:  # Hard
            return DifficultyModifiers(
                enemy_health_multiplier=enemy_mult,
                enemy_damage_multiplier=enemy_mult * 0.95,
                enemy_speed_multiplier=1.1,
                enemy_mana_multiplier=1.2,
                enemy_defense_multiplier=enemy_mult * 0.9,
                enemy_spell_frequency=1.3,
                loot_quality_multiplier=loot_mult,
                experience_multiplier=0.95,
                enemy_ai_aggression=1.3,
                status_effect_resistance=0.3
            )
        elif enemy_mult <= 1.7:  # Very Hard
            return DifficultyModifiers(
                enemy_health_multiplier=enemy_mult,
                enemy_damage_multiplier=enemy_mult * 0.9,
                enemy_speed_multiplier=1.2,
                enemy_mana_multiplier=1.4,
                enemy_defense_multiplier=enemy_mult * 0.85,
                enemy_spell_frequency=1.6,
                loot_quality_multiplier=loot_mult,
                experience_multiplier=0.9,
                enemy_ai_aggression=1.6,
                status_effect_resistance=0.4
            )
        else:  # Extreme
            return DifficultyModifiers(
                enemy_health_multiplier=enemy_mult,
                enemy_damage_multiplier=enemy_mult * 0.85,
                enemy_speed_multiplier=1.4,
                enemy_mana_multiplier=1.8,
                enemy_defense_multiplier=enemy_mult * 0.8,
                enemy_spell_frequency=2.0,
                loot_quality_multiplier=loot_mult,
                experience_multiplier=0.85,
                enemy_ai_aggression=2.0,
                status_effect_resistance=0.5
            )
            
    def _create_default_modifiers(self):
        """Create default difficulty modifiers as fallback."""
        self.difficulty_modifiers = {
            DifficultyLevel.VERY_EASY: DifficultyModifiers(
                enemy_health_multiplier=0.6,
                enemy_damage_multiplier=0.7,
                enemy_speed_multiplier=0.8,
                enemy_mana_multiplier=0.8,
                enemy_defense_multiplier=0.7,
                enemy_spell_frequency=0.5,
                loot_quality_multiplier=1.3,
                experience_multiplier=1.2,
                enemy_ai_aggression=0.6,
                status_effect_resistance=0.0
            ),
            DifficultyLevel.EASY: DifficultyModifiers(
                enemy_health_multiplier=0.8,
                enemy_damage_multiplier=0.85,
                enemy_speed_multiplier=0.9,
                enemy_mana_multiplier=0.9,
                enemy_defense_multiplier=0.85,
                enemy_spell_frequency=0.7,
                loot_quality_multiplier=1.15,
                experience_multiplier=1.1,
                enemy_ai_aggression=0.8,
                status_effect_resistance=0.1
            ),
            DifficultyLevel.NORMAL: DifficultyModifiers(
                enemy_health_multiplier=1.0,
                enemy_damage_multiplier=1.0,
                enemy_speed_multiplier=1.0,
                enemy_mana_multiplier=1.0,
                enemy_defense_multiplier=1.0,
                enemy_spell_frequency=1.0,
                loot_quality_multiplier=1.0,
                experience_multiplier=1.0,
                enemy_ai_aggression=1.0,
                status_effect_resistance=0.2
            ),
            DifficultyLevel.HARD: DifficultyModifiers(
                enemy_health_multiplier=1.3,
                enemy_damage_multiplier=1.2,
                enemy_speed_multiplier=1.1,
                enemy_mana_multiplier=1.2,
                enemy_defense_multiplier=1.15,
                enemy_spell_frequency=1.3,
                loot_quality_multiplier=0.9,
                experience_multiplier=0.95,
                enemy_ai_aggression=1.3,
                status_effect_resistance=0.3
            ),
            DifficultyLevel.VERY_HARD: DifficultyModifiers(
                enemy_health_multiplier=1.6,
                enemy_damage_multiplier=1.4,
                enemy_speed_multiplier=1.2,
                enemy_mana_multiplier=1.4,
                enemy_defense_multiplier=1.3,
                enemy_spell_frequency=1.6,
                loot_quality_multiplier=0.8,
                experience_multiplier=0.9,
                enemy_ai_aggression=1.6,
                status_effect_resistance=0.4
            ),
            DifficultyLevel.EXTREME: DifficultyModifiers(
                enemy_health_multiplier=2.0,
                enemy_damage_multiplier=1.7,
                enemy_speed_multiplier=1.4,
                enemy_mana_multiplier=1.8,
                enemy_defense_multiplier=1.5,
                enemy_spell_frequency=2.0,
                loot_quality_multiplier=0.7,
                experience_multiplier=0.85,
                enemy_ai_aggression=2.0,
                status_effect_resistance=0.5
            )
        }
        
    def record_battle_start(self):
        """Record the start of a battle."""
        self.metrics.last_battle_time = time.time()
        
    def record_battle_result(self, player_won: bool, battle_duration: float = 0.0,
                           damage_dealt: float = 0.0, damage_received: float = 0.0):
        """Record the result of a battle."""
        if player_won:
            self.metrics.battles_won += 1
            self.metrics.win_streak += 1
            self.metrics.loss_streak = 0
        else:
            self.metrics.battles_lost += 1
            self.metrics.loss_streak += 1
            self.metrics.win_streak = 0
            self.metrics.deaths += 1
            
        # Update damage totals
        self.metrics.total_damage_dealt += damage_dealt
        self.metrics.total_damage_received += damage_received
        
        # Update average battle duration
        total_battles = self.metrics.battles_won + self.metrics.battles_lost
        if total_battles == 1:
            self.metrics.average_battle_duration = battle_duration
        else:
            # Running average
            current_avg = self.metrics.average_battle_duration
            self.metrics.average_battle_duration = (
                (current_avg * (total_battles - 1) + battle_duration) / total_battles
            )
            
        self.logger.info(f"Battle result recorded: {'Win' if player_won else 'Loss'}, "
                        f"Duration: {battle_duration:.1f}s, "
                        f"Win rate: {self.metrics.win_rate:.1%}")
        
        # Consider difficulty adjustment
        self._consider_difficulty_adjustment()
        
    def record_spell_cast(self):
        """Record a spell being cast."""
        self.metrics.spells_cast += 1
        
    def record_item_used(self):
        """Record an item being used."""
        self.metrics.items_used += 1
        
    def record_level_up(self):
        """Record a level up."""
        self.metrics.level_ups += 1
        
    def _consider_difficulty_adjustment(self):
        """Consider whether to adjust difficulty based on performance."""
        total_battles = self.metrics.battles_won + self.metrics.battles_lost
        
        # Need minimum battles and cooldown period
        if (total_battles < self.adjustment_threshold or 
            time.time() - self.last_adjustment_time < self.adjustment_cooldown):
            return
            
        current_win_rate = self.metrics.win_rate
        old_difficulty = self.current_difficulty
        
        # Determine if adjustment is needed
        if current_win_rate > self.target_win_rate + 0.15:  # 80%+ win rate
            self._increase_difficulty()
        elif current_win_rate < self.target_win_rate - 0.15:  # 50%- win rate
            self._decrease_difficulty()
        elif self.metrics.win_streak >= 8:  # Long win streak
            self._increase_difficulty()
        elif self.metrics.loss_streak >= 5:  # Long loss streak
            self._decrease_difficulty()
            
        if self.current_difficulty != old_difficulty:
            self.last_adjustment_time = time.time()
            self.logger.info(f"Difficulty adjusted from {old_difficulty.value} to "
                           f"{self.current_difficulty.value} "
                           f"(Win rate: {current_win_rate:.1%})")
            
    def _increase_difficulty(self):
        """Increase difficulty level."""
        difficulty_levels = list(DifficultyLevel)
        current_index = difficulty_levels.index(self.current_difficulty)
        
        if current_index < len(difficulty_levels) - 1:
            self.current_difficulty = difficulty_levels[current_index + 1]
            
    def _decrease_difficulty(self):
        """Decrease difficulty level."""
        difficulty_levels = list(DifficultyLevel)
        current_index = difficulty_levels.index(self.current_difficulty)
        
        if current_index > 0:
            self.current_difficulty = difficulty_levels[current_index - 1]
            
    def get_current_modifiers(self) -> DifficultyModifiers:
        """Get current difficulty modifiers."""
        return self.difficulty_modifiers[self.current_difficulty]
        
    def apply_modifiers_to_enemy(self, enemy: Any) -> Any:
        """Apply difficulty modifiers to an enemy."""
        modifiers = self.get_current_modifiers()
        
        # Apply health modifier
        if hasattr(enemy, 'max_health'):
            original_health = enemy.max_health
            enemy.max_health *= modifiers.enemy_health_multiplier
            enemy.current_health = enemy.max_health
            
        # Apply damage modifier
        if hasattr(enemy, 'base_stats') and 'attack' in enemy.base_stats:
            enemy.base_stats['attack'] *= modifiers.enemy_damage_multiplier
            
        # Apply speed modifier
        if hasattr(enemy, 'base_stats') and 'speed' in enemy.base_stats:
            enemy.base_stats['speed'] *= modifiers.enemy_speed_multiplier
            
        # Apply mana modifier
        if hasattr(enemy, 'max_mana'):
            enemy.max_mana *= modifiers.enemy_mana_multiplier
            enemy.current_mana = enemy.max_mana
            
        # Apply defense modifier
        if hasattr(enemy, 'base_stats') and 'defense' in enemy.base_stats:
            enemy.base_stats['defense'] *= modifiers.enemy_defense_multiplier
            
        # Store AI aggression modifier for use by AI system
        if not hasattr(enemy, 'ai_modifiers'):
            enemy.ai_modifiers = {}
        enemy.ai_modifiers['aggression'] = modifiers.enemy_ai_aggression
        enemy.ai_modifiers['spell_frequency'] = modifiers.enemy_spell_frequency
        enemy.ai_modifiers['status_resistance'] = modifiers.status_effect_resistance
        
        # Update derived stats if method exists
        if hasattr(enemy, 'update_stats'):
            enemy.update_stats()
            
        self.logger.debug(f"Applied {self.current_difficulty.value} modifiers to {getattr(enemy, 'name', 'enemy')}")
        
        return enemy
        
    def get_loot_quality_modifier(self) -> float:
        """Get loot quality modifier for current difficulty."""
        return self.get_current_modifiers().loot_quality_multiplier
        
    def get_experience_modifier(self) -> float:
        """Get experience modifier for current difficulty."""
        return self.get_current_modifiers().experience_multiplier
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of current performance metrics."""
        total_battles = self.metrics.battles_won + self.metrics.battles_lost
        
        return {
            'difficulty_level': self.current_difficulty.value,
            'total_battles': total_battles,
            'battles_won': self.metrics.battles_won,
            'battles_lost': self.metrics.battles_lost,
            'win_rate': self.metrics.win_rate,
            'win_streak': self.metrics.win_streak,
            'loss_streak': self.metrics.loss_streak,
            'damage_ratio': self.metrics.damage_ratio,
            'average_battle_duration': self.metrics.average_battle_duration,
            'spells_cast': self.metrics.spells_cast,
            'items_used': self.metrics.items_used,
            'level_ups': self.metrics.level_ups,
            'deaths': self.metrics.deaths
        }
        
    def force_difficulty_level(self, difficulty: DifficultyLevel):
        """Force a specific difficulty level (for testing/debugging)."""
        old_difficulty = self.current_difficulty
        self.current_difficulty = difficulty
        self.last_adjustment_time = time.time()
        
        self.logger.info(f"Difficulty manually set from {old_difficulty.value} to {difficulty.value}")
        
    def reset_metrics(self):
        """Reset performance metrics (for new player or testing)."""
        self.metrics = PerformanceMetrics()
        self.current_difficulty = DifficultyLevel.NORMAL
        self.last_adjustment_time = time.time()
        
        self.logger.info("Performance metrics and difficulty reset to defaults")
