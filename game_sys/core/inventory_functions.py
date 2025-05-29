# game_sys/core/inventory_functions.py

from typing import Dict, Optional
from game_sys.items.item_base import Equipable, Item
from game_sys.items.consumable_list import Consumable

class Inventory:
    def __init__(self, owner):
        self.owner = owner
        # items: item_id -> {"item": Item, "quantity": int}
        self.items: Dict[str, Dict[str, object]] = {}
        # equipment slots
        self.equipment: Dict[str, Optional[Equipable]] = {
            "weapon": None,
            "armor": None,
            "accessory": None,
            "ring": None,
        }

    def add_item(self, item: Item, quantity: int = 1, auto_equip: bool = False):
        """Add copies of `item` to inventory. If auto_equip and Equipable, equip it."""
        entry = self.items.setdefault(item.id, {"item": item, "quantity": 0})
        entry["quantity"] += quantity

        if auto_equip and isinstance(item, Equipable):
            self.equip_item(item.id)

    def remove_item(self, item: Item, quantity: int = 1):
        """Remove copies; raise if not enough."""
        entry = self.items.get(item.id)
        if not entry or entry["quantity"] < quantity:
            raise ValueError(f"Not enough of {item.id} to remove")
        entry["quantity"] -= quantity
        if entry["quantity"] == 0:
            del self.items[item.id]

    def equip_item(self, item_id: str):
        """Move one copy from inventory into the correct slot and apply bonuses."""
        entry = self.items.get(item_id)
        if not entry:
            raise ValueError(f"{item_id} not in inventory")
        item = entry["item"]
        if not isinstance(item, Equipable):
            raise TypeError(f"Cannot equip non-equipable {item_id}")

        slot = item.slot
        # Unequip existing in that slot
        if self.equipment.get(slot):
            self.unequip_item(slot)

        # Remove one from bag & put into slot
        self.remove_item(item, 1)
        self.equipment[slot] = item

        # APPLY STATS VIA Stats.add_modifier()
        for stat, bonus in item.bonuses.items():
            self.owner.stats.add_modifier(stat, bonus)

    def unequip_item(self, slot: str):
        """Remove equipped item from `slot`, reverse bonuses, and return to inventory."""
        item = self.equipment.get(slot)
        if not item:
            return

        # REVERSE STATS VIA Stats.add_modifier()
        for stat, bonus in item.bonuses.items():
            self.owner.stats.add_modifier(stat, -bonus)

        # return to bag
        self.add_item(item, quantity=1)
        self.equipment[slot] = None

    def use_item(self, item: Item):
        """
        Consume one `Consumable` from inventory, apply its effect, and remove it.
        """
        # 1) Ensure it has an id
        item_id = getattr(item, "id", None)
        if item_id is None:
            raise ValueError(f"No {item.name} to use")

        # 2) Ensure it’s in the bag
        entry = self.items.get(item_id)
        if not entry or entry["quantity"] < 1:
            raise ValueError(f"No {item.name} left to use")

        # 3) Must be consumable
        if not isinstance(item, Consumable):
            raise TypeError(f"{item.name} is not consumable")

        # 4) Apply effect
        cap = self.owner.stats.effective()
        if item.effect == "health":
            self.owner.current_health = min(
                self.owner.current_health + item.amount,
                cap.get("health", self.owner.current_health),
            )
        elif item.effect == "mana":
            self.owner.current_mana = min(
                self.owner.current_mana + item.amount,
                cap.get("mana", self.owner.current_mana),
            )
        elif item.effect == "stamina":
            self.owner.current_stamina = min(
                self.owner.current_stamina + item.amount,
                cap.get("stamina", self.owner.current_stamina),
            )
        # (extend with other effects here)

        # 5) Finally, remove one copy
        self.remove_item(item, 1)