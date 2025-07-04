# game_sys/effects/extensions.py

from typing import Any
from game_sys.effects.base import Effect
from game_sys.config.feature_flags import FeatureFlags
from game_sys.logging import effects_logger, log_exception

flags = FeatureFlags()

class HealEffect(Effect):
    """
    Instantly restores health to the target.
    """
    def __init__(self, amount: float, **kwargs):
        super().__init__(id=f"heal_{amount}")
        self.amount = amount
        effects_logger.debug(f"Created HealEffect with amount: {amount}")

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if not hasattr(target, 'current_health') or not hasattr(target, 'max_health'):
            effects_logger.warning(
                f"Cannot heal target {target}, missing health attributes"
            )
            return "Cannot heal target"
            
        old_health = target.current_health
        target.current_health = min(
            target.max_health,
            target.current_health + self.amount
        )
        actual_heal = target.current_health - old_health
        
        effects_logger.info(
            f"Healed {target.name} for {actual_heal}/{self.amount} " 
            f"({target.current_health}/{target.max_health})"
        )
        return f"Healed for {actual_heal}"


class BuffEffect(Effect):
    """
    Applies a temporary stat bonus via a StatusEffect-like wrapper.
    """
    def __init__(self, stat: str, amount: float, duration: float, **kwargs):
        super().__init__(id=f"buff_{stat}_{amount}_{duration}")
        self.stat      = stat
        self.amount    = amount
        self.duration  = duration
        effects_logger.debug(
            f"Created BuffEffect: {stat} +{amount} for {duration}s"
        )

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if not hasattr(target, 'stat_bonus_ids'):
            effects_logger.debug(f"Initializing stat_bonus_ids for {target.name}")
            target.stat_bonus_ids = []
        
        target.stat_bonus_ids.append(self.id)
        target.apply_status(self)
        
        effects_logger.info(
            f"Applied buff to {target.name}: {self.stat} +{self.amount} "
            f"for {self.duration}s"
        )
        return f"Applied {self.stat} buff"

    def modify_stat(self, base_stat: float, actor: Any) -> float:
        if self.id in getattr(actor, 'stat_bonus_ids', []):
            new_value = base_stat + self.amount
            effects_logger.debug(
                f"BuffEffect: {actor.name} {self.stat} {base_stat} -> {new_value}"
            )
            return new_value
        return base_stat

    def tick(self, actor: Any, dt: float) -> None:
        self.duration -= dt
        effects_logger.debug(
            f"BuffEffect tick: {actor.name} {self.stat} buff remaining: {self.duration}s"
        )
        if self.duration <= 0 and self.id in actor.stat_bonus_ids:
            actor.stat_bonus_ids.remove(self.id)
            effects_logger.info(f"Buff expired: {self.stat} on {actor.name}")


class DebuffEffect(Effect):
    """
    Applies a negative stat modifier temporarily.
    """
    def __init__(self, stat: str, amount: float, duration: float, **kwargs):
        super().__init__(id=f"debuff_{stat}_{amount}_{duration}")
        self.stat     = stat
        self.amount   = amount
        self.duration = duration

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if not hasattr(target, 'stat_bonus_ids'):
            effects_logger.debug(f"Initializing stat_bonus_ids for {target.name}")
            target.stat_bonus_ids = []
            
        target.stat_bonus_ids.append(self.id)
        target.apply_status(self)
        
        effects_logger.info(
            f"Applied debuff to {target.name}: {self.stat} -{self.amount} "
            f"for {self.duration}s"
        )
        return f"Applied {self.stat} debuff"

    def modify_stat(self, base_stat: float, actor: Any) -> float:
        if self.id in getattr(actor, 'stat_bonus_ids', []):
            new_value = base_stat - self.amount
            effects_logger.debug(
                f"DebuffEffect: {actor.name} {self.stat} "
                f"{base_stat} -> {new_value}"
            )
            return new_value
        return base_stat

    def tick(self, actor: Any, dt: float) -> None:
        self.duration -= dt
        effects_logger.debug(
            f"DebuffEffect tick: {actor.name} {self.stat} "
            f"remaining: {self.duration}s"
        )
        if self.duration <= 0 and self.id in actor.stat_bonus_ids:
            actor.stat_bonus_ids.remove(self.id)
            effects_logger.info(f"Debuff expired: {self.stat} on {actor.name}")


class StatusEffect(Effect):
    """
    A generic status that ticks damage over time.
    """
    def __init__(self, name: str, duration: float, tick_damage: float, 
                 **kwargs):
        super().__init__(id=f"status_{name}_{duration}_{tick_damage}")
        self.name = name
        self.duration = duration
        self.tick_damage = tick_damage
        effects_logger.debug(
            f"Created StatusEffect: {name}, duration={duration}s, "
            f"tick_damage={tick_damage}"
        )

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        target.apply_status(self)
        effects_logger.info(
            f"Applied status {self.name} to {target.name} "
            f"(damage={self.tick_damage}/tick, duration={self.duration}s)"
        )
        return f"Applied {self.name} status"

    def tick(self, actor: Any, dt: float) -> None:
        # deal tick_damage each second
        damage = self.tick_damage * dt
        actor.take_damage(damage, None)
        effects_logger.debug(
            f"StatusEffect tick: {self.name} dealt {damage} damage to {actor.name}"
        )
        
        self.duration -= dt
        if self.duration <= 0:
            effects_logger.info(f"Status {self.name} expired on {actor.name}")
            actor.active_statuses.pop(self.id, None)


class StatBonusEffect(Effect):
    """
    Temporarily (or permanently, if duration=0) adds `amount` to a stat.
    Accepts JSON param 'stat' for compatibility.
    """
    def __init__(self, stat: str = None, stat_name: str = None, 
                 amount: float = 0.0, duration: float = 0.0, **kwargs):
        name = stat_name or stat
        super().__init__(id=f"stat_bonus_{name}_{amount}_{duration}")
        self.stat_name = name
        self.amount = amount
        self.duration = duration
        effects_logger.debug(
            f"Created StatBonusEffect: {name} +{amount} "
            f"for {duration}s"
        )

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if not hasattr(target, 'stat_bonus_ids'):
            effects_logger.debug(f"Creating stat_bonus_ids for {target.name}")
            target.stat_bonus_ids = []
            
        target.stat_bonus_ids.append(self.id)
        target.apply_status(self)
        
        effects_logger.info(
            f"Applied stat bonus to {target.name}: {self.stat_name} +{self.amount}"
        )
        return f"Applied {self.stat_name} bonus"

    def modify_stat(self, current: float, actor: Any) -> float:
        if self.id in getattr(actor, 'stat_bonus_ids', []):
            return current + self.amount
        return current

    def tick(self, actor: Any, dt: float) -> None:
        if self.duration == 0:
            # Permanent effect, don't tick down
            return
            
        self.duration -= dt
        effects_logger.debug(
            f"StatBonus tick: {actor.name} {self.stat_name} "
            f"remaining: {self.duration}s"
        )
        
        if self.duration <= 0 and self.id in actor.stat_bonus_ids:
            actor.stat_bonus_ids.remove(self.id)
            effects_logger.info(
                f"Stat bonus expired: {self.stat_name} on {actor.name}"
            )


class ResourceDrainEffect(Effect):
    """
    Drains a named resource (mana/stamina/health) at `rate` per second.
    """

    def __init__(self, resource: str, rate: float, duration: float):
        super().__init__(id=f"resource_drain_{resource}_{rate}_{duration}")
        self.resource = resource
        self.rate = rate
        self.duration = duration
        effects_logger.debug(
            f"Created ResourceDrainEffect: {resource} at rate={rate}/s "
            f"for {duration}s"
        )

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        target.apply_status(self)
        effects_logger.info(
            f"Applied resource drain to {target.name}: "
            f"{self.resource} at {self.rate}/s"
        )
        return f"Applied {self.resource} drain"

    def tick(self, actor: Any, dt: float) -> None:
        attr = f"current_{self.resource}"
        if hasattr(actor, attr):
            cur = getattr(actor, attr)
            new_value = max(0.0, cur - self.rate * dt)
            setattr(actor, attr, new_value)
            
            effects_logger.debug(
                f"ResourceDrain tick: {actor.name} {self.resource} "
                f"{cur} -> {new_value} (drained {cur - new_value})"
            )
            
        self.duration -= dt
        if self.duration <= 0:
            effects_logger.info(
                f"Resource drain expired: {self.resource} on {actor.name}"
            )
            actor.active_statuses.pop(self.id, None)
