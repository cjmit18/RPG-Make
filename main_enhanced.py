#!/usr/bin/env python3
"""
Enhanced Modular UI with Dynamic Tab System
Demonstrates the improved modular system with dynamic tab loading and proper integration
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).parent  # Current directory is the project root
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

from rpg_engine.ui.modular_ui_system import ModularUIManager, ModularApplication
from rpg_engine.ui.ui_builder import UIBuilder
from rpg_engine.ui.modular_ui_system import LayoutType
from rpg_engine.ui.dynamic_tab_manager import DynamicTabManager
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus
import json
import logging
import tkinter as tk
from tkinter import ttk

# Import tab providers
from tabs.start_screen_provider import StartScreenTabProvider
from tabs.browse_templates_provider import BrowseTemplatesTabProvider
from tabs.character_creation_provider import CharacterCreationTabProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedUIManager:
    """Enhanced UI manager with dynamic tab support"""
    
    def __init__(self, base_ui_manager):
        self.base_ui_manager = base_ui_manager
        self.tab_manager = None
        self.current_app = None
        
        # Tab providers
        self.start_provider = None
        self.browse_provider = None
        self.creation_provider = None
    
    def create_main_application(self) -> 'ModularApplication':
        """Create the main application with fully streamlined integrated UI"""
        
        # Build the completely streamlined UI structure - single content area only
        builder = (
            UIBuilder("🎮 RPG Engine - Enhanced Character Manager")
            .with_size(1400, 900)
            .with_theme("clam")
            .with_layout(LayoutType.PACK)
            
            # Single main content area - everything integrated here
            .begin_frame()
            .with_pack_layout(fill="both", expand=True, padx=5, pady=5)
            .end_container()
            
            # Commands for global access
            .with_command("close_application", self._close_application)
            .with_command("go_home", self._go_home)
            .with_command("refresh_data", self._refresh_data)
        )
        
        # Build the UI definition
        ui_def = builder.build()
        
        # Create the application
        try:
            app = self.base_ui_manager.create_application(ui_def)
            if app:
                app.build_ui()  # Build the UI explicitly
                self.current_app = app
                self.base_ui_manager.current_app = app  # Also set on base manager
                
                self._setup_fully_integrated_ui()
                
                return app
            else:
                logger.error("create_application returned None")
                return None
        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _setup_fully_integrated_ui(self) -> None:
        """Setup fully integrated UI with header, navigation, and tabs all in one streamlined container"""
        try:
            # Find the main content frame (should be the only child now)
            main_frames = []
            for child in self.current_app.root.winfo_children():
                if isinstance(child, (tk.Frame, ttk.Frame)):
                    main_frames.append(child)
            
            if len(main_frames) >= 1:
                main_content_frame = main_frames[0]  # Single content area
                self.setup_streamlined_interface(main_content_frame)
                logger.info("Fully integrated streamlined UI setup completed")
            else:
                logger.error(f"Expected at least 1 frame, found {len(main_frames)}")
                
        except Exception as e:
            logger.error(f"Failed to setup fully integrated UI: {e}")
    
    def setup_streamlined_interface(self, main_content_frame) -> None:
        """Setup the completely streamlined interface with header, navigation, and tabs all integrated"""
        
        # Clear the main content frame
        for widget in main_content_frame.winfo_children():
            widget.destroy()
        
        # Create integrated header/navigation bar
        header_nav_frame = ttk.Frame(main_content_frame)
        header_nav_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Left side - Integrated branding and tab info
        left_section = ttk.Frame(header_nav_frame)
        left_section.pack(side="left", fill="x", expand=True)
        
        # Main title
        title_label = ttk.Label(left_section,
                               text="⚔️ RPG CHARACTER ENGINE ⚔️", 
                               font=("Segoe UI", 20, "bold"), 
                               foreground="#2c3e50")
        title_label.pack(side="left", padx=(0, 15))
        
        # Dynamic subtitle/tab info
        self.tab_info_label = ttk.Label(left_section, 
                                       text="🎯 Advanced Character Management & Creation Suite", 
                                       font=("Segoe UI", 11, "italic"), 
                                       foreground="#7f8c8d")
        self.tab_info_label.pack(side="left", padx=(10, 0))
        
        # Right side - Navigation buttons
        nav_buttons_frame = ttk.Frame(header_nav_frame)
        nav_buttons_frame.pack(side="right", padx=10)
        
        # Create navigation buttons with improved styling
        home_btn = ttk.Button(nav_buttons_frame, text="🏠 Home", 
                             command=self._go_home, width=8)
        home_btn.pack(side="right", padx=3)
        
        refresh_btn = ttk.Button(nav_buttons_frame, text="🔄 Refresh", 
                                command=self._refresh_data, width=10)
        refresh_btn.pack(side="right", padx=3)
        
        exit_btn = ttk.Button(nav_buttons_frame, text="❌ Exit", 
                             command=self._close_application, width=8)
        exit_btn.pack(side="right", padx=3)
        
        # Add separator
        separator = ttk.Separator(main_content_frame, orient="horizontal")
        separator.pack(fill="x", padx=10, pady=(5, 10))
        
        # Create dynamic tab manager in remaining space
        tab_container = ttk.Frame(main_content_frame)
        tab_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.tab_manager = DynamicTabManager(tab_container, ui_manager=self)
        
        # Create and register tab providers
        self.start_provider = StartScreenTabProvider(ui_manager=self)
        self.browse_provider = BrowseTemplatesTabProvider(ui_manager=self)
        self.creation_provider = CharacterCreationTabProvider(ui_manager=self)
        
        # Register tabs - start screen first
        self.tab_manager.register_tab_provider('start_screen', self.start_provider)
        self.tab_manager.register_tab_provider('browse_templates', self.browse_provider)
        self.tab_manager.register_tab_provider('character_creation', self.creation_provider)
        
        # Load the start screen by default
        self.tab_manager.switch_to_tab('start_screen')
        
        logger.info("Fully streamlined interface with integrated header/navigation initialized")
    
    def _show_welcome_tip(self) -> None:
        """Show a welcome tip to the user"""
        from tkinter import messagebox
        
        template_count = getattr(self, 'template_count', 7)
        
        tip_message = f"""🎮 Welcome to RPG Character Engine!
        
