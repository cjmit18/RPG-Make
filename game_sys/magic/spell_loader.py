# game_sys/magic/spell_loader.py

from game_sys.magic.factory import SpellFactory
from game_sys.logging import magic_logger, log_exception


@log_exception
def load_spell(spell_id: str):
    """Load a spell by ID from the spell data."""
    magic_logger.debug(f"Loading spell: {spell_id}")
    spell = SpellFactory.create(spell_id)
    magic_logger.info(f"Loaded spell: {spell.name} ({spell_id})")
    return spell
