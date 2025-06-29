from typing import List, Any

def filter_targets(
    actors: List[Any],
    group: str,
    caster: Any,
    primary_target: Any = None
) -> List[Any]:
    """
    group: 'enemies', 'allies', 'all', 'self', 'target'
    """
    if group == 'enemies':
        return [a for a in actors if getattr(a, 'team', None) != caster.team]
    if group == 'allies':
        return [a for a in actors if getattr(a, 'team', None) == caster.team and a is not caster]
    if group == 'all':
        return actors.copy()
    if group == 'self':
        return [caster]
    if group == 'target' and primary_target is not None:
        return [primary_target]
    return []
