# game_sys/skills/passive_manager.py

from typing import Any, Callable
from game_sys.hooks.hooks_setup import on, emit, ON_CHARACTER_CREATED
from game_sys.skills.passive_factory import PassiveFactory

class PassiveManager:
    """
    Subscribes each Actor’s passives to the event bus so they fire correctly.
    """

    @staticmethod
    def register_actor(actor: Any):
        for pid in getattr(actor, "passive_ids", []):
            passive = PassiveFactory.get(pid)
            if not passive:
                continue

            # For each trigger, subscribe a properly bound callback:
            for trig in passive.triggers:
                evt = trig["event"]
                # strip 'on_' prefix to match hook names
                if evt.startswith("on_"):
                    ev_name = evt[3:]
                else:
                    ev_name = evt
                # map spawn to character_created event
                if ev_name == "spawn":
                    ev_name = ON_CHARACTER_CREATED

                # Capture p and ev_name in defaults to avoid late binding:
                def make_cb(p=passive, ev=ev_name) -> Callable[..., Any]:
                    def _cb(**ctx):
                        p.try_trigger(ev, **ctx)
                    return _cb

                # register callback
                cb = make_cb()
                on(ev_name, cb)
