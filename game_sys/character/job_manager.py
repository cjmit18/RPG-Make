# game_sys/character/job_manager.py
"""
Module: game_sys.character.job_manager

Static helper to assign jobs (classes) to actors, applying any
stat‐bonus effects defined by those jobs and emitting an event.
"""
from typing import Any
from game_sys.effects.registry import EffectRegistry
from game_sys.hooks.hooks_setup import emit, ON_JOB_ASSIGNED


class JobManager:
    """
    Assigns a job_id to an Actor, applies its stat bonuses, and fires ON_JOB_ASSIGNED.
    """

    @staticmethod
    def assign(actor: Any, job_id: str):
        """
        Give this actor the specified job.
        - Records the job_id on the actor
        - Applies any associated stat-bonus effect(s)
        - Emits ON_JOB_ASSIGNED for downstream systems
        """
        actor.job_id = job_id

        # If there's a matching Effect for this job, register it
        # (you must register your job effects in EffectRegistry under the same id)
        if EffectRegistry._registry.get(job_id):
            actor.stat_bonus_ids.append(job_id)

        emit(ON_JOB_ASSIGNED, actor=actor, job_id=job_id)