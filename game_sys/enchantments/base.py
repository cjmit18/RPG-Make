# game_sys/enchantments/base.py

import json
from pathlib import Path
from typing import Any, Dict, List
from abc import ABC, abstractmethod
from game_sys.core.rarity import Rarity
from game_sys.core.damage_types import DamageType
from logs.logs import get_logger
from game_sys.hooks.hooks import hook_dispatcher

log = get_logger(__name__)


class Enchantment(ABC):
    """
    Abstract base class for item enchantments.
    """
    def __init__(
        self,
        enchant_id: str,
        name: str,
        description: str,
        level: int,
        grade: int,
        rarity: Rarity,
        applicable_slots: List[str],
        stat_bonuses: Dict[str, int],
        damage_modifiers: Dict[DamageType, int],
    ) -> None:
        self.enchant_id = enchant_id
        self.name = name
        self.description = description
        self.level = level
        self.grade = grade
        self.rarity = rarity
        self.applicable_slots = applicable_slots
        self.stat_bonuses = stat_bonuses
        self.damage_modifiers = damage_modifiers
        # Track hooks so they can be unregistered
        self._hook_refs: List[Any] = []

    def __str__(self):
        return f"\nEnchantment ID: {self.enchant_id} | Name: {self.name}\n Level: {self.level} | Grade: {self.grade}| Rarity: {self.rarity.name})"

    @abstractmethod
    def apply(self, actor: Any, item: Any) -> None:
        """
        Apply stat and damage bonuses when an item is equipped.
        """
        pass

    @abstractmethod
    def remove(self, actor: Any, item: Any) -> None:
        """
        Remove stat and damage bonuses when an item is unequipped.
        """
        pass

    @classmethod
    def load_all(cls, path: Path) -> Dict[str, Any]:
        """
        Load every JSON template under path/data/*.json.
        """
        templates: Dict[str, Any] = {}
        data_dir = Path(path) / "data"
        for json_file in data_dir.glob("*.json"):
            try:
                raw = json.loads(json_file.read_text(encoding="utf-8"))
                for entry in raw:
                    templates[entry.get("id")] = entry
            except Exception as e:
                log.warning(f"Failed to load enchantment file {json_file}: {e}")
        return templates


class BasicEnchantment(Enchantment):
    """
    Concrete Enchantment: applies stat bonuses and optional damage hooks.
    """

    def apply(self, actor: Any, item: Any) -> None:
        # Apply each stat bonus via StatsManager
        for stat, amt in self.stat_bonuses.items():
            key = f"{item.id}-{self.enchant_id}-{stat}"
            actor.stats_mgr.stats.add_modifier(key, stat, amt)

        # Hook into combat for damage modifiers
        def _on_before_damage(attacker, defender, amount, damage_type):
            if attacker is actor and damage_type in self.damage_modifiers:
                bonus = self.damage_modifiers[damage_type]
                defender.take_damage(bonus, damage_type)

        self._hook_refs.append(("combat.before_damage", _on_before_damage))

    def remove(self, actor: Any, item: Any) -> None:
        # Remove all stat modifiers added on apply
        for stat in self.stat_bonuses:
            key = f"{item.id}-{self.enchant_id}-{stat}"
            actor.stats_mgr.stats.remove_modifier(key)

        # Unregister all hooks
        for event, fn in self._hook_refs:
            hook_dispatcher.unregister(event, fn)
        self._hook_refs.clear()

    def serialize_damage_modifiers(self) -> Dict[str, int]:
        return {dt.name: amt for dt, amt in self.damage_modifiers.items()}

    def __repr__(self):
        damage_str = {k.name: v for k, v in self.damage_modifiers.items()}
        return (f"\nEnchantment ID: {self.enchant_id} | Name: {self.name}\n "
                f"Level: {self.level} | Grade: {self.grade}\n "
                f"Rarity: {self.rarity.name}\n "
                f"Bonuses: {self.stat_bonuses}\n "
                f"Damage Modifiers: {damage_str})")