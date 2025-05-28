""" Base class for all character jobs in the game. """
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Any
from typing import TypedDict
if TYPE_CHECKING:
    from core.character_creation import Character
    from items.items_list import Item
class StatBlock(TypedDict):
    attack: int; defense: int; speed: int
    health: int; mana: int; stamina: int
log = logging.getLogger(__name__)

@dataclass(frozen=True)
class StartingItem:
    """Helper that says “create this item, qty times, then optionally auto-equip it.”"""
    factory: Callable[..., Item]
    args: tuple[Any, ...]       = field(default_factory=tuple)
    kwargs: dict[str, Any]      = field(default_factory=dict)
    quantity: int               = 1
    auto_equip: bool            = False


class Base:
    """Base class for all character jobs in the game."""
    def __init__(
        self,
        character: Character,
        stats: dict[str, int] | None = None,
        starting_items: list[StartingItem] | None = None,
        name: str | None= None,
    ) -> None:
        self.character = character
        self.job       = name or self.__class__.__name__
        # store any flat stat overrides
        self.stats = stats or {}

        # apply flat stat overrides
        if self.stats:
            for key, value in self.stats.items():
                self.character.stats.set_base(key, value)

        # spawn items and optionally equip
        if starting_items:
            inv = self.character.inventory
            for si in starting_items:
                item = si.factory(*si.args, **si.kwargs)
                inv.add(item, quantity=si.quantity, auto_equip=si.auto_equip)
    def base_stats(self, lvl: int) -> StatBlock:
            """
            Default curve for all stats: 3 × level.
            """
            return { stat: 3 * lvl
                    for stat in ("attack", "defense", "speed", "health", "mana", "stamina") }
    def __str__(self) -> str:
        eff = self.character.stats.effective()
        parts = [f"Class: {self.job}"]
        for stat in ("attack", "defense", "speed", "health", "mana", "stamina"):
            base = self.character.stats.base.get(stat, 0)
            total = eff.get(stat, 0)
            bonus = total - base
            line = f"{stat.capitalize()}: {total}"
            if bonus:
                line += f" (Base: {base} + Bonus: {bonus})"
            parts.append(line)
        return "\n".join(parts)

    def __repr__(self) -> str:
        return f"<{self.job} {self.character.name} (Lvl {self.character.lvl})>"
