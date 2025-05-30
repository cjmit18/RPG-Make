"""Character Creation Module
This module contains the Character class, its subclasses (NPC, Enemy, Player),
and a built-in factory for creating characters from JSON templates or overrides."""
from typing import Dict, Any, Type
import json
from pathlib import Path
from dataclasses import asdict
from game_sys.core.actor import Actor
from game_sys.core.stats import Stats
from game_sys.jobs.base import Job
from game_sys.items.item_base import Item as BaseItem, Equipable
from game_sys.items.consumable_list import Consumable

# Load character templates
_TEMPLATES_PATH = Path(__file__).parent / 'data' / 'character_templates.json'
try:
    with open(_TEMPLATES_PATH) as f:
        _CHAR_TEMPLATES = json.load(f)
except FileNotFoundError:
    _CHAR_TEMPLATES = {}

class Character(Actor):
    """Base class for all characters in the game. Supports JSON serialization and
    inventory persistence."""
    def __init__(
        self,
        name: str = "Template",
        level: int = 1,
        experience: int = 0
    ) -> None:
        super().__init__(name, level, experience, job_class=Job)

    def __str__(self) -> str:
        eff = self.stats.effective()
        lines = [
            f"{self.__class__.__name__}: {self.name}",
            f"Level: {self.levels.lvl}  Experience: {self.levels.experience}",
            f"Class: {self.job.name }",
            "-" * 20,
        ]
        for stat in ("attack", "defense", "speed", "health", "mana", "stamina"):
            val = eff.get(stat, 0)
            if stat in ("health", "mana", "stamina"):
                cur = getattr(self, f"current_{stat}", 0)
                lines.append(f"{stat.capitalize()}: {cur}/{val}")
            else:
                lines.append(f"{stat.capitalize()}: {val}")
        lines.append("-" * 20)
        lines.append(str(self.inventory))
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this character to a JSON-compatible dict, including inventory."""
        eff = self.stats.effective()
        data: Dict[str, Any] = {
            "type": self.__class__.__name__,
            "name": self.name,
            "level": self.levels.lvl,
            "experience": self.levels.experience,
            "job": self.job.__class__.__name__,
            "stats": {stat: eff.get(stat, 0) for stat in ("attack", "defense", "speed", "health", "mana", "stamina")},
            "current": {stat: getattr(self, f"current_{stat}", 0) for stat in ("health", "mana", "stamina")},
            "inventory": []
        }
        for entry in self.inventory.items.values():
            item_obj = entry["item"]
            qty = entry["quantity"]
            item_data = asdict(item_obj)
            item_data["type"] = item_obj.__class__.__name__
            data["inventory"].append({"item": item_data, "quantity": qty})
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """Recreate a Character, its base stats, current resources, and inventory, from a dict.
        This method clears defaults and applies JSON state entirely."""
        # Map types to classes
        type_map: Dict[str, Type[Character]] = {
            "Character": Character,
            "NPC": NPC,
            "Enemy": Enemy,
            "Player": Player
        }
        # Instantiate core object
        klass = type_map.get(data.get("type"), cls)
        inst = klass(
            name=data.get("name", ""),
            level=data.get("level", 1),
            experience=data.get("experience", 0)
        )
        # Clear any starting inventory and equipment
        inst.inventory.items.clear()
        inst.inventory._equipped_items = {slot: None for slot in inst.inventory.equipped_items}
        # Override stats from JSON
        inst.stats = Stats(data.get("stats", {}))
        # Refill current resources to full based on new stats
        caps = inst.stats.effective()
        inst.current_health = caps.get("health", 0)
        inst.current_mana = caps.get("mana", 0)
        inst.current_stamina = caps.get("stamina", 0)
        # Apply JSON-provided current values
        for stat, val in data.get("current", {}).items():
            setattr(inst, f"current_{stat}", val)
        # Restore inventory items and auto-equip to apply modifiers
        for inv in data.get("inventory", []):
            item_info = inv.get("item", {})
            itype = item_info.get("type")
            # Strip out type to pass remaining args
            item_args = {k: v for k, v in item_info.items() if k != "type"}
            qty = inv.get("quantity", 1)
            if itype == "Consumable":
                item_obj = Consumable(**item_args)
            elif itype == "Equipable":
                item_obj = Equipable(**item_args)
            else:
                item_obj = BaseItem(**item_args)
            inst.inventory.add_item(item_obj, quantity=qty, auto_equip=isinstance(item_obj, Equipable))
        return inst


class NPC(Character):
    """Non-Playable Character class with no starting experience."""
    def __init__(self, name: str = "NPC", level: int = 1) -> None:
        super().__init__(name, level, experience=0)


class Enemy(Character):
    """Enemy class for combat encounters; grants XP on defeat."""
    def __init__(
        self,
        name: str = "Enemy",
        level: int = 1,
        experience: int = 0
    ) -> None:
        super().__init__(name, level, experience)
        if experience == 0:
            self.levels.experience = level * 100


class Player(Character):
    """Player class for the main character; extend as needed."""
    def __init__(self, name: str = "Hero", level: int = 1, experience: int = 0) -> None:
        super().__init__(name, level, experience)
        # add player-specific hooks here


# JSON I/O utilities

def save_character_to_json(character: Character, path: str) -> None:
    """Save a character to disk as JSON."""
    with open(path, 'w') as f:
        json.dump(character.to_dict(), f, indent=2)


def load_character_from_json(path: str) -> Character:
    """Load a Character instance from a JSON file."""
    with open(path, 'r') as f:
        data = json.load(f)
    return Character.from_dict(data)


# Built-in factory: JSON templates with optional overrides

def create_character(template_name: str, **overrides) -> Character:
    """
    Instantiate a Character using a template from character_templates.json.
    Keyword args override template values.
    Example: create_character('Player') or create_character('Hero')
    """
    # Try direct key lookup
    tmpl = _CHAR_TEMPLATES.get(template_name)
    # Fallback: search by inner `name` field
    if tmpl is None:
        for key, val in _CHAR_TEMPLATES.items():
            if val.get("name", "").lower() == template_name.lower():
                tmpl = val
                break
    if tmpl is None:
        available = ", ".join(_CHAR_TEMPLATES.keys())
        raise KeyError(f"No character template for '{template_name}'. Available: {available}")
    # Merge template with overrides
    data = {**tmpl, **overrides}
    return Character.from_dict(data)