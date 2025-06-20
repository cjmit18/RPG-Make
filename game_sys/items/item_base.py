from typing import Dict, List, Optional, Union, Any
from logs.logs import get_logger
from game_sys.core.rarity import Rarity
from game_sys.core.damage_types import DamageType
from game_sys.enchantments.base import BasicEnchantment
from game_sys.hooks.hooks import hook_dispatcher
from game_sys.effects.base import Effect
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from game_sys.character.actor import Actor
log = get_logger(__name__)

class Item:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        grade: int = 1,
        rarity: Union[Rarity, str] = Rarity.COMMON,
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.level = level
        self.grade = grade
        self.rarity = rarity if isinstance(rarity, Rarity) else Rarity[rarity.upper()]

    def __str__(self) -> str:
        return f"{self.name} (Level {self.level})"

    def apply(self, user: 'Actor', target: Optional['Actor'] = None) -> Any:
        log.debug(f"No direct effect for item {self.id}")
        return None

class EquipableItem(Item):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        slot: str,
        grade: int = 1,
        rarity: Union[Rarity, str] = Rarity.COMMON,
        base_bonus_ranges: Optional[Dict[str, Dict[str, int]]] = None,
        damage_map: Optional[Dict[str, Dict[str, int]]] = None,
        percent_bonuses: Optional[Dict[str, float]] = None,
        passive_effects: Optional[List[Union[str, Dict[str, Any]]]] = None,
        enchantments: Optional[List[BasicEnchantment]] = None,
        resistances: Optional[Dict[DamageType, float]] = None,
    ) -> None:
        super().__init__(id, name, description, price, level, grade, rarity)
        self.slot = slot
        self.base_bonus_ranges = base_bonus_ranges or {}
        self.damage_map = damage_map or {}
        self.percent_bonuses = percent_bonuses or {}
        self.passive_effects = passive_effects or []
        self.enchantments = enchantments or []
        self.resistances = resistances or {}
        self.bonuses = self._calculate_bonus_totals()

    def _calculate_bonus_totals(self) -> Dict[str, int]:
        totals: Dict[str, int] = {}
        for stat, rng in self.base_bonus_ranges.items():
            totals[stat] = totals.get(stat, 0) + int(rng.get("min", 0))
        for ench in self.enchantments:
            for stat, val in ench.stat_bonuses.items():
                totals[stat] = totals.get(stat, 0) + val
        return totals

    def total_damage_map(self) -> Dict[DamageType, int]:
        final: Dict[DamageType, int] = {}
        for dt_name, dmg in self.damage_map.items():
            try:
                dt = DamageType[dt_name.upper()]
                avg = int((dmg.get("min", 0) + dmg.get("max", 0)) / 2)
                if avg > 0:
                    final[dt] = final.get(dt, 0) + avg
            except KeyError:
                continue
        for ench in self.enchantments:
            for dt, val in ench.damage_modifiers.items():
                final[dt] = final.get(dt, 0) + val
        return final

    def apply(self, user: 'Actor', target: Optional['Actor'] = None) -> None:
        log.debug(f"Equipable item {self.id} used; equipping logic handled elsewhere")
        return None

    def __str__(self) -> str:
        lines = [
            f"| Item: {self.name} (ID: {self.id})",
            f"| Level: {self.level} | Price: {self.price}",
            f"| Description: {self.description}",
            f"| Slot: {self.slot} | Grade: {self.grade} | Rarity: {self.rarity.name}"
        ]
        if self.bonuses:
            lines.append("| Bonuses: " + ", ".join(f"{k}: {v}" for k, v in self.bonuses.items()))

        total_dmg = self.total_damage_map()
        if total_dmg:
            dmg_str = ", ".join(f"{dt.name}: {val}" for dt, val in total_dmg.items())
            lines.append(f"| Damage: {dmg_str}")

        if self.resistances:
            res_str = ", ".join(f"{dt.name}: {mult:.2f}" for dt, mult in self.resistances.items())
            lines.append(f"| Resistances: {res_str}")

        if self.enchantments:
            lines.append("| Enchantments:")
            for ench in self.enchantments:
                lines.append(str(ench))

        if self.passive_effects:
            pe_list: List[str] = []
            for pe in self.passive_effects:
                if isinstance(pe, dict):
                    pe_list.append(pe.get("id", str(pe)))
                else:
                    pe_list.append(str(pe))
            lines.append("| Passive Effects: " + ", ".join(pe_list))

        return "\n".join(lines)


class ConsumableItem(Item):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        effects_data: List[Dict[str, Any]],
        amount: int = 1,
        grade: int = 1,
        rarity: Union[Rarity, str] = Rarity.COMMON,
    ) -> None:
        super().__init__(id, name, description, price, level, grade, rarity)
        self.effects_data = effects_data
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.name} x{self.amount} (Effects: {len(self.effects_data)})"

    def apply(self, user: 'Actor', target: Optional['Actor'] = None) -> List[Any]:
        results: List[Any] = []
        for eff_data in self.effects_data:
            effect_obj = Effect.from_dict(eff_data)
            actual_target = target or user
            hook_dispatcher.fire("effect.before_apply", effect=eff_data, caster=user, target=actual_target)
            res = effect_obj.apply(user, actual_target)
            hook_dispatcher.fire("effect.after_apply", effect=eff_data, caster=user, target=actual_target, result=res)
            results.append(res)
        self.amount -= 1
        if self.amount <= 0:
            hook_dispatcher.fire("item.consumed", item=self, user=user)
        return results
