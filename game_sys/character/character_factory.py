# game_sys/character/character_factory.py

import json
import random
from pathlib import Path
from typing import Any, Dict
from game_sys.config.config_manager import ConfigManager
from game_sys.character.actor import Actor, Player, NPC, Enemy
from game_sys.character.job_manager import JobManager
from game_sys.skills.passive_manager import PassiveManager
from game_sys.logging import character_logger

def create_character(template_id: str, **overrides) -> Actor:
    character_logger.info(f"Creating character from template: {template_id}")
    return CharacterFactory.create(template_id, **overrides)

class CharacterFactory:
    """
    Loads character templates from JSON and instantiates Actor subclasses,
    assigning job, grade (numeric), rarity, and initializing stats.
    Also registers any passive abilities defined in the template.
    """
    _templates: Dict[str, Dict] = {}

    @classmethod
    def _load_templates(cls):
        path = Path(__file__).parent / 'data' / 'character_templates.json'
        cls._templates = json.loads(path.read_text())
        character_logger.debug(f"Loaded {len(cls._templates)} character templates")

    @classmethod
    def create(cls, template_id: str, **overrides) -> Actor:
        # Load if not already
        if not cls._templates:
            character_logger.debug("Templates not loaded, loading now")
            cls._load_templates()

        data = cls._templates.get(template_id.lower())
        if not data:
            character_logger.warning(f"Template '{template_id}' not found, creating blank actor")
            # Fallback blank actor
            return Actor(name=template_id, base_stats={}, **overrides)

        # 1) Choose the correct Actor subclass
        ctype = data.get('type', 'player').lower()
        character_logger.debug(f"Creating {ctype} from template: {template_id}")
        
        if ctype == 'enemy':
            actor = Enemy(
                name=data.get('display_name', template_id),
                base_stats=data.get('base_stats', {}),
                **overrides
            )
            character_logger.info(f"Created enemy: {actor.name}")
        elif ctype == 'npc':
            actor = NPC(
                name=data.get('display_name', template_id),
                base_stats=data.get('base_stats', {}),
                **overrides
            )
            character_logger.info(f"Created NPC: {actor.name}")
        else:
            actor = Player(
                name=data.get('display_name', template_id),
                base_stats=data.get('base_stats', {}),
                **overrides
            )
            character_logger.info(f"Created player: {actor.name}")

        cfg = ConfigManager()

        # 2) Assign job and apply its stat modifiers
        job_id = data.get('job_id', data.get('job', 'commoner'))
        JobManager.assign(actor, job_id)
        character_logger.debug(f"Assigned job '{job_id}' to {actor.name}")

        # 3) Determine grade (numeric) from the configured grade‐names/weights
        grades = cfg.get('defaults.grades', [])
        grade_weights = [
            cfg.get('randomness.grade_weights', {}).get(g, 0.0) 
            for g in grades
        ]
        grade_name = random.choices(grades, grade_weights, k=1)[0]
        actor.grade_name = grade_name
        actor.grade = grades.index(grade_name) + 1
        character_logger.debug(f"Assigned grade {actor.grade} ({grade_name}) to {actor.name}")

        # 4) Determine rarity (string) from the configured rarities/weights
        rarities = list(cfg.get('randomness.rarity_weights', {}).keys())
        rarity_weights = list(cfg.get('randomness.rarity_weights', {}).values())
        actor.rarity = random.choices(rarities, rarity_weights, k=1)[0]
        character_logger.debug(f"Assigned rarity '{actor.rarity}' to {actor.name}")

        # 5) Register passives (if any) so they hook into events immediately
        actor.passive_ids = data.get('passives', [])
        if actor.passive_ids:
            PassiveManager.register_actor(actor)
            character_logger.debug(
                f"Registered {len(actor.passive_ids)} passives for {actor.name}"
            )
            
            # Trigger spawn event for passives
            from game_sys.hooks.hooks_setup import emit, ON_CHARACTER_CREATED
            emit(ON_CHARACTER_CREATED, actor=actor)
            character_logger.debug(f"Emitted character created event for {actor.name}")

        # 6) Finalize stats & pools
        actor.update_stats()
        actor.restore_all()
        character_logger.debug(f"Finalized stats for {actor.name}")

        return actor
