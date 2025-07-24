# game_sys/character/character_factory.py

import json
import random
from pathlib import Path
import re
from typing import Any, Dict
from game_sys.config.config_manager import ConfigManager
from game_sys.character.actor import Actor, Player, NPC, Enemy
from game_sys.character.job_manager import JobManager
from game_sys.character.resistance_manager import resistance_manager
from game_sys.skills.passive_manager import PassiveManager
from game_sys.logging import character_logger

def create_character(template_id: str, **overrides) -> Actor:
    character_logger.info(f"Creating character from template: {template_id}")

    character = CharacterFactory.create(template_id, **overrides)
    if character.team == 'enemy':
        from game_sys.core.scaling_manager import ScalingManager
        ScalingManager.auto_allocate_stat_points(character)
    character_logger.info(f"Character created: {character.name} (Type: {character.__class__.__name__})")

    return character


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
        
        # Base stats from template, overridden by any provided in overrides
        base_stats = dict(data.get('base_stats', {}))
        if ctype == 'enemy':
            actor = Enemy(
                name=data.get('display_name', template_id),
                base_stats=base_stats,
                **overrides
            )
            character_logger.info(f"Created enemy: {actor.name}")
        elif ctype == 'npc':
            actor = NPC(
                name=data.get('display_name', template_id),
                base_stats=base_stats,
                **overrides
            )
            character_logger.info(f"Created NPC: {actor.name}")
        else:
            actor = Player(
                name=data.get('display_name', template_id),
                base_stats=base_stats,
                _skip_default_job=True,  # Skip default job since we'll assign one
                **overrides
            )
            character_logger.info(f"Created player: {actor.name}")

        # Always set template_id for loot and other systems
        setattr(actor, 'template_id', template_id.lower())

        # Automatically add AI if enabled in config and actor is NPC or Enemy
        cfg = ConfigManager()
        ai_enabled = cfg.get('toggles.ai', False)
        if ai_enabled and (isinstance(actor, Enemy) or isinstance(actor, NPC)):
            try:
                # Use a global AI controller for all actors
                global _GLOBAL_AI_CONTROLLER
                if '_GLOBAL_AI_CONTROLLER' not in globals() or _GLOBAL_AI_CONTROLLER is None:
                    from game_sys.ai.ai_demo_integration import AIDemoController
                    try:
                        from game_sys.combat.combat_service import CombatService
                        temp_combat_service = CombatService()
                    except Exception:
                        temp_combat_service = None
                    _GLOBAL_AI_CONTROLLER = AIDemoController(temp_combat_service) if temp_combat_service else AIDemoController()
                _GLOBAL_AI_CONTROLLER.enable_ai_for_enemy(actor)
                character_logger.info(f"AI enabled for {actor.name} (auto, global controller)")
            except Exception as e:
                character_logger.warning(f"Failed to auto-enable AI for {actor.name}: {e}")

        cfg = ConfigManager()
    
        # 2) Assign job and apply its stat modifiers
        job_id = data.get('job_id', data.get('job', 'commoner'))
        JobManager.assign(actor, job_id)
        character_logger.debug(f"Assigned job '{job_id}' to {actor.name}")

        # 2.5) Set level if provided in overrides
        if 'level' in overrides:
            actor.level = overrides['level']
            character_logger.debug(f"Set level to {actor.level} for {actor.name}")

        # 3) Determine grade (numeric) - use override if provided, otherwise use template constraint
        if 'grade' in overrides:
            actor.grade = overrides['grade']
            # Try to find the corresponding grade name
            grades = cfg.get('defaults.grades', [])
            # Handle both 0-indexed and 1-indexed grade values
            if grades:
                if 0 <= actor.grade < len(grades):
                    # 0-indexed grade (0=ONE, 1=TWO, etc.)
                    setattr(actor, 'grade_name', grades[actor.grade])
                elif 1 <= actor.grade <= len(grades):
                    # 1-indexed grade (1=ONE, 2=TWO, etc.) - convert to 0-indexed
                    setattr(actor, 'grade_name', grades[actor.grade - 1])
                    actor.grade = actor.grade - 1  # Store as 0-indexed internally
                else:
                    setattr(actor, 'grade_name', f"GRADE_{actor.grade}")
            else:
                setattr(actor, 'grade_name', f"GRADE_{actor.grade}")
            character_logger.debug(f"Used override grade {actor.grade} ({getattr(actor, 'grade_name')}) for {actor.name}")
        else:
            # Generate random grade based on template constraint
            grades = cfg.get('defaults.grades', [])
            template_max_grade = data.get('grade', 0)  # Template grade is the maximum allowed
            
            if grades and template_max_grade > 0:
                # Random grade from 0 to template_max_grade-1 (so grade 3 means 0,1,2 -> ONE,TWO,THREE)
                max_grade_index = min(template_max_grade - 1, len(grades) - 1)
                actor.grade = random.randint(0, max_grade_index)
                setattr(actor, 'grade_name', grades[actor.grade])
                character_logger.debug(f"Assigned random grade {actor.grade} ({grades[actor.grade]}) to {actor.name} (max from template: {template_max_grade})")
            else:
                actor.grade = 0
                setattr(actor, 'grade_name', "ONE")

        # 4) Determine rarity (string) - use override if provided, otherwise use template constraint
        if 'rarity' in overrides:
            actor.rarity = overrides['rarity']
            character_logger.debug(f"Used override rarity '{actor.rarity}' for {actor.name}")
        else:
            # Generate random rarity based on template constraint
            rarities = cfg.get('defaults.rarities', [])
            template_max_rarity = data.get('rarity', 'COMMON')  # Template rarity is the maximum allowed
            
            if rarities and template_max_rarity in rarities:
                # Find the index of the max rarity in the list
                max_rarity_index = rarities.index(template_max_rarity)
                # Select random rarity from COMMON up to the template max
                available_rarities = rarities[:max_rarity_index + 1]
                
                # Use weighted selection (higher rarities are less likely)
                weights = [0.60, 0.25, 0.10, 0.04, 0.008, 0.002, 0.0005]  # Decreasing probabilities
                rarity_weights = weights[:len(available_rarities)]
                
                # Normalize weights
                total_weight = sum(rarity_weights)
                if total_weight > 0:
                    rarity_weights = [w / total_weight for w in rarity_weights]
                
                actor.rarity = random.choices(available_rarities, rarity_weights, k=1)[0]
                character_logger.debug(f"Assigned random rarity '{actor.rarity}' to {actor.name} (max from template: {template_max_rarity})")
            else:
                actor.rarity = 'COMMON'
                character_logger.debug(f"Used fallback rarity 'COMMON' for {actor.name}")

        # 5) Load weaknesses and resistances from template
        from game_sys.core.damage_types import DamageType
        
        # Load weaknesses
        weakness_data = data.get('weakness', {})
        for damage_type_name, weakness_value in weakness_data.items():
            try:
                damage_type = DamageType[damage_type_name]
                # Values in JSON are already in decimal format (0.25 = 25%)
                actor.weaknesses[damage_type] = weakness_value
                character_logger.debug(
                    f"Added weakness to {damage_type_name}: "
                    f"{weakness_value*100:.1f}%"
                )
            except KeyError:
                character_logger.warning(
                    f"Unknown damage type for weakness: {damage_type_name}"
                )
        
        # Load resistances
        resistance_data = data.get('resistance', {})
        for damage_type_name, resistance_value in resistance_data.items():
            try:
                damage_type = DamageType[damage_type_name]
                # Values in JSON are already in decimal format (0.4 = 40%)
                actor.resistances[damage_type] = resistance_value
                character_logger.debug(
                    f"Added resistance to {damage_type_name}: "
                    f"{resistance_value*100:.1f}%"
                )
            except KeyError:
                character_logger.warning(
                    f"Unknown damage type for resistance: {damage_type_name}"
                )

        # 6) Register passives (if any) so they hook into events immediately
        # Merge template passives with any existing passives (e.g., from job assignment)
        template_passives = data.get('passives', [])
        if not hasattr(actor, 'passive_ids'):
            actor.passive_ids = []
        
        # Add template passives that aren't already present
        for passive_id in template_passives:
            if passive_id not in actor.passive_ids:
                actor.passive_ids.append(passive_id)
                character_logger.debug(f"Added template passive '{passive_id}' to {actor.name}")
        
        if actor.passive_ids:
            PassiveManager.register_actor(actor)
            character_logger.debug(
                f"Registered {len(actor.passive_ids)} total passives for "
                f"{actor.name}: {actor.passive_ids}"
            )
            
            # Trigger spawn event for passives
            from game_sys.hooks.hooks_setup import emit, ON_CHARACTER_CREATED
            emit(ON_CHARACTER_CREATED, actor=actor)
            character_logger.debug(
                f"Emitted character created event for {actor.name}"
            )

        # 6) Finalize stats & pools
        actor.update_stats()
        actor.restore_all()
        character_logger.debug(f"Finalized stats for {actor.name}")
        
        # 7) Apply elemental resistances and weaknesses from template
        resistance_manager.apply_resistances_and_weaknesses(actor, template_id)

        return actor
