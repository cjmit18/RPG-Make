#!/usr/bin/env python3
"""
RPG Engine Showcase Demo v3
===========================

A comprehensive demonstration of the RPG Engine's capabilities featuring:
- Modern character creation workshop
- Combat testing arena  
- Equipment & inventory management
- Character library & saves
- Developer tools & admin panel
- System performance monitoring

This demo showcases the complete service layer architecture and 
demonstrates all major engine features in a polished, user-friendly interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Core system imports
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import get_logger
from game_sys.character.character_creation_service import CharacterCreationService
from game_sys.combat.combat_service import CombatService

# Reusable UI components
from ui.core.window_manager import WindowManager, WindowConfig
from ui.core.tabbed_interface import TabbedInterface, TabConfig, TabContentProvider
from ui.components.character_workshop import CharacterWorkshop, CharacterWorkshopCallbacks, WorkshopConfig
from ui.components.combat_arena import CombatArena, CombatArenaCallbacks, ArenaConfig

# Controller imports
from ui.controllers.admin_panel_controller import AdminPanelController

# Interface imports for type safety
try:
    from interfaces.game_interfaces import UIServiceProtocol
except ImportError:
    class UIServiceProtocol: pass


class DemoTab(Enum):
    """Enumeration for demo tabs."""
    CHARACTER_WORKSHOP = "character_workshop"
    COMBAT_ARENA = "combat_arena"
    INVENTORY_MANAGER = "inventory_manager"
    CHARACTER_LIBRARY = "character_library"
    DEVELOPER_TOOLS = "developer_tools"
    SYSTEM_MONITOR = "system_monitor"


@dataclass
class DemoConfig:
    """Configuration for the demo application."""
    window_title: str = "RPG Engine Showcase Demo v3"
    window_geometry: str = "1400x900"
    theme: str = "modern"
    auto_save: bool = True
    debug_mode: bool = False
    performance_monitoring: bool = True


class CharacterWorkshopTabProvider:
    """Tab content provider for character workshop."""
    
    def __init__(self, character_service: CharacterCreationService, demo_app):
        self.character_service = character_service
        self.demo_app = demo_app
        self.workshop: Optional[CharacterWorkshop] = None
        self.logger = get_logger(f"{__name__}.CharacterWorkshopTab")
    
    def create_content(self, parent: tk.Widget) -> tk.Widget:
        """Create the character workshop content."""
        try:
            # Create callbacks for the workshop
            callbacks = WorkshopCallbacksImpl(self.demo_app)
            
            # Configure workshop
            config = WorkshopConfig(
                show_preview=True,
                show_library_buttons=True,
                show_admin_buttons=False,  # Disable admin buttons - now available in top menu
                auto_preview=False,  # Disable auto preview to test manual creation
                compact_mode=False
            )
            
            # Create workshop component
            self.workshop = CharacterWorkshop(
                parent, 
                self.character_service,
                callbacks,
                config
            )
            
            self.logger.info("Character workshop content created")
            return parent
            
        except Exception as e:
            self.logger.error(f"Failed to create workshop content: {e}")
            # Create error display
            error_label = tk.Label(parent, text=f"Error creating workshop: {e}", fg="red")
            error_label.pack(expand=True)
            return parent
    
    def refresh_content(self) -> None:
        """Refresh the workshop content."""
        if self.workshop:
            self.workshop.refresh()
    
    def on_tab_selected(self) -> None:
        """Called when this tab is selected."""
        self.demo_app.update_status("Character Workshop active - Create and customize characters")
    
    def on_tab_deselected(self) -> None:
        """Called when this tab is deselected."""
        pass
    
    def can_close(self) -> bool:
        """Return whether this tab can be closed."""
        return False  # Core tab, cannot be closed


class CombatArenaTabProvider:
    """Tab content provider for combat arena."""
    
    def __init__(self, combat_service: CombatService, character_service: CharacterCreationService, demo_app):
        self.combat_service = combat_service
        self.character_service = character_service
        self.demo_app = demo_app
        self.arena: Optional[CombatArena] = None
        self.logger = get_logger(f"{__name__}.CombatArenaTab")
    
    def create_content(self, parent: tk.Widget) -> tk.Widget:
        """Create the combat arena content."""
        try:
            # Create callbacks for the arena
            callbacks = ArenaCallbacksImpl(self.demo_app)
            
            # Configure arena
            config = ArenaConfig(
                show_detailed_log=True,
                auto_scroll_log=True,
                show_statistics=True,
                enable_auto_combat=True,
                combat_delay=1.0
            )
            
            # Create arena component
            self.arena = CombatArena(
                parent,
                self.combat_service,
                self.character_service,
                callbacks,
                config
            )
            
            self.logger.info("Combat arena content created")
            return parent
            
        except Exception as e:
            self.logger.error(f"Failed to create arena content: {e}")
            # Create error display
            error_label = tk.Label(parent, text=f"Error creating arena: {e}", fg="red")
            error_label.pack(expand=True)
            return parent
    
    def refresh_content(self) -> None:
        """Refresh the arena content."""
        if self.arena:
            self.arena.refresh()
    
    def on_tab_selected(self) -> None:
        """Called when this tab is selected."""
        self.demo_app.update_status("Combat Arena active - Test combat mechanics and strategies")
    
    def on_tab_deselected(self) -> None:
        """Called when this tab is deselected."""
        pass
    
    def can_close(self) -> bool:
        """Return whether this tab can be closed."""
        return False  # Core tab, cannot be closed


class PlaceholderTabProvider:
    """Placeholder tab content provider for future features."""
    
    def __init__(self, title: str, description: str, demo_app):
        self.title = title
        self.description = description
        self.demo_app = demo_app
    
    def create_content(self, parent: tk.Widget) -> tk.Widget:
        """Create placeholder content."""
        container = tk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Center the content
        center_frame = tk.Frame(container)
        center_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(
            center_frame,
            text=f"🏗️ {self.title}",
            font=("Arial", 18, "bold"),
            fg="#7f8c8d"
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            center_frame,
            text=self.description,
            font=("Arial", 12),
            fg="#95a5a6"
        )
        desc_label.pack(pady=10)
        
        # Coming soon message
        soon_label = tk.Label(
            center_frame,
            text="Coming Soon!",
            font=("Arial", 14, "italic"),
            fg="#e74c3c"
        )
        soon_label.pack(pady=20)
        
        return container
    
    def refresh_content(self) -> None:
        """Refresh placeholder content."""
        pass
    
    def on_tab_selected(self) -> None:
        """Called when this tab is selected."""
        self.demo_app.update_status(f"{self.title} - {self.description}")
    
    def on_tab_deselected(self) -> None:
        """Called when this tab is deselected."""
        pass
    
    def can_close(self) -> bool:
        """Return whether this tab can be closed."""
        return False


class WorkshopCallbacksImpl:
    """Implementation of character workshop callbacks with auto-refresh support."""
    
    def __init__(self, demo_app):
        self.demo_app = demo_app
    
    def on_character_created(self, character: Any) -> None:
        """Called when a character is successfully created."""
        self.demo_app.current_character = character
        self.demo_app.update_status(f"Character '{character.name}' created successfully!")
        # Auto-refresh is now handled by the observer system
    
    def on_character_updated(self, character: Any) -> None:
        """Called when a character is updated."""
        self.demo_app.current_character = character
        # Auto-refresh is now handled by the observer system
    
    def on_status_update(self, message: str, msg_type: str = "info") -> None:
        """Called to update status display."""
        self.demo_app.update_status(message)
    
    def get_admin_service(self):
        """Get admin service for admin panel access."""
        return getattr(self.demo_app.character_service, '_admin_service', None)


class ArenaCallbacksImpl:
    """Implementation of combat arena callbacks."""
    
    def __init__(self, demo_app):
        self.demo_app = demo_app
    
    def on_combat_started(self, attacker: Any, defender: Any) -> None:
        """Called when combat starts."""
        self.demo_app.update_status(f"Combat started: {attacker.name} vs {defender.name}")
    
    def on_combat_finished(self, result: Dict[str, Any]) -> None:
        """Called when combat finishes."""
        self.demo_app.update_status("Combat finished - Check log for details")
    
    def on_status_update(self, message: str, msg_type: str = "info") -> None:
        """Called to update status display."""
        self.demo_app.update_status(message)


class RPGEngineDemoV3:
    """
    Third iteration RPG Engine Demo with comprehensive feature showcase.
    
    This demo provides a complete showcase of the RPG Engine's capabilities
    with a modern, professional interface and extensive functionality using
    reusable UI components.
    """
    
    def __init__(self):
        """Initialize the RPG Engine Demo v3."""
        # Configuration and logging
        self.config = ConfigManager()
        self.demo_config = DemoConfig()
        self.logger = get_logger(__name__)
        
        # Core services
        self.character_service = CharacterCreationService()
        self.combat_service = CombatService()
        
        # UI components
        self.window_manager: Optional[WindowManager] = None
        self.tabbed_interface: Optional[TabbedInterface] = None
        
        # Tab content providers
        self.tab_providers: Dict[str, TabContentProvider] = {}
        
        # UI elements
        self.status_label: Optional[tk.Label] = None
        self.performance_label: Optional[tk.Label] = None
        
        # State management
        self.current_character = None
        self.demo_state: Dict[str, Any] = {
            'initialized': False,
            'performance_data': [],
            'last_update': datetime.now()
        }
        
        # Controllers
        self.admin_controller: Optional[AdminPanelController] = None
        
        self.logger.info("RPG Engine Demo v3 initialized")
    
    def initialize(self) -> bool:
        """Initialize the demo application."""
        try:
            self.logger.info("Starting demo initialization...")
            
            # Create window manager
            window_config = WindowConfig(
                title=self.demo_config.window_title,
                geometry=self.demo_config.window_geometry,
                theme=self.demo_config.theme,
                center_on_screen=True
            )
            
            self.window_manager = WindowManager(window_config)
            
            # Create main window
            root = self.window_manager.create_window()
            
            # Create standard layout
            layout = self.window_manager.create_standard_layout()
            
            # Set up header
            self._create_header(layout['header'])
            
            # Create tabbed interface
            self.tabbed_interface = TabbedInterface(layout['content'])
            
            # Set up tabs
            self._setup_tabs()
            
            # Create status bar
            self._create_status_bar(layout['status'])
            
            # Set up window callbacks
            self._setup_window_callbacks()
            
            # Start performance monitoring
            if self.demo_config.performance_monitoring:
                self._start_performance_monitoring()
            
            self.demo_state['initialized'] = True
            self.logger.info("Demo initialization completed successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Demo initialization failed: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize demo: {e}")
            return False
    
    def _create_header(self, header_frame: tk.Frame) -> None:
        """Create the application header."""
        # Title
        title_label = tk.Label(
            header_frame,
            text="🎮 RPG Engine Showcase Demo v3",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Quick action buttons
        actions_frame = tk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT)
        
        # Admin/Debug dropdown menu
        self._create_admin_debug_menu(actions_frame)
        
        tk.Button(
            actions_frame,
            text="💾 Quick Save",
            command=self._quick_save_character
        ).pack(side=tk.RIGHT, padx=5)
    
    def _setup_tabs(self) -> None:
        """Set up all demo tabs."""
        try:
            # Character Workshop tab
            workshop_provider = CharacterWorkshopTabProvider(self.character_service, self)
            workshop_config = TabConfig(
                tab_id=DemoTab.CHARACTER_WORKSHOP.value,
                title="👤 Character Workshop",
                tooltip="Create and customize characters"
            )
            self.tabbed_interface.add_tab(workshop_config, workshop_provider)
            self.tab_providers[DemoTab.CHARACTER_WORKSHOP.value] = workshop_provider
            
            # Combat Arena tab
            arena_provider = CombatArenaTabProvider(self.combat_service, self.character_service, self)
            arena_config = TabConfig(
                tab_id=DemoTab.COMBAT_ARENA.value,
                title="⚔️ Combat Arena",
                tooltip="Test combat mechanics and strategies"
            )
            self.tabbed_interface.add_tab(arena_config, arena_provider)
            self.tab_providers[DemoTab.COMBAT_ARENA.value] = arena_provider
            
            # Placeholder tabs for future features
            inventory_provider = PlaceholderTabProvider("Inventory Manager", "Manage equipment and items", self)
            inventory_config = TabConfig(
                tab_id=DemoTab.INVENTORY_MANAGER.value,
                title="🎒 Inventory",
                tooltip="Manage equipment and items"
            )
            self.tabbed_interface.add_tab(inventory_config, inventory_provider)
            
            library_provider = PlaceholderTabProvider("Character Library", "Save and load characters", self)
            library_config = TabConfig(
                tab_id=DemoTab.CHARACTER_LIBRARY.value,
                title="📚 Character Library",
                tooltip="Save and load characters"
            )
            self.tabbed_interface.add_tab(library_config, library_provider)
            
            tools_provider = PlaceholderTabProvider("Developer Tools", "Debug and configuration tools", self)
            tools_config = TabConfig(
                tab_id=DemoTab.DEVELOPER_TOOLS.value,
                title="🔧 Developer Tools",
                tooltip="Debug and configuration tools"
            )
            self.tabbed_interface.add_tab(tools_config, tools_provider)
            
            monitor_provider = PlaceholderTabProvider("System Monitor", "Performance and system status", self)
            monitor_config = TabConfig(
                tab_id=DemoTab.SYSTEM_MONITOR.value,
                title="📊 System Monitor",
                tooltip="Performance and system status"
            )
            self.tabbed_interface.add_tab(monitor_config, monitor_provider)
            
            self.logger.info("All demo tabs set up successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup tabs: {e}")
            raise
    
    def _create_status_bar(self, status_frame: tk.Frame) -> None:
        """Create the status bar."""
        # Status label
        self.status_label = tk.Label(
            status_frame,
            text="Ready - Select a tab to begin",
            font=("Arial", 9),
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Performance indicator
        if self.demo_config.performance_monitoring:
            self.performance_label = tk.Label(
                status_frame,
                text="Performance: Monitoring...",
                font=("Arial", 9)
            )
            self.performance_label.pack(side=tk.RIGHT)
    
    def _setup_window_callbacks(self) -> None:
        """Set up window event callbacks."""
        if self.window_manager:
            self.window_manager.register_callback('before_close', self._on_before_close)
            self.window_manager.register_callback('on_close', self._on_close)
            self.window_manager.register_callback('refresh', self._refresh_current_tab)
    
    def _start_performance_monitoring(self) -> None:
        """Start performance monitoring in a separate thread."""
        def monitor():
            while self.demo_state.get('initialized', False):
                try:
                    # Collect performance data
                    perf_data = {
                        'timestamp': datetime.now(),
                        'memory_usage': self._get_memory_usage(),
                        'ui_responsiveness': self._check_ui_responsiveness()
                    }
                    
                    self.demo_state['performance_data'].append(perf_data)
                    
                    # Keep only last 100 entries
                    if len(self.demo_state['performance_data']) > 100:
                        self.demo_state['performance_data'].pop(0)
                    
                    # Update performance display
                    if self.performance_label and self.window_manager.get_root():
                        self.window_manager.get_root().after(0, self._update_performance_display, perf_data)
                    
                    time.sleep(1)  # Update every second
                    
                except Exception as e:
                    self.logger.error(f"Performance monitoring error: {e}")
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except (ImportError, Exception):
            # Fallback to basic memory estimation
            import sys
            return sys.getsizeof(self.demo_state) / 1024 / 1024
    
    def _check_ui_responsiveness(self) -> bool:
        """Check if UI is responsive."""
        try:
            root = self.window_manager.get_root() if self.window_manager else None
            return root and root.winfo_exists()
        except Exception:
            return False
    
    def _update_performance_display(self, perf_data: Dict[str, Any]) -> None:
        """Update the performance display."""
        try:
            memory_mb = perf_data.get('memory_usage', 0)
            responsive = perf_data.get('ui_responsiveness', False)
            
            status_text = f"Memory: {memory_mb:.1f}MB | UI: {'✓' if responsive else '✗'}"
            
            if self.performance_label:
                self.performance_label.config(text=status_text)
                
        except Exception as e:
            self.logger.error(f"Performance display update error: {e}")
    
    # Event handlers
    def _refresh_current_tab(self) -> None:
        """Refresh the currently active tab."""
        if self.tabbed_interface:
            self.tabbed_interface.refresh_active_tab()
    
    def _create_admin_debug_menu(self, parent_frame: tk.Frame) -> None:
        """Create admin/debug dropdown menu."""
        # Create menu button
        menu_button = tk.Menubutton(
            parent_frame,
            text="🔧 Admin/Debug",
            relief=tk.RAISED,
            borderwidth=1
        )
        menu_button.pack(side=tk.RIGHT, padx=5)
        
        # Create dropdown menu
        menu = tk.Menu(menu_button, tearoff=0)
        menu_button.config(menu=menu)
        
        # Admin section
        menu.add_command(label="🔧 Admin Panel", command=self._show_admin_panel)
        menu.add_separator()
        
        # Character management
        menu.add_command(label="🔍 Character Inspector", command=self._show_character_inspector)
        menu.add_command(label="👤 Character Editor", command=self._show_character_editor)
        menu.add_separator()
        
        # Profiler controls
        menu.add_command(label="⏱️ Enable Profiler", command=self._enable_profiler)
        menu.add_command(label="🛑 Disable Profiler", command=self._disable_profiler)
        menu.add_command(label="📊 Show Profiler Results", command=self._show_profiler_results)
        menu.add_command(label="🗑️ Clear Profiler Data", command=self._clear_profiler_data)
        menu.add_separator()
        
        # Debug section
        menu.add_command(label="🐛 Debug Info", command=self._show_debug_info)
        menu.add_command(label="📊 System Stats", command=self._show_system_stats)
        menu.add_separator()
        
        # Item & Inventory management (placeholders)
        inventory_submenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="🎒 Inventory Tools", menu=inventory_submenu)
        inventory_submenu.add_command(label="� Item Creator", command=self._show_item_creator)
        inventory_submenu.add_command(label="⚔️ Weapon Editor", command=self._show_weapon_editor)
        inventory_submenu.add_command(label="🛡️ Armor Editor", command=self._show_armor_editor)
        inventory_submenu.add_command(label="💰 Add Gold", command=self._add_gold_dialog)
        inventory_submenu.add_command(label="🗑️ Clear Inventory", command=self._clear_inventory)
        menu.add_separator()
        
        # Quick actions
        menu.add_command(label="🗑️ Clear All Data", command=self._clear_all_data)
        menu.add_command(label="🔄 Reload Services", command=self._reload_services)
        menu.add_command(label="📝 Export Logs", command=self._export_logs)
        menu.add_separator()
        
        # Performance tools
        menu.add_command(label="⚡ Performance Test", command=self._run_performance_test)
        menu.add_command(label="🧪 Stress Test", command=self._run_stress_test)
    
    def _quick_save_character(self) -> None:
        """Quick save current character to the library."""
        try:
            if self.current_character:
                # Generate save name with timestamp
                save_name = f"QuickSave_{self.current_character.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Get template_id from character or use default
                template_id = getattr(self.current_character, 'template_id', 'unknown')
                if not template_id or template_id == 'unknown':
                    # Try to get it from the character's type or use a fallback
                    if hasattr(self.current_character, 'type') and self.current_character.type == 'Player':
                        template_id = 'hero'  # Default player template
                    else:
                        template_id = 'unknown'
                
                # Use the library service directly to save the character
                library_service = getattr(self.character_service, '_library_service', None)
                if library_service:
                    result = library_service.save_character(
                        self.current_character,
                        save_name,
                        template_id
                    )
                    
                    if result.get('success', False):
                        self.logger.info(f"Quick save successful: {result.get('message', 'Character saved')}")
                        self.update_status(f"Quick saved: {self.current_character.name}")
                    else:
                        error_msg = result.get('message', 'Unknown error')
                        self.logger.error(f"Quick save failed: {error_msg}")
                        self.update_status(f"Quick save failed: {error_msg}")
                else:
                    self.logger.error("Character library service not available")
                    self.update_status("Quick save failed: Library service not available")
                    
            else:
                self.update_status("No character to save")
                
        except Exception as e:
            self.logger.error(f"Quick save error: {e}")
            self.update_status(f"Quick save error: {str(e)}")
    
    def _show_admin_panel(self) -> None:
        """Show the admin panel."""
        try:
            if not self.admin_controller:
                root = self.window_manager.get_root() if self.window_manager else None
                if not root:
                    raise ValueError("No root window available")
                
                # Access the private admin service for now
                admin_service = getattr(self.character_service, '_admin_service', None)
                if not admin_service:
                    raise ValueError("Admin service not available")
                
                self.admin_controller = AdminPanelController(
                    parent_window=root,
                    admin_service=admin_service,
                    character_service=self.character_service,
                    ui_callbacks={}
                )
            
            self.admin_controller.show_admin_panel()
            
        except Exception as e:
            self.logger.error(f"Admin panel error: {e}")
            messagebox.showerror("Error", f"Could not open admin panel: {e}")
    
    def _show_debug_info(self) -> None:
        """Show debug information dialog."""
        try:
            debug_info = []
            debug_info.append(f"=== RPG Engine Debug Info ===")
            debug_info.append(f"Current Character: {self.current_character.name if self.current_character else 'None'}")
            debug_info.append(f"Character Service: {type(self.character_service).__name__}")
            debug_info.append(f"Combat Service: {type(self.combat_service).__name__}")
            debug_info.append(f"Demo State: {len(self.demo_state)} keys")
            debug_info.append(f"Active Tabs: {len(self.tab_providers)}")
            debug_info.append(f"Performance Monitoring: {self.demo_config.performance_monitoring}")
            
            if self.current_character:
                debug_info.append(f"\n=== Current Character Details ===")
                debug_info.append(f"Name: {self.current_character.name}")
                debug_info.append(f"Level: {getattr(self.current_character, 'level', 'N/A')}")
                debug_info.append(f"Grade: {getattr(self.current_character, 'grade', 'N/A')} ({getattr(self.current_character, 'grade_name', 'N/A')})")
                debug_info.append(f"Rarity: {getattr(self.current_character, 'rarity', 'N/A')}")
                debug_info.append(f"Type: {getattr(self.current_character, 'type', 'N/A')}")
            
            debug_text = "\n".join(debug_info)
            
            # Create debug window
            debug_window = tk.Toplevel(self.window_manager.get_root())
            debug_window.title("Debug Information")
            debug_window.geometry("600x400")
            
            # Create text widget with scrollbar
            frame = tk.Frame(debug_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(frame, wrap=tk.WORD)
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            text_widget.insert(tk.END, debug_text)
            text_widget.configure(state=tk.DISABLED)
            
            self.update_status("Debug information displayed")
            
        except Exception as e:
            self.logger.error(f"Debug info error: {e}")
            messagebox.showerror("Error", f"Could not show debug info: {e}")
    
    def _show_system_stats(self) -> None:
        """Show system statistics dialog."""
        try:
            import sys
            import gc
            
            stats_info = []
            stats_info.append(f"=== System Statistics ===")
            stats_info.append(f"Python Version: {sys.version}")
            stats_info.append(f"Platform: {sys.platform}")
            
            # Memory stats
            try:
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                stats_info.append(f"Memory RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
                stats_info.append(f"Memory VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
                stats_info.append(f"CPU Percent: {process.cpu_percent():.2f}%")
            except ImportError:
                stats_info.append("Memory stats: psutil not available")
            
            # Garbage collection stats
            gc_stats = gc.get_stats()
            stats_info.append(f"GC Collections: {len(gc_stats)} generations")
            
            # Performance data
            if self.demo_state.get('performance_data'):
                perf_data = self.demo_state['performance_data']
                stats_info.append(f"\n=== Performance History ===")
                stats_info.append(f"Data Points: {len(perf_data)}")
                if perf_data:
                    latest = perf_data[-1]
                    stats_info.append(f"Latest Memory: {latest.get('memory_usage', 0):.2f} MB")
                    stats_info.append(f"UI Responsive: {latest.get('ui_responsiveness', False)}")
            
            stats_text = "\n".join(stats_info)
            
            # Show in dialog
            messagebox.showinfo("System Statistics", stats_text)
            self.update_status("System statistics displayed")
            
        except Exception as e:
            self.logger.error(f"System stats error: {e}")
            messagebox.showerror("Error", f"Could not show system stats: {e}")
    
    def _show_character_inspector(self) -> None:
        """Show character inspector dialog."""
        try:
            if not self.current_character:
                messagebox.showwarning("Character Inspector", "No character currently loaded")
                return
            
            # Create inspector window
            inspector = tk.Toplevel(self.window_manager.get_root())
            inspector.title(f"Character Inspector - {self.current_character.name}")
            inspector.geometry("800x600")
            
            # Create notebook for tabs
            notebook = ttk.Notebook(inspector)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Basic Info Tab
            basic_frame = ttk.Frame(notebook)
            notebook.add(basic_frame, text="Basic Info")
            
            # Character Editing Frame
            edit_frame = ttk.LabelFrame(basic_frame, text="Character Editor")
            edit_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Level editor
            level_frame = tk.Frame(edit_frame)
            level_frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(level_frame, text="Level:").pack(side=tk.LEFT)
            level_var = tk.StringVar(value=str(getattr(self.current_character, 'level', 1)))
            level_entry = tk.Entry(level_frame, textvariable=level_var, width=10)
            level_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(level_frame, text="Set", 
                     command=lambda: self._set_character_level(int(level_var.get()))).pack(side=tk.LEFT)
            
            # Grade editor
            grade_frame = tk.Frame(edit_frame)
            grade_frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(grade_frame, text="Grade:").pack(side=tk.LEFT)
            grade_var = tk.StringVar(value=str(getattr(self.current_character, 'grade', 0)))
            grade_entry = tk.Entry(grade_frame, textvariable=grade_var, width=10)
            grade_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(grade_frame, text="Set", 
                     command=lambda: self._set_character_grade(int(grade_var.get()))).pack(side=tk.LEFT)
            
            # Rarity editor
            rarity_frame = tk.Frame(edit_frame)
            rarity_frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(rarity_frame, text="Rarity:").pack(side=tk.LEFT)
            rarity_var = tk.StringVar(value=str(getattr(self.current_character, 'rarity', 'COMMON')))
            rarity_combo = ttk.Combobox(rarity_frame, textvariable=rarity_var, width=15,
                                       values=['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE'])
            rarity_combo.pack(side=tk.LEFT, padx=5)
            tk.Button(rarity_frame, text="Set", 
                     command=lambda: self._set_character_rarity(rarity_var.get())).pack(side=tk.LEFT)
            
            # Stats Tab
            stats_frame = ttk.Frame(notebook)
            notebook.add(stats_frame, text="Stats")
            
            # Create text widget for stats display
            stats_text = tk.Text(stats_frame, wrap=tk.WORD)
            stats_scrollbar = tk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=stats_text.yview)
            stats_text.configure(yscrollcommand=stats_scrollbar.set)
            
            stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Get character stats
            stats_info = self._get_character_stats_info()
            stats_text.insert(tk.END, stats_info)
            stats_text.configure(state=tk.DISABLED)
            
            # Inventory Tab (placeholder)
            inventory_frame = ttk.Frame(notebook)
            notebook.add(inventory_frame, text="Inventory")
            tk.Label(inventory_frame, text="Inventory Editor - Coming Soon!", 
                    font=("Arial", 14), fg="gray").pack(expand=True)
            
            self.update_status(f"Character inspector opened for {self.current_character.name}")
            
        except Exception as e:
            self.logger.error(f"Character inspector error: {e}")
            messagebox.showerror("Error", f"Could not open character inspector: {e}")
    
    def _clear_all_data(self) -> None:
        """Clear all data with confirmation."""
        try:
            if messagebox.askyesno("Clear All Data", 
                                  "This will clear all performance data and reset the demo state. Continue?"):
                self.demo_state['performance_data'].clear()
                self.demo_state['last_update'] = datetime.now()
                
                # Clear profiler data if available
                try:
                    from game_sys.utils.profiler import profiler
                    profiler.clear()
                    self.logger.info("Profiler data cleared")
                except Exception as e:
                    self.logger.warning(f"Could not clear profiler data: {e}")
                
                self.update_status("All data cleared")
                self.logger.info("Demo data cleared by user")
                
        except Exception as e:
            self.logger.error(f"Clear data error: {e}")
            messagebox.showerror("Error", f"Could not clear data: {e}")
    
    def _reload_services(self) -> None:
        """Reload services and configurations."""
        try:
            if messagebox.askyesno("Reload Services", 
                                  "This will reload all services and configurations. Continue?"):
                # Reload character service
                self.character_service = CharacterCreationService()
                
                # Reload combat service
                self.combat_service = CombatService()
                
                # Refresh all tabs
                for provider in self.tab_providers.values():
                    if hasattr(provider, 'refresh_content'):
                        provider.refresh_content()
                
                self.update_status("Services reloaded successfully")
                self.logger.info("All services reloaded")
                
        except Exception as e:
            self.logger.error(f"Reload services error: {e}")
            messagebox.showerror("Error", f"Could not reload services: {e}")
    
    def _export_logs(self) -> None:
        """Export logs to a file."""
        try:
            from tkinter import filedialog
            import shutil
            
            # Ask user where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("All files", "*.*")],
                title="Export Logs"
            )
            
            if filename:
                # Copy current log file
                import os
                log_dir = "logs"
                if os.path.exists(log_dir):
                    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
                    if log_files:
                        latest_log = os.path.join(log_dir, sorted(log_files)[-1])
                        shutil.copy2(latest_log, filename)
                        self.update_status(f"Logs exported to {filename}")
                        self.logger.info(f"Logs exported to {filename}")
                    else:
                        messagebox.showwarning("Export Logs", "No log files found")
                else:
                    messagebox.showwarning("Export Logs", "Log directory not found")
                    
        except Exception as e:
            self.logger.error(f"Export logs error: {e}")
            messagebox.showerror("Error", f"Could not export logs: {e}")
    
    def _run_performance_test(self) -> None:
        """Run performance test."""
        try:
            from game_sys.utils.profiler import profiler
            
            if not profiler.is_enabled():
                profiler.enable()
            
            # Run test with profiling
            with profiler.span("performance_test"):
                # Create multiple characters quickly
                test_results = []
                start_time = time.time()
                
                for i in range(10):
                    with profiler.span(f"character_creation_{i}"):
                        char = self.character_service.create_character_preview("hero")
                        test_results.append(char)
                
                end_time = time.time()
                duration = end_time - start_time
            
            # Show results
            profiler.print_summary()
            
            messagebox.showinfo("Performance Test", 
                               f"Created 10 characters in {duration:.3f} seconds\n"
                               f"Average: {duration/10:.3f} seconds per character\n"
                               f"Check console for detailed profiling results")
            
            self.update_status(f"Performance test completed: {duration:.3f}s for 10 characters")
            
        except Exception as e:
            self.logger.error(f"Performance test error: {e}")
            messagebox.showerror("Error", f"Performance test failed: {e}")
    
    def _run_stress_test(self) -> None:
        """Run stress test."""
        try:
            if messagebox.askyesno("Stress Test", 
                                  "This will create 100 characters rapidly. Continue?"):
                from game_sys.utils.profiler import profiler
                
                if not profiler.is_enabled():
                    profiler.enable()
                
                start_time = time.time()
                success_count = 0
                error_count = 0
                
                with profiler.span("stress_test"):
                    for i in range(100):
                        try:
                            char = self.character_service.create_character_preview("warrior")
                            success_count += 1
                        except Exception:
                            error_count += 1
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Show results
                profiler.print_summary()
                
                messagebox.showinfo("Stress Test Results", 
                                   f"Duration: {duration:.3f} seconds\n"
                                   f"Successful: {success_count}\n"
                                   f"Errors: {error_count}\n"
                                   f"Rate: {success_count/duration:.2f} characters/second")
                
                self.update_status(f"Stress test: {success_count} chars in {duration:.3f}s")
                
        except Exception as e:
            self.logger.error(f"Stress test error: {e}")
            messagebox.showerror("Error", f"Stress test failed: {e}")
    
    def _set_character_level(self, level: int) -> None:
        """Set character level using admin service."""
        try:
            if not self.current_character:
                messagebox.showwarning("Set Level", "No character loaded")
                return
            
            admin_service = getattr(self.character_service, '_admin_service', None)
            if not admin_service:
                messagebox.showerror("Set Level", "Admin service not available")
                return
            
            # Ensure admin mode is enabled before attempting to use admin functions
            if hasattr(admin_service, 'enable_admin_mode'):
                admin_service.enable_admin_mode()
            elif hasattr(admin_service, 'set_admin_mode'):
                admin_service.set_admin_mode(True)
            
            if hasattr(admin_service, "set_character_level"):
                result = admin_service.set_character_level(self.current_character, level)
                
                if result.get('success'):
                    messagebox.showinfo("Set Level", result.get('message', 'Level changed'))
                    self.update_status(f"Character level set to {level}")
                    # Refresh current tab
                    self._refresh_current_tab()
                else:
                    error_msg = result.get('message', 'Failed to set level')
                    messagebox.showerror("Set Level", error_msg)
                    self.logger.error(f"Set level failed: {error_msg}")
            else:
                messagebox.showerror("Set Level", "Admin service does not support setting character level")
                return
            
        except ValueError as e:
            messagebox.showerror("Set Level", f"Invalid level value: {str(e)}")
        except Exception as e:
            self.logger.error(f"Set level error: {e}")
            messagebox.showerror("Error", f"Could not set level: {str(e)}")
    
    def _set_character_grade(self, grade: int) -> None:
        """Set character grade using admin service."""
        try:
            if not self.current_character:
                messagebox.showwarning("Set Grade", "No character loaded")
                return
            
            admin_service = getattr(self.character_service, '_admin_service', None)
            if not admin_service:
                messagebox.showerror("Set Grade", "Admin service not available")
                return
            
            result = admin_service.set_character_grade(self.current_character, grade)
            
            if result.get('success'):
                messagebox.showinfo("Set Grade", result.get('message', 'Grade changed'))
                self.update_status(f"Character grade set to {grade}")
                # Refresh current tab
                self._refresh_current_tab()
            else:
                messagebox.showerror("Set Grade", result.get('message', 'Failed to set grade'))
                
        except ValueError as e:
            messagebox.showerror("Set Grade", str(e))
        except Exception as e:
            self.logger.error(f"Set grade error: {e}")
            messagebox.showerror("Error", f"Could not set grade: {e}")
    
    def _set_character_rarity(self, rarity: str) -> None:
        """Set character rarity using admin service."""
        try:
            if not self.current_character:
                messagebox.showwarning("Set Rarity", "No character loaded")
                return
            
            admin_service = getattr(self.character_service, '_admin_service', None)
            if not admin_service:
                messagebox.showerror("Set Rarity", "Admin service not available")
                return
            
            result = admin_service.set_character_rarity(self.current_character, rarity)
            
            if result.get('success'):
                messagebox.showinfo("Set Rarity", result.get('message', 'Rarity changed'))
                self.update_status(f"Character rarity set to {rarity}")
                # Refresh current tab
                self._refresh_current_tab()
            else:
                messagebox.showerror("Set Rarity", result.get('message', 'Failed to set rarity'))
                
        except ValueError as e:
            messagebox.showerror("Set Rarity", str(e))
        except Exception as e:
            self.logger.error(f"Set rarity error: {e}")
            messagebox.showerror("Error", f"Could not set rarity: {e}")
    
    def _get_character_stats_info(self) -> str:
        """Get formatted character stats information."""
        try:
            if not self.current_character:
                return "No character loaded"
            
            char = self.current_character
            info = []
            
            info.append(f"=== {char.name} Stats ===")
            info.append(f"Level: {getattr(char, 'level', 'N/A')}")
            info.append(f"Grade: {getattr(char, 'grade', 'N/A')} ({getattr(char, 'grade_name', 'N/A')})")
            info.append(f"Rarity: {getattr(char, 'rarity', 'N/A')}")
            info.append(f"Type: {getattr(char, 'type', 'N/A')}")
            
            # Base stats
            if hasattr(char, 'stats'):
                info.append(f"\n=== Base Stats ===")
                stats = char.stats
                for stat_name in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma', 'agility', 'luck', 'vitality']:
                    if hasattr(stats, stat_name):
                        value = getattr(stats, stat_name)
                        info.append(f"{stat_name.title()}: {value}")
            
            # Equipment
            if hasattr(char, 'equipment'):
                info.append(f"\n=== Equipment ===")
                equipment = char.equipment
                for slot in ['weapon', 'offhand', 'head', 'body', 'legs', 'feet', 'hands', 'ring', 'necklace']:
                    item = getattr(equipment, slot, None)
                    if item:
                        info.append(f"{slot.title()}: {item.name}")
                    else:
                        info.append(f"{slot.title()}: None")
            
            # Inventory count
            if hasattr(char, 'inventory'):
                inv = char.inventory
                item_count = len(getattr(inv, 'items', []))
                max_size = getattr(inv, 'max_size', 'N/A')
                info.append(f"\n=== Inventory ===")
                info.append(f"Items: {item_count}/{max_size}")
            
            return "\n".join(info)
            
        except Exception as e:
            self.logger.error(f"Get character stats error: {e}")
            return f"Error getting character stats: {e}"
    
    def _show_character_editor(self) -> None:
        """Show standalone character editor dialog."""
        try:
            if not self.current_character:
                messagebox.showwarning("Character Editor", "No character currently loaded")
                return
            
            # Create editor window
            editor = tk.Toplevel(self.window_manager.get_root())
            editor.title(f"Character Editor - {self.current_character.name}")
            editor.geometry("400x300")
            
            # Main frame
            main_frame = tk.Frame(editor)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Character info
            info_frame = ttk.LabelFrame(main_frame, text="Character Information")
            info_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(info_frame, text=f"Name: {self.current_character.name}", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=5, pady=2)
            tk.Label(info_frame, text=f"Type: {getattr(self.current_character, 'type', 'N/A')}").pack(anchor=tk.W, padx=5)
            
            # Quick edit frame
            edit_frame = ttk.LabelFrame(main_frame, text="Quick Edit")
            edit_frame.pack(fill=tk.X, pady=5)
            
            # Level
            level_frame = tk.Frame(edit_frame)
            level_frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(level_frame, text="Level:", width=8).pack(side=tk.LEFT)
            level_var = tk.StringVar(value=str(getattr(self.current_character, 'level', 1)))
            tk.Entry(level_frame, textvariable=level_var, width=10).pack(side=tk.LEFT, padx=5)
            tk.Button(level_frame, text="Set", command=lambda: self._set_character_level(int(level_var.get()))).pack(side=tk.LEFT)
            
            # Grade
            grade_frame = tk.Frame(edit_frame)
            grade_frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(grade_frame, text="Grade:", width=8).pack(side=tk.LEFT)
            grade_var = tk.StringVar(value=str(getattr(self.current_character, 'grade', 0)))
            tk.Entry(grade_frame, textvariable=grade_var, width=10).pack(side=tk.LEFT, padx=5)
            tk.Button(grade_frame, text="Set", command=lambda: self._set_character_grade(int(grade_var.get()))).pack(side=tk.LEFT)
            
            # Rarity
            rarity_frame = tk.Frame(edit_frame)
            rarity_frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(rarity_frame, text="Rarity:", width=8).pack(side=tk.LEFT)
            rarity_var = tk.StringVar(value=str(getattr(self.current_character, 'rarity', 'COMMON')))
            rarity_combo = ttk.Combobox(rarity_frame, textvariable=rarity_var, width=12,
                                       values=['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE'])
            rarity_combo.pack(side=tk.LEFT, padx=5)
            tk.Button(rarity_frame, text="Set", command=lambda: self._set_character_rarity(rarity_var.get())).pack(side=tk.LEFT)
            
            # Actions frame
            actions_frame = tk.Frame(main_frame)
            actions_frame.pack(fill=tk.X, pady=10)
            
            tk.Button(actions_frame, text="Open Full Inspector", 
                     command=self._show_character_inspector).pack(side=tk.LEFT, padx=5)
            tk.Button(actions_frame, text="Close", 
                     command=editor.destroy).pack(side=tk.RIGHT, padx=5)
            
            self.update_status(f"Character editor opened for {self.current_character.name}")
            
        except Exception as e:
            self.logger.error(f"Character editor error: {e}")
            messagebox.showerror("Error", f"Could not open character editor: {e}")
    
    def _enable_profiler(self) -> None:
        """Enable the profiler."""
        try:
            from game_sys.utils.profiler import profiler
            profiler.enable()
            self.update_status("Profiler enabled")
            messagebox.showinfo("Profiler", "Profiler has been enabled")
            
        except Exception as e:
            self.logger.error(f"Enable profiler error: {e}")
            messagebox.showerror("Error", f"Could not enable profiler: {e}")
    
    def _disable_profiler(self) -> None:
        """Disable the profiler."""
        try:
            from game_sys.utils.profiler import profiler
            profiler.disable()
            self.update_status("Profiler disabled")
            messagebox.showinfo("Profiler", "Profiler has been disabled")
            
        except Exception as e:
            self.logger.error(f"Disable profiler error: {e}")
            messagebox.showerror("Error", f"Could not disable profiler: {e}")
    
    def _show_profiler_results(self) -> None:
        """Show profiler results in a dialog."""
        try:
            from game_sys.utils.profiler import profiler
            
            results = profiler.get_results()
            if not results:
                messagebox.showinfo("Profiler Results", "No profiling data available.\nRun some operations with profiler enabled first.")
                return
            
            # Create results window
            results_window = tk.Toplevel(self.window_manager.get_root())
            results_window.title("Profiler Results")
            results_window.geometry("800x600")
            
            # Create text widget with scrollbar
            frame = tk.Frame(results_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(frame, wrap=tk.WORD, font=("Courier", 10))
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Format results
            results_text = "=== Profiler Results ===\n\n"
            for span in results:
                results_text += self._format_profiler_span(span, 0)
            
            text_widget.insert(tk.END, results_text)
            text_widget.configure(state=tk.DISABLED)
            
            # Buttons frame
            buttons_frame = tk.Frame(results_window)
            buttons_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Button(buttons_frame, text="Print to Console", 
                     command=lambda: profiler.print_summary()).pack(side=tk.LEFT)
            tk.Button(buttons_frame, text="Clear Data", 
                     command=lambda: [profiler.clear(), results_window.destroy()]).pack(side=tk.LEFT, padx=5)
            tk.Button(buttons_frame, text="Close", 
                     command=results_window.destroy).pack(side=tk.RIGHT)
            
            self.update_status(f"Profiler results displayed ({len(results)} spans)")
            
        except Exception as e:
            self.logger.error(f"Show profiler results error: {e}")
            messagebox.showerror("Error", f"Could not show profiler results: {e}")
    
    def _format_profiler_span(self, span, indent: int) -> str:
        """Format a profiler span for display."""
        prefix = "  " * indent
        duration_ms = (span.duration or 0) * 1000
        result = f"{prefix}{span.name}: {duration_ms:.2f}ms\n"
        
        for child in span.children:
            result += self._format_profiler_span(child, indent + 1)
        
        return result
    
    def _clear_profiler_data(self) -> None:
        """Clear profiler data."""
        try:
            from game_sys.utils.profiler import profiler
            
            count = len(profiler.get_results())
            profiler.clear()
            
            self.update_status(f"Profiler data cleared ({count} spans)")
            messagebox.showinfo("Profiler", f"Cleared {count} profiling spans")
            
        except Exception as e:
            self.logger.error(f"Clear profiler data error: {e}")
            messagebox.showerror("Error", f"Could not clear profiler data: {e}")
    
    def _show_item_creator(self) -> None:
        """Show item creator dialog (placeholder)."""
        try:
            # Create placeholder dialog
            creator = tk.Toplevel(self.window_manager.get_root())
            creator.title("Item Creator")
            creator.geometry("600x400")
            
            # Main frame
            main_frame = tk.Frame(creator)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            title_label = tk.Label(main_frame, text="🔨 Item Creator", font=("Arial", 18, "bold"), fg="#3498db")
            title_label.pack(pady=20)
            
            # Description
            desc_label = tk.Label(main_frame, text="Advanced item creation and editing tools", font=("Arial", 12), fg="#7f8c8d")
            desc_label.pack(pady=10)
            
            # Features list
            features_frame = tk.Frame(main_frame)
            features_frame.pack(expand=True)
            
            features = [
                "🎯 Create custom weapons with stat bonuses",
                "🛡️ Design armor pieces with resistances", 
                "💎 Generate enchantments and effects",
                "⚗️ Craft consumables and potions",
                "📊 Set item levels, grades, and rarities",
                "🎨 Customize item appearance and descriptions"
            ]
            
            for feature in features:
                tk.Label(features_frame, text=feature, font=("Arial", 11), anchor=tk.W).pack(anchor=tk.W, pady=2)
            
            # Coming soon
            tk.Label(main_frame, text="🚧 Coming Soon in Future Update! 🚧", 
                    font=("Arial", 14, "bold"), fg="#e74c3c").pack(pady=20)
            
            # Close button
            tk.Button(main_frame, text="Close", command=creator.destroy, 
                     font=("Arial", 12)).pack(pady=10)
            
            self.update_status("Item creator dialog displayed")
            
        except Exception as e:
            self.logger.error(f"Item creator error: {e}")
            messagebox.showerror("Error", f"Could not show item creator: {e}")
    
    def _show_weapon_editor(self) -> None:
        """Show weapon editor dialog (placeholder)."""
        messagebox.showinfo("Weapon Editor", 
                           "🔧 Weapon Editor\n\n"
                           "Advanced weapon editing capabilities:\n"
                           "• Modify damage types and values\n"
                           "• Set weapon speed and critical rates\n"
                           "• Add special effects and enchantments\n"
                           "• Configure durability and repair costs\n\n"
                           "🚧 Coming Soon! 🚧")
        self.update_status("Weapon editor - coming soon")
    
    def _show_armor_editor(self) -> None:
        """Show armor editor dialog (placeholder)."""
        messagebox.showinfo("Armor Editor", 
                           "🛡️ Armor Editor\n\n"
                           "Advanced armor editing capabilities:\n"
                           "• Modify defense values and resistances\n"
                           "• Set armor weight and movement penalties\n"
                           "• Add protective enchantments\n"
                           "• Configure durability and appearance\n\n"
                           "🚧 Coming Soon! 🚧")
        self.update_status("Armor editor - coming soon")
    
    def _add_gold_dialog(self) -> None:
        """Show add gold dialog (placeholder)."""
        try:
            if not self.current_character:
                messagebox.showwarning("Add Gold", "No character currently loaded")
                return
            
            amount = simpledialog.askinteger("Add Gold", 
                                           "Enter amount of gold to add:",
                                           minvalue=1, maxvalue=999999)
            if amount:
                # This would normally add gold to character
                messagebox.showinfo("Add Gold", 
                                   f"Added {amount} gold to {self.current_character.name}\n\n"
                                   "Note: This is a placeholder implementation.\n"
                                   "Actual gold system integration coming soon!")
                self.update_status(f"Added {amount} gold (placeholder)")
                
        except Exception as e:
            self.logger.error(f"Add gold error: {e}")
            messagebox.showerror("Error", f"Could not add gold: {e}")
    
    def _clear_inventory(self) -> None:
        """Clear character inventory (placeholder)."""
        try:
            if not self.current_character:
                messagebox.showwarning("Clear Inventory", "No character currently loaded")
                return
            
            if messagebox.askyesno("Clear Inventory", 
                                  f"Clear all items from {self.current_character.name}'s inventory?\n\n"
                                  "This action cannot be undone."):
                # This would normally clear the inventory
                messagebox.showinfo("Clear Inventory", 
                                   f"Inventory cleared for {self.current_character.name}\n\n"
                                   "Note: This is a placeholder implementation.\n"
                                   "Actual inventory system integration coming soon!")
                self.update_status("Inventory cleared (placeholder)")

        except Exception as e:
            self.logger.error(f"Clear inventory error: {e}")
            messagebox.showerror("Error", f"Could not clear inventory: {e}")

    def _on_before_close(self) -> bool:
        """Handle before window close event."""
        # Return False to prevent close, True to allow
        return True
    
    def _on_close(self) -> None:
        """Handle window close event."""
        self.demo_state['initialized'] = False
        self.logger.info("Demo application closed")
    
    # Public methods
    def update_status(self, message: str) -> None:
        """Update the status bar message."""
        if self.status_label:
            self.status_label.config(text=message)
        self.logger.info(f"Status: {message}")
    
    def run(self) -> None:
        """Run the demo application."""
        try:
            if self.initialize():
                self.logger.info("Starting demo main loop...")
                
                # Show initial tab
                if self.tabbed_interface and self.tabbed_interface.get_tab_count() > 0:
                    self.tabbed_interface.select_tab(DemoTab.CHARACTER_WORKSHOP.value)
                
                self.window_manager.run()
            else:
                self.logger.error("Demo initialization failed")
                
        except Exception as e:
            self.logger.error(f"Demo run error: {e}")
            messagebox.showerror("Demo Error", f"Demo encountered an error: {e}")


def main():
    """Main entry point for the RPG Engine Demo v3."""
    try:
        # Create and run the demo
        demo = RPGEngineDemoV3()
        demo.run()
        
    except Exception as e:
        print(f"Demo startup error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
