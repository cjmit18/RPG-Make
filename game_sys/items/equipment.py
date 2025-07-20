# game_sys/items/equipment.py

from typing import Any, List, Optional
import uuid
def create_item_with_uuid(item_id: str, **attrs):
    """Factory to create an item with a unique UUID, stackable by id."""
    # This should be extended to support all item types (Weapon, Armor, etc.)
    # For now, try Weapon, then Armor, then Equipment
    from game_sys.items.weapon import Weapon
    from game_sys.items.armor import Armor
    # Try to load item data from JSON or config if needed
    # For now, just pass through attrs
    try:
        return Weapon(item_id=item_id, name=attrs.get('name', item_id), description=attrs.get('description', ''), base_damage=attrs.get('base_damage', 1), effect_ids=attrs.get('effect_ids', []), damage_type=attrs.get('damage_type', 'PHYSICAL'), uuid=str(uuid.uuid4()), **attrs)
    except Exception:
        pass
    try:
        return Armor(item_id=item_id, name=attrs.get('name', item_id), description=attrs.get('description', ''), uuid=str(uuid.uuid4()), **attrs)
    except Exception:
        pass
    return Equipment(item_id=item_id, name=attrs.get('name', item_id), description=attrs.get('description', ''), slot=attrs.get('slot', 'body'), uuid=str(uuid.uuid4()), **attrs)
from game_sys.items.base import Item

class Equipment(Item):
    """
    Base class for equippable gear.
    Tracks both raw effect_ids and which enchantment items have been slotted.
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        slot: str,
        effect_ids: List[str] = None,
        **attrs
    ):
        super().__init__(item_id, name, description, **attrs)
        self.slot = slot
        self.stats = attrs.get('stats', {})
        self.effect_ids = effect_ids or []
        self.enchantments = []  # List[str] of applied enchantment item IDs

    def apply(self, user: Any, target: Any = None) -> None:
        """
        Equip this item on the user using the equipment service.
        
        This method now delegates to the equipment service for consistent
        dual-wield logic and conflict resolution.
        """
        try:
            # Import here to avoid circular imports
            from game_sys.items.equipment_service import equipment_service
            
            # Use the equipment service for smart equipment logic
            success, message = equipment_service.equip_item(user, self)
            
            if not success:
                # Log the failure but don't raise exception for backward compatibility
                from game_sys.logging import get_logger
                logger = get_logger(__name__)
                logger.warning(f"Equipment failed for {self.name}: {message}")
                
        except Exception as e:
            # Fallback to legacy direct equipment for compatibility
            self._legacy_apply(user, target)
            
    def _legacy_apply(self, user: Any, target: Any = None) -> None:
        """
        Legacy equipment method for backward compatibility.
        """
    def _legacy_apply(self, user: Any, target: Any = None) -> None:
        """
        Legacy equipment method for backward compatibility.
        """
        # Delegate to actor's equip methods for weapon/offhand slots
        if self.slot == "weapon":
            if hasattr(user, 'equip_weapon_smart'):
                user.equip_weapon_smart(self)
            elif hasattr(user, 'equip_weapon'):
                user.equip_weapon(self)
            else:
                setattr(user, "weapon", self)
        elif self.slot == "offhand":
            if hasattr(user, 'equip_offhand'):
                user.equip_offhand(self)
            else:
                setattr(user, "offhand", self)
        else:
            # For armor and other slots, first unequip existing item in slot
            existing_item = getattr(user, f"equipped_{self.slot}", None)
            if existing_item:
                # Return existing item to inventory before equipping new one
                if (hasattr(user, 'inventory') and
                        hasattr(existing_item, 'stats')):
                    user.inventory.add_item(existing_item)
                
                # Remove old bonuses
                if hasattr(existing_item, 'stats'):
                    for stat_name, bonus in existing_item.stats.items():
                        current_value = user.base_stats.get(stat_name, 0.0)
                        new_value = max(0.0, current_value - bonus)
                        user.base_stats[stat_name] = new_value
                
                # Remove old effect IDs
                if hasattr(existing_item, 'effect_ids'):
                    for effect_id in existing_item.effect_ids:
                        if effect_id in user.skill_effect_ids:
                            user.skill_effect_ids.remove(effect_id)
            
            # Apply new item bonuses
            for stat_name, bonus in self.stats.items():
                current_value = user.base_stats.get(stat_name, 0.0)
                user.base_stats[stat_name] = current_value + bonus
            
            # Add effect IDs to actor's skill effect IDs
            user.skill_effect_ids.extend(self.effect_ids)
            
            # Set the equipment slot
            setattr(user, f"equipped_{self.slot}", self)
        
        # Update actor's computed stats after equipment change
        if hasattr(user, 'update_stats'):
            user.update_stats()

    def unequip(self, user: Any) -> None:
        """
        Unequip this item from the user, removing all bonuses.
        """
        if self.slot == "weapon":
            if hasattr(user, 'unequip_weapon'):
                user.unequip_weapon()
            else:
                setattr(user, "weapon", None)
        elif self.slot == "offhand":
            if hasattr(user, 'unequip_offhand'):
                user.unequip_offhand()
            else:
                setattr(user, "offhand", None)
        else:
            # For armor and other slots, remove bonuses and clear slot
            for stat_name, bonus in self.stats.items():
                current_value = user.base_stats.get(stat_name, 0.0)
                new_value = max(0.0, current_value - bonus)
                user.base_stats[stat_name] = new_value
            
            # Remove effect IDs
            for effect_id in self.effect_ids:
                if effect_id in user.skill_effect_ids:
                    user.skill_effect_ids.remove(effect_id)
            
            # Clear the equipment slot
            setattr(user, f"equipped_{self.slot}", None)
        
        # Update actor's computed stats after equipment change
        if hasattr(user, 'update_stats'):
            user.update_stats()
