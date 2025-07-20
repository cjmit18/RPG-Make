# game_sys/items/registry.py
"""
Module: game_sys.items.registry

Registry mapping item‐type strings to Item subclasses.
"""
from typing import Type, Dict
from game_sys.items.base import Item, NullItem
from game_sys.items.consumable import Consumable
from game_sys.items.material import Material
from game_sys.items.weapon import Weapon, OffhandWeapon, TwoHandedWeapon
from game_sys.items.armor import Armor, Shield
from game_sys.items.accessory import Accessory
from game_sys.items.enchantment import Enchantment


class ItemRegistry:
    """
    Maps type IDs (e.g. 'consumable', 'weapon') to concrete classes.
    """
    _registry: Dict[str, Type[Item]] = {}

    @classmethod
    def register(cls, type_id: str, item_cls: Type[Item]):
        cls._registry[type_id] = item_cls

    @classmethod
    def get(cls, type_id: str) -> Type[Item]:
        return cls._registry.get(type_id, NullItem)

# register built‐ins

ItemRegistry.register('null', NullItem)
ItemRegistry.register('consumable', Consumable)
ItemRegistry.register('material', Material)
ItemRegistry.register('weapon', Weapon)
ItemRegistry.register('two_handed_weapon', TwoHandedWeapon)
ItemRegistry.register('armor', Armor)
ItemRegistry.register('accessory', Accessory)
ItemRegistry.register('enchantment', Enchantment)
ItemRegistry.register('offhand_weapon', OffhandWeapon)
ItemRegistry.register('shield', Shield)
