# game_sys/character/actor.py

"""
Defines the Actor class, representing any entity with stats, inventory,
status effects, and combat interactions (players, NPCs, enemies, etc.).
Refactored to delegate leveling and stat growth to StatsManager, with
inline handling of resources, statuses, and damage application until
their respective managers are implemented.
"""

from typing import Any, Dict, List, Optional, Type
from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.core.hooks import hook_dispatcher
from game_sys.inventory.inventory import Inventory
from game_sys.items.item_base import EquipableItem
from game_sys.effects.status import StatusEffect



# StatsManager handles all stat calculations and modifiers:
from game_sys.managers.stats_manager import StatsManager, Stats

log = get_logger(__name__)


class Actor:
    """
    Base class for all actors (Player, Enemy, NPC).
    Delegates leveling, stats, and XP to StatsManager. All other subsystems
    (resources, statuses, combat, jobs, equipment) remain inline until
    their managers are added.
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

        # Stats & leveling
        self.stats_mgr = StatsManager(self)
        self.stats_mgr.levels.lvl = level
        self.stats_mgr.levels.experience = experience
        self.stats_mgr.stats = self.stats_mgr.calculate_stats()

        # Inventory
        self.inventory = Inventory(self)
        # Equip/unequip hooks to update stats when equipment changes
        hook_dispatcher.register('inventory.equip', self._on_item_equipped)
        hook_dispatcher.register('inventory.unequip', self._on_item_unequipped)

        # Status effects (inline)
        self.statuses: Dict[str, StatusEffect] = {}
        self.defending = False

        # Weakness & resistance maps
        self.weakness = weakness or {}
        self.resistance = resistance or {}

        # Gold
        self.gold = gold or 0

        # Initialize private resource fields
        self._current_health = self.max_health
        self._current_mana = self.max_mana
        self._current_stamina = self.max_stamina

        # Auto-assign default job if provided
        if job_class:
            self.assign_job_by_id(job_class.__name__.lower())

        hook_dispatcher.fire("character.created", actor=self)

    # ——————————————————————————————————————————————
    # Facade Properties for Level, XP, and Stats
    # ——————————————————————————————————————————————
    @property
    def level(self) -> int:
        return self.stats_mgr.levels.lvl

    @property
    def experience(self) -> int:
        return self.stats_mgr.levels.experience

    @property
    def stats(self) -> Stats:
        return self.stats_mgr.stats

    # ——————————————————————————————————————————————
    # Resource Properties for current/max HP, MP, ST
    # ——————————————————————————————————————————————
    @property
    def current_health(self) -> int:
        return self._current_health

    @current_health.setter
    def current_health(self, value: int):
        self._current_health = max(0, min(value, self.max_health))

    @property
    def max_health(self) -> int:
        return self.stats.effective().get("health", 0)

    @property
    def current_mana(self) -> int:
        return self._current_mana

    @current_mana.setter
    def current_mana(self, value: int):
        self._current_mana = max(0, min(value, self.max_mana))

    @property
    def max_mana(self) -> int:
        return self.stats.effective().get("mana", 0)

    @property
    def current_stamina(self) -> int:
        return self._current_stamina

    @current_stamina.setter
    def current_stamina(self, value: int):
        self._current_stamina = max(0, min(value, self.max_stamina))

    @property
    def max_stamina(self) -> int:
        return self.stats.effective().get("stamina", 0)

    # ——————————————————————————————————————————————
    # Status Methods (inline)
    # ——————————————————————————————————————————————
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
        for effect in list(self.status_effects):
            effect.tick()
            hook_dispatcher.fire("actor.status_ticked", actor=self, effect=effect)
            if effect.is_expired():
                expired.append(effect.name)
        for name in expired:
            expired_eff = self.statuses.pop(name)
            log.info("%s's status '%s' has expired.", self.name, name)
            hook_dispatcher.fire("actor.status_expired", actor=self, effect=expired_eff)

    def tick(self) -> None:
        """Advance one turn of all statuses."""
        self.tick_statuses()

    # ——————————————————————————————————————————————
    # Damage Helpers and Combat Methods
    # ——————————————————————————————————————————————
    def _resistance_multiplier(self, damage_type: Optional[DamageType]) -> float:
        if not damage_type:
            return 1.0
        return self.resistance.get(damage_type, 1.0) * self.weakness.get(damage_type, 1.0)

    def _apply_damage(self, raw: int, damage_type: Optional[DamageType]) -> int:
        amt = int(raw * self._resistance_multiplier(damage_type))
        if self.defending:
            amt //= 2
            self.defending = False
        self.current_health -= amt
        return amt

    def take_damage(
        self,
        amount: int,
        damage_type: Optional[DamageType] = None
    ) -> None:
        hook_dispatcher.fire(
            "actor.before_damage",
            actor=self,
            amount=amount,
            damage_type=damage_type
        )
        dealt = self._apply_damage(amount, damage_type)
        log.info(
            "%s takes %d %sdamage; HP is now %d/%d.",
            self.name,
            dealt,
            f"({damage_type.name}) " if damage_type else "",
            self.current_health,
            self.max_health
        )
        hook_dispatcher.fire(
            "actor.after_damage",
            actor=self,
            amount=dealt,
            damage_type=damage_type
        )

    # ——————————————————————————————————————————————
    # Resource Methods (inline)
    # ——————————————————————————————————————————————
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

    # ——————————————————————————————————————————————
    # Stat Facade (attack, defense, speed)
    # ——————————————————————————————————————————————
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

    # ——————————————————————————————————————————————
    # Inventory & Equipment (inline)
    # ——————————————————————————————————————————————
    def equip_item(self, item: EquipableItem) -> None:
        self.inventory.equip_item(item)

    def unequip_item(self, slot: str) -> None:
        self.inventory.unequip_item(slot)

    # ——————————————————————————————————————————————
    # Job Methods (inline)
    # ——————————————————————————————————————————————
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
        self.stats_mgr.assign_job("")  # resets to no-job defaults
        self.restore_all()
        hook_dispatcher.fire("character.job_removed", actor=self, old_job=old)

    # Equipment hook handlers: only add/remove modifiers, no full recalculation
    def _on_item_equipped(self, inventory: Inventory, slot: str, item: EquipableItem) -> None:
        """Handler for when an item is equipped: adds its bonuses to stats."""
        for stat_name, amount in item.bonuses.items():
            self.stats_mgr.stats.add_modifier(item.id, stat_name, amount)
        for ench in item.enchantments:
            ench.apply(self, item)
        hook_dispatcher.fire("actor.stats_updated", actor=self)

    def _on_item_unequipped(self, inventory: Inventory, slot: str, item: EquipableItem) -> None:
        """Handler for when an item is unequipped: removes its modifiers from stats."""
        self.stats_mgr.stats.remove_modifier(item.id)
        for ench in item.enchantments:
            ench.remove(self, item)
        hook_dispatcher.fire("actor.stats_updated", actor=self)
