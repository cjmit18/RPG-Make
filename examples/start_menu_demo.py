"""
Simple Start Menu Demo - Quick test of the RPG start menu system
"""
import asyncio
import tkinter as tk
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set working directory to project root
os.chdir(str(project_root))

from rpg_engine.ui.start_menu import StartMenuManager
from rpg_engine.ui.modular_ui_system import ModularUIManager
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus

async def run_start_menu_demo():
    """Run a simple start menu demo"""
    print("🎮 Starting RPG Game Menu...")
    
    # Create service container
    service_container = ServiceContainer()
    
    # Register services with proper constructors
    service_container.register_singleton(EventBus, lambda container: EventBus())
    service_container.register_singleton(ModularUIManager, lambda container: ModularUIManager(container))
    
    # Initialize services
    event_bus = await service_container.get_service(EventBus)
    ui_manager = await service_container.get_service(ModularUIManager)
    
    # Create and initialize start menu
    start_menu = StartMenuManager(service_container)
    await start_menu.initialize()
    
    print("✅ Start menu initialized")
    print("🎯 Launching main menu...")
    
    # Run the menu
    start_menu.run_menu()

if __name__ == "__main__":
    try:
        asyncio.run(run_start_menu_demo())
    except KeyboardInterrupt:
        print("\n👋 Menu closed by user")
    except Exception as e:
        print(f"❌ Error running start menu: {e}")
        import traceback
        traceback.print_exc()
