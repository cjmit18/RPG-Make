# stats.py

from dataclasses import dataclass, field
from typing import Dict, Literal, Tuple

StatName = Literal["attack", "defense", "speed", "health", "mana", "stamina"]

@dataclass
class Stats:
    # Your “base” stats (health here is max-health, etc.)
    base: Dict[StatName, int]

    # Any number of additive modifiers (equipment, buffs, runes…)
    modifiers: Dict[StatName, int] = field(
        default_factory=lambda: {s: 0 for s in Stats.stat_keys()}
    )

    @staticmethod
    def stat_keys() -> Tuple[StatName, ...]:
        return ("attack", "defense", "speed", "health", "mana", "stamina")

    def effective(self) -> Dict[StatName, int]:
        """
        Returns base + modifiers for each stat, clamped >= 0.
        For health/mana/stamina this is your *maximum* pool.
        """
        return {
            s: max(0, self.base.get(s, 0) + self.modifiers.get(s, 0))
            for s in Stats.stat_keys()
        }

    def set_base(self, stat: StatName, value: int) -> None:
        """Reset a base stat (e.g. via setter)."""
        if value < 0:
            raise ValueError(f"Base {stat} cannot be negative.")
        self.base[stat] = value

    def add_modifier(self, stat: StatName, amount: int) -> None:
        """Add (or subtract) a modifier to a stat."""
        self.modifiers[stat] = self.modifiers.get(stat, 0) + amount

    def clear_modifiers(self) -> None:
        """Wipe all modifiers back to zero."""
        for s in Stats.stat_keys():
            self.modifiers[s] = 0

    def clamp_all(self,
                  mins: Dict[StatName, int],
                  maxs: Dict[StatName, int]) -> None:
        """
        Optionally enforce lower/upper bounds on each stat.
        E.g. keep current health between [0, max_health].
        """
        for s in Stats.stat_keys():
            val = self.base.get(s, 0) + self.modifiers.get(s, 0)
            if s in mins:
                val = max(val, mins[s])
            if s in maxs:
                val = min(val, maxs[s])
            # store clamped value back into base (so effective() reflects it next time)
            self.base[s] = val - self.modifiers.get(s, 0)
