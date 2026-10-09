#!/usr/bin/env python3
"""
Simple Enhanced Modular UI - A cleaner, more reliable version
Focuses on working functionality with better styling
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

from rpg_engine.ui.modular_ui_system import ModularUIManager
from rpg_engine.ui.ui_builder import UIBuilder
from rpg_engine.ui.modular_ui_system import LayoutType
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus
import json

# Import tab modules
from tabs import build_browse_templates_tab


def build_ui_def(ui_manager):
    """Build the complete tabbed UI definition"""
    
    # Load tab configuration
    browse_templates_tab = build_browse_templates_tab()
    
    # Build the UI using the fluent UIBuilder pattern
    builder = (
        UIBuilder("🎮 RPG Engine - Enhanced Character Manager")
        .with_size(800, 600)
        .with_theme("clam")
        .with_layout(LayoutType.PACK)
        
        # Header
        .begin_frame()
        .add_label("🎮 RPG Character Engine", 
                  font=("Segoe UI", 24, "bold"), 
                  foreground="#2c3e50")
        .with_pack_layout(pady=20)
        .add_label("Advanced Character Management System", 
                  font=("Segoe UI", 12), 
                  foreground="#7f8c8d")
        .with_pack_layout(pady=(0, 20))
        .end_container()
        .with_pack_layout(fill="x")
        
        # Main content area with tab-like styling
        .begin_frame()
        .with_pack_layout(fill="both", expand=True, padx=20, pady=10)
        
        # Tab header simulation
        .begin_frame()
        .with_pack_layout(fill="x", pady=(0, 10))
        .add_label(browse_templates_tab['title'], 
                  font=("Segoe UI", 14, "bold"), 
                  foreground="#2c3e50",
                  background="#ecf0f1",
                  relief="raised",
                  borderwidth=2)
        .with_pack_layout(fill="x", pady=5, padx=5)
        .end_container()
        
        # Content area
        .begin_frame()
        .with_pack_layout(fill="both", expand=True)
    )
    
    # Add browse templates content
    builder = browse_templates_tab['content_builder'](builder)
    
    # Complete the UI
    builder = (
        builder
        .end_container()  # End content frame
        .end_container()  # End main frame
        
        # Footer
        .begin_frame()
        .add_button("❌ Exit", 
                   command="close_window")
        .with_pack_layout(side="right", padx=20)
        .end_container()
        .with_pack_layout(fill="x", pady=10)
    )
    
    # Register all commands
    all_commands = {}
    
    # Handle commands that need ui_manager
    browse_commands = browse_templates_tab['commands']
    for cmd_name, cmd_func in browse_commands.items():
        if cmd_name == 'view_characters':
            all_commands[cmd_name] = lambda ui_mgr=ui_manager: cmd_func(ui_mgr)
        else:
            all_commands[cmd_name] = cmd_func
    
    # Add main window commands
    all_commands['close_window'] = lambda: ui_manager.current_app.root.destroy()
        
    # Apply all commands
    for command_name, command_func in all_commands.items():
        builder = builder.with_command(command_name, command_func)
    
    return builder.build()

def main():
    """Main entry point"""
    # Set up service container
    container = ServiceContainer()
    container.register_singleton(EventBus, lambda c: EventBus())
    container.register_singleton(ModularUIManager, ModularUIManager)

    import asyncio
    asyncio.run(container.initialize_all_async())
    ui_manager = container.get(ModularUIManager)

    # Load template count for display
    try:
        data_path = Path(__file__).parent / "data" / "character_templates.json"
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        template_count = len(data.get("character_templates", {}))
        print(f"✅ Loaded {template_count} character templates")
    except Exception as e:
        print(f"⚠️ Could not load templates: {e}")
        template_count = 0

    # Build and run the UI
    ui_def = build_ui_def(ui_manager)
    app = ui_manager.create_application(ui_def)
    ui_manager.current_app = app
    
    print("🎮 Starting RPG Character Manager...")
    app.run()

if __name__ == "__main__":
    main()
