# game_sys/magic/spell_loader.py

from game_sys.magic.factory import SpellFactory


def load_spell(spell_id: str):
    return SpellFactory.create(spell_id)
