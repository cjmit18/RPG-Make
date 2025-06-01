# game_sys/character/character_creation.py

from __future__ import annotations
import json
from pathlib import Path
from random import randint
from typing import Any, Dict, Optional

from game_sys.core.actor import Actor
from game_sys.core.stats import Stats
from game_sys.inventory.inventory import Inventory
from game_sys.items.item_base import Equipable
from game_sys.skills.learning import LearningSystem

# _CHAR_TEMPLATES is loaded once at import time
_TEMPLATES_PATH = Path(__file__).parent / "data" / "character_templates.json"
try:
    with open(_TEMPLATES_PATH, "r", encoding="utf-8") as f:
        _CHAR_TEMPLATES = json.load(f)
except FileNotFoundError:
    _CHAR_TEMPLATES = {}


class Character(Actor):
    """
    Base class for all characters in the game. Inherits from Actor.
    Handles JSON‐based templates, leveling, and inventory persistence.
    """

    def __init__(
        self,
        name: str = "Template",
        level: int = 1,
        experience: int = 0,
    ) -> None:
        # 0) Prepare a place for “job_item_ids” before ANY job gets assigned:
        #    These IDs track exactly which items were given by the current job,
        #    so we can remove them cleanly later.
        self._job_item_ids: list[str] = []

        # 1) Call Actor.__init__ with no job (so Actor doesn’t auto-equip anything yet)
        super().__init__(name=name, level=level, experience=experience, job_class=None)

        # 2) Immediately assign “commoner.” Because _job_item_ids exists,
        #    any commoner items will be recorded there.
        try:
            self.assign_job_by_id("commoner")
        except Exception:
            # If “commoner” job is missing, reset stats to zeros
            from game_sys.jobs.base import Job as BaseJob

            self.job = None
            self.stats = Stats({stat: 0 for stat in BaseJob.base_stats.keys()})
            self.restore_all()

    def __str__(self) -> str:
        """String representation of the character showing name, level, stats, and inventory."""
        eff = self.stats.effective()
        lines = [
            f"{self.__class__.__name__}: {self.name}",
            f"Level: {self.levels.lvl}  Experience: {self.levels.experience}",
            f"Class: {self.job.name if self.job else 'None'}",
            f"Gold : {getattr(self, 'gold', 0)}",
            "-" * 20,
        ]
        for stat in ("attack", "defense", "speed", "health", "mana", "stamina", "intellect"):
            val = eff.get(stat, 0)
            if stat in ("health", "mana", "stamina"):
                cur = getattr(self, f"current_{stat}", 0)
                lines.append(f"{stat.capitalize():<7}: {cur}/{val}")
            else:
                lines.append(f"{stat.capitalize():<7}: {val}")
        lines.append("-" * 20)
        lines.append(str(self.inventory))
        return "\n".join(lines)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Character:
        """
        Reconstruct a Character (or subclass) from serialized data.
        **This version will NOT automatically pull in “template starting_items”**
        if you plan to override job_id. Instead, template starting_items are
        ignored when a job_id is provided at creation time.
        """
        name = data.get("name", "Template")
        level = data.get("level", 1)
        experience = data.get("experience", 0)
        char = cls(name=name, level=level, experience=experience)
        return char

    def assign_job_by_id(self, job_id: str) -> None:
        """
        Assign a job to this Character by its string ID.
        Steps:
          1) Unequip & remove all old job items (exactly as many copies as exist).
          2) Build new Job via create_job(job_id, level).
          3) Overwrite self.stats with new_job.stats_mods.
          4) Restore current_health/current_mana/current_stamina from those stats.
          5) Auto-equip any starting_items that the Job defines, and record those IDs
             in self._job_item_ids (for future removal).
        """
        from game_sys.jobs.base import Job
        from game_sys.jobs.factory import create_job

        try:
            new_job = create_job(job_id.lower(), self.levels.lvl)
        except KeyError:
            return  # invalid job_id → do nothing

        # 1) Remove old job’s items (if any) by removing exactly the quantity present
        for old_item_id in self._job_item_ids:
            # If that item is currently equipped, unequip it
            for slot, equipped_id in list(self.inventory._equipped_items.items()):
                if equipped_id == old_item_id:
                    self.inventory.unequip_item(slot)

            # Now remove as many copies as exist
            entry = self.inventory._items.get(old_item_id)
            if entry:
                remove_qty = entry["quantity"]
                try:
                    self.inventory.remove_item(old_item_id, quantity=remove_qty)
                except KeyError:
                    pass

        self._job_item_ids.clear()

        # 2) Switch to the new job
        self.job = new_job

        # 3) Overwrite stats with new job’s stats_mods
        base_stats = getattr(new_job, "stats_mods", {})
        full_stats = {stat: base_stats.get(stat, 0) for stat in Job.base_stats.keys()}
        self.stats = Stats(full_stats)

        # 4) Restore current_health/current_mana/current_stamina to match new stats
        self.restore_all()

        # 5) Auto-equip any starting_items from the Job, recording each ID
        for item_obj in getattr(new_job, "starting_items", []):
            if item_obj:
                self.inventory.add_item(item_obj, quantity=1, auto_equip=True)
                self._job_item_ids.append(item_obj.id)

        # 6) Recalculate any derived stats if needed
        try:
            self.update_stats()
        except Exception:
            pass


