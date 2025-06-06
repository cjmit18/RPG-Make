# game_sys/character/character_creation.py

from __future__ import annotations
import json
from pathlib import Path
from random import randint
from typing import Any, Dict, Optional
from game_sys.core.actor import Actor
from game_sys.core.stats import Stats
from game_sys.skills.learning import LearningSystem, SkillRegistry

# Two separate template files (character and job templates)
_CHAR_TEMPLATES_PATH = Path(__file__).parent / "data" / "character_templates.json"
_JOB_TEMPLATES_PATH = Path(__file__).parent.parent / "jobs" / "data" / "jobs.json"

# Load each one into its own dict
try:
    with open(_CHAR_TEMPLATES_PATH, "r", encoding="utf-8") as f:
        _CHAR_TEMPLATES = json.load(f)
except FileNotFoundError:
    _CHAR_TEMPLATES = {}

try:
    from pathlib import Path

    with open(_JOB_TEMPLATES_PATH, "r", encoding="utf-8") as f:
        job_list = json.load(f)
        _JOB_TEMPLATES = {tpl["id"].lower(): tpl for tpl in job_list}
except FileNotFoundError:
    _JOB_TEMPLATES = {}


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

    def __str__(self) -> str:
        """String representation of the character showing name, level, stats, and inventory."""
        eff = self.stats.effective()
        lines = [
            f"{self.__class__.__name__}: {self.name}",
            f"Level: {self.levels.lvl}  Experience: {self.levels.experience}",
            f"Class: {self.job.name.capitalize() if self.job else 'None'}",
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
        # CAST level/experience to int here:
        level = int(data.get("level", 1))
        experience = int(data.get("experience", 0))
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


def create_character(template_name: str = "character", **overrides) -> Character:
    """
    Instantiate a Character (or subclass) from JSON templates and apply any overrides.
    If 'job_id' is passed, we skip adding JSON-template starting_items and go straight
    to job-assignment. That ensures no “commoner” or template items remain.
    """
    key = template_name.lower()
    requested_job: Optional[str] = overrides.pop("job_id", None)

    raw_resistance: dict[str, float] = {}
    raw_weakness: dict[str, float] = {}

    if requested_job:
        requested_job = requested_job.lower()
        raw_weakness = _JOB_TEMPLATES.get(requested_job, {}).get("weakness", {}) or {}
        raw_resistance = _JOB_TEMPLATES.get(requested_job, {}).get("resistance", {}) or {}

    # ---------------------------------------------------------------------
    # 1) If user explicitly asked for a subclass by name, build that subclass
    # ---------------------------------------------------------------------
    if key == "player":
        # 1a) Build a bare Player (this already assigns “commoner” in __init__)
        data = {**_CHAR_TEMPLATES.get(key, {}), **overrides}

        # ───────────────────────────────────────────────────────────────────
        # CAST any incoming level/experience to int before from_dict:
        data["level"] = int(data.get("level", 1))
        data["experience"] = int(data.get("experience", 0))
        # ───────────────────────────────────────────────────────────────────

        template: Player = Player.from_dict(data)

        # 1b) If job_id was provided, switch to that job and skip template items
        if requested_job:
            template.assign_job_by_id(requested_job)

    # ---------------------------------------------------------------------
    elif key == "npc":
        data = {**_CHAR_TEMPLATES.get(key, {}), **overrides}
        data["type"] = key

        # CAST here as well (for safety—though NPC rarely uses floats)
        data["level"] = int(data.get("level", 1))
        data["experience"] = int(data.get("experience", 0))

        template: NPC = NPC.from_dict(data)
        if requested_job:
            template.assign_job_by_id(requested_job)

    # ---------------------------------------------------------------------
    # 2) If user asked for a specific enemy type, build that subclass
    # ---------------------------------------------------------------------
    elif key in ["enemy", "goblin", "orc", "dragon", "zombie"]:
        data = {**_CHAR_TEMPLATES.get(key, {}), **overrides}
        data["type"] = "enemy"

        # CAST here too
        data["level"] = int(data.get("level", 1))
        data["experience"] = int(data.get("experience", 0))

        template: Enemy = Enemy.from_dict(data)
        template.name = data.get("name", key.capitalize())  # Default name if not provided
        template.assign_job_by_id(key if key != "enemy" else "goblin")

        gold_min = _CHAR_TEMPLATES.get(key, {}).get("gold_min", 0)
        gold_max = _CHAR_TEMPLATES.get(key, {}).get("gold_max", 0)
        if gold_min and gold_max:
            template.gold_min = gold_min
            template.gold_max = gold_max
            try:
                template.gold = randint(randint(gold_min, gold_max), (randint(gold_min, gold_max) * template.levels.lvl))
            except ValueError:
                template.gold = randint(1, 100) * template.levels.lvl
        else:
            template.gold = randint(1, 100) * template.levels.lvl

    elif key == "character":
        data = {**_CHAR_TEMPLATES.get(key, {}), **overrides}

        # CAST here
        data["level"] = int(data.get("level", 1))
        data["experience"] = int(data.get("experience", 0))

        template: Character = Character.from_dict(data)

    else:
        data = {**_CHAR_TEMPLATES.get(key, {}), **overrides}
        data["type"] = "character"

        # CAST here
        data["level"] = int(data.get("level", 1))
        data["experience"] = int(data.get("experience", 0))

        template: Character = Character.from_dict(data)

    # ---------------------------------------------------------------------
    # Apply weakness/resistance maps (if coming from a job template)
    # ---------------------------------------------------------------------
    if raw_weakness:
        from game_sys.core.damage_types import DamageType

        weak_parsed: dict[DamageType, float] = {}
        for key_str, mult in raw_weakness.items():
            try:
                dt = DamageType[key_str.upper()]
                weak_parsed[dt] = mult
            except KeyError:
                continue
        template.weakness = weak_parsed

    if raw_resistance:
        from game_sys.core.damage_types import DamageType

        resis_parsed: dict[DamageType, float] = {}
        for key_str, mult in raw_resistance.items():
            try:
                dt = DamageType[key_str.upper()]
                resis_parsed[dt] = mult
            except KeyError:
                continue
        template.resistance = resis_parsed

    # ---------------------------------------------------------------------
    # If a job_id was specified, load starting skills, if any
    # ---------------------------------------------------------------------
    if requested_job:
        # (a) Reload the SkillRegistry from wherever you store your JSON of skills.
        SkillRegistry.load_from_file(
            Path(__file__).parent.parent / "skills" / "data" / "skills.json"
        )

        # (b) Collect the “starting_skills” list from jobs.json, plus any override list:
        job_tpl: dict = _JOB_TEMPLATES.get(requested_job, {})
        json_skills: list[str] = job_tpl.get("starting_skills", []) or []
        override_skills: list[str] = overrides.get("starting_skills", []) or []

        # Properly concatenate the two lists (instead of `{**...}`):
        all_starting_skills = list(json_skills) + list(override_skills)

        # (c) Use the Player’s existing learning system; give them some SP so they can learn.
        #     For simplicity, give 100 SP if they are a Player:
        if isinstance(template, Player):
            template.learning.add_sp(100)

        # (d) Now loop through each skill ID and call .learn()
        for skill_id in all_starting_skills:
            if not skill_id:
                continue
            try:
                template.learning.learn(skill_id)
            except Exception as e:
                # If SP or prereqs fail, you might want to log or ignore—
                # but this shows why a “starting_skills” didn’t get applied.
                print(f"Warning: could not learn '{skill_id}' on creation: {e}")
        if isinstance(template, Player):
            template.learning.available_sp = 0  # No SP left after learning all starting skills

    return template
