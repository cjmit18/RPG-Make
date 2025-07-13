import json
from pathlib import Path
from typing import Any, Dict, List
from game_sys.effects.factory import EffectFactory
from game_sys.effects.registry import EffectRegistry
from game_sys.hooks.hooks_setup import emit, ON_COMBO_TRIGGERED, ON_COMBO_FINISHED
from game_sys.logging import magic_logger, log_exception


class ComboManager:
    """
    Tracks recent casts per actor and triggers combo effects.
    """
    _sequences: Dict[Any, List[str]] = {}
    _combos:    Dict[str, Dict] = {}

    @classmethod
    @log_exception
    def load_combos(cls, path: Path):
        magic_logger.info(f"Loading combos from {path}")
        try:
            data = json.loads(path.read_text()).get('combos', {})
            for cid, defn in data.items():
                cls._combos[cid] = defn
            magic_logger.info(f"Loaded {len(cls._combos)} spell combos")
        except Exception as e:
            magic_logger.error(f"Failed to load combos: {e}")
            raise

    @classmethod
    @log_exception
    def record_cast(cls, actor: Any, spell_id: str):
        magic_logger.debug(f"{actor.name} cast spell: {spell_id}")
        
        seq = cls._sequences.setdefault(actor, [])
        seq.append(spell_id)
        magic_logger.debug(f"Current sequence for {actor.name}: {seq}")
        
        # trim to longest combo
        maxlen = max(
            (len(d['sequence']) for d in cls._combos.values()), default=0
        )
        if len(seq) > maxlen:
            seq.pop(0)
            magic_logger.debug(f"Trimmed sequence to {seq}")
            
        # check combos
        for cid, defn in cls._combos.items():
            seq_needed = defn['sequence']
            if seq[-len(seq_needed):] == seq_needed:
                magic_logger.info(
                    f"Combo triggered: {cid} by {actor.name} "
                    f"with sequence {seq_needed}"
                )
                
                # apply combo effects
                emit(ON_COMBO_TRIGGERED, actor=actor, combo=cid)
                for eff_def in defn.get('effects', []):
                    effect = EffectFactory.create(eff_def)
                    result = effect.apply(actor, actor)
                    magic_logger.debug(
                        f"Applied combo effect {effect.id}: {result}"
                    )
                    if not result:
                        magic_logger.warning(f"Combo effect {effect.id} failed")
                    emit(ON_COMBO_FINISHED, actor=actor, combo=cid)
                # clear sequence after triggering
                seq.clear()
                magic_logger.debug(f"Cleared sequence for {actor.name}")

                break


# load at import time
ComboManager.load_combos(Path(__file__).parent / 'data' / 'combos.json')
