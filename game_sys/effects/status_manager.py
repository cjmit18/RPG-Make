# game_sys/effects/status_manager.py
"""
Module: game_sys.effects.status_manager

Manages expiration and periodic ticks of status effects applied to actors.
Integrates with AsyncTimeManager by providing a synchronous tick(dt) method.
"""
import asyncio
from typing import Any, List
from game_sys.hooks.hooks_setup import ON_STATUS_EXPIRED, emit


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

    def unregister_actor(self, actor: Any):
        """Unregister an actor, stopping status updates."""
        if actor in self.actors:
            self.actors.remove(actor)

    def tick(self, dt: float):
        """
        For each actor, advance each active StatusEffect instance,
        call its on_tick(), and expire it when time's up.
        """
        for actor in list(self.actors):
            to_remove = []
            for eid, (eff, remaining) in actor.active_statuses.items():
                # call on_tick first to include the final tick
                on_tick = getattr(eff, 'on_tick', None)
                if on_tick:
                    if asyncio.iscoroutinefunction(on_tick):
                        asyncio.create_task(on_tick(actor, dt))
                    else:
                        on_tick(actor, dt)
                # decrease remaining duration
                new_remaining = remaining - dt
                if new_remaining <= 0:
                    to_remove.append(eid)
                else:
                    actor.active_statuses[eid] = (eff, new_remaining)

            # expire finished statuses
            for eid in to_remove:
                eff, _ = actor.active_statuses.pop(eid)
                emit(ON_STATUS_EXPIRED, actor=actor, status=eff.id)

# Global instance


status_manager = StatusEffectManager()
