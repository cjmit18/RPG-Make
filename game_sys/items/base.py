# game_sys/items/base.py
"""
Module: game_sys.items.base

Defines abstract Item interface and a NullItem fallback.
"""
from abc import ABC, abstractmethod
from typing import Any


class Item(ABC):
    """
    Base class for all in‐game items.
    """

    def __init__(self, item_id: str, name: str, description: str, **attrs):
        import uuid
        self.id = item_id
        self.name = name
        self.description = description
        # Unique instance identifier for stackable/unique logic
        self.uuid = attrs.pop('uuid', str(uuid.uuid4()))
        # Level and stat requirements
        self.level_requirement = attrs.get('level_requirement', 1)
        self.stat_requirements = attrs.get('stat_requirements', {})
        # any extra attributes (e.g. stats) get attached
        for k, v in attrs.items():
            setattr(self, k, v)

    @abstractmethod
    def apply(self, user: Any, target: Any = None) -> None:
        """
        Execute the item's effect.
        - For consumables, target might be the user.
        - For equipment, this might equip the item.
        """
        ...
    
    def can_be_used_by(self, actor) -> bool:
        """Check if the actor meets the requirements to use this item."""
        # Check level requirement
        if hasattr(actor, 'level') and actor.level < self.level_requirement:
            return False
            
        # Check stat requirements
        if hasattr(actor, 'base_stats') and self.stat_requirements:
            for stat, required_value in self.stat_requirements.items():
                current_value = actor.base_stats.get(stat, 0)
                if current_value < required_value:
                    return False
                    
        return True
    
    def get_requirement_text(self) -> str:
        """Get a text description of the item's requirements."""
        requirements = []
        
        if self.level_requirement > 1:
            requirements.append(f"Level {self.level_requirement}")
            
        if self.stat_requirements:
            for stat, value in self.stat_requirements.items():
                stat_name = stat.replace('_', ' ').title()
                requirements.append(f"{stat_name} {value}")
                
        if requirements:
            return f"Requires: {', '.join(requirements)}"
        else:
            return "No requirements"


class NullItem(Item):
    """
    No-op item used when an item_id isn’t registered.
    """
    def __init__(self, item_id="null", name="Null Item", description="No effect"):
        super().__init__(
            item_id=item_id,
            name=name,
            description=description
        )

    def apply(self, user: Any, target: Any = None) -> None:
        pass
