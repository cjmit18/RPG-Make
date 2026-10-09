"""
Inventory System - Character inventory and equipment management

Handles item storage, equipment slots, and inventory operations
with async support and event-driven updates.
"""
import asyncio
from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass
from enum import Enum

from ...core.service_container import ServiceContainer, AsyncInitializable
from ...core.event_bus import EventBus, GameEvent
from .character_system import Character


# Equipment slot types
class EquipmentSlot(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    BOOTS = "boots"
    GLOVES = "gloves"
    ACCESSORY = "accessory"


# Inventory events
@dataclass(frozen=True)
class ItemAddedEvent(GameEvent):
    character_id: str = ""
    item_id: str = ""
    quantity: int = 0
    slot_type: Optional[str] = None


@dataclass(frozen=True)
class ItemRemovedEvent(GameEvent):
    character_id: str = ""
    item_id: str = ""
    quantity: int = 0


@dataclass(frozen=True)
class ItemEquippedEvent(GameEvent):
    character_id: str = ""
    item_id: str = ""
    equipment_slot: str = ""
    previous_item: Optional[str] = None


# Item data structure
@dataclass
class Item:
    """Basic item data structure"""
    id: str
    name: str
    description: str
    item_type: str
    value: int
    weight: float
    stackable: bool = False
    max_stack: int = 1
    equipable: bool = False
    equipment_slot: Optional[EquipmentSlot] = None
    stat_bonuses: Dict[str, int] = None
    
    def __post_init__(self):
        if self.stat_bonuses is None:
            self.stat_bonuses = {}


# Inventory item entry
@dataclass
class InventoryItem:
    """Item in inventory with quantity"""
    item: Item
    quantity: int = 1


# Inventory System
class InventorySystem(AsyncInitializable):
    """
    Character inventory and equipment management system
    
    Handles item storage, equipment, and inventory operations
    with async patterns and event notifications.
    """
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.event_bus: Optional[EventBus] = None
        
        # Character inventories (character_id -> inventory items)
        self.character_inventories: Dict[str, Dict[str, InventoryItem]] = {}
        
        # Character equipment (character_id -> slot -> item_id)
        self.character_equipment: Dict[str, Dict[EquipmentSlot, str]] = {}
        
        # Item database (would be loaded from external source)
        self.item_database: Dict[str, Item] = {}
        
        # Default inventory size
        self.max_inventory_size = 50
    
    async def initialize_async(self) -> None:
        """Initialize the inventory system"""
        self.event_bus = await self.service_container.get_service(EventBus)
        
        # Initialize with some default items
        await self._load_default_items()
    
    async def _load_default_items(self) -> None:
        """Load default items into the database"""
        default_items = [
            Item(
                id="sword_basic",
                name="Basic Sword", 
                description="A simple iron sword",
                item_type="weapon",
                value=50,
                weight=3.0,
                equipable=True,
                equipment_slot=EquipmentSlot.WEAPON,
                stat_bonuses={"strength": 2, "attack_power": 5}
            ),
            Item(
                id="leather_armor",
                name="Leather Armor",
                description="Basic leather protection",
                item_type="armor",
                value=30,
                weight=5.0,
                equipable=True,
                equipment_slot=EquipmentSlot.ARMOR,
                stat_bonuses={"defense": 3, "constitution": 1}
            ),
            Item(
                id="health_potion",
                name="Health Potion",
                description="Restores health",
                item_type="consumable",
                value=10,
                weight=0.5,
                stackable=True,
                max_stack=10
            )
        ]
        
        for item in default_items:
            self.item_database[item.id] = item
    
    async def get_character_inventory_async(self, character_id: str) -> Dict[str, InventoryItem]:
        """Get character's inventory"""
        if character_id not in self.character_inventories:
            self.character_inventories[character_id] = {}
        return self.character_inventories[character_id]
    
    async def add_item_async(self, 
                           character_id: str, 
                           item_id: str, 
                           quantity: int = 1) -> bool:
        """
        Add item to character inventory
        
        Args:
            character_id: Character to add item to
            item_id: ID of item to add
            quantity: Number of items to add
            
        Returns:
            True if successful, False if inventory full or item not found
        """
        if item_id not in self.item_database:
            return False
        
        item = self.item_database[item_id]
        inventory = await self.get_character_inventory_async(character_id)
        
        # Check inventory space
        if len(inventory) >= self.max_inventory_size and item_id not in inventory:
            return False
        
        # Handle stackable items
        if item.stackable and item_id in inventory:
            current_item = inventory[item_id]
            new_quantity = current_item.quantity + quantity
            
            if new_quantity <= item.max_stack:
                current_item.quantity = new_quantity
            else:
                return False  # Stack would exceed maximum
        else:
            # Add new item
            inventory[item_id] = InventoryItem(item=item, quantity=quantity)
        
        # Publish event
        if self.event_bus:
            await self.event_bus.publish(ItemAddedEvent(
                character_id=character_id,
                item_id=item_id,
                quantity=quantity,
                timestamp=asyncio.get_event_loop().time()
            ))
        
        return True
    
    async def remove_item_async(self, 
                              character_id: str, 
                              item_id: str, 
                              quantity: int = 1) -> bool:
        """
        Remove item from character inventory
        
        Args:
            character_id: Character to remove item from
            item_id: ID of item to remove
            quantity: Number of items to remove
            
        Returns:
            True if successful, False if not enough items
        """
        inventory = await self.get_character_inventory_async(character_id)
        
        if item_id not in inventory:
            return False
        
        current_item = inventory[item_id]
        
        if current_item.quantity < quantity:
            return False
        
        # Remove items
        current_item.quantity -= quantity
        
        # Remove from inventory if quantity reaches 0
        if current_item.quantity <= 0:
            del inventory[item_id]
        
        # Publish event
        if self.event_bus:
            await self.event_bus.publish(ItemRemovedEvent(
                character_id=character_id,
                item_id=item_id,
                quantity=quantity,
                timestamp=asyncio.get_event_loop().time()
            ))
        
        return True
    
    async def equip_item_async(self, 
                             character_id: str, 
                             item_id: str) -> bool:
        """
        Equip an item from inventory
        
        Args:
            character_id: Character to equip item on
            item_id: ID of item to equip
            
        Returns:
            True if successful, False if item can't be equipped
        """
        inventory = await self.get_character_inventory_async(character_id)
        
        if item_id not in inventory:
            return False
        
        item = inventory[item_id].item
        
        if not item.equipable or not item.equipment_slot:
            return False
        
        # Initialize equipment if needed
        if character_id not in self.character_equipment:
            self.character_equipment[character_id] = {}
        
        equipment = self.character_equipment[character_id]
        previous_item = equipment.get(item.equipment_slot)
        
        # Unequip previous item if exists
        if previous_item:
            await self.unequip_item_async(character_id, item.equipment_slot)
        
        # Equip new item
        equipment[item.equipment_slot] = item_id
        
        # Publish event
        if self.event_bus:
            await self.event_bus.publish(ItemEquippedEvent(
                character_id=character_id,
                item_id=item_id,
                equipment_slot=item.equipment_slot.value,
                previous_item=previous_item,
                timestamp=asyncio.get_event_loop().time()
            ))
        
        return True
    
    async def unequip_item_async(self, 
                               character_id: str, 
                               equipment_slot: EquipmentSlot) -> bool:
        """
        Unequip an item from equipment slot
        
        Args:
            character_id: Character to unequip from
            equipment_slot: Slot to unequip
            
        Returns:
            True if successful, False if nothing equipped
        """
        if character_id not in self.character_equipment:
            return False
        
        equipment = self.character_equipment[character_id]
        
        if equipment_slot not in equipment:
            return False
        
        item_id = equipment[equipment_slot]
        del equipment[equipment_slot]
        
        # TODO: Could publish unequip event here
        
        return True
    
    async def get_equipped_items_async(self, character_id: str) -> Dict[EquipmentSlot, str]:
        """Get all equipped items for a character"""
        if character_id not in self.character_equipment:
            return {}
        return self.character_equipment[character_id].copy()
    
    async def get_equipment_bonuses_async(self, character_id: str) -> Dict[str, int]:
        """Calculate total stat bonuses from equipped items"""
        equipped_items = await self.get_equipped_items_async(character_id)
        total_bonuses = {}
        
        for slot, item_id in equipped_items.items():
            if item_id in self.item_database:
                item = self.item_database[item_id]
                for stat, bonus in item.stat_bonuses.items():
                    total_bonuses[stat] = total_bonuses.get(stat, 0) + bonus
        
        return total_bonuses
    
    async def shutdown_async(self) -> None:
        """Cleanup inventory system"""
        self.character_inventories.clear()
        self.character_equipment.clear()
