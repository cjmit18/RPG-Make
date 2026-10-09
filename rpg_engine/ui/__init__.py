"""
UI Module - Comprehensive modular user interface system
Provides easy-to-use components for creating expandable applications

Features:
- Declarative UI definition using simple syntax
- Fluent builder APIs for rapid development
- Custom game-specific widgets
- Template system for common UI patterns
- JSON-driven configuration support
- Event system integration
"""

# Original UI system
from .ui_system import AsyncUIManager, UIComponent

# Modular UI system
from .modular_ui_system import (
    ModularUIManager, ModularApplication, UIDefinition, WidgetConfig, 
    WidgetType, LayoutType, StandardWidgetFactory
)

# Start Menu system
from .start_menu import StartMenuManager

# UI Builders
from .ui_builder import (
    UIBuilder, FormBuilder, DialogBuilder, MenuBuilder, UITemplate,
    create_simple_window, create_form_dialog, create_message_dialog,
    create_confirmation_dialog, create_input_dialog
)

# Custom game widgets
from .custom_widgets import (
    CharacterStatDisplayFactory, HealthBarFactory, InventoryGridFactory,
    SkillTreeFactory, CombatLogFactory, MinimapFactory, ChatSystemFactory,
    AchievementPanelFactory, GameHUDFactory, register_game_widgets,
    update_character_stats, update_health_bar, add_combat_message, add_chat_message
)

# Character creation (existing)
try:
    from .character_creation_screen import CharacterCreationScreen
    _has_character_creation = True
except ImportError:
    _has_character_creation = False

__all__ = [
    # Core UI system
    'AsyncUIManager', 'UIComponent',
    
    # Modular UI system
    'ModularUIManager', 'ModularApplication', 'UIDefinition', 'WidgetConfig',
    'WidgetType', 'LayoutType', 'StandardWidgetFactory',
    
    # Start Menu
    'StartMenuManager',
    
    # Builders
    'UIBuilder', 'FormBuilder', 'DialogBuilder', 'MenuBuilder', 'UITemplate',
    
    # Quick creation functions
    'create_simple_window', 'create_form_dialog', 'create_message_dialog',
    'create_confirmation_dialog', 'create_input_dialog',
    
    # Custom game widgets
    'CharacterStatDisplayFactory', 'HealthBarFactory', 'InventoryGridFactory',
    'SkillTreeFactory', 'CombatLogFactory', 'MinimapFactory', 'ChatSystemFactory',
    'AchievementPanelFactory', 'GameHUDFactory', 'register_game_widgets',
    
    # Widget helpers
    'update_character_stats', 'update_health_bar', 'add_combat_message', 'add_chat_message'
]

# Add character creation if available
if _has_character_creation:
    __all__.append('CharacterCreationScreen')
