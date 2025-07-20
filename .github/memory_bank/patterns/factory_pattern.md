# Factory Pattern Implementation for GitHub Copilot

This pattern ensures consistent object creation and extensibility through registry-based factories.

## Pattern Structure

```python
from typing import Dict, Type, Any, Optional
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import get_logger

class BaseFactory:
    """Base factory class with registry pattern."""
    
    _registry: Dict[str, Type] = {}
    _config_key: str = ""
    
    @classmethod
    def register(cls, name: str, item_class: Type) -> None:
        """Register a class in the factory."""
        cls._registry[name] = item_class
        logger = get_logger(__name__)
        logger.debug(f"Registered {item_class.__name__} as '{name}'")
    
    @classmethod
    def create(cls, name: str, **kwargs) -> Any:
        """
        Create an object by name with parameters.
        
        Args:
            name: Registered name of the object to create
            **kwargs: Additional parameters for object creation
            
        Returns:
            Created object instance
            
        Raises:
            KeyError: If name is not registered
            ValueError: If creation fails
        """
        if name not in cls._registry:
            available = list(cls._registry.keys())
            raise KeyError(f"Unknown {cls.__name__} '{name}'. Available: {available}")
        
        try:
            item_class = cls._registry[name]
            return item_class(**kwargs)
        except Exception as e:
            logger = get_logger(__name__)
            logger.error(f"Failed to create {name}: {e}")
            raise ValueError(f"Failed to create {name}: {e}")
    
    @classmethod
    def create_from_config(cls, name: str, config_data: Dict[str, Any]) -> Any:
        """
        Create an object from configuration data.
        
        Args:
            name: Object name/identifier
            config_data: Configuration dictionary
            
        Returns:
            Created object with configuration applied
        """
        if name not in cls._registry:
            raise KeyError(f"Unknown {cls.__name__} '{name}'")
        
        item_class = cls._registry[name]
        return item_class.from_config(config_data)
    
    @classmethod
    def get_available(cls) -> list:
        """Get list of available registered names."""
        return list(cls._registry.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a name is registered."""
        return name in cls._registry

# Concrete Factory Example
class ItemFactory(BaseFactory):
    """Factory for creating game items."""
    
    _config_key = "data.items"
    
    @classmethod
    def create_item(cls, item_name: str) -> 'Item':
        """
        Create item from JSON configuration.
        
        Args:
            item_name: Name of item in configuration
            
        Returns:
            Created item instance
        """
        config = ConfigManager()
        items_data = config.get(cls._config_key, {})
        
        if item_name not in items_data:
            available = list(items_data.keys())
            raise KeyError(f"Unknown item '{item_name}'. Available: {available}")
        
        item_config = items_data[item_name]
        item_type = item_config.get('type', 'generic')
        
        # Create using registered class
        item = cls.create(item_type, name=item_name, **item_config)
        return item

# Registration Pattern
def register_item_types():
    """Register all item types with the factory."""
    from game_sys.items.weapon import Weapon
    from game_sys.items.armor import Armor
    from game_sys.items.shield import Shield
    from game_sys.items.consumable import Consumable
    
    ItemFactory.register('weapon', Weapon)
    ItemFactory.register('armor', Armor)
    ItemFactory.register('shield', Shield)
    ItemFactory.register('consumable', Consumable)

# Auto-registration with decorator
def register_item(name: str):
    """Decorator to automatically register item classes."""
    def decorator(cls):
        ItemFactory.register(name, cls)
        return cls
    return decorator

@register_item('special_weapon')
class SpecialWeapon:
    """Example of auto-registered item class."""
    pass
```

## Base Class Pattern

```python
class BaseItem:
    """Base class for all items with factory support."""
    
    def __init__(self, name: str, **kwargs):
        """Initialize base item."""
        self.name = name
        self.config = kwargs
        
    @classmethod
    def from_config(cls, config_data: Dict[str, Any]) -> 'BaseItem':
        """
        Create instance from configuration data.
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            Configured instance
        """
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to dictionary."""
        return {
            'name': self.name,
            'type': self.__class__.__name__.lower(),
            **self.config
        }

class Weapon(BaseItem):
    """Weapon item implementation."""
    
    def __init__(self, name: str, damage: int = 10, **kwargs):
        """Initialize weapon with damage."""
        super().__init__(name, **kwargs)
        self.damage = damage
    
    @classmethod
    def from_config(cls, config_data: Dict[str, Any]) -> 'Weapon':
        """Create weapon from configuration."""
        return cls(
            name=config_data.get('name', 'Unknown Weapon'),
            damage=config_data.get('damage', 10),
            **{k: v for k, v in config_data.items() if k not in ['name', 'damage']}
        )
```

## Service Integration Pattern

