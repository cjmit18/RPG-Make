"""
Enhanced Equipment Manager
=========================

Comprehensive equipment management system with intelligent dual-wield logic,
conflict resolution, and smart equipment suggestions.

This manager handles all equipment operations including:
- Smart slot availability checking
- Automatic dual-wield management
- Two-handed weapon conflict resolution
- Equipment suggestions and error handling
"""

from typing import Any, Dict, List, Optional, Tuple
from game_sys.logging import get_logger

logger = get_logger(__name__)


class EquipmentManager:
    """
    Advanced equipment management system with comprehensive dual-wield support.
    
    Features:
    - Smart slot availability checking
    - Automatic weapon-to-offhand movement
    - Two-handed weapon handling
    - Intelligent conflict resolution
    - User-friendly error messages
    """
    
    def __init__(self):
        self.logger = logger
        
    def check_equipment_slot_availability(self, actor: Any, item: Any, slot: str) -> Tuple[bool, Optional[str]]:
        """
        Enhanced equipment slot checking with comprehensive dual-wield logic.
        
        Args:
            actor: The character attempting to equip the item
            item: The item to be equipped
            slot: The target equipment slot
            
        Returns:
            tuple: (slot_available: bool, conflict_message: str or None)
        """
        current_weapon = getattr(actor, 'weapon', None)
        current_offhand = getattr(actor, 'offhand', None)
        item_name = getattr(item, 'name', str(item))
        
        if slot == 'weapon':
            return self._check_weapon_slot_availability(item, item_name, current_weapon, current_offhand)
        elif slot == 'offhand':
            return self._check_offhand_slot_availability(item, item_name, current_weapon, current_offhand)
        elif slot == 'two_handed':
            return self._check_two_handed_slot_availability(item, item_name, current_weapon, current_offhand)
        else:
            # Regular armor/accessory slots
            slot_attr = f'equipped_{slot}' if slot != 'ring' else 'ring'
            current_item = getattr(actor, slot_attr, None)
            if current_item is None:
                return True, None
            else:
                current_name = getattr(current_item, 'name', str(current_item))
                return False, f"{slot.title()} slot occupied by {current_name}"

    def _check_weapon_slot_availability(self, item: Any, item_name: str, current_weapon: Any, current_offhand: Any) -> Tuple[bool, Optional[str]]:
        """Check weapon slot availability with dual-wield logic."""
        is_item_dual = getattr(item, 'dual_wield', False)
        is_item_two_handed = getattr(item, 'two_handed', False)
        
        # Two-handed weapons need both slots free
        if is_item_two_handed:
            if current_weapon is None and current_offhand is None:
                return True, None
            else:
                conflicts = []
                if current_weapon: 
                    conflicts.append(f"weapon ({current_weapon.name})")
                if current_offhand: 
                    conflicts.append(f"offhand ({current_offhand.name})")
                return False, f"Two-handed weapon requires both hands free. Currently occupied: {', '.join(conflicts)}"
        
        # No weapon equipped - always available
        if current_weapon is None:
            return True, None
        
        # Weapon slot occupied - analyze dual-wield possibilities
        current_weapon_dual = getattr(current_weapon, 'dual_wield', False)
        current_weapon_two_handed = getattr(current_weapon, 'two_handed', False)
        current_weapon_name = getattr(current_weapon, 'name', str(current_weapon))
        
        # Current weapon is two-handed - cannot dual-wield
        if current_weapon_two_handed:
            return False, f"Cannot equip {item_name}: {current_weapon_name} is two-handed and cannot be dual-wielded"
        
        # Both weapons can dual-wield and offhand is free
        if is_item_dual and current_weapon_dual and current_offhand is None:
            return True, None  # Will auto-move current weapon to offhand
        
        # Generate appropriate conflict messages
        if is_item_dual:
            if not current_weapon_dual:
                return False, f"Cannot dual-wield: {current_weapon_name} is not dual-wieldable"
            elif current_offhand is not None:
                offhand_name = getattr(current_offhand, 'name', str(current_offhand))
                return False, f"Cannot dual-wield: offhand occupied by {offhand_name}. Unequip first."
            else:
                return False, f"Weapon slot occupied by {current_weapon_name}"
        else:
            return False, f"Weapon slot occupied by {current_weapon_name}. Unequip first."

    def _check_offhand_slot_availability(self, item: Any, item_name: str, current_weapon: Any, current_offhand: Any) -> Tuple[bool, Optional[str]]:
        """Check offhand slot availability with dual-wield logic."""
        is_item_dual = getattr(item, 'dual_wield', False)
        slot_restriction = getattr(item, 'slot_restriction', None)
        
        # Offhand slot occupied
        if current_offhand is not None:
            offhand_name = getattr(current_offhand, 'name', str(current_offhand))
            return False, f"Offhand slot occupied by {offhand_name}. Unequip first."
        
        # Check slot restrictions
        if slot_restriction == 'offhand_only':
            # Item can only go in offhand (shields, focuses, etc.)
            if current_weapon and getattr(current_weapon, 'two_handed', False):
                weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                return False, f"Cannot equip {item_name}: {weapon_name} is two-handed and requires both hands"
            return True, None
        
        # Item can dual-wield
        if is_item_dual:
            if current_weapon is None:
                return True, None
            elif getattr(current_weapon, 'dual_wield', False):
                return True, None
            elif getattr(current_weapon, 'two_handed', False):
                weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                return False, f"Cannot dual-wield: {weapon_name} is two-handed"
            else:
                weapon_name = getattr(current_weapon, 'name', str(current_weapon))
                return False, f"Cannot dual-wield: {weapon_name} is not dual-wieldable"
        
        # Regular offhand item
        return True, None

    def _check_two_handed_slot_availability(self, item: Any, item_name: str, current_weapon: Any, current_offhand: Any) -> Tuple[bool, Optional[str]]:
        """Check availability for two-handed weapons."""
        conflicts = []
        if current_weapon:
            weapon_name = getattr(current_weapon, 'name', str(current_weapon))
            conflicts.append(f"weapon ({weapon_name})")
        if current_offhand:
            offhand_name = getattr(current_offhand, 'name', str(current_offhand))
            conflicts.append(f"offhand ({offhand_name})")
        
        if conflicts:
            return False, f"Two-handed weapon requires both hands free. Currently occupied: {', '.join(conflicts)}"
        else:
            return True, None

    def suggest_equipment_resolution(self, actor: Any, item: Any, slot: str) -> str:
        """Suggest alternative actions for equipment conflicts."""
        current_weapon = getattr(actor, 'weapon', None)
        current_offhand = getattr(actor, 'offhand', None)
        is_item_dual = getattr(item, 'dual_wield', False)
        is_item_two_handed = getattr(item, 'two_handed', False)
        
        suggestions = []
        
        if is_item_two_handed:
            if current_weapon:
                suggestions.append("Unequip your main weapon")
            if current_offhand:
                suggestions.append("Unequip your offhand item")
            if suggestions:
                return f"Two-handed weapon needs both hands free. {' and '.join(suggestions)}."
        
        if slot == 'weapon' and is_item_dual and current_weapon:
            current_weapon_dual = getattr(current_weapon, 'dual_wield', False)
            current_weapon_two_handed = getattr(current_weapon, 'two_handed', False)
            
            if current_weapon_two_handed:
                return "Unequip your two-handed weapon first."
            elif current_weapon_dual and current_offhand is not None:
                offhand_name = getattr(current_offhand, 'name', 'offhand item')
                return f"Unequip {offhand_name} first to make room for dual-wielding."
            elif not current_weapon_dual:
                weapon_name = getattr(current_weapon, 'name', 'main weapon')
                return f"Unequip {weapon_name} first (not dual-wieldable)."
        
        elif slot == 'offhand':
            if is_item_dual and current_weapon:
                current_weapon_dual = getattr(current_weapon, 'dual_wield', False)
                current_weapon_two_handed = getattr(current_weapon, 'two_handed', False)
                
                if current_weapon_two_handed:
                    weapon_name = getattr(current_weapon, 'name', 'weapon')
                    return f"Unequip {weapon_name} first (two-handed weapons use both hands)."
                elif not current_weapon_dual:
                    weapon_name = getattr(current_weapon, 'name', 'main weapon')
                    return f"Equip a dual-wieldable weapon first (current: {weapon_name})."
                    
            if current_offhand:
                offhand_name = getattr(current_offhand, 'name', 'offhand item')
                return f"Unequip {offhand_name} first."
        
        return "Try unequipping conflicting items first."

    def get_dual_wield_status_info(self, actor: Any) -> str:
        """Get current dual-wield status for display."""
        current_weapon = getattr(actor, 'weapon', None)
        current_offhand = getattr(actor, 'offhand', None)
        
        if not current_weapon and not current_offhand:
            return "Empty hands - ready for any weapon"
        
        weapon_name = getattr(current_weapon, 'name', 'Unknown') if current_weapon else None
        offhand_name = getattr(current_offhand, 'name', 'Unknown') if current_offhand else None
        
        status_parts = []
        
        if current_weapon:
            weapon_two_handed = getattr(current_weapon, 'two_handed', False)
            weapon_dual = getattr(current_weapon, 'dual_wield', False)
            
            if weapon_two_handed:
                status_parts.append(f"Two-handed: {weapon_name}")
            elif weapon_dual:
                status_parts.append(f"Dual-wieldable: {weapon_name}")
            else:
                status_parts.append(f"Single weapon: {weapon_name}")
        
        if current_offhand:
            offhand_dual = getattr(current_offhand, 'dual_wield', False)
            slot_restriction = getattr(current_offhand, 'slot_restriction', None)
            
            if offhand_dual:
                status_parts.append(f"Dual-wielding: {offhand_name}")
            elif slot_restriction == 'offhand_only':
                status_parts.append(f"Shield/Focus: {offhand_name}")
            else:
                status_parts.append(f"Offhand: {offhand_name}")
        
        return " | ".join(status_parts)

    def execute_dual_wield_weapon_swap(self, actor: Any, new_item: Any) -> bool:
        """
        Execute the weapon-to-offhand move for dual-wielding.
        
        Args:
            actor: The character performing the swap
            new_item: The new item being equipped to weapon slot
            
        Returns:
            bool: True if swap was successful, False otherwise
        """
        current_weapon = getattr(actor, 'weapon', None)
        if not current_weapon or not hasattr(current_weapon, 'dual_wield') or not current_weapon.dual_wield:
            return False
        
        if not hasattr(actor, 'equip_offhand'):
            logger.warning("Actor does not support offhand equipment")
            return False
        
        try:
            # Step 1: Temporarily store current weapon
            temp_weapon = current_weapon
            weapon_name = getattr(temp_weapon, 'name', str(temp_weapon))
            
            # Step 2: Clear weapon slot
            setattr(actor, 'weapon', None)
            
            # Step 3: Move old weapon to offhand
            actor.equip_offhand(temp_weapon)
            
            # Step 4: Log the successful move
            logger.info(f"Moved {weapon_name} to offhand for dual-wielding")
            return True
            
        except Exception as e:
            # Step 5: Restore weapon slot if move failed
            setattr(actor, 'weapon', current_weapon)
            logger.error(f"Failed to move weapon to offhand: {e}")
            return False

    def equip_item_with_smart_logic(
        self, 
        actor: Any, 
        item: Any, 
        preferred_slot: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Equip an item with intelligent dual-wield logic and conflict resolution.
        
        Args:
            actor: The character equipping the item
            item: The item to equip
            preferred_slot: Optional preferred slot (auto-detected if None)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Determine slot if not specified
            slot = preferred_slot or getattr(item, 'slot', None)
            if not slot:
                return False, f"Cannot equip {item.name} - no equipment slot defined"
            
            item_name = getattr(item, 'name', str(item))
            
            # Check slot availability
            slot_available, conflict_message = self.check_equipment_slot_availability(actor, item, slot)
            
            # Handle conflicts
            if not slot_available:
                suggestion = self.suggest_equipment_resolution(actor, item, slot)
                full_message = f"Cannot equip {item_name}: {conflict_message} {suggestion}"
                return False, full_message
            
            # Check if we need automatic dual-wield swap
            weapon_moved_to_offhand = False
            if (slot == 'weapon' and 
                hasattr(item, 'dual_wield') and item.dual_wield and
                getattr(actor, 'weapon', None) is not None and
                getattr(actor, 'offhand', None) is None):
                
                current_weapon = getattr(actor, 'weapon', None)
                if current_weapon and getattr(current_weapon, 'dual_wield', False):
                    weapon_moved_to_offhand = self.execute_dual_wield_weapon_swap(actor, item)
                    if not weapon_moved_to_offhand:
                        return False, f"Failed to move {current_weapon.name} to offhand for dual-wielding"
            
            # Attempt to equip using multiple methods
            success = self._attempt_equipment(actor, item, slot)
            
            if success:
                # Generate success message
                if weapon_moved_to_offhand:
                    message = f"Equipped {item_name} (moved previous weapon to offhand for dual-wielding)"
                else:
                    message = f"Equipped {item_name}"
                    
                # Remove from inventory if equipped successfully and item is in inventory
                if hasattr(actor, 'inventory') and hasattr(actor.inventory, 'remove_item'):
                    # Check if item is actually in inventory before trying to remove
                    if hasattr(actor.inventory, 'has_item') and actor.inventory.has_item(item):
                        actor.inventory.remove_item(item)
                    elif hasattr(actor.inventory, 'items') and item in actor.inventory.items:
                        actor.inventory.remove_item(item)
                    # If item is not in inventory, that's fine - it might be initial equipment
                    
                # Update stats
                if hasattr(actor, 'update_stats'):
                    actor.update_stats()
                    
                return True, message
            else:
                return False, f"Failed to equip {item_name}"
                
        except Exception as e:
            logger.error(f"Error equipping item {item}: {e}")
            return False, f"Equipment error: {e}"

    def _attempt_equipment(self, actor: Any, item: Any, slot: str) -> bool:
        """
        Attempt to equip an item using multiple methods.
        
        Args:
            actor: The character equipping the item
            item: The item to equip
            slot: The equipment slot
            
        Returns:
            bool: True if successful, False otherwise
        """
        item_uuid = getattr(item, 'uuid', None)
        logger.info(f"DEBUG: _attempt_equipment called for {getattr(item, 'name', str(item))} in slot '{slot}'")
        
        # Method 1: UUID-based equipment (preferred)
        if item_uuid and hasattr(actor, 'equip_item_by_uuid'):
            try:
                logger.info(f"DEBUG: Trying Method 1 - equip_item_by_uuid")
                result = actor.equip_item_by_uuid(item_uuid)
                logger.info(f"DEBUG: Method 1 result: {result}")
                return result
            except Exception as e:
                logger.warning(f"UUID-based equipment failed: {e}")
        else:
            logger.info(f"DEBUG: Skipping Method 1 - UUID: {item_uuid}, has_method: {hasattr(actor, 'equip_item_by_uuid')}")
        
        # Method 2: Generic equip_item method
        if item_uuid and hasattr(actor, 'equip_item'):
            try:
                logger.info(f"DEBUG: Trying Method 2 - equip_item")
                result = actor.equip_item(item_uuid)
                logger.info(f"DEBUG: Method 2 result: {result}")
                return result
            except Exception as e:
                logger.warning(f"Generic equip_item failed: {e}")
        else:
            logger.info(f"DEBUG: Skipping Method 2 - UUID: {item_uuid}, has_method: {hasattr(actor, 'equip_item')}")
        
        # Method 3: Slot-specific methods
        logger.info(f"DEBUG: Trying Method 3 - slot-specific methods")
        try:
            if slot == 'weapon' and hasattr(actor, 'equip_weapon'):
                logger.info(f"DEBUG: Method 3 - equip_weapon")
                actor.equip_weapon(item)
                return True
            elif slot == 'offhand' and hasattr(actor, 'equip_offhand'):
                logger.info(f"DEBUG: Method 3 - equip_offhand")
                actor.equip_offhand(item)
                return True
            elif slot in ['body', 'helmet', 'legs', 'feet', 'gloves', 'boots', 'cloak'] and hasattr(actor, 'equip_armor'):
                logger.info(f"DEBUG: Method 3 - equip_armor")
                actor.equip_armor(item)
                return True
            else:
                logger.info(f"DEBUG: Method 3 - no matching slot-specific method for '{slot}'")
        except Exception as e:
            logger.warning(f"Slot-specific equipment failed: {e}")
        if item_uuid and hasattr(actor, 'equip_item_by_uuid'):
            try:
                return actor.equip_item_by_uuid(item_uuid)
            except Exception as e:
                logger.warning(f"UUID-based equipment failed: {e}")
        
        # Method 2: Generic equip_item method
        if item_uuid and hasattr(actor, 'equip_item'):
            try:
                return actor.equip_item(item_uuid)
            except Exception as e:
                logger.warning(f"Generic equip_item failed: {e}")
        
        # Method 3: Slot-specific methods
        try:
            if slot == 'weapon' and hasattr(actor, 'equip_weapon'):
                actor.equip_weapon(item)
                return True
            elif slot == 'offhand' and hasattr(actor, 'equip_offhand'):
                actor.equip_offhand(item)
                return True
            elif slot in ['body', 'helmet', 'legs', 'feet', 'gloves', 'boots', 'cloak'] and hasattr(actor, 'equip_armor'):
                actor.equip_armor(item)
                return True
        except Exception as e:
            logger.warning(f"Slot-specific equipment failed: {e}")
        
        # Method 4: Direct attribute setting (fallback)
        try:
            logger.info(f"DEBUG: Attempting direct attribute setting for slot '{slot}'")
            if slot == 'weapon':
                setattr(actor, 'weapon', item)
                logger.info(f"DEBUG: Successfully set weapon")
                return True
            elif slot == 'offhand':
                setattr(actor, 'offhand', item)
                logger.info(f"DEBUG: Successfully set offhand")
                return True
            elif slot == 'ring':
                logger.info(f"DEBUG: Setting ring to {getattr(item, 'name', str(item))}")
                setattr(actor, 'ring', item)
                logger.info(f"DEBUG: Successfully set ring")
                return True
            else:
                logger.info(f"DEBUG: Setting equipped_{slot}")
                setattr(actor, f'equipped_{slot}', item)
                logger.info(f"DEBUG: Successfully set equipped_{slot}")
                return True
        except Exception as e:
            logger.error(f"Direct attribute setting failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return False

    def unequip_item_from_slot(self, actor: Any, slot: str) -> Tuple[bool, str]:
        """
        Unequip an item from a specific slot.
        
        Args:
            actor: The character unequipping the item
            slot: The slot to unequip from
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Get current item in slot
            if slot == 'weapon':
                current_item = getattr(actor, 'weapon', None)
            elif slot == 'offhand':
                current_item = getattr(actor, 'offhand', None)
            elif slot == 'ring':
                current_item = getattr(actor, 'ring', None)
            else:
                current_item = getattr(actor, f'equipped_{slot}', None)
            
            if not current_item:
                return False, f"No item equipped in {slot} slot"
            
            item_name = getattr(current_item, 'name', str(current_item))
            
            # Attempt unequipping using multiple methods
            success = self._attempt_unequipment(actor, current_item, slot)
            
            if success:
                # Add back to inventory if possible
                if hasattr(actor, 'inventory') and hasattr(actor.inventory, 'add_item'):
                    actor.inventory.add_item(current_item)
                
                # Update stats
                if hasattr(actor, 'update_stats'):
                    actor.update_stats()
                    
                return True, f"Unequipped {item_name} from {slot} slot"
            else:
                return False, f"Failed to unequip {item_name} from {slot} slot"
                
        except Exception as e:
            logger.error(f"Error unequipping from {slot}: {e}")
            return False, f"Unequip error: {e}"

    def _attempt_unequipment(self, actor: Any, item: Any, slot: str) -> bool:
        """
        Attempt to unequip an item using multiple methods.
        
        Args:
            actor: The character unequipping the item
            item: The item to unequip
            slot: The equipment slot
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Method 1: UUID-based unequipment
        if hasattr(actor, 'unequip_item_by_slot'):
            try:
                return actor.unequip_item_by_slot(slot) is not None
            except Exception as e:
                logger.warning(f"UUID-based unequipment failed: {e}")
        
        # Method 2: Slot-specific methods
        try:
            if slot == 'weapon' and hasattr(actor, 'unequip_weapon'):
                actor.unequip_weapon()
                return True
            elif slot == 'offhand' and hasattr(actor, 'unequip_offhand'):
                actor.unequip_offhand()
                return True
            elif hasattr(item, 'unequip'):
                item.unequip(actor)
                return True
        except Exception as e:
            logger.warning(f"Slot-specific unequipment failed: {e}")
        
        # Method 3: Direct attribute clearing (fallback)
        try:
            if slot == 'weapon':
                setattr(actor, 'weapon', None)
                return True
            elif slot == 'offhand':
                setattr(actor, 'offhand', None)
                return True
            elif slot == 'ring':
                setattr(actor, 'ring', None)
                return True
            else:
                setattr(actor, f'equipped_{slot}', None)
                return True
        except Exception as e:
            logger.error(f"Direct attribute clearing failed: {e}")
        
        return False


# Singleton instance for global use
equipment_manager = EquipmentManager()
