import json
from pathlib import Path
from typing import Any, Dict
from game_sys.items.factory import ItemFactory
from game_sys.items.equipment import Equipment
from game_sys.logging import character_logger, log_exception


class JobManager:
    """
    Loads job definitions from JSON and assigns/progresses jobs on Actors.
    """

    _jobs: Dict[str, Dict] = {}

    @classmethod
    def load_jobs(cls) -> None:
        path = Path(__file__).parent / "data" / "jobs.json"
        data = json.loads(path.read_text())
        cls._jobs = data.get("jobs", {})
        character_logger.info(f"Loaded {len(cls._jobs)} job definitions")

    @classmethod
    @log_exception
    def assign(cls, actor: Any, job_id: str) -> bool:
        """
        Give `actor` the specified job, applying base stat mods,
        known abilities, and starting items.
        Called by Player.__init__.
        """
        if not cls._jobs:
            character_logger.debug("Jobs not loaded, loading now")
            cls.load_jobs()

        job_def = cls._jobs.get(job_id)
        if not job_def:
            character_logger.warning(f"Job '{job_id}' not found for {actor.name}")
            return False

        character_logger.info(f"Assigning job '{job_id}' to {actor.name}")
        actor.job_id = job_id
        actor.job_name = job_def["name"]
        actor.job_level = 1
        actor.job_xp = 0.0
        actor.job_mods = job_def.get("base_stat_mods", {}).copy()
        # Apply base‐stat modifiers immediately
        for stat, bonus in actor.job_mods.items():
            actor.base_stats[stat] = actor.base_stats.get(stat, 0.0) + bonus
        
        character_logger.debug(f"Applied job stat modifiers for {actor.name}: {actor.job_mods}")

        character_logger.debug(
            f"Applied job stat modifiers for {actor.name}: {actor.job_mods}"
        )

        # Grant initial skills & spells
        actor.known_skills = job_def.get("skill_list", []).copy()
        actor.known_spells = job_def.get("spell_list", []).copy()
        
        if actor.known_skills:
            character_logger.debug(
                f"Granted skills to {actor.name}: {actor.known_skills}"
            )
        if actor.known_spells:
            character_logger.debug(
                f"Granted spells to {actor.name}: {actor.known_spells}"
            )
        
        # Grant starting items
        starting_items = job_def.get("starting_items", [])
        for item_data in starting_items:
            item_id = item_data["item_id"]
            quantity = item_data.get("quantity", 1)
            for _ in range(quantity):
                try:
                    item = ItemFactory.create(item_id)
                    if item:
                        # Auto-equip equipment, add consumables to inventory
                        if isinstance(item, Equipment):
                            item.apply(actor)  # Merges stats & effects, equips
                        else:
                            actor.inventory.add_item(item)  # Consumables
                        character_logger.debug(
                            f"Added item {item_id} to {actor.name}"
                        )
                    else:
                        character_logger.warning(
                            f"Failed to create item {item_id} for {actor.name}"
                        )
                except Exception as e:
                    character_logger.error(
                        f"Error creating item {item_id} for {actor.name}: {e}"
                    )
                    # Continue with other items instead of failing completely
        
        character_logger.info(
            f"Job '{job_id}' assigned to {actor.name} successfully"
        )
        return True

    @classmethod
    @log_exception
    def gain_xp(cls, actor: Any, amount: float) -> None:
        """
        Award job XP, level up when threshold reached (100 * level by default),
        and optionally reapply stat mods or unlock new abilities.
        """
        character_logger.debug(
            f"{actor.name} gained {amount} job XP for {actor.job_name}"
        )
        actor.job_xp += amount
        threshold = 100.0 * actor.job_level
        while actor.job_xp >= threshold:
            actor.job_xp -= threshold
            old_level = actor.job_level
            actor.job_level += 1
            character_logger.info(
                f"{actor.name}'s job {actor.job_name} leveled up from "
                f"{old_level} to {actor.job_level}"
            )
            # TODO: optionally bump stat_mods or unlock skills per-job
            # emit a ON_JOB_LEVEL_UP event here if desired
            threshold = 100.0 * actor.job_level