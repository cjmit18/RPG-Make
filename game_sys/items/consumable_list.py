import uuid
from game_sys.items.item_base import Item
from game_sys.combat.status import StatusEffect


class Consumable(Item):
    """
    A consumable can either:
      - Heal instantly (effect="health", duration=0)
      - Restore mana instantly (effect="mana", duration=0)
      - Grant a temporary stat buff (duration > 0).
    """
    def __init__(
        self,
        name: str,
        description: str,
        price: int,
        level: int,
        effect: str,      # "health", "mana", or a stat name like "attack"
        amount: int,
        duration: int,    # number of turns (0 = instant)
        id: str = None,
    ):
        # Initialize base Item fields (name, description, price, level)
        super().__init__(name, description, price, level)

        # Store consumable-specific attributes
        self.effect = effect
        self.amount = amount
        self.duration = duration

        # Auto-generate a UUID if no `id` was supplied
        self.id = id or str(uuid.uuid4())

    def apply(self, owner) -> None:
        """
        Use this consumable on the owner (an Actor):
        - If duration == 0, perform an instant heal/restore of HP or MP.
        - If duration > 0, create a StatusEffect that lasts for `duration` turns.
        """
        if self.duration == 0:
            if self.effect == "health":
                owner.health += self.amount
            elif self.effect == "mana":
                owner.mana += self.amount
            else:
                raise ValueError(f"Unknown consumable effect '{self.effect}'")
        else:
            # Create a temporary buff (StatusEffect) that modifies `self.effect`
            buff_mods = {self.effect: self.amount}
            buff_name = f"{self.id}-buff"
            status = StatusEffect(name=buff_name, stat_mods=buff_mods, duration=self.duration)
            owner.status_effects.append(status)
