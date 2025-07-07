# game_sys/items/consumable.py
"""
Module: game_sys.items.consumable

A one‐use item that applies a list of effect IDs to a target.
"""
from typing import Any
from game_sys.items.base import Item
from game_sys.effects.factory import EffectFactory


class Consumable(Item):
    """
    Consumable item that applies effects on use.
    JSON attrs:
      - effect_ids: List[str] of effect IDs to apply
      - effects: List[Dict] of effect definitions (legacy compatibility)
    """
    def __init__(self, item_id: str, name: str, description: str, **attrs):
        super().__init__(item_id, name, description, **attrs)
        
        # Handle both new effect_ids format and legacy effects format
        effect_ids = attrs.get('effect_ids', [])
        effects = attrs.get('effects', [])
        
        # Pre‐parse effect definitions into Effect instances
        self._effects = []
        
        # Process effect_ids (new format)
        for effect_id in effect_ids:
            if isinstance(effect_id, str):
                # Map common effect_ids to proper effect definitions
                effect_def = self._map_effect_id_to_definition(effect_id)
                if effect_def:
                    self._effects.append(EffectFactory.create(effect_def))
        
        # Process effects (legacy format)
        for effect_def in effects:
            self._effects.append(EffectFactory.create(effect_def))

    def _map_effect_id_to_definition(self, effect_id: str) -> dict:
        """
        Map an effect_id to a proper effect definition.
        This is a temporary solution until proper effect registry exists.
        """
        # Common effect patterns
        if effect_id.startswith('heal_'):
            amount = float(effect_id.split('_')[1])
            return {"type": "heal", "params": {"amount": amount}}
        elif effect_id.startswith('restore_mana_'):
            amount = float(effect_id.split('_')[2])
            return {"type": "instant_mana", "params": {"amount": amount}}
        elif effect_id.startswith('flat_'):
            amount = float(effect_id.split('_')[1])
            return {"type": "flat", "params": {"amount": amount}}
        elif effect_id.startswith('percent_'):
            multiplier = float(effect_id.split('_')[1]) / 100.0
            return {"type": "percent", "params": {"multiplier": multiplier}}
        else:
            # Unknown effect_id, return None to skip
            return None

    def apply(self, user: Any, target: Any = None) -> None:
        """
        Apply each configured effect, passing user as caster and target.
        """
        for eff in self._effects:
            eff.apply(user, target or user)
