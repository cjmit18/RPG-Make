import json
from pathlib import Path
from typing import Any, Dict, List
from game_sys.effects.factory import EffectFactory
from game_sys.hooks.hooks_setup import emit, ON_COMBO_TRIGGERED


class ComboManager:
    """
    Tracks recent casts per actor and triggers combo effects.
    """
    _sequences: Dict[Any, List[str]] = {}
    _combos:    Dict[str, Dict] = {}

    @classmethod
    def load_combos(cls, path: Path):
        data = json.loads(path.read_text()).get('combos', {})
        for cid, defn in data.items():
            cls._combos[cid] = defn

    @classmethod
    def record_cast(cls, actor: Any, spell_id: str):
        seq = cls._sequences.setdefault(actor, [])
        seq.append(spell_id)
        # trim to longest combo
        maxlen = max((len(d['sequence']) for d in cls._combos.values()), default=0)
        if len(seq) > maxlen:
            seq.pop(0)
        # check combos
        for cid, defn in cls._combos.items():
            seq_needed = defn['sequence']
            if seq[-len(seq_needed):] == seq_needed:
                # apply combo effects
                for eff_def in defn.get('effects', []):
                    EffectFactory.create(eff_def).apply(actor, actor)
                emit(ON_COMBO_TRIGGERED, actor=actor, combo=cid)
                seq.clear()
                break

# load at import time
ComboManager.load_combos(Path(__file__).parent / 'data' / 'combos.json')
