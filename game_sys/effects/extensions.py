# game_sys/effects/extensions.py
"""
Module: game_sys.effects.extensions

Additional concrete Effect implementations:
- HealEffect: restores health to the target.
- BuffEffect: temporarily increases a stat for a duration.
- DebuffEffect: temporarily decreases a stat for a duration.
- StatusEffect: generic status application (e.g., stun, poison over time).
"""
from typing import Any, Optional
from game_sys.effects.base import Effect
from game_sys.hooks.hooks_setup import emit, ON_STATUS_APPLIED


class HealEffect(Effect):
    """
    Restores a flat amount of health to the target actor.
    Params:
        amount (float): Flat health to restore.
    """
    def __init__(self, amount: float):
        super().__init__(id=f"heal_{amount}")
        self.amount = amount

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        target.current_health = min(target.max_health, target.current_health + self.amount)
        return f"{target.name} healed for {self.amount} HP"


class InstantRestoreEffect(Effect):
    """
    Instantly restores a flat amount of selected resource (e.g., mana, stamina).
    Params:
        resource (str): Name of the resource to restore.
        amount (float): Flat amount to restore.
    """
    def __init__(self, resource: str, amount: float):
        super().__init__(id=f"restore_{resource}_{amount}")
        self.resource = resource
        self.amount = amount

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        # support resources named by 'health', 'mana', etc. mapping to current_<resource> and max_<resource>
        resource_attr = f"current_{self.resource}"
        max_attr = f"max_{self.resource}"
        if hasattr(target, resource_attr) and hasattr(target, max_attr):
            current_value = getattr(target, resource_attr)
            max_value = getattr(target, max_attr)
            setattr(target, resource_attr, min(max_value, current_value + self.amount))
            return f"{target.name} restored {self.amount} {self.resource}"
        return f"{target.name} has no resource '{self.resource}' to restore"


class BuffEffect(Effect):
    """
    Temporarily buffs a stat on the target.
    Params:
        stat (str): Name of the stat to buff.
        amount (float): Flat bonus to add.
        duration (float): Time in seconds the buff lasts.
    """
    def __init__(self, stat: str, amount: float, duration: float):
        super().__init__(id=f"buff_{stat}_{amount}_{duration}")
        self.stat = stat
        self.amount = amount
        self.duration = duration

    def modify_stat(self, base_stat: float, actor: Any) -> float:
        return base_stat + self.amount

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        target.apply_status(self)
        target.stat_bonus_ids.append(self.id)
        emit(ON_STATUS_APPLIED, actor=target, status=self.id)
        return f"{target.name} gains +{self.amount} {self.stat} for {self.duration}s"


class DebuffEffect(Effect):
    """
    Temporarily debuffs a stat on the target.
    Params:
        stat (str): Name of the stat to debuff.
        amount (float): Flat penalty to subtract.
        duration (float): Time in seconds the debuff lasts.
    """
    def __init__(self, stat: str, amount: float, duration: float):
        super().__init__(id=f"debuff_{stat}_{amount}_{duration}")
        self.stat = stat
        self.amount = -abs(amount)
        self.duration = duration

    def modify_stat(self, base_stat: float, actor: Any) -> float:
        return base_stat + self.amount

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        target.apply_status(self)
        target.stat_bonus_ids.append(self.id)
        emit(ON_STATUS_APPLIED, actor=target, status=self.id)
        return f"{target.name} suffers {abs(self.amount)} {self.stat} debuff for {self.duration}s"


class StatusEffect(Effect):
    """
    Generic status effect like 'stun' or 'poison'.
    Params:
        name (str): Status identifier.
        duration (float): Time in seconds.
        tick_damage (float, optional): Damage per tick for poison, else None.
    """
    def __init__(self, name: str, duration: float, tick_damage: Optional[float] = None):
        super().__init__(id=f"status_{name}_{duration}")
        self.name = name
        self.duration = duration
        self.tick_damage = tick_damage

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        target.apply_status(self)
        emit(ON_STATUS_APPLIED, actor=target, status=self.name)
        return f"{target.name} is afflicted with {self.name} for {self.duration}s"

    def on_tick(self, actor: Any, dt: float):
        if self.tick_damage:
            actor.take_damage(self.tick_damage * dt)


class StatBonusEffect(Effect):
    def __init__(self, stat: str = "", amount: float = 0.0):
        super().__init__(id=f"stat_bonus_{stat}_{amount}")
        self.stat = stat
        self.amount = amount

    def modify_stat(self, base_stat: float, actor: Any) -> float:
        return base_stat + self.amount
