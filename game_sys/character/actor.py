# game_sys/character/actor.py

from typing import Any, Dict, List, Optional, Type
from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.hooks.hooks import hook_dispatcher
from game_sys.inventory.inventory import Inventory
from game_sys.items.item_base import EquipableItem
from game_sys.effects.status import StatusEffect, Effect
from game_sys.managers.stats_manager import StatsManager, Stats

log = get_logger(__name__)


class Actor:
    """
    Base class for all actors (Player, Enemy, NPC).
    Handles leveling, stats, resistances, statuses, and equipment.
    """

    def __init__(
        self,
        name: str,
        gold: Optional[int] = None,
        level: int = 1,
        experience: int = 0,
        job_class: Optional[Type[Any]] = None,
        weakness: Optional[Dict[DamageType, float]] = None,
        resistance: Optional[Dict[DamageType, float]] = None,
    ) -> None:
        self.name = name
        self.stats_mgr = StatsManager(self)
        self.stats_mgr.levels.lvl = level
        self.stats_mgr.levels.experience = experience
        self.stats_mgr.stats = self.stats_mgr.calculate_stats()

        # Inventory and equip/unequip hooks
        self.inventory = Inventory(self)
        hook_dispatcher.register("inventory.equip", self._on_item_equipped)
        hook_dispatcher.register("inventory.unequip", self._on_item_unequipped)

        # Status effects and defending state
        self.statuses: Dict[str, StatusEffect] = {}
        self.passive_effects: Dict[str, Effect] = {}
        self.defending = False

        # Base resistances/weakness
        self.weakness = weakness or {}
        self.resistance = resistance or {}

        # Resources
        self.gold = gold or 0
        self._current_health = self.max_health
        self._current_mana = self.max_mana
        self._current_stamina = self.max_stamina

        # Assign job if provided
        if job_class:
            self.assign_job_by_id(job_class.__name__.lower())

        hook_dispatcher.fire("character.created", actor=self)

    @property
    def level(self) -> int:
        return self.stats_mgr.levels.lvl

    @property
    def experience(self) -> int:
        return self.stats_mgr.levels.experience

    @property
    def stats(self) -> Stats:
        return self.stats_mgr.stats

    @property
    def max_health(self) -> int:
        return self.stats.effective().get("health", 0)

    @property
    def max_mana(self) -> int:
        return self.stats.effective().get("mana", 0)

    @property
    def max_stamina(self) -> int:
        return self.stats.effective().get("stamina", 0)

    @property
    def current_health(self) -> int:
        return self._current_health

    @current_health.setter
    def current_health(self, value: int):
        self._current_health = max(0, min(value, self.max_health))

    @property
    def current_mana(self) -> int:
        return self._current_mana

    @current_mana.setter
    def current_mana(self, value: int):
        self._current_mana = max(0, min(value, self.max_mana))

    @property
    def current_stamina(self) -> int:
        return self._current_stamina

    @current_stamina.setter
    def current_stamina(self, value: int):
        self._current_stamina = max(0, min(value, self.max_stamina))

    @property
    def status_effects(self) -> List[StatusEffect]:
        return list(self.statuses.values())

    def add_status(self, status_obj: StatusEffect) -> None:
        self.statuses[status_obj.name] = status_obj
        log.info(
            "%s gains status '%s' for %d turns.",
            self.name, status_obj.name, status_obj.duration
        )
        hook_dispatcher.fire("actor.status_added", actor=self, effect=status_obj)

    def tick_statuses(self) -> None:
        expired: List[str] = []
        for eff in list(self.status_effects):
            eff.tick()
            hook_dispatcher.fire("actor.status_ticked", actor=self, effect=eff)
            if eff.is_expired():
                expired.append(eff.name)
        for name in expired:
            old = self.statuses.pop(name)
            log.info("%s's status '%s' has expired.", self.name, name)
            hook_dispatcher.fire("actor.status_expired", actor=self, effect=old)

    def start_turn(self) -> None:
        self.defending = False

    def log_turn_summary(self) -> None:
        log.info(
            "%s — HP: %d/%d, MP: %d, ST: %d, Gold: %d", 
            self.name,
            self.current_health, self.max_health,
            self.current_mana, self.current_stamina,
            self.gold
        )

    def _resistance_multiplier(self, damage_type: Optional[DamageType]) -> float:
        base = self.resistance.get(damage_type, 1.0) * self.weakness.get(damage_type, 1.0)
        item_res = sum(
            float(itm.resistances.get(damage_type if damage_type is not None else DamageType.DEFAULT, 0.0))
            for itm in self.inventory.equipped_items.values()
        )
        item_res = min(item_res, 0.75)
        status_res = sum(
            status.stat_mods.get("DamageReduction", 0) / 100.0
            for status in self.statuses.values()
        )
        status_res = min(status_res, 0.75)
        total = min(item_res + status_res, 0.75)
        return base * (1.0 - total)

    def _apply_damage(self, raw: int, damage_type: Optional[DamageType]) -> int:
        amt = int(round(raw * self._resistance_multiplier(damage_type)))
        if self.defending:
            amt //= 2
            self.defending = False
        before = self.current_health
        self.current_health -= amt
        return before - self.current_health

    def take_damage(
        self,
        amount: int,
        damage_type: Optional[DamageType] = None
    ) -> None:
        hook_dispatcher.fire("actor.before_damage", actor=self, amount=amount, damage_type=damage_type)
        lost = self._apply_damage(amount, damage_type)
        log.info(
            "%s takes %d %sdamage; HP now %d/%d.",
            self.name,
            lost,
            f"({damage_type.name}) " if damage_type else "",
            self.current_health,
            self.max_health
        )
        hook_dispatcher.fire("actor.after_damage", actor=self, amount=lost, damage_type=damage_type)

    def heal(self, amount: int) -> None:
        old = self.current_health
        self.current_health += amount
        healed = self.current_health - old
        log.info("%s heals %d HP; now %d/%d.", self.name, healed, self.current_health, self.max_health)
        hook_dispatcher.fire("actor.healed", actor=self, amount=healed)

    def drain_mana(self, amount: int) -> None:
        old = self.current_mana
        self.current_mana -= amount
        drained = old - self.current_mana
        log.info("%s uses %d MP; now %d/%d.", self.name, drained, self.current_mana, self.max_mana)
        hook_dispatcher.fire("actor.mana_drained", actor=self, amount=drained)

    def restore_all(self) -> None:
        self.current_health = self.max_health
        self.current_mana = self.max_mana
        self.current_stamina = self.max_stamina
        log.info(
            "%s fully restored: HP=%d, MP=%d, ST=%d.",
            self.name, self.current_health, self.current_mana, self.current_stamina
        )
        hook_dispatcher.fire("actor.restored_all", actor=self)

    def _on_item_equipped(
        self, inventory: Inventory, slot: str, item: EquipableItem
    ) -> None:
        # preserve full resource states
        full_hp = self.current_health >= self.max_health
        full_mp = self.current_mana >= self.max_mana
        full_st = self.current_stamina >= self.max_stamina

        # apply stat bonuses
        for stat, val in item.bonuses.items():
            self.stats_mgr.stats.add_modifier(item.id, stat, val)
        # apply enchantments
        for ench in item.enchantments:
            ench.apply(self, item)
        hook_dispatcher.fire("actor.stats_updated", actor=self)

        # restore preserved resources
        if full_hp and full_mp and full_st:
            self.restore_all()
        else:
            if full_hp:
                self.current_health = self.max_health
            if full_mp:
                self.current_mana = self.max_mana
            if full_st:
                self.current_stamina = self.max_stamina

    def _on_item_unequipped(
        self, inventory: Inventory, slot: str, item: EquipableItem
    ) -> None:
        # remove stat bonuses
        self.stats_mgr.stats.remove_modifier(item.id)
        # remove enchantments
        for ench in item.enchantments:
            ench.remove(self, item)
        hook_dispatcher.fire("actor.stats_updated", actor=self)

    @property
    def attack(self) -> int:
        return self.stats.effective().get("attack", 0)

    @property
    def defense(self) -> int:
        return self.stats.effective().get("defense", 0)

    @property
    def speed(self) -> int:
        return self.stats.effective().get("speed", 0)

    @property
    def intellect(self) -> int:
        return self.stats.effective().get("intellect", 0)

    @property
    def magic_attack(self) -> int:
        return self.stats.effective().get("magic_attack", 0)

    def equip_item(self, item: EquipableItem) -> None:
        self.inventory.equip_item(item)

    def unequip_item(self, slot: str) -> None:
        self.inventory.unequip_item(slot)

    def assign_job_by_id(self, job_id: str) -> None:
        old = getattr(self, "job", None)
        from game_sys.jobs.factory import create_job
        self.job = create_job(job_id)
        log.info("%s assigned job '%s'.", self.name, job_id)
        self.stats_mgr.assign_job(job_id)
        self.restore_all()
        hook_dispatcher.fire("character.job_changed", actor=self, old_job=old, new_job=self.job)

    def remove_job(self) -> None:
        old = getattr(self, "job", None)
        self.job = None
        self.stats_mgr.assign_job("")
        self.restore_all()
        hook_dispatcher.fire("character.job_removed", actor=self, old_job=old)
