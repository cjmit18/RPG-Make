# game_sys/items/usage_manager.py
"""
Item Usage Manager
=================

Handles item usage, equipping, and application of item effects.
"""

from typing import List, Any, Optional, Dict
from dataclasses import dataclass

from game_sys.character.actor import Actor
from game_sys.logging import item_logger
from game_sys.utils.profiler import profiler


@dataclass
class ItemUsageResult:
    """Result of an item usage operation."""
    success: bool
    message: str
    health_restored: float = 0.0
    mana_restored: float = 0.0
    stamina_restored: float = 0.0
    effects_applied: List[str] = None
    
    def __post_init__(self):
        if self.effects_applied is None:
            self.effects_applied = []


class ItemUsageManager:
    """Manages item usage and application of effects."""
    
    def use_item(
        self, actor: Actor, item: Any, target: Optional[Actor] = None
    ) -> ItemUsageResult:
        """
        Use an item on a target (or self if no target provided).
        
        Args:
            actor: The actor using the item
            item: The item to use
            target: Optional target actor (defaults to self)
            
        Returns:
            ItemUsageResult with details of the item usage
        """
        with profiler.span("use_item"):
            return self._use_item_internal(actor, item, target)
    
    def _use_item_internal(
        self, actor: Actor, item: Any, target: Optional[Actor] = None
    ) -> ItemUsageResult:
        """Internal implementation of item usage."""
        # Default to self if no target provided
        if target is None:
            target = actor
            
        # Validate inputs
        if not actor:
            return ItemUsageResult(False, "No actor provided")
        
        if not item:
            return ItemUsageResult(False, "No item provided")
            
        if not target:
            return ItemUsageResult(False, "Invalid target")
            
        # Check if item is in inventory
        if hasattr(actor, 'inventory'):
            if not actor.inventory.has_item(item):
                return ItemUsageResult(
                    False, 
                    f"Actor does not have item {item.name} in inventory"
                )
        
        # Process item based on type
        item_type = getattr(item, 'item_type', 'unknown')
        
        # Health potion
        if item_type == 'potion' and getattr(item, 'effect_type', '') == 'heal':
            return self._handle_healing_item(actor, item, target)
            
        # Mana potion
        elif item_type == 'potion' and getattr(item, 'effect_type', '') == 'mana':
            return self._handle_mana_item(actor, item, target)
            
        # Buff item
        elif item_type == 'scroll' or getattr(item, 'has_effect', False):
            return self._handle_effect_item(actor, item, target)
            
        # Equipment
        elif item_type in ('weapon', 'armor', 'offhand', 'accessory'):
            return self._handle_equipment(actor, item)
            
        # Unknown item type
        else:
            return ItemUsageResult(
                False,
                f"Unknown or unsupported item type: {item_type}"
            )
    
    def _handle_healing_item(
        self, actor: Actor, item: Any, target: Actor
    ) -> ItemUsageResult:
        """Handle healing potions and items."""
        # Calculate healing amount
        base_heal = getattr(item, 'power', 0)
        healing = base_heal
        
        # Apply healing
        old_health = target.current_health
        target.current_health = min(
            target.current_health + healing, 
            target.max_health
        )
        actual_healing = target.current_health - old_health
        
        # Remove from inventory if consumable
        if getattr(item, 'consumable', True):
            if hasattr(actor, 'inventory'):
                actor.inventory.remove_item(item)
        
        # Return result
        return ItemUsageResult(
            True,
            f"Used {item.name} to restore {actual_healing:.1f} health",
            health_restored=actual_healing
        )
    
    def _handle_mana_item(
        self, actor: Actor, item: Any, target: Actor
    ) -> ItemUsageResult:
        """Handle mana potions and items."""
        # Calculate mana restoration
        base_restore = getattr(item, 'power', 0)
        mana_restore = base_restore
        
        # Apply mana restoration
        old_mana = target.current_mana
        target.current_mana = min(
            target.current_mana + mana_restore, 
            target.max_mana
        )
        actual_restore = target.current_mana - old_mana
        
        # Remove from inventory if consumable
        if getattr(item, 'consumable', True):
            if hasattr(actor, 'inventory'):
                actor.inventory.remove_item(item)
        
        # Return result
        return ItemUsageResult(
            True,
            f"Used {item.name} to restore {actual_restore:.1f} mana",
            mana_restored=actual_restore
        )
    
    def _handle_effect_item(
        self, actor: Actor, item: Any, target: Actor
    ) -> ItemUsageResult:
        """Handle items with effects (scrolls, buffs, etc.)."""
        effects_applied = []
        
        # Apply effects
        if hasattr(item, 'effects') and item.effects:
            for effect in item.effects:
                if hasattr(effect, 'apply'):
                    effect.apply(actor, target)
                    effect_name = getattr(effect, 'name', 'unknown effect')
                    effects_applied.append(effect_name)
        
        # Remove from inventory if consumable
        if getattr(item, 'consumable', True):
            if hasattr(actor, 'inventory'):
                actor.inventory.remove_item(item)
        
        # Return result
        return ItemUsageResult(
            True,
            f"Used {item.name} and applied {len(effects_applied)} effects",
            effects_applied=effects_applied
        )
    
    def _handle_equipment(self, actor: Actor, item: Any) -> ItemUsageResult:
        """Handle equipping items using the equipment service."""
        try:
            # Import here to avoid circular imports
            from game_sys.items.equipment_service import equipment_service
            
            # Use the equipment service for smart equipment logic
            success, message = equipment_service.equip_item(actor, item)
            
            if success:
                return ItemUsageResult(
                    True,
                    message,
                    effects_applied=getattr(item, 'effect_ids', [])
                )
            else:
                return ItemUsageResult(
                    False,
                    message
                )
                
        except Exception as e:
            item_logger.error(f"Equipment error: {e}")
            return ItemUsageResult(
                False,
                f"Equipment failed: {e}"
            )


# Singleton instance
item_usage_manager = ItemUsageManager()
