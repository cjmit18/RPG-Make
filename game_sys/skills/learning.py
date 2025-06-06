# game_sys/skills/learning.py

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from game_sys.effects.base import Effect
from game_sys.core.actor import Actor
from game_sys.skills.base import Skill


__all__ = ["SkillRecord", "SkillRegistry", "LearningSystem"]


class SkillRecord:
    """
    Holds metadata for a Skill:
      - skill_id, name, description, mana_cost, stamina_cost, cooldown, effects
      - sp_cost, min_level, prereq_skills
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
        sp_cost: int = 1,
        min_level: int = 1,
        prereq_skills: Optional[List[str]] = None,
    ) -> None:
        self.skill_id: str = skill_id
        self.name: str = name
        self.description: str = description
        self.mana_cost: int = mana_cost
        self.stamina_cost: int = stamina_cost
        self.cooldown: int = cooldown
        self.effects: List[Effect] = list(effects)
        self.sp_cost: int = sp_cost
        self.min_level: int = min_level
        self.prereq_skills: Set[str] = set(prereq_skills or [])

    def can_character_learn(
        self,
        actor: Actor,
        known_skills: Set[str],
        available_sp: int,
    ) -> bool:
        """
        Return True if:
          - actor.levels.lvl ≥ min_level
          - available_sp ≥ sp_cost
          - prereq_skills ⊆ known_skills
        """
        if actor.levels.lvl < self.min_level:
            return False
        if available_sp < self.sp_cost:
            return False
        if not self.prereq_skills.issubset(known_skills):
            return False
        return True

    def build_skill_instance(self) -> Skill:
        """
        Instantiate a Skill (with a shallow copy of effects).
        """
        return Skill(
            skill_id=self.skill_id,
            name=self.name,
            description=self.description,
            mana_cost=self.mana_cost,
            stamina_cost=self.stamina_cost,
            cooldown=self.cooldown,
            effects=list(self.effects),
        )

    @classmethod
    def load_from_json_array(
        cls, path: Union[str, Path]
    ) -> List[SkillRecord]:
        """
        Read a JSON array of skill definitions (UTF-8), convert each “effects” entry
        via Effect.from_dict(...), and return a list of SkillRecord instances.
        """
        path_obj = Path(path)
        if not path_obj.is_file():
            raise FileNotFoundError(f"Skill JSON file not found at: {path_obj}")

        raw_text = path_obj.read_text(encoding="utf-8")
        raw_list: List[Dict[str, Any]] = json.loads(raw_text)

        records: List[SkillRecord] = []
        for entry in raw_list:
            # 1) Build a list of Effect objects for this skill
            effect_objs: List[Effect] = []
            for e in entry.get("effects", []):
                effect_objs.append(Effect.from_dict(e))

            # 2) Required fields (error if missing or wrong type)
            sid    = entry.get("skill_id")
            name   = entry.get("name")
            desc   = entry.get("description", "")
            m_cost = entry.get("mana_cost", 0)
            s_cost = entry.get("stamina_cost", 0)
            cd     = entry.get("cooldown", 0)
            spc    = entry.get("sp_cost", 1)
            minl   = entry.get("min_level", 1)
            prereqs = entry.get("prereq_skills", [])

            # Validate required top‐level fields:
            if not isinstance(sid, str):
                raise ValueError(f"SkillRecord requires string 'skill_id', got {sid!r}")
            if not isinstance(name, str):
                raise ValueError(f"SkillRecord requires string 'name', got {name!r}")
            if not isinstance(m_cost, int):
                raise ValueError(f"SkillRecord requires integer 'mana_cost', got {m_cost!r}")
            if not isinstance(s_cost, int):
                raise ValueError(f"SkillRecord requires integer 'stamina_cost', got {s_cost!r}")
            if not isinstance(cd, int):
                raise ValueError(f"SkillRecord requires integer 'cooldown', got {cd!r}")
            if not isinstance(spc, int):
                raise ValueError(f"SkillRecord requires integer 'sp_cost', got {spc!r}")
            if not isinstance(minl, int):
                raise ValueError(f"SkillRecord requires integer 'min_level', got {minl!r}")
            if not isinstance(prereqs, list) or not all(isinstance(x, str) for x in prereqs):
                raise ValueError(f"SkillRecord requires list-of-strings 'prereq_skills', got {prereqs!r}")

            # 3) Construct the SkillRecord
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
                prereq_skills=prereqs,
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
        self.owner: Actor = owner
        self.available_sp: int = initial_sp
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
            raise RuntimeError(f"Not enough SP: required={amount}, available={self.available_sp}")
        self.available_sp -= amount

    def learn(self, skill_id: str) -> None:
        if skill_id in self.known_skills:
            raise RuntimeError(f"Already learned '{skill_id}'.")

        try:
            record = SkillRegistry.get(skill_id)
        except KeyError as e:
            raise RuntimeError(f"Unknown skill '{skill_id}'") from e

        if not record.can_character_learn(
            self.owner,
            self.known_skills,
            self.available_sp,
        ):
            raise RuntimeError(f"Cannot learn '{skill_id}': prerequisites or SP not met.")

        self.spend_sp(record.sp_cost)
        self.known_skills.add(skill_id)
        self.instantiated_skills[skill_id] = record.build_skill_instance()

    def unlearn(self, skill_id: str) -> None:
        if skill_id not in self.known_skills:
            raise RuntimeError(f"'{skill_id}' is not known.")

        rec = SkillRegistry.get(skill_id)
        self.available_sp += rec.sp_cost
        self.known_skills.remove(skill_id)
        del self.instantiated_skills[skill_id]

    def get_known_skills(self) -> List[str]:
        return list(self.known_skills)

    def get_skill_object(self, skill_id: str) -> Skill:
        if skill_id not in self.instantiated_skills:
            raise KeyError(f"Skill '{skill_id}' not instantiated for this actor.")
        return self.instantiated_skills[skill_id]

    def available_to_learn(self) -> List[str]:
        can_learn: List[str] = []
        for sid in SkillRegistry.all_ids():
            if sid in self.known_skills:
                continue
            rec = SkillRegistry.get(sid)
            if rec.can_character_learn(
                self.owner,
                self.known_skills,
                self.available_sp,
            ):
                can_learn.append(sid)
        return can_learn

    def tick_all_cooldowns(self) -> None:
        for skill in self.instantiated_skills.values():
            try:
                skill.tick_cooldown()
            except AttributeError:
                pass
