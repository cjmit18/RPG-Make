# game_sys/skills/passive.py

import random
from typing import Any, Dict, List
from game_sys.effects.factory import EffectFactory

class Passive:
    """
    Represents a passive ability that listens for named events
    and applies one or more effects when triggered.
    """

    def __init__(self, pid: str, name: str, description: str, triggers: List[Dict]):
        self.id          = pid
        self.name        = name
        self.description = description
        self.triggers    = triggers  # list of { event, chance?, effects }

    def try_trigger(self, event_name: str, **ctx: Any) -> None:
        """
        Called by the hook system when any event fires.
        For each trigger matching event_name:
          - roll optional chance
          - instantiate and apply each effect
        """
        caster = ctx.get("actor") or ctx.get("source")
        for trig in self.triggers:
            raw_evt = trig.get("event", "")
            # normalize JSON event name (strip 'on_' prefix)
            if raw_evt.startswith("on_"):
                trig_evt = raw_evt[3:]
            else:
                trig_evt = raw_evt
            # map 'spawn' to 'character_created'
            if trig_evt == "spawn":
                trig_evt = "character_created"
            if trig_evt != event_name:
                continue
            # optional probability check
            if "chance" in trig and random.random() > trig["chance"]:
                continue
            # apply each effect in that trigger
            for defn in trig.get("effects", []):
                eff = EffectFactory.create(defn)
                target = ctx.get("target") or caster
                eff.apply(caster, target)
