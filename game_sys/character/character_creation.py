# game_sys/character/character_creation.py

"""
Character Creation Module
This module contains the Character class, its subclasses (NPC, Enemy, Player),
and a built-in factory for creating characters from JSON templates.
"""

from typing import Dict, Any, Type
import json
from pathlib import Path
from dataclasses import asdict
from random import randint

from game_sys.core.actor import Actor
from game_sys.core.stats import Stats
from game_sys.jobs.base import Job
from game_sys.items.item_base import Item as BaseItem, Equipable
from game_sys.items.consumable_list import Consumable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_sys.character.character_creation import Character

# Load character templates
_TEMPLATES_PATH = Path(__file__).parent / "data" / "character_templates.json"
try:
    with open(_TEMPLATES_PATH) as f:
        _CHAR_TEMPLATES = json.load(f)
except FileNotFoundError:
    _CHAR_TEMPLATES: Dict[str, Any] = {}


class Character(Actor):
    """
    Base class for all characters in the game.
    Supports JSON serialization and inventory persistence.
    """

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
            f"Class: {self.job.name}",
            "-" * 20
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
        """
        Serialize this character to a JSON-compatible dict, including inventory.
        """
        eff = self.stats.effective()
        data: Dict[str, Any] = {
            "type": self.__class__.__name__,
            "name": self.name,
            "level": self.levels.lvl,
            "experience": self.levels.experience,
            "job": self.job.__class__.__name__,
            "stats": {
                stat: eff.get(stat, 0) for stat in (
                    "attack", "defense", "speed", "health", "mana", "stamina"
                )
            },
            "current": {
                stat: getattr(self, f"current_{stat}", 0) for stat in (
                    "health", "mana", "stamina"
                )
            },
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
        """
        Recreate a Character, its base stats, current resources, and inventory, from a dict.
        """
        # Map types to classes
        type_map: Dict[str, Type[Character]] = {
            "Character": Character,
            "NPC": NPC,
            "Enemy": Enemy,
            "Player": Player
        }
        klass = type_map.get(data.get("type"), cls)
        inst = klass(
            name=data.get("name", ""),
            level=data.get("level", 1),
            experience=data.get("experience", 0)
        )

        # Clear inventory and equipped slots
        inst.inventory.items.clear()
        inst.inventory._equipped_items = {
            slot: None for slot in inst.inventory.equipped_items
        }
        inst.inventory._equipped_item_objs.clear()

        # Build stats from provided values and scale by level
        inst.stats = Stats(dict(data.get("stats", {})))
        inst.update_stats()
        caps = inst.stats.effective()

        # Set current resources to saved values or maxes
        inst.current_health = data.get("current", {}).get("health", caps.get("health", 0))
        inst.current_mana = data.get("current", {}).get("mana", caps.get("mana", 0))
        inst.current_stamina = data.get("current", {}).get("stamina", caps.get("stamina", 0))

        # Restore inventory items and auto-equip if needed
        for inv in data.get("inventory", []):
            item_info = inv.get("item", {})
            itype = item_info.get("type")
            item_args = {k: v for k, v in item_info.items() if k != "type"}
            qty = inv.get("quantity", 1)
            if itype == "Consumable":
                item_obj = Consumable(**item_args)
            elif itype == "Equipable":
                item_obj = Equipable(**item_args)
            else:
                item_obj = BaseItem(**item_args)

            inst.inventory.add_item(
                item_obj,
                quantity=qty,
                auto_equip=isinstance(item_obj, Equipable)
            )

        return inst


class NPC(Character):
    """
    Non-Playable Character class with no starting experience.
    """
    def __init__(self, name: str = "NPC", level: int = 1) -> None:
        super().__init__(name, level, experience=0)


class Enemy(Character):
    """
    Enemy class for combat encounters; grants XP on defeat.
    """
    def __init__(
        self,
        name: str = "Enemy",
        level: int = 1,
        experience: int = 0
    ) -> None:
        super().__init__(name, level, experience)
        if experience == 0:
            # Default experience: random between 50 and 150 × level
            self.levels.experience = randint(50, 150) * level

    @property
    def exp_value(self) -> int:
        """Amount of XP awarded when this Enemy is defeated."""
        return self.levels.experience


class Player(Character):
    """
    Player class for the main character; extend as needed with XP‐gain logic.
    """
    def __init__(self, name: str = "Hero", level: int = 1, experience: int = 0) -> None:
        super().__init__(name, level, experience)
        if not hasattr(self, "current_xp"):
            self.current_xp = self.levels.experience

    def gain_experience(self, xp: int) -> None:
        """
        Add xp to the player and auto‐level up if thresholds are met.
        """
        if not hasattr(self, "current_xp"):
            self.current_xp = 0
        self.current_xp += xp

        # Level‐up loop
        while self.current_xp >= self.xp_to_next_level():
            self.current_xp -= self.xp_to_next_level()
            self.levels.level_up()


# JSON I/O utilities

def save_character_to_json(character: "Character", path: str) -> None:
    """
    Save a character to disk as JSON.
    """
    with open(path, "w") as f:
        json.dump(character.to_dict(), f, indent=2)


def load_character_from_json(path: str) -> "Character":
    """
    Load a Character instance from a JSON file.
    """
    with open(path, "r") as f:
        data = json.load(f)
    return Character.from_dict(data)


def create_character(template_name: str, **overrides) -> "Character":
    """
    Instantiate a Character using a template from character_templates.json.
    Keyword args override template values.
    Example: create_character('Player', job_id='knight')
    """
    tmpl = _CHAR_TEMPLATES.get(template_name)
    if tmpl is None:
        for key, val in _CHAR_TEMPLATES.items():
            if val.get("name", "").lower() == template_name.lower():
                tmpl = val
                break
    if tmpl is None:
        available = ", ".join(_CHAR_TEMPLATES.keys())
        raise KeyError(f"No character template for '{template_name}'. Available: {available}")

    job_id = overrides.pop("job_id", None)
    data = {**tmpl, **overrides}
    stats = data.pop("base_stats", data.pop("stats", {}))
    data["stats"] = stats
    type_name = data.get("type", "").capitalize()

    if type_name == "Player":
        char = Player.from_dict(data)
    elif type_name in ("Npc", "NPC"):
        char = NPC.from_dict(data)
    elif type_name == "Enemy":
        char = Enemy.from_dict(data)
    else:
        char = Character.from_dict(data)

    if job_id:
        char.assign_job_by_id(job_id.lower())
        if isinstance(char, Enemy):
            char.name = char.job.name

    return char
