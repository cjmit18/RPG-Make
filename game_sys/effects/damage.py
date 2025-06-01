# game_sys/effects/damage.py

from typing import Optional
from game_sys.core.actor import Actor


class DamageEffect:
    """
    Deal flat damage to a target, optionally requiring a status or scaled by a multiplier.

    Attributes:
        amount (int): Base damage value.
        multiplier (float): Damage is amount * multiplier.
        requires_status (Optional[str]): If set, only apply damage when the target has this status.
    """

    def __init__(
        self,
        amount: int,
        multiplier: float = 1.0,
        requires_status: Optional[str] = None,
    ) -> None:
        if not isinstance(amount, int):
            raise TypeError(f"DamageEffect amount must be int, got {amount!r}")
        if not isinstance(multiplier, (int, float)):
            raise TypeError(f"DamageEffect multiplier must be int or float, got {multiplier!r}")
        if requires_status is not None and not isinstance(requires_status, str):
            raise TypeError(f"DamageEffect requires_status must be str or None, got {requires_status!r}")

        self.amount: int = amount
        self.multiplier: float = float(multiplier)
        self.requires_status: Optional[str] = requires_status

    def apply(self, caster: Actor, target: Actor) -> None:
        """
        Apply damage to the target. If `requires_status` is set, only apply if the target has that status.

        Damage dealt = int(self.amount * self.multiplier).
        """

        # If a required status is specified, check target’s statuses
        if self.requires_status:
            has_status = any(
                status.name == self.requires_status for status in target.status_effects
            )
            if not has_status:
                return  # Target lacks required status → no damage

        # Compute final damage (rounded down to int)
        damage_to_deal = int(self.amount * self.multiplier)
        target.take_damage(damage_to_deal)
