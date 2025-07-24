"""
UI Controllers Package
=====================

Controller classes for managing UI interactions and business logic.

Controllers:
- AdminPanelController: Administrative interface management
- CharacterController: Character-related UI operations
- CombatController: Combat interface management
- InventoryController: Inventory UI management

Features:
- Separation of UI and business logic
- Event handling and delegation
- State management for UI components
- Cross-controller communication
"""

try:
    from .admin_panel_controller import AdminPanelController
except ImportError:
    AdminPanelController = None

__all__ = [
    "AdminPanelController",
]