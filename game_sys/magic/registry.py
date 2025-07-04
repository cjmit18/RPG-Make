# game_sys/magic/registry.py

from typing import Type, Dict
from game_sys.magic.base import Spell
from game_sys.logging import magic_logger, log_exception


class SpellRegistry:
    """
    Maps spell_id to Spell subclasses (if you have special ones).
    """
    _registry: Dict[str, Type[Spell]] = {}

    @classmethod
    def register(cls, spell_id: str, spell_cls: Type[Spell]):
        magic_logger.info(f"Registering spell class for {spell_id}")
        cls._registry[spell_id] = spell_cls

    @classmethod
    @log_exception
    def get(cls, spell_id: str) -> Type[Spell]:
        spell_cls = cls._registry.get(spell_id, Spell)
        if spell_cls == Spell and spell_id in cls._registry:
            magic_logger.warning(
                f"Using base Spell class for {spell_id} instead of a custom class"
            )
        magic_logger.debug(f"Using {spell_cls.__name__} for spell {spell_id}")
        return spell_cls
