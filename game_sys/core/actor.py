# game_sys/core/actor.py

from typing import Any, Dict, List, Optional, Type
from logs.logs import get_logger

from game_sys.inventory.inventory import Inventory
from game_sys.core.experience_functions import Levels
from game_sys.core.stats import Stats
from game_sys.items.item_base import Equipable
from game_sys.combat.status import StatusEffect

log = get_logger(__name__)


class Actor:
    """
    Base class for all actors (Player, Enemy, NPC).
    Each Actor has:
      - name (str)
      - levels (Levels): handles XP and leveling
      - job (optional): assigned via assign_job_by_id()
      - stats (Stats): base and derived stats
      - current_health, current_mana, current_stamina
      - inventory (Inventory)
      - statuses (active StatusEffect objects)
    """

    def __init__(
        self,
        name: str,
        level: int = 1,
        experience: int = 0,
        job_class: Optional[Type[Any]] = None,
    ) -> None:
        self.name: str = name

        # 1) Levels and experience tracker
        self.levels: Levels = Levels(self, level, experience)

        # 2) Placeholder for job (assigned later if job_class provided)
        self.job: Optional[Any] = None

        # 3) Stats object: initialize all keys to zero
        zeroed = {stat: 0 for stat in self._all_job_stats_keys()}
        self.stats: Stats = Stats(zeroed)

        # 4) Current resources
        self.current_health: int = 0
        self.current_mana: int = 0
        self.current_stamina: int = 0

        # 5) Inventory (manages items, equipment, consumables)
        self.inventory: Inventory = Inventory(self)

        # 6) Active status effects
        self.statuses: Dict[str, StatusEffect] = {}

        # 7) If a job_class was specified, assign it now
        if job_class:
            self.assign_job_by_id(job_class.__name__.lower())

    @staticmethod
    def _all_job_stats_keys() -> List[str]:
        """
        Return all valid stat keys from Job.base_stats. Uses a lazy import
        to avoid circular dependencies.
        """
        try:
            from game_sys.jobs.base import Job
            return list(Job.base_stats.keys())
        except ImportError:
            return []

    @property
    def status_effects(self) -> List[StatusEffect]:
        return list(self.statuses.values())

    # ------------------------------------------------------------------------
    # 1) Status & Damage Helpers
    # ------------------------------------------------------------------------
    def add_status(self, status_obj: StatusEffect) -> None:
        """
        Attach a new StatusEffect to this actor. Logs the applied modifiers and duration.
        """
        self.statuses[status_obj.name] = status_obj
        mods = status_obj.stat_mods
        dur = status_obj.duration
        log.info(
            "%s gains status '%s' (mods=%s) for %d turns.",
            self.name,
            status_obj.name,
            mods,
            dur,
        )

    def tick_statuses(self) -> None:
        """
        Called once per turn: decrement each effect's duration by 1.
        If any expire, remove them and call on_expire() if defined.
        """
        expired: List[str] = []

        for name, effect in list(self.statuses.items()):
            effect.tick()
            if effect.is_expired():
                expired.append(name)

        for name in expired:
            effect = self.statuses.pop(name)
            try:
                effect.on_expire(self)
            except AttributeError:
                pass
            log.info("%s's status '%s' has expired.", self.name, name)

    def take_damage(self, amount: int) -> None:
        """
        Reduce current_health by 'amount', clamped at 0. If reduced to 0, log defeat.
        """
        # Check for DamageReduction status
        dr_effect = self.statuses.get("DamageReduction")
        if dr_effect:
            reduction_pct = dr_effect.stat_mods.get("DamageReduction", 0)
            reduced_amount = amount * (100 - reduction_pct) // 100
            log.info(
                "%s's DamageReduction (%d%%) reduces incoming from %d to %d.",
                self.name,
                reduction_pct,
                amount,
                reduced_amount,
            )
            amount = reduced_amount

        self.current_health = max(0, self.current_health - amount)
        log.info(
            "%s takes %d damage; HP is now %d/%d.",
            self.name,
            amount,
            self.current_health,
            self.max_health,
        )

        if self.current_health == 0:
            log.info("%s has been defeated!", self.name)

    def heal(self, amount: int) -> None:
        """
        Increase current_health by 'amount', clamped at max_health.
        """
        old_hp = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        healed_amt = self.current_health - old_hp
        log.info(
            "%s heals %d HP; HP is now %d/%d.",
            self.name,
            healed_amt,
            self.current_health,
            self.max_health,
        )

    # ------------------------------------------------------------------------
    # 2) Resource Restoration & Stat Placeholder
    # ------------------------------------------------------------------------
    def restore_all(self) -> None:
        """
        Restore health, mana, and stamina to their max values based on stats.effective().
        """
        eff = self.stats.effective()
        self.current_health = eff.get("health", self.current_health)
        self.current_mana = eff.get("mana", self.current_mana)
        self.current_stamina = eff.get("stamina", self.current_stamina)
        log.info(
            "%s restores to HP=%d, MP=%d, ST=%d.",
            self.name,
            self.current_health,
            self.current_mana,
            self.current_stamina,
        )

    def update_stats(self) -> None:
        """
        Recalculate derived stats (e.g., after leveling or equipment change).
        Subclasses may override this.
        """
        pass

    # ------------------------------------------------------------------------
    # 3) Stat Properties (base + status modifiers)
    # ------------------------------------------------------------------------
    @property
    def attack(self) -> int:
        base = self.stats.effective().get("attack", 0)
        bonus = sum(
            mods.get("attack", 0)
            for mods in (e.stat_mods for e in self.status_effects)
        )
        return base + bonus

    @property
    def defense(self) -> int:
        base = self.stats.effective().get("defense", 0)
        bonus = sum(
            mods.get("defense", 0)
            for mods in (e.stat_mods for e in self.status_effects)
        )
        return base + bonus

    @property
    def speed(self) -> int:
        base = self.stats.effective().get("speed", 0)
        bonus = sum(
            mods.get("speed", 0)
            for mods in (e.stat_mods for e in self.status_effects)
        )
        return base + bonus

    @property
    def max_health(self) -> int:
        return self.stats.effective().get("health", 0)

    @property
    def health(self) -> int:
        return self.current_health

    @health.setter
    def health(self, value: int) -> None:
        self.current_health = max(0, min(value, self.max_health))

    @property
    def max_mana(self) -> int:
        return self.stats.effective().get("mana", 0)

    @property
    def mana(self) -> int:
        return self.current_mana

    @mana.setter
    def mana(self, value: int) -> None:
        self.current_mana = max(0, min(value, self.max_mana))

    @property
    def max_stamina(self) -> int:
        return self.stats.effective().get("stamina", 0)

    @property
    def stamina(self) -> int:
        return self.current_stamina

    @stamina.setter
    def stamina(self, value: int) -> None:
        self.current_stamina = max(0, min(value, self.max_stamina))

    # ------------------------------------------------------------------------
    # 4) Job Initialization & Helpers
    # ------------------------------------------------------------------------
    def assign_job_by_id(self, job_id: str) -> None:
        """
        Assign a job by its string ID (e.g., 'knight', 'mage').
        Uses lazy imports to avoid circular dependencies.
        """
        from game_sys.jobs.factory import create_job
        from game_sys.jobs.base import Job

        try:
            self.job = create_job(job_id, self.levels.lvl)
            log.info("%s assigned job '%s'.", self.name, job_id)
        except Exception as e:
            self.job = None
            log.warning("Failed to assign job '%s' to %s: %s", job_id, self.name, e)
            return

        # 1) Overwrite stats with this job’s base stats (defaulting missing keys to 0)
        base_stats = getattr(self.job, "base_stats", {})
        all_stats = {stat: base_stats.get(stat, 0) for stat in Job.base_stats.keys()}
        self.stats = Stats(all_stats)

        # 2) Restore resources
        self.restore_all()

        # 3) Auto-equip any starting_items
        for item_obj in getattr(self.job, "starting_items", []):
            self.inventory.add_item(item_obj, quantity=1)
            if isinstance(item_obj, Equipable):
                self.inventory.equip_item(item_obj.id)

    def remove_job(self) -> None:
        """
        Remove the current job’s starting items, clear job, zero out stats,
        and reset current resources.
        """
        if not self.job:
            return

        from game_sys.jobs.base import Job

        old_job = self.job

        # 1) Unequip & remove all of old_job’s starting_items
        for item_obj in getattr(old_job, "starting_items", []):
            for slot, equipped_id in list(self.inventory._equipped_items.items()):
                if equipped_id == item_obj.id:
                    self.inventory.unequip_item(slot)
            entry = self.inventory._items.get(item_obj.id)
            if entry:
                try:
                    self.inventory.remove_item(item_obj.id, quantity=entry["quantity"])
                except KeyError:
                    pass

        # 2) Clear job reference
        self.job = None

        # 3) Zero out all base stats
        zeroed = {stat: 0 for stat in Job.base_stats.keys()}
        self.stats = Stats(zeroed)

        # 4) Reset current resources to match zeroed stats
        self.restore_all()
