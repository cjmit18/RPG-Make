# game_sys/effects/heal.py

from game_sys.core.actor import Actor

class HealEffect:
    """
    Instantly restores HP to the target.
    """

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def apply(self, caster: Actor, target: Actor) -> None:
        target.heal(self.amount)
