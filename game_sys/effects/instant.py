"""Instant effects that apply immediately to the target.
These effects are typically used for healing, mana restoration, or other immediate buffs.
"""
from game_sys.effects.base import Effect

class InstantHeal(Effect):
    """
    Applies a flat amount of healing to the target.
    This is typically used for healing skills or potions.
    """
    def __init__(self, amount: int):
        self.amount = amount

    def apply(self, source, target):
        target.health = min(target.max_health, target.health + self.amount)

class InstantMana(Effect):
    """
    Applies a flat amount of mana restoration to the target.
    This is typically used for mana potions or skills that restore mana.
    """
    def __init__(self, amount: int):
        self.amount = amount

    def apply(self, source, target):
        target.mana = min(target.max_mana, target.mana + self.amount)