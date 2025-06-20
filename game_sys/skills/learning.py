# File: game_sys/skills/learning.py

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
import random

from game_sys.core.rarity import Rarity
from game_sys.effects.base import Effect
from game_sys.skills.base import Skill
from game_sys.skills.factory import create_skill
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_sys.character.actor import Actor

__all__ = ["SkillRecord", "SkillRegistry", "LearningSystem"]


class SkillRecord:
    """
    Holds metadata for a Skill:
      - skill_id, name, description, mana_cost, stamina_cost, cooldown, effects
      - sp_cost, min_level, prereq_skills, requirements, grade, rarity
    """
    def __init__(
        self,
        skill_id: str,
        name: str,
        description: str,
        mana_cost: int,
        stamina_cost: int,
        cooldown: int,
        effects: List[Effect],
        sp_cost: int,
        min_level: int,
        prereq_skills: Set[str],
        requirements: Dict[str, int],
        grade: int = 1,
        rarity: Rarity = Rarity.COMMON,
    ) -> None:
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.stamina_cost = stamina_cost
        self.cooldown = cooldown
        self.effects = list(effects)
        self.sp_cost = sp_cost
        self.min_level = min_level
        self.prereq_skills = set(prereq_skills or [])
        self.requirements = requirements or {}
        self.grade = grade
        self.rarity = rarity

    def can_character_learn(
        self,
        actor: Actor,
        known_skills: Set[str],
        available_sp: int,
    ) -> bool:
        if actor.level < self.min_level:
            return False
        if available_sp < self.sp_cost:
            return False
        if not self.prereq_skills.issubset(known_skills):
            return False
        for stat_name, threshold in self.requirements.items():
            if not hasattr(actor, stat_name):
                raise ValueError(f"Actor does not have stat '{stat_name}'")
            if getattr(actor, stat_name) < threshold:
                return False
        return True

    def build_skill_instance(
        self,
        actor: Actor,
        seed: Optional[int] = None,
        rng: Optional[random.Random] = None,
    ) -> Skill:
        """
        Instantiate a Skill via factory to apply:
        scaling, grade, rarity, and RNG.
        """
        return create_skill(
            self.skill_id,
            level=actor.level,
            grade=self.grade,
            rarity=self.rarity,
            seed=seed,
            rng=rng,
        )

    @classmethod
    def load_from_json_array(
        cls, path: Union[str, Path]
    ) -> List[SkillRecord]:
        """
        Read a JSON array of skill definitions (UTF-8), convert each “effects”
        entry via Effect.from_dict(...),
        and return a list of SkillRecord instances.
        """
        path_obj = Path(path)
        if not path_obj.is_file():
            raise FileNotFoundError(
                f"Skill JSON file not found at: {path_obj}"
            )

        raw_text = path_obj.read_text(encoding="utf-8")
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in skill file {path}: {e}") from e
        from game_sys.hooks.hooks import hook_dispatcher
        hook_dispatcher.fire("data.loaded", module=__name__, data=data)
        records: List[SkillRecord] = []
        for entry in data:
            sid = entry.get("skill_id")
            if not isinstance(sid, str):
                raise ValueError(
                    f"SkillRecord requires 'skill_id' string, got {sid!r}"
                )

            name = entry.get("name", "")
            desc = entry.get("description", "")
            m_cost = int(entry.get("mana_cost", 0))
            s_cost = int(entry.get("stamina_cost", 0))
            cd = int(entry.get("cooldown", 0))

            # Effects
            effs = entry.get("effects", [])
            effect_objs: List[Effect] = []
            if not isinstance(effs, list):
                raise ValueError(f"'effects' must be a list for skill '{sid}'")
            for eff in effs:
                effect_objs.append(Effect.from_dict(eff.copy()))

            # SP cost
            spc = int(entry.get("sp_cost", 1))
            # Min level
            minl = int(entry.get("min_level", 1))

            # Prereq skills
            prereqs = entry.get("prereq_skills", []) or []
            if not isinstance(prereqs, list):
                raise ValueError(
                    f"'prereq_skills' must be a list for skill '{sid}'"
                )

            # Requirements
            reqs = entry.get("requirements", {}) or {}
            requirements: Dict[str, int] = {
                stat: int(val) for stat, val in reqs.items()
            }

            # Grade & Rarity
            g = int(entry.get("grade", 1))
            r_str = entry.get("rarity", "COMMON").upper()
            try:
                r = Rarity[r_str]
            except KeyError:
                raise ValueError(f"Unknown rarity '{r_str}' for skill '{sid}'")

            rec = SkillRecord(
                skill_id=sid,
                name=name,
                description=desc,
                mana_cost=m_cost,
                stamina_cost=s_cost,
                cooldown=cd,
                effects=effect_objs,
                sp_cost=spc,
                min_level=minl,
                prereq_skills=set(prereqs),
                requirements=requirements,
                grade=g,
                rarity=r,
            )
            records.append(rec)

        return records


