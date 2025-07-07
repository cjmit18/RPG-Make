# game_sys/items/armor.py
"""
Module: game_sys.items.armor

Concrete Armor subclass with defensive stats.
"""
from typing import Any
from game_sys.items.equipment import Equipment

class Armor(Equipment):
    """
    Armor item.
    JSON attrs:
      - stats: dict with defense and other stat bonuses
      - effect_ids: optional List[str] of damage‐taken modifiers
    """
    def __init__(self, item_id: str, name: str, description: str, **attrs):
        slot = attrs.pop('slot', 'body')  # Extract slot or default to body
        stats = attrs.pop('stats', {})    # Extract stats
        effect_ids = attrs.pop('effect_ids', [])  # Extract effect_ids
        
        super().__init__(item_id, name, description,
                         slot=slot,
                         stats=stats,
                         effect_ids=effect_ids,
                         **attrs)

    def apply(self, user: Any, target: Any = None) -> None:
        super().apply(user, target)


class Shield(Armor):
    """
    Shield item: armor that can be equipped in the offhand slot
    for dual wielding.
    
    JSON schema adds:
      dual_wield: bool (should be True for shields)
      block_chance: float (chance to block attacks, 0.0-1.0)
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        dual_wield: bool = True,
        block_chance: float = 0.1,
        **attrs
    ):
        # Extract stats and add block_chance
        stats = attrs.pop('stats', {})
        stats["block_chance"] = block_chance
        
        super().__init__(
            item_id=item_id,
            name=name,
            description=description,
            stats=stats,
            **attrs
        )
        self.slot = "offhand"  # Override slot to offhand
        self.dual_wield = dual_wield
        self.block_chance = block_chance

    def apply(self, user: Any, target: Any = None) -> None:
        """Equip as offhand shield."""
        if hasattr(user, 'equip_offhand'):
            user.equip_offhand(self)
        else:
            # Fallback to regular equipment
            super().apply(user, target)

    def can_block(self) -> bool:
        """Check if this shield can block an incoming attack."""
        import random
        return random.random() < self.block_chance

    def __str__(self) -> str:
        """String representation for debugging."""
        return (
            f"Shield (id={self.id}, name={self.name}, "
            f"defense={self.stats.get('defense', 0)}, "
            f"block_chance={self.block_chance}, "
            f"dual_wield={self.dual_wield}, effects={self.effect_ids})"
        )
