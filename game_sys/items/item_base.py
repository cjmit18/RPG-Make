# game_sys/items/item_base.py
from typing import Dict
class Item:
    def __init__(self, name: str, description: str, price: int, level: int):
        self.name = name
        self.description = description
        self.price = price
        self.level = level
        self.id = None

class Equipable(Item):
    def __init__(self, 
                 name: str, 
                 description: str, 
                 price: int, 
                 level: int, 
                 slot: str, 
                 bonuses: Dict[str, int], 
                 grade: int, 
                 rarity: str, 
                 is_enchanable: bool,
                 offhand: bool
                 ):
        super().__init__(name, description, price, level)
        self.slot = slot
        self.bonuses = bonuses
        self.grade = grade
        self.rarity = rarity
        self.is_enchantable = is_enchanable
        self.offhand = offhand
    def apply(self, actor):
        """
        When equipped, apply bonuses as status modifiers.
        (Simplest approach: modify actor.stats directly, then call update_stats.)
        """
        for stat, amt in self.bonuses.items():
            actor.stats.add_modifier(self.id, stat, amt)
        try:
            actor.update_stats()
        except AttributeError:
            pass

    def remove(self, actor):
        """
        When unequipped, remove bonuses from actor.stats.
        """
        actor.stats.remove_modifier(self.id)
        try:
            actor.update_stats()
        except AttributeError:
            pass

class Consumable(Item):
    def __init__(self, name: str, description: str, price: int, level: int, effect: str, amount: int, duration: int):
        super().__init__(name, description, price, level)
        self.effect = effect
        self.amount = amount
        self.duration = duration

    def apply(self, actor):
        """
        When used, create a StatusEffect on the actor for buffs, or heal immediately.
        """
        from game_sys.combat.status import StatusEffect
        if self.effect == "health":
            actor.heal(self.amount)
        elif self.effect == "mana":
            actor.restore_mana(self.amount)