# game_sys/magic/registry.py

from typing import Type, Dict
from game_sys.magic.base import Spell

class SpellRegistry:
    """
    Maps spell_id to Spell subclasses (if you have special ones).
    """
    _registry: Dict[str, Type[Spell]] = {}

    @classmethod
    def register(cls, spell_id: str, spell_cls: Type[Spell]):
        cls._registry[spell_id] = spell_cls

    @classmethod
    def get(cls, spell_id: str) -> Type[Spell]:
        return cls._registry.get(spell_id, Spell)
