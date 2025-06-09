# game_sys/core/actor.py

from typing import Any, Dict, List, Optional, Type
from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.inventory.inventory import Inventory
from game_sys.core.experience import Levels
from game_sys.core.stats import Stats
from game_sys.items.item_base import EquipableItem

log = get_logger(__name__)


class Actor:
    """
    Base class for all actors (Player, Enemy, NPC).
    Each Actor has:
      - name (str)
      - levels (Levels): handles XP and leveling
      - job (optional): assigned via assign_job_by_id()
      - stats (Stats): base and derived stats
      - current_health, current_mana, current_stamina (with max determined by stats)
      - inventory (Inventory)
      - statuses (active StatusEffect objects)
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
        self.name: str = name

        # 1) Levels and experience tracker
        self.levels: Levels = Levels(self, level, experience)

        # 2) Placeholder for job (assigned later if job_class provided)
        self.job: Optional[Any] = None

        # 3) Stats object: initialize all keys to zero (will be overwritten by job or remain zeros)
        zeroed = {stat: 0 for stat in self._all_job_stats_keys()}
        self.stats: Stats = Stats(zeroed)

        # 4) Current resources: these will be clamped via @property methods
        self.current_health: int = 0
        self.current_mana: int = 0
        self.current_stamina: int = 0

        # 5) Inventory (manages items, equipment, consumables)
        self.inventory: Inventory = Inventory(self)

        # 6) Active status effects (name → StatusEffect instance)
        self.statuses: Dict[str, Any] = {}

        # 7) Flag for defending this turn (halves incoming damage)
        self.defending: bool = False

        # 8) If a job_class was specified, assign it now
        if job_class:
            self.assign_job_by_id("commoner")

        # 9) Weaknesses & Resistances to damage types
        self.weakness: Dict[DamageType, float] = weakness or {}
        self.resistance: Dict[DamageType, float] = resistance or {}

        # 10) Gold or currency
        self.gold: int = gold or 0

        # 11) Initialize resources to max based on current (possibly zero) stats
        #     Subclasses/jobs will set stats and then call restore_all()
        self.restore_all()

    @staticmethod
    def _all_job_stats_keys() -> List[str]:
        """
        Return all valid stat keys from Job.base_stats.
        Uses a lazy import to avoid circular dependencies.
        """
        try:
            from game_sys.jobs.base import Job
            return list(Job.base_stats.keys())
        except ImportError:
            return []

    @property
    def status_effects(self) -> List[Any]:
        """
        Return a list of active StatusEffect instances.
        """
        return list(self.statuses.values())

    def add_status(self, status_obj: Any) -> None:
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

    def take_damage(self, amount: int, damage_type: Optional[DamageType] = None) -> None:
        """
        Apply incoming damage:
          - Adjust for weakness & resistance (combined)
          - Apply DamageReduction status
          - Halve if defending
          - Clamp at zero and log defeat
        """
        # 1) Weakness & Resistance
        if damage_type:
            resist = self.resistance.get(damage_type, 1.0)
            weak = self.weakness.get(damage_type, 1.0)
            multiplier = resist * weak
            original = amount
            amount = round(amount * multiplier)
            if  multiplier != 1.0:
                log.info(
                    "%s is hit with %s damage. Multiplier: %.2f× (from %d to %d)",
                    self.name, damage_type.name, multiplier, original, amount
            )
            else:
                log.info(
                    "%s is hit with %s damage.",
                    self.name, damage_type.name
                )

        # 2) DamageReduction effect
        dr_effect = self.statuses.get("DamageReduction")
        if dr_effect:
            reduction_pct = dr_effect.stat_mods.get("DamageReduction", 0)
            reduced_amount = amount * (100 - reduction_pct) // 100
            log.info(
                "%s's DamageReduction (%d%%) reduces incoming from %d to %d.",
                self.name, reduction_pct, amount, reduced_amount
            )
            amount = reduced_amount

        # 3) Defending halves damage
        if self.defending:
            amount //= 2
            self.defending = False
            log.info("%s defended, halving damage to %d.", self.name, amount)

        # 4) Apply to health
        self.current_health = max(0, self.current_health - amount)
        log.info(
            "%s takes %d damage; HP is now %d/%d.",
            self.name, amount, self.current_health, self.max_health
        )

        # 5) Defeat check
        if self.current_health == 0:
            log.info("%s has been defeated!", self.name)

    def drain_mana(self, amount: int) -> None:
        """
        Reduce current_mana by 'amount', clamped at 0.
        """
        old_mp = self.current_mana
        self.current_mana = max(0, self.current_mana - amount)
        drained_amt = old_mp - self.current_mana
        log.info(
            "%s drains %d MP; MP is now %d/%d.",
            self.name,
            drained_amt,
            self.current_mana,
            self.max_mana,
        )

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

    def restore_mana(self, amount: int) -> None:
        """
        Increase current_mana by 'amount', clamped at max_mana.
        """
        old_mp = self.current_mana
        self.current_mana = min(self.max_mana, self.current_mana + amount)
        restored_amt = self.current_mana - old_mp
        log.info(
            "%s restores %d MP; MP is now %d/%d.",
            self.name,
            restored_amt,
            self.current_mana,
            self.max_mana,
        )

    # ------------------------------------------------------------------------
    # Resource Restoration & Stat Placeholder
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
    # Stat Properties (base + equipment + status modifiers)
    # ------------------------------------------------------------------------
    @property
    def attack(self) -> int:
        """
        Calculate total attack:
          - Base from stats.effective()["attack"]
          - + equipped weapon bonus
          - + status_effect modifiers
          - Falls back to 1 if still zero
        """
        base = self.stats.effective().get("attack", 0)
        weapon = self.inventory.equipment.get("weapon")
        if isinstance(weapon, EquipableItem):
            base += weapon.bonuses.get("attack", 0)
        for status in self.status_effects:
            base += status.stat_mods.get("attack", 0)
        return base if base > 0 else 1

    @property
    def defense(self) -> int:
        """
        Calculate total defense.
        """
        base = self.stats.effective().get("defense", 0)
        armor = self.inventory.equipment.get("armor")
        if isinstance(armor, EquipableItem):
            base += armor.bonuses.get("defense", 0)
        for status in self.status_effects:
            base += status.stat_mods.get("defense", 0)
        return base

    @property
    def speed(self) -> int:
        """
        Calculate total speed.
        """
        base = self.stats.effective().get("speed", 0)
        boots = self.inventory.equipment.get("boots")
        if isinstance(boots, EquipableItem):
            base += boots.bonuses.get("speed", 0)
        for status in self.status_effects:
            base += status.stat_mods.get("speed", 0)
        return base

    @property
    def max_health(self) -> int:
        """
        Return the maximum health based on effective stats.
        """
        return self.stats.effective().get("health", 0)

    @property
    def health(self) -> int:
        """
        Return current health, clamped between 0 and max_health.
        """
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

    @property
    def intellect(self) -> int:
        """
        Calculate total intellect.
        """
        base = self.stats.effective().get("intellect", 0)
        for status in self.status_effects:
            base += status.stat_mods.get("intellect", 0)
        return base

    @property
    def magic_power(self) -> int:
        """
        Calculate total magic power.
        """
        return self.stats.effective().get("magic_power", 0) + self.intellect

    @property
    def level(self) -> int:
        """
        Return the current level.
        """
        return self.levels.lvl

    # ------------------------------------------------------------------------
    # Job Initialization & Helpers
    # ------------------------------------------------------------------------
    def assign_job_by_id(self, job_id: str) -> None:
        """
        Assign a job by its string ID (e.g., 'knight', 'mage').
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

        # Overwrite stats with this job’s base stats
        base = getattr(self.job, "base_stats", {})
        all_stats = {k: base.get(k, 0) for k in Job.base_stats.keys()}
        self.stats = Stats(all_stats)

        # Restore and auto-equip
        self.restore_all()
        for item in getattr(self.job, "starting_items", []):
            self.inventory.add_item(item, 1)
            if isinstance(item, EquipableItem):
                self.inventory.equip_item(item.id)

    def remove_job(self) -> None:
        """
        Remove current job, unequip & remove starting items, zero stats.
        """
        from game_sys.jobs.base import Job

        if not self.job:
            return

        old = self.job
        for slot, eid in list(self.inventory._equipped_items.items()):
            if eid in {i.id for i in getattr(old, "starting_items", [])}:
                self.inventory.unequip_item(slot)

        for itm in getattr(old, "starting_items", []):
            self.inventory.remove_item(itm.id, self.inventory._items.get(itm.id, {}).get("quantity", 0))

        self.job = None
        zeroed = {k: 0 for k in Job.base_stats.keys()}
        self.stats = Stats(zeroed)
        self.restore_all()

    def get_weakness_multiplier(self, damage_type: DamageType) -> float:
        """
        Get the weakness multiplier for a specific damage type.
        """
        return self.weakness.get(damage_type, 1.0)

    def get_resistance_multiplier(self, damage_type: DamageType) -> float:
        """
        Get the resistance multiplier for a specific damage type.
        """
        return self.resistance.get(damage_type, 1.0)
