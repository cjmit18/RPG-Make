"""
Simple Working Start Menu - Minimal implementation to verify functionality
"""
import asyncio
import tkinter as tk
from tkinter import messagebox
import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set working directory to project root
os.chdir(str(project_root))

# Import our modular UI system
from rpg_engine.ui.modular_ui_system import ModularUIManager
from rpg_engine.ui.ui_builder import UIBuilder
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus

logger = logging.getLogger(__name__)

class SimpleStartMenu:
    """Simple working start menu for testing"""
    
    def __init__(self, service_container):
        self.service_container = service_container
        self.ui_manager = None
        self.current_app = None
    
    async def initialize(self):
        """Initialize the menu"""
        self.ui_manager = await self.service_container.get_service(ModularUIManager)
        logger.info("Simple start menu initialized")
    
    def create_menu(self):
        """Create a simple menu"""
        return UIBuilder("🎮 RPG Game Menu") \
            .with_size(600, 400) \
            .add_label("Welcome to RPG Adventure!") \
            .with_pack_layout(pady=30) \
            .add_label("Choose your action:") \
            .with_pack_layout(pady=10) \
            .add_button("New Game", command="new_game") \
            .with_pack_layout(pady=5) \
            .add_button("Load Game", command="load_game") \
            .with_pack_layout(pady=5) \
            .add_button("Settings", command="settings") \
            .with_pack_layout(pady=5) \
            .add_button("Exit", command="exit") \
            .with_pack_layout(pady=5) \
            .with_command("new_game", self.new_game) \
            .with_command("load_game", self.load_game) \
            .with_command("settings", self.settings) \
            .with_command("exit", self.exit_game) \
            .build()
    
    def new_game(self):
        """Handle new game"""
        messagebox.showinfo("New Game", "Starting new adventure!")
        logger.info("New game started")
    
    def load_game(self):
        """Handle load game"""
        messagebox.showinfo("Load Game", "Loading your saved adventure!")
        logger.info("Game loaded")
    
    def settings(self):
        """Handle settings"""
        messagebox.showinfo("Settings", "Opening game settings...")
        logger.info("Settings opened")
    
    def exit_game(self):
        """Handle exit"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.close()
    
    def run(self):
        """Run the menu"""
        if not self.ui_manager:
            logger.error("UI manager not initialized")
            return
        
        menu_def = self.create_menu()
        self.current_app = self.ui_manager.create_application(menu_def)
        self.current_app.run()
    
    def close(self):
        """Close the menu"""
        if self.current_app:
            self.current_app.destroy()

async def test_simple_menu():
    """Test the simple menu"""
    print("🎮 Testing Simple Start Menu...")
    
    # Setup services
    container = ServiceContainer()
    container.register_singleton(EventBus, lambda c: EventBus())
    container.register_singleton(ModularUIManager, lambda c: ModularUIManager(c))
    
    # Create menu
    menu = SimpleStartMenu(container)
    await menu.initialize()
    
    print("✅ Menu created successfully")
    print("🚀 Launching menu...")
    
    # Run the menu (this will block until window is closed)
    menu.run()
    
    print("👋 Menu closed")

def main():
    """Main function that handles the async setup properly"""
    # Run the async initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Initialize async components
        container = ServiceContainer()
        container.register_singleton(EventBus, lambda c: EventBus())
        container.register_singleton(ModularUIManager, lambda c: ModularUIManager(c))
        
        menu = SimpleStartMenu(container)
        
        # Initialize async
        loop.run_until_complete(menu.initialize())
        
        print("🎮 Testing Simple Start Menu...")
        print("✅ Menu created successfully")
        print("🚀 Launching menu...")
        
        # Run the UI (this blocks until closed)
        menu.run()
        
        print("👋 Menu closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        loop.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMenu interrupted")
    except Exception as e:
        print(f"Startup error: {e}")
        import traceback
        traceback.print_exc()