🔥 New Features Available:
• Random stat distribution system
• {template_count} character templates with smart AI
• Enhanced UI with character info panels
• Real-time stat validation

💡 Quick Start:
1. Browse templates to explore available classes
2. Use Character Creation for custom builds
3. Try the 'Apply Template' for intelligent stat allocation

🏠 Use the Home button to return to template browser
🔄 Use Refresh to reload template data"""
        
        # Schedule the tip to show after UI is fully loaded
        if self.current_app and self.current_app.root:
            self.current_app.root.after(1000, lambda: messagebox.showinfo("🎮 Welcome!", tip_message))
    
    def switch_to_character_creation(self, template_name: str = None) -> None:
        """Switch to character creation tab with optional template"""
        if template_name:
            # Store template to load when tab becomes active
            self._pending_template = template_name
            logger.info(f"Switching to character creation with template: {template_name}")
        
        if self.tab_manager:
            self.tab_manager.switch_to_tab('character_creation')
            self._update_tab_info("🧙‍♂️ Character Creation - Build Your Perfect Character")
    
    def switch_to_browse_templates(self) -> None:
        """Switch to browse templates tab"""
        if self.tab_manager:
            self.tab_manager.switch_to_tab('browse_templates')
            self._update_tab_info("📋 Browse Templates - Explore Character Archetypes")
            logger.info("Navigated to browse templates tab")
    
    def switch_to_start_screen(self) -> None:
        """Switch to start screen tab"""
        if self.tab_manager:
            self.tab_manager.switch_to_tab('start_screen')
            self._update_tab_info("🎯 Advanced Character Management & Creation Suite")
            logger.info("Navigated to start screen tab")
    
    def _update_tab_info(self, text: str) -> None:
        """Update the tab info label"""
        if hasattr(self, 'tab_info_label'):
            self.tab_info_label.config(text=text)
    
    def update_tab_title(self, tab_id: str, new_title: str) -> None:
        """Update a tab's title"""
        if self.tab_manager and tab_id in self.tab_manager.tab_states:
            tab_state = self.tab_manager.tab_states[tab_id]
            tab_state.title = new_title
            self.tab_manager._update_tab_title(tab_id)
    
    def _close_application(self) -> None:
        """Close the application"""
        if self.current_app:
            self.current_app.root.destroy()
    
    def _go_home(self) -> None:
        """Navigate to the home/start screen tab"""
        if self.tab_manager:
            self.tab_manager.switch_to_tab('start_screen')
            self._update_tab_info("🎯 Advanced Character Management & Creation Suite")
            logger.info("Navigated to start screen tab")
    
    def _refresh_data(self) -> None:
        """Refresh application data"""
        try:
            # Refresh template count
            template_count = load_template_count()
            self.template_count = template_count
            logger.info(f"🔄 Refreshed data - {template_count} templates available")
            
            # Show refresh confirmation
            from tkinter import messagebox
            messagebox.showinfo("Data Refreshed", 
                               f"✅ Successfully refreshed!\n\n📋 {template_count} templates loaded\n🔄 All systems updated")
            
            # If we have active tab providers, refresh them
            if self.start_provider:
                # Refresh start screen stats
                if hasattr(self.start_provider, '_load_stats'):
                    self.start_provider._load_stats()
            
            if self.browse_provider:
                # Trigger a refresh of the browse templates
                if hasattr(self.browse_provider, 'refresh_templates'):
                    self.browse_provider.refresh_templates()
            
            if self.creation_provider:
                # Refresh creation provider if it has a refresh method
                if hasattr(self.creation_provider, 'refresh_data'):
                    self.creation_provider.refresh_data()
                    
        except Exception as e:
            logger.error(f"Failed to refresh data: {e}")
            from tkinter import messagebox
            messagebox.showerror("Refresh Failed", f"❌ Failed to refresh data:\n{str(e)}")

def load_template_count() -> int:
    """Load and return the number of available templates"""
    try:
        data_path = Path(__file__).parent / "data" / "character_templates.json"
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return len(data.get("character_templates", {}))
    except Exception as e:
        logger.warning(f"Could not load template count: {e}")
        return 0

def main():
    """Main entry point"""
    try:
        # Set up service container
        container = ServiceContainer()
        container.register_singleton(EventBus, lambda c: EventBus())
        container.register_singleton(ModularUIManager, ModularUIManager)

        import asyncio
        asyncio.run(container.initialize_all_async())
        base_ui_manager = container.get(ModularUIManager)

        # Load template count for display
        template_count = load_template_count()
        logger.info(f"✅ Loaded {template_count} character templates")

        # Create enhanced UI manager
        ui_manager = EnhancedUIManager(base_ui_manager)
        ui_manager.template_count = template_count  # Store for display
        
        # Create the main application
        app = ui_manager.create_main_application()
        
        if not app or not app.root:
            logger.error("Failed to create application")
            return
        
        logger.info("🎮 Starting Enhanced RPG Character Manager with Integrated UI...")
        
        # Run the application
        app.run()
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()
