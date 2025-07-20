# game_sys/effects/extensions.py

from typing import Any
from game_sys.effects.base import Effect
from game_sys.config.feature_flags import FeatureFlags
from game_sys.logging import effects_logger, log_exception

flags = FeatureFlags()

class HealEffect(Effect):
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        # Async extensibility: pre-apply hook
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)

        # Default: call sync apply
        result = self.apply(caster, target, combat_engine)

        # Async extensibility: post-apply hook
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)

        return result
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
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
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

    def modify_stat(self, base_stat: float, actor: Any, stat_name: str = None) -> float:
        if (self.id in getattr(actor, 'stat_bonus_ids', []) and 
            stat_name == self.stat):  # Only modify the target stat
            new_value = base_stat + self.amount
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
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
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

    def modify_stat(self, base_stat: float, actor: Any, stat_name: str = None) -> float:
        if self.id in getattr(actor, 'stat_bonus_ids', []) and stat_name == self.stat:
            stat_name = stat_name or self.stat
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
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
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
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
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

    def modify_stat(self, current: float, actor: Any, stat_name: str = None) -> float:
        if self.id in getattr(actor, 'stat_bonus_ids', []) and stat_name == self.stat_name:
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


class InstantManaEffect(Effect):
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
    """
    Instantly restores mana to the target.
    """
    def __init__(self, amount: float, **kwargs):
        super().__init__(id=f"instant_mana_{amount}")
        self.amount = amount
        effects_logger.debug(f"Created InstantManaEffect with amount: {amount}")

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if not hasattr(target, 'current_mana') or not hasattr(target, 'max_mana'):
            effects_logger.warning(
                f"Cannot restore mana to target {target}, missing mana attributes"
            )
            return "Cannot restore mana to target"
            
        old_mana = target.current_mana
        target.current_mana = min(
            target.max_mana,
            target.current_mana + self.amount
        )
        actual_restore = target.current_mana - old_mana
        
        effects_logger.info(
            f"Restored mana to {target.name} for {actual_restore}/{self.amount} " 
            f"({target.current_mana}/{target.max_mana})"
        )
        return f"Restored {actual_restore} mana"
    
class InstantStaminaEffect(Effect):
    def __init__(self, amount: float, **kwargs):
        super().__init__(id=f"instant_stamina_{amount}")
        self.amount = amount
        effects_logger.debug(f"Created InstantStaminaEffect with amount: {amount}")

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if not hasattr(target, 'current_stamina') or not hasattr(target, 'max_stamina'):
            effects_logger.warning(
                f"Cannot restore stamina to target {target}, missing stamina attributes"
            )
            return "Cannot restore stamina to target"
            
        old_stamina = target.current_stamina
        target.current_stamina = min(
            target.max_stamina,
            target.current_stamina + self.amount
        )
        actual_restore = target.current_stamina - old_stamina
        
        effects_logger.info(
            f"Restored stamina to {target.name} for {actual_restore}/{self.amount} " 
            f"({target.current_stamina}/{target.max_stamina})"
        )
        return f"Restored {actual_restore} stamina"

    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        return self.apply(caster, target, combat_engine)


class RestorationEffect(Effect):
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
    """
    Instantly restores all resources (health, mana and stamina) to the target.
    """
    def __init__(self, health_amount: float, mana_amount: float, stamina_amount: float, **kwargs):
        super().__init__(id=f"restoration_{health_amount}_{mana_amount}_{stamina_amount}")
        self.health_amount = health_amount
        self.mana_amount = mana_amount
        self.stamina_amount = stamina_amount
        effects_logger.debug(f"Created RestorationEffect with health: {health_amount}, mana: {mana_amount}, stamina: {stamina_amount}")

    @log_exception
    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        heal_effect = HealEffect(self.health_amount)
        mana_effect = InstantManaEffect(self.mana_amount)
        stamina_effect = InstantStaminaEffect(self.stamina_amount)
        heal_result = heal_effect.apply(caster, target, combat_engine)
        mana_result = mana_effect.apply(caster, target, combat_engine)
        stamina_result = stamina_effect.apply(caster, target, combat_engine)
        return f"{heal_result}; {mana_result}; {stamina_result}"

class ResourceDrainEffect(Effect):
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
    """
    Drains a resource (health, mana, stamina) from the target.
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


class EquipmentStatEffect(Effect):
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
    """
    Passive stat bonus from equipment. Always active when item is equipped.
    """
    def __init__(self, stat_name: str, amount: float, **kwargs):
        super().__init__(id=f"equipment_{stat_name}_{amount}")
        self.stat_name = stat_name
        self.amount = amount
        effects_logger.debug(
            f"Created EquipmentStatEffect: {stat_name} +{amount}"
        )

    def modify_stat(self, current: float, actor: Any, stat_being_computed: str = None) -> float:
        # Only modify the stat this effect is for
        if stat_being_computed == self.stat_name:
            return current + self.amount
        return current

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        # Equipment effects don't need explicit application
        return f"Equipment bonus: {self.stat_name} +{self.amount}"


class RegenerationEffect(Effect):
    async def apply_async(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        if hasattr(self, 'on_pre_apply_async') and callable(getattr(self, 'on_pre_apply_async')):
            await self.on_pre_apply_async(caster, target)
        result = self.apply(caster, target, combat_engine)
        if hasattr(self, 'on_post_apply_async') and callable(getattr(self, 'on_post_apply_async')):
            await self.on_post_apply_async(caster, target, result)
        return result
    """
    Passive regeneration effect that continuously restores a resource.
    """
    def __init__(self, resource: str, amount: float, **kwargs):
        super().__init__(id=f"regen_{resource}_{amount}")
        self.resource = resource
        self.amount = amount
        effects_logger.debug(
            f"Created RegenerationEffect: {resource} +{amount}/s"
        )

    def tick(self, actor: Any, dt: float) -> None:
        """Apply regeneration each tick."""
        attr = f"current_{self.resource}"
        max_attr = f"max_{self.resource}"
        
        if hasattr(actor, attr) and hasattr(actor, max_attr):
            current = getattr(actor, attr)
            maximum = getattr(actor, max_attr)
            
            # Apply regeneration
            new_value = min(maximum, current + self.amount * dt)
            setattr(actor, attr, new_value)
            
            if new_value > current:
                effects_logger.debug(
                    f"Regenerated {new_value - current:.2f} {self.resource} "
                    f"for {actor.name} ({new_value:.1f}/{maximum:.1f})"
                )

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        """Apply this regeneration effect to the target."""
        target.apply_status(self)
        return f"Applied {self.resource} regeneration"
