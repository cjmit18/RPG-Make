# game_sys/effects/status_manager.py
"""
Module: game_sys.effects.status_manager

Manages expiration and periodic ticks of status effects applied to actors.
Integrates with AsyncTimeManager by providing a synchronous tick(dt) method.
"""
import asyncio
from typing import Any, List
from game_sys.hooks.hooks_setup import ON_STATUS_EXPIRED, emit
from game_sys.logging import effects_logger


class StatusEffectManager:
    """
    Handles tick updates for all registered actors' status effects.
    """
    def __init__(self):
        # We no longer import Actor here to avoid circular dependencies
        self.actors: List[Any] = []

    def register_actor(self, actor: Any):
        """Register an actor to have its statuses updated each tick."""
        if actor not in self.actors:
            self.actors.append(actor)
            effects_logger.debug(f"Registered actor {actor.name} with StatusEffectManager")

    def unregister_actor(self, actor: Any):
        """Unregister an actor, stopping status updates."""
        if actor in self.actors:
            self.actors.remove(actor)
            effects_logger.debug(f"Unregistered actor {actor.name} from StatusEffectManager")

    def tick(self, dt: float):
        """
        For each actor, advance each active StatusEffect instance,
        call its on_tick(), and expire it when time's up.
        """
        for actor in list(self.actors):
            to_remove = []
            for eid, (eff, remaining) in list(actor.active_statuses.items()):
                # call tick method on effect if defined
                tick_fn = getattr(eff, 'tick', None)
                if tick_fn:
                    try:
                        tick_fn(actor, dt)
                    except Exception as e:
                        effects_logger.error(f"Error ticking effect {eid} on {actor.name}: {e}")
                # compute remaining duration
                new_remaining = remaining - dt
                # permanent buff if effect.duration == 0
                is_permanent = getattr(eff, 'duration', None) == 0
                if new_remaining <= 0:
                    if not is_permanent:
                        to_remove.append(eid)
                        effects_logger.debug(f"Effect {eid} expired on {actor.name}")
                    # else permanent: keep alive without updating remaining
                else:
                    actor.active_statuses[eid] = (eff, new_remaining)

            # expire finished statuses
            for eid in to_remove:
                eff, _ = actor.active_statuses.pop(eid)
                effects_logger.info(f"Removed effect {eid} from {actor.name}")
                emit(ON_STATUS_EXPIRED, actor=actor, status=eff.id)

# Global instance


status_manager = StatusEffectManager()
