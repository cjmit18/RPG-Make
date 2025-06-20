# game_sys/effects/passives/lifesteal.py
from logs.logs import get_logger
from game_sys.hooks.hooks import hook_dispatcher
from game_sys.effects.base import Effect
import math

log = get_logger(__name__)


class LifeStealPassive(Effect):
    def __init__(self, percent: float):
        self.pct = percent / 100.0
        self.handle = None

    @classmethod
    def from_dict(cls, data):
        return cls(percent=data.get("percent", 0.0))
    
    def apply(
        self,
        caster,
        target,
        combat_engine=None
    ) -> str:
        """
        Passive effect: lifesteal is handled via hooks on damage.
        No direct application.
        """
        return ""

    def register(self, actor):
        def _handler(effect, caster, target, result, **kwargs):
            if caster is actor and isinstance(result, dict):
                dmg = result.get("damage", 0)
                if dmg > 0:
                    heal_amt = max(1, math.ceil(dmg * self.pct))
                    actor.heal(heal_amt)
                    log.info(
                        "%s heals for %d HP from lifesteal.",
                        actor.name,
                        heal_amt
                    )
        self.handle = hook_dispatcher.register("effect.after_apply", _handler)

    def unregister(self, actor):
        hook_dispatcher.unregister("effect.after_apply", self.handle)