class SkillRegistry:
    """
    Global registry mapping skill_id → SkillRecord.
    """
    _registry: Dict[str, SkillRecord] = {}

    @classmethod
    def register(cls, record: SkillRecord) -> None:
        if record.skill_id in cls._registry:
            raise ValueError(f"Skill '{record.skill_id}' already registered.")
        cls._registry[record.skill_id] = record

    @classmethod
    def get(cls, skill_id: str) -> SkillRecord:
        if skill_id not in cls._registry:
            raise KeyError(f"Skill '{skill_id}' not found in registry.")
        return cls._registry[skill_id]

    @classmethod
    def all_ids(cls) -> List[str]:
        return list(cls._registry.keys())

    @classmethod
    def load_from_file(cls, path: Union[str, Path]) -> None:
        """
        Clear the registry, then load all SkillRecords from the JSON at path.
        """
        cls._registry.clear()
        records = SkillRecord.load_from_json_array(path)
        for rec in records:
            cls.register(rec)


class LearningSystem:
    """
    Tracks a character's known skills and unspent skill points (SP).
    """
    def __init__(self, owner: Actor, initial_sp: int = 0) -> None:
        self.owner = owner
        self.available_sp = initial_sp
        self.known_skills: Set[str] = set()
        self.instantiated_skills: Dict[str, Skill] = {}

    def unspent_sp(self) -> int:
        return self.available_sp

    def add_sp(self, amount: int) -> None:
        if amount < 0:
            raise ValueError(f"Cannot add negative SP: {amount}")
        self.available_sp += amount

    def spend_sp(self, amount: int) -> None:
        if amount > self.available_sp:
            raise RuntimeError(
                (
                    f"Not enough SP: required={amount}, "
                    f"available={self.available_sp}"
                )
            )
        self.available_sp -= amount

    def learn(self, skill_id: str) -> None:
        if skill_id in self.known_skills:
            raise RuntimeError(f"Already learned '{skill_id}'.")
        rec = SkillRegistry.get(skill_id)
        if not rec.can_character_learn(
            self.owner, self.known_skills, self.available_sp
        ):
            raise RuntimeError(
                f"Cannot learn '{skill_id}': prerequisites or SP not met."
            )
        self.spend_sp(rec.sp_cost)
        self.known_skills.add(skill_id)
        self.instantiated_skills[skill_id] = rec.build_skill_instance(
            self.owner
        )
        from game_sys.hooks.hooks import hook_dispatcher
        hook_dispatcher.fire("skill.learned", actor=self.owner, skill=skill_id)

    def unlearn(self, skill_id: str) -> None:
        if skill_id not in self.known_skills:
            raise RuntimeError(f"'{skill_id}' is not known.")
        rec = SkillRegistry.get(skill_id)
        self.available_sp += rec.sp_cost
        self.known_skills.remove(skill_id)
        del self.instantiated_skills[skill_id]
        from game_sys.hooks.hooks import hook_dispatcher
        hook_dispatcher.fire("skill.unlearned", actor=self.owner, skill=skill_id)

    def get_known_skills(self) -> List[str]:
        return list(self.known_skills)

    def get_skill_object(self, skill_id: str) -> Skill:
        if skill_id not in self.instantiated_skills:
            raise KeyError(
                f"Skill '{skill_id}' not instantiated for this actor."
            )
        return self.instantiated_skills[skill_id]

    def available_to_learn(self) -> List[str]:
        can_learn: List[str] = []
        for sid in SkillRegistry.all_ids():
            if sid in self.known_skills:
                continue
            rec = SkillRegistry.get(sid)
            if rec.can_character_learn(
                self.owner, self.known_skills, self.available_sp
            ):
                can_learn.append(sid)
        return can_learn

    def tick_all_cooldowns(self) -> None:
        for skill in self.instantiated_skills.values():
            try:
                skill.tick_cooldown()
            except AttributeError:
                pass
        from game_sys.hooks.hooks import hook_dispatcher
        hook_dispatcher.fire("skill.cooldown_tick", actor=self.owner)