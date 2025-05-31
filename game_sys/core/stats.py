"""Stats management for game characters."""
from dataclasses import dataclass, field
from typing import Dict, Literal, Tuple

StatName = Literal["attack", "defense", "speed", "health", "mana", "stamina"]


@dataclass
class Stats:
    """A class to manage character stats, including base values and modifiers.
    Supports both simple stat modifiers and named modifiers (e.g. from items)."""
    base: Dict[StatName, int]
    # keeps simple per‑stat totals
    modifiers: Dict[StatName, int] = field(
        default_factory=lambda: {s: 0 for s in Stats.stat_keys()}
    )
    # new: storage for named modifiers (e.g. equipment by id)
    _modifiers: Dict[str, Dict[StatName, int]] = field(default_factory=dict,
                                                       init=False,
                                                       repr=False)

    @staticmethod
    def stat_keys() -> Tuple[StatName, ...]:
        """Return the keys for all stats in a tuple."""
        return ("attack", "defense", "speed", "health", "mana", "stamina")

    def effective(self) -> Dict[StatName, int]:
        """Calculate the effective stats by combining base, simple modifiers, and named modifiers.
        Returns a dictionary of effective stats with non-negative values."""
        # first sum up all named modifiers
        total_named = {s: 0 for s in Stats.stat_keys()}
        for mods in self._modifiers.values():
            for stat, amt in mods.items():
                total_named[stat] = total_named.get(stat, 0) + amt
        # then add base + simple modifiers + named modifiers
        return {
            s: max(
                0,
                self.base.get(s, 0)
                + self.modifiers.get(s, 0)
                + total_named.get(s, 0),
            )
            for s in Stats.stat_keys()
        }

    def clear_modifiers(self) -> None:
        """Reset all simple modifiers to zero."""
        for s in Stats.stat_keys():
            self.modifiers[s] = 0

    # your “named” modifiers, keyed by mod_id (e.g. item.name or item.id)
    def add_modifier(self, mod_id: str, stat: StatName, amount: int) -> None:
        self._modifiers.setdefault(mod_id, {})[stat] = amount

    def remove_modifier(self, mod_id: str) -> None:
        """Remove a named modifier by its ID."""
        self._modifiers.pop(mod_id, None)

    def set_base(self, stat: StatName, value: int) -> None:
        """Override the base value for a given stat."""
        if stat not in Stats.stat_keys():
            raise ValueError(f"Unknown stat '{stat}'")
        self.base[stat] = value