class NPC(Character):
    """NPC subclass (non-player character)."""
    def __init__(
        self,
        name: str = "NPC",
        level: int = 1,
        experience: int = 0,
    ) -> None:
        super().__init__(name, level, experience)


class Enemy(Character):
    """Enemy subclass: randomize experience if not provided."""
    def __init__(
        self,
        name: str = "Enemy",
        level: int = 1,
        experience: int = 0,
    ) -> None:
        super().__init__(name, level, experience)
        if experience == 0:
            self.levels.experience = randint(50, 150) * level


class Player(Character):
    """Player subclass: includes a LearningSystem."""
    def __init__(
        self,
        name: str = "Hero",
        level: int = 1,
        experience: int = 0,
    ) -> None:
        super().__init__(name, level, experience)
        self.learning = LearningSystem(self, initial_sp=0)
        self.current_xp = self.levels.experience


def create_character(template_name: str = "character", **overrides) -> Character:
    """
    Instantiate a Character (or subclass) from JSON templates and apply any overrides.
    If 'job_id' is passed, we skip adding JSON-template starting_items and go straight
    to job-assignment. That ensures no “commoner” or template items remain.
    """
    key = template_name.lower()
    requested_job: Optional[str] = overrides.pop("job_id", None)
    if requested_job:
        requested_job = requested_job.lower()

    # ---------------------------------------------------------------------
    # 1) If user explicitly asked for a subclass by name, build that subclass
    # ---------------------------------------------------------------------
    if key == "player":
        # 1a) Build a bare Player (this already assigns “commoner” in __init__)
        data = {**_CHAR_TEMPLATES.get("Player", {}), **overrides}
        data["type"] = "player"
        player: Player = Player.from_dict(data)

        # 1b) If job_id was provided, switch to that job and skip template items
        if requested_job:
            player.assign_job_by_id(requested_job)

        return player

    if key == "npc":
        data = {**_CHAR_TEMPLATES.get("NPC", {}), **overrides}
        data["type"] = "npc"
        npc: NPC = NPC.from_dict(data)
        if requested_job:
            npc.assign_job_by_id(requested_job)
        return npc

    if key == "enemy":
        data = {**_CHAR_TEMPLATES.get("Enemy", {}), **overrides}
        data["type"] = "enemy"
        enemy: Enemy = Enemy.from_dict(data)

        gold_min = _CHAR_TEMPLATES.get("Enemy", {}).get("gold_min", 0)
        gold_max = _CHAR_TEMPLATES.get("Enemy", {}).get("gold_max", 0)
        if gold_min or gold_max:
            enemy.gold_min = gold_min
            enemy.gold_max = gold_max
            enemy.gold = randint(gold_min, gold_max)
        else:
            enemy.gold = randint(1, enemy.levels.lvl * 10)

        # Add level-based template items if any (but if job_id, we’ll override them)
        buckets = _CHAR_TEMPLATES.get("Enemy", {}).get("starting_items_by_level", [])
        for bucket in buckets:
            if bucket["min_level"] <= enemy.levels.lvl <= bucket["max_level"]:
                for item_id in bucket.get("items", []):
                    try:
                        item_obj = enemy.inventory.generate_item(item_id)
                        if item_obj:
                            enemy.inventory.add_item(item_obj, quantity=1, auto_equip=True)
                    except Exception:
                        pass
                break

        job_to_assign = requested_job or data.get("name", "").lower()
        if job_to_assign:
            enemy.assign_job_by_id(job_to_assign)

        return enemy

    if key == "character":
        data = {**_CHAR_TEMPLATES.get("Character", {}), **overrides}
        data["type"] = "character"
        char: Character = Character.from_dict(data)
        if requested_job:
            char.assign_job_by_id(requested_job)
        return char

    # ---------------------------------------------------------------------
    # 2) Otherwise, find a template by name (e.g. “Goblin” → “Enemy” template)
    # ---------------------------------------------------------------------
    tmpl = _CHAR_TEMPLATES.get(template_name)
    if tmpl is None:
        for val in _CHAR_TEMPLATES.values():
            if val.get("name", "").lower() == key:
                tmpl = val
                break

    if tmpl is None:
        available = ", ".join(_CHAR_TEMPLATES.keys())
        raise KeyError(f"No character template for '{template_name}'. Available: {available}")

    data = {**tmpl, **overrides}
    ttype = data.get("type", "character").lower()

    if requested_job:
        new_char: Character = Character.from_dict(data)
        new_char.assign_job_by_id(requested_job)
        return new_char

    return Character.from_dict(data)
