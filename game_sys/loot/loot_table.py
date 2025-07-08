
# --- Local data loader helpers (for loot enrichment) ---
def _load_character_templates_local():
    """Load character templates from JSON (local fallback)."""
    import os, json
    char_file = os.path.join(os.path.dirname(__file__), "..", "character", "data", "character_templates.json")
    with open(char_file, 'r') as f:
        data = json.load(f)
    # Lowercase keys for matching
    return {k.lower(): v for k, v in data.items()}

def _load_jobs_local():
    """Load jobs from JSON (local fallback)."""
    import os, json
    jobs_file = os.path.join(os.path.dirname(__file__), "..", "character", "data", "jobs.json")
    with open(jobs_file, 'r') as f:
        data = json.load(f)
    return data.get('jobs', {})

# game_sys/loot/loot_table.py
"""
Dynamic loot table system that loads data from JSON and generates loot based on
enemy type, level, and player luck.
"""

import random
import json
import os
from typing import Dict, List, Optional, Tuple, Any

from game_sys.items.factory import ItemFactory
from game_sys.logging import character_logger
from game_sys.config.config_manager import ConfigManager


class LootTable:
    """
    Dynamic loot table that loads data from JSON and adjusts based on 
    enemy type, level, grade, rarity and player luck.
    """
    
    def __init__(self):
        """Initialize the loot table with data from JSON."""
        self.cfg = ConfigManager()
        self.loot_data = self._load_loot_data()
        
        # Get rarities from config
        self.rarities = self.cfg.get('defaults.rarities', [
            "COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "DIVINE"
        ])
        
        # Get grades from config
        self.grades = self.cfg.get('defaults.grades', [
            "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN"
        ])
        
        # Get rarity weights from config
        rarity_weights = self.cfg.get('randomness.rarity_weights', {
            "COMMON": 0.60,
            "UNCOMMON": 0.20,
            "RARE": 0.10,
            "EPIC": 0.05,
            "LEGENDARY": 0.03,
            "MYTHIC": 0.015,
            "DIVINE": 0.005
        })
        
        # Convert to our base drop rates format
        self.base_drop_rates = {k.lower(): v for k, v in rarity_weights.items()}
        
        # Get grade weights from config
        self.grade_weights = self.cfg.get('randomness.grade_weights', {
            "ONE": 0.40,
            "TWO": 0.25,
            "THREE": 0.15,
            "FOUR": 0.10,
            "FIVE": 0.06,
            "SIX": 0.03,
            "SEVEN": 0.01
        })
        
        # Experience and gold base amounts
        self.base_exp_per_level = 50
        self.base_gold_per_level = 25
        
    def _load_loot_data(self) -> Dict[str, Any]:
        """Load loot tables from JSON file."""
        try:
            loot_file = os.path.join(
                os.path.dirname(__file__), 
                "data", 
                "loot_tables.json"
            )
            with open(loot_file, 'r') as f:
                data = json.load(f)
                character_logger.info(
                    f"Loaded loot tables for {len(data.get('loot_tables', {}))} enemies"
                )
                return data.get('loot_tables', {})
        except Exception as e:
            character_logger.error(f"Error loading loot tables: {e}")
            return {}
    
    def apply_luck_modifier(self, base_chance: float, luck_stat: int) -> float:
        """Apply luck stat modifier to drop chance."""
        # Each point of luck above 10 increases drop chance by 1%
        # Each point below 10 decreases by 0.5%
        luck_modifier = 0.0
        if luck_stat > 10:
            luck_modifier = (luck_stat - 10) * 0.01
        elif luck_stat < 10:
            luck_modifier = (luck_stat - 10) * 0.005
        
        # Cap the modifier to prevent extreme values
        luck_modifier = max(-0.5, min(0.5, luck_modifier))
        
        return min(1.0, max(0.0, base_chance + luck_modifier))
    
    def get_enemy_loot_table(self, enemy_type: str) -> Dict[str, Any]:
        """Get the loot table for a specific enemy type."""
        # Try to match exactly, then try lowercase
        if enemy_type in self.loot_data:
            return self.loot_data[enemy_type]
        
        # Try partial matching (e.g., "Ancient Dragon" -> "dragon")
        for key in self.loot_data:
            if key.lower() in enemy_type.lower():
                return self.loot_data[key]
        
        # Fall back to default
        if "default" in self.loot_data:
            character_logger.warning(
                f"No loot table found for '{enemy_type}', using default"
            )
            return self.loot_data["default"]
        
        # Empty fallback if no default exists
        character_logger.error(
            f"No loot table found for '{enemy_type}' and no default table"
        )
        return {}
    
    def determine_item_level(self, enemy_level: int, enemy_type: str) -> int:
        """Determine the item level based on the enemy."""
        table = self.get_enemy_loot_table(enemy_type)
        base_level = table.get("default_item_level", enemy_level)
        
        # Add some randomness (±2 levels)
        variance = random.randint(-2, 2)
        return max(1, base_level + variance)
    
    def determine_item_grade(self, enemy_type: str, player_luck: int) -> str:
        """Determine the grade of items that drop."""
        table = self.get_enemy_loot_table(enemy_type)
        
        # Use the grades from the config if available in the table
        # Otherwise, use the default grade weights from config
        grade_chances = table.get("grade_chances", self.grade_weights)
        
        # Apply luck to each chance
        weighted_grades = []
        for grade, chance in grade_chances.items():
            modified_chance = self.apply_luck_modifier(chance, player_luck)
            weighted_grades.append((grade, modified_chance))
        
        # Sort by chance (highest first) for weighted selection
        weighted_grades.sort(key=lambda x: x[1], reverse=True)
        
        # Roll for grade
        roll = random.random()
        current_threshold = 0
        for grade, chance in weighted_grades:
            current_threshold += chance
            if roll <= current_threshold:
                return grade
        
        # Fallback to the first grade in our list
        return self.grades[0] if self.grades else "ONE"
    
    def determine_item_rarity(self, enemy_type: str, player_luck: int) -> str:
        """Determine the rarity of items that drop."""
        table = self.get_enemy_loot_table(enemy_type)
        rarity_chances = table.get("rarity_chances", self.base_drop_rates)
        
        # Apply luck to each chance
        weighted_rarities = []
        for rarity, chance in rarity_chances.items():
            modified_chance = self.apply_luck_modifier(chance, player_luck)
            weighted_rarities.append((rarity, modified_chance))
        
        # Sort by chance (highest first) for weighted selection
        weighted_rarities.sort(key=lambda x: x[1], reverse=True)
        
        # Roll for rarity
        roll = random.random()
        current_threshold = 0
        for rarity, chance in weighted_rarities:
            current_threshold += chance
            if roll <= current_threshold:
                return rarity
        
        # Fallback to the first rarity in our list
        return self.rarities[0] if self.rarities else "COMMON"
    
    def get_possible_items(self, enemy_type: str) -> List[str]:
        """Get the list of possible items that can drop, using job and character templates if available."""
        table = self.get_enemy_loot_table(enemy_type)
        items = set(table.get("possible_items", []))

        # Try to add items from character template and job
        try:
            char_templates = _load_character_templates_local()
            jobs = _load_jobs_local()
            template = char_templates.get(enemy_type.lower())
            if template:
                for entry in template.get("starting_items", []):
                    if isinstance(entry, dict):
                        items.add(entry.get("item_id"))
                    else:
                        items.add(entry)
                job_id = template.get("job_id")
                if job_id and job_id in jobs:
                    for entry in jobs[job_id].get("starting_items", []):
                        if isinstance(entry, dict):
                            items.add(entry.get("item_id"))
                        else:
                            items.add(entry)
        except Exception as e:
            character_logger.warning(f"Could not enrich possible_items for {enemy_type}: {e}")

        # Remove None and empty strings
        return [item for item in items if item]

    def get_guaranteed_items(self, enemy_type: str) -> List[str]:
        """Get the list of guaranteed items that will drop, using job and character templates if available."""
        table = self.get_enemy_loot_table(enemy_type)
        items = set(table.get("guaranteed_items", []))

        # Try to add guaranteed items from character template and job
        try:
            char_templates = _load_character_templates_local()
            jobs = _load_jobs_local()
            template = char_templates.get(enemy_type.lower())
            if template:
                for entry in template.get("starting_items", []):
                    if isinstance(entry, dict):
                        items.add(entry.get("item_id"))
                    else:
                        items.add(entry)
                job_id = template.get("job_id")
                if job_id and job_id in jobs:
                    for entry in jobs[job_id].get("starting_items", []):
                        if isinstance(entry, dict):
                            items.add(entry.get("item_id"))
                        else:
                            items.add(entry)
        except Exception as e:
            character_logger.warning(f"Could not enrich guaranteed_items for {enemy_type}: {e}")

        # Remove None and empty strings
        return [item for item in items if item]
    
    def calculate_exp_reward(self, enemy_level: int, enemy_type: str) -> int:
        """Calculate experience reward based on enemy stats."""
        table = self.get_enemy_loot_table(enemy_type)
        multiplier = table.get("exp_multiplier", 1.0)
        
        base_exp = self.base_exp_per_level * enemy_level * multiplier
        
        # Add some randomness (±20%)
        variance = random.uniform(0.8, 1.2)
        return int(base_exp * variance)
    
    def calculate_gold_reward(self, enemy_level: int, enemy_type: str) -> int:
        """Calculate gold reward based on enemy stats."""
        table = self.get_enemy_loot_table(enemy_type)
        gold_range = table.get("gold_range", [10, 50])
        
        # Scale by level
        min_gold = gold_range[0] * (1 + 0.1 * enemy_level)
        max_gold = gold_range[1] * (1 + 0.1 * enemy_level)
        
        return random.randint(int(min_gold), int(max_gold))
    
    def generate_loot(self, enemy_level: int, enemy_type: str, 
                      player_luck: int = 10) -> Dict:
        """Generate loot drops for a defeated enemy."""
        loot = {
            'experience': self.calculate_exp_reward(enemy_level, enemy_type),
            'gold': self.calculate_gold_reward(enemy_level, enemy_type),
            'items': []
        }
        
        # Add guaranteed items
        guaranteed_items = self.get_guaranteed_items(enemy_type)
        for item_id in guaranteed_items:
            try:
                item = ItemFactory.create(item_id)
                if item:
                    # Set grade and rarity
                    item.grade = self.determine_item_grade(enemy_type, player_luck)
                    item.rarity = self.determine_item_rarity(enemy_type, player_luck)
                    item.level = self.determine_item_level(enemy_level, enemy_type)
                    
                    loot['items'].append(item)
                    character_logger.info(
                        f"Generated guaranteed item: {item.name} "
                        f"(Lvl {item.level}, {item.grade}, {item.rarity})"
                    )
            except Exception as e:
                character_logger.warning(
                    f"Failed to create guaranteed item {item_id}: {e}"
                )
        
        # Determine if any random items drop
        rarity = self.determine_item_rarity(enemy_type, player_luck)
        if rarity:
            # Select a random item from possible items
            possible_items = self.get_possible_items(enemy_type)
            if possible_items:
                item_id = random.choice(possible_items)
                
                # Try to create the item
                try:
                    item = ItemFactory.create(item_id)
                    if item:
                        # Set grade, rarity and level
                        item.grade = self.determine_item_grade(enemy_type, player_luck)
                        item.rarity = rarity
                        item.level = self.determine_item_level(enemy_level, enemy_type)
                        
                        loot['items'].append(item)
                        character_logger.info(
                            f"Generated random item: {item.name} "
                            f"(Lvl {item.level}, {item.grade}, {item.rarity})"
                        )
                except Exception as e:
                    character_logger.warning(
                        f"Failed to create random item {item_id}: {e}"
                    )
        
        return loot
    
    def get_drop_chances_display(self, enemy_type: str, 
                                player_luck: int) -> Dict[str, float]:
        """Get display-friendly drop chances for the player's current luck."""
        table = self.get_enemy_loot_table(enemy_type)
        rarity_chances = table.get("rarity_chances", self.base_drop_rates)
        
        chances = {}
        for rarity, base_chance in rarity_chances.items():
            modified_chance = self.apply_luck_modifier(base_chance, player_luck)
            chances[rarity] = modified_chance * 100  # Convert to percentage
        
        return chances


# Global loot table instance
loot_table = LootTable()