```python
class ItemService:
    """Service for item management using factory."""
    
    def __init__(self):
        """Initialize service with factory."""
        self.factory = ItemFactory()
        self.logger = get_logger(__name__)
    
    def create_item(self, item_name: str) -> 'Item':
        """
        Create item using factory.
        
        Args:
            item_name: Name of item to create
            
        Returns:
            Created item instance
            
        Raises:
            ValueError: If item creation fails
        """
        try:
            item = self.factory.create_item(item_name)
            self.logger.info(f"Created item: {item.name}")
            return item
        except KeyError as e:
            self.logger.error(f"Item not found: {e}")
            raise ValueError(f"Item '{item_name}' not found")
        except Exception as e:
            self.logger.error(f"Item creation failed: {e}")
            raise ValueError(f"Failed to create item '{item_name}': {e}")
    
    def get_available_items(self) -> list:
        """Get list of available items."""
        config = ConfigManager()
        items_data = config.get('data.items', {})
        return list(items_data.keys())
    
    def create_multiple_items(self, item_names: list) -> list:
        """Create multiple items with error handling."""
        items = []
        for name in item_names:
            try:
                item = self.create_item(name)
                items.append(item)
            except ValueError as e:
                self.logger.warning(f"Skipped item {name}: {e}")
        return items
```

## Configuration Pattern

```json
# items.json
{
  "iron_sword": {
    "type": "weapon",
    "damage": 15,
    "durability": 100,
    "value": 50
  },
  "leather_armor": {
    "type": "armor",
    "defense": 5,
    "durability": 80,
    "value": 30
  },
  "wooden_shield": {
    "type": "shield",
    "defense": 3,
    "block_chance": 0.15,
    "durability": 60,
    "value": 25
  }
}
```

## Testing Pattern

```python
import pytest
from unittest.mock import Mock, patch
from item_factory import ItemFactory, ItemService

class TestItemFactory:
    """Test cases for ItemFactory."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Clear registry for clean tests
        ItemFactory._registry.clear()
        
    def test_register_and_create(self):
        """Test registration and creation."""
        # Register mock class
        mock_class = Mock()
        ItemFactory.register('test_item', mock_class)
        
        # Test creation
        result = ItemFactory.create('test_item', param1='value1')
        
        assert result == mock_class.return_value
        mock_class.assert_called_once_with(param1='value1')
    
    def test_create_unknown_item(self):
        """Test creation of unregistered item."""
        with pytest.raises(KeyError) as exc_info:
            ItemFactory.create('unknown_item')
        
        assert "Unknown ItemFactory 'unknown_item'" in str(exc_info.value)
    
    @patch('item_factory.ConfigManager')
    def test_create_from_config(self, mock_config):
        """Test creation from configuration."""
        # Setup mock configuration
        mock_config.return_value.get.return_value = {
            'test_item': {
                'type': 'weapon',
                'damage': 20
            }
        }
        
        # Register mock class
        mock_class = Mock()
        mock_class.from_config.return_value = "configured_item"
        ItemFactory.register('weapon', mock_class)
        
        # Test creation
        result = ItemFactory.create_item('test_item')
        
        assert result == "configured_item"
        mock_class.from_config.assert_called_once()

class TestItemService:
    """Test cases for ItemService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = ItemService()
    
    @patch.object(ItemFactory, 'create_item')
    def test_create_item_success(self, mock_create):
        """Test successful item creation."""
        mock_item = Mock()
        mock_item.name = 'test_item'
        mock_create.return_value = mock_item
        
        result = self.service.create_item('test_item')
        
        assert result == mock_item
        mock_create.assert_called_once_with('test_item')
    
    @patch.object(ItemFactory, 'create_item')
    def test_create_item_failure(self, mock_create):
        """Test item creation failure."""
        mock_create.side_effect = KeyError("Item not found")
        
        with pytest.raises(ValueError) as exc_info:
            self.service.create_item('unknown_item')
        
        assert "Item 'unknown_item' not found" in str(exc_info.value)
```

## GitHub Copilot Guidelines

### When to Use Factory Pattern
- ✅ Creating objects from configuration
- ✅ Supporting multiple object types
- ✅ Need for extensible object creation
- ✅ Registry-based type management
- ✅ Plugin-style architecture

### What Copilot Should Generate
- ✅ Registry-based factory classes
- ✅ Proper error handling for unknown types
- ✅ Configuration integration
- ✅ Type safety with proper type hints
- ✅ Comprehensive testing

### Integration Points
- ✅ Service layer uses factories for object creation
- ✅ Configuration drives available types
- ✅ UI components use services, not factories directly
- ✅ Testing validates factory behavior

## Key Benefits

1. **Extensibility**: Easy to add new object types
2. **Configuration Driven**: Objects created from JSON config
3. **Type Safety**: Proper error handling for unknown types
4. **Testability**: Factory behavior easily tested
5. **Consistency**: Standardized object creation
6. **Registry Pattern**: Centralized type management

## GitHub Copilot Tips

- Open this file when implementing object creation
- Use BaseFactory as template for new factories
- Reference service integration for proper usage
- Follow configuration pattern for JSON-driven creation
- Use testing patterns for comprehensive coverage
