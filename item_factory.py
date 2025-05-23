# item_factory.py
from items_list import Item, Consumable
from weapon_list import Sword, Axe, Dagger, Bow, Staff, Off_Hand
from armor_list import Armor, Shield, Robe
from potion_list import Health_Potion, Mana_Potion
from amulet_list import Amulet
from boots_list import Boot
from ring_list import Ring

ITEM_CLASSES = {
    "Item": Item,
    "Consumable": Consumable,
    "Sword": Sword,
    "Axe": Axe,
    "Dagger": Dagger,
    "Bow": Bow,
    "Staff": Staff,
    "Off_Hand": Off_Hand,
    "Armor": Armor,
    "Shield": Shield,
    "Robe": Robe,
    "Health_Potion": Health_Potion,
    "Mana_Potion": Mana_Potion,
    "Amulet": Amulet,
    "Boot": Boot,
    "Ring": Ring
}

def item_from_dict(data: dict):
    """Factory loader that builds the correct item subclass from saved data."""
    item_type = data.get("type", "Item")
    cls = ITEM_CLASSES.get(item_type, Item)
    return cls.from_dict(data)
