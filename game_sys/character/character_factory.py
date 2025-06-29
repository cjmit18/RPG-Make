# game_sys/character/character_factory.py
"""
Module: game_sys.character.character_factory

Provides factory functions to create Actor subclasses from JSON templates,
assigning base stats, progression, grade/rarity, gold, levels,
weaknesses/resistances, jobs, items, skills, and emitting creation events.
"""
import json
import random
from pathlib import Path
from typing import Type
from game_sys.config.config_manager import ConfigManager
from game_sys.hooks.hooks_setup import emit, ON_CHARACTER_CREATED, ON_DATA_LOADED
from game_sys.character.actor import Player, NPC, Enemy, Actor
from game_sys.items.item_loader import load_item
from game_sys.skills.skill_loader import load_skill
from game_sys.character.job_manager import JobManager
from game_sys.core.damage_types import DamageType

# Load templates once
def _load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}

CFG = ConfigManager()
BASE_DIR = Path(__file__).parent / 'data'
_CHAR_TEMPLATES = _load_json(BASE_DIR / 'character_templates.json')
_JOB_TEMPLATES = _load_json(BASE_DIR.parent / 'jobs.json')

class CharacterFactory:
    """Factory for creating characters from templates."""
    @staticmethod
    def create(template_id: str, **overrides) -> Actor:
        data = {**_CHAR_TEMPLATES.get(template_id, {}), **overrides}
        cls_map = {'player': Player, 'npc': NPC, 'enemy': Enemy}
        cls: Type[Actor] = cls_map.get(data.get('type','').lower(), Player)
        actor = cls(name=data.get('display_name', template_id), base_stats=data.get('base_stats', {}))

        # Grade & Rarity
        grades = CFG.get('defaults.grades', [])
        grade_weights = CFG.get('randomness.grade_weights', {})
        gw = [grade_weights.get(g, 1.0) for g in grades]
        actor.grade = random.choices(grades, gw, k=1)[0]

        ranks = CFG.get('defaults.ranks', [])
        rarity_weights = CFG.get('randomness.rarity_weights', {})
        rw = [rarity_weights.get(r.lower(), 1.0) for r in ranks]
        actor.rarity = random.choices(ranks, rw, k=1)[0]

        # Gold
        gcfg = data.get('gold', {})
        actor.gold = random.randint(gcfg.get('min',0), gcfg.get('max',0))

        # Level & XP
        lvl = data.get('level',{})
        actor.level = lvl.get('start',1)
        actor.xp = lvl.get('start',0)

        # Weakness/Resistance
        for k, v in data.get('weakness', {}).items():
            try: actor.weaknesses[DamageType[k.upper()]] = v
            except: pass
        for k, v in data.get('resistance', {}).items():
            try: actor.resistances[DamageType[k.upper()]] = v
            except: pass

        # Job
        JobManager.assign(actor, data.get('job_id',''))

        # Stats & Pools
        actor.update_stats(); actor.restore_all()

        # Items
        for iid in data.get('starting_items',[]):
            itm = load_item(iid)
            if hasattr(itm,'base_damage'): actor.weapon=itm
            else: actor.inventory.add_item(itm)

        # Skills
        for sid in data.get('starting_skills',[]): actor.skill_effect_ids.append(sid)

        emit(ON_CHARACTER_CREATED, actor=actor)
        emit(ON_DATA_LOADED, actor=actor, template=template_id)
        return actor

# Convenience function
def create_character(template_id: str, **overrides) -> Actor:
    return CharacterFactory.create(template_id, **overrides)
