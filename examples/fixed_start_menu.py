"""
Fixed Simple Start Menu - Non-async version that should work
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

# Import our modular UI system
from rpg_engine.ui.modular_ui_system import ModularUIManager, UIDefinition, WidgetConfig, WidgetType
from rpg_engine.ui.ui_builder import UIBuilder
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus

class FixedStartMenu:
    """Fixed start menu that avoids async issues"""
    
    def __init__(self):
        self.ui_manager = None
        self.current_app = None
        self.setup_services()
    
    def setup_services(self):
        """Setup services without async"""
        print("🔧 Setting up services...")
        
        # Create service container
        self.service_container = ServiceContainer()
        
        # Register services
        self.service_container.register_singleton(EventBus, lambda c: EventBus())
        
        # Create UI manager directly (skip async initialization)
        self.ui_manager = ModularUIManager(self.service_container)
        
        print("✅ Services setup complete")
    
    def create_menu(self):
        """Create menu using UIBuilder"""
        print("🎨 Creating menu definition...")
        
        menu_def = UIDefinition(
            title="🎮 RPG Game Menu",
            geometry="600x400",
            widgets=[
                WidgetConfig(
                    widget_type=WidgetType.LABEL,
                    text="Welcome to RPG Adventure!",
                    layout={'pady': 30}
                ),
                WidgetConfig(
                    widget_type=WidgetType.LABEL,
                    text="Choose your action:",
                    layout={'pady': 10}
                ),
                WidgetConfig(
                    widget_type=WidgetType.BUTTON,
                    text="New Game",
                    command="new_game",
                    layout={'pady': 5}
                ),
                WidgetConfig(
                    widget_type=WidgetType.BUTTON,
                    text="Load Game", 
                    command="load_game",
                    layout={'pady': 5}
                ),
                WidgetConfig(
                    widget_type=WidgetType.BUTTON,
                    text="Settings",
                    command="settings",
                    layout={'pady': 5}
                ),
                WidgetConfig(
                    widget_type=WidgetType.BUTTON,
                    text="Exit",
                    command="exit",
                    layout={'pady': 5}
                )
            ],
            commands={
                "new_game": self.new_game,
                "load_game": self.load_game,
                "settings": self.settings,
                "exit": self.exit_game
            }
        )
        
        print("✅ Menu definition created")
        return menu_def
    
    def new_game(self):
        """Handle new game"""
        messagebox.showinfo("New Game", "🎮 Starting new adventure!")
        print("New game started")
    
    def load_game(self):
        """Handle load game"""
        messagebox.showinfo("Load Game", "💾 Loading your saved adventure!")
        print("Game loaded")
    
    def settings(self):
        """Handle settings"""
        messagebox.showinfo("Settings", "⚙️ Opening game settings...")
        print("Settings opened")
    
    def exit_game(self):
        """Handle exit"""
        if messagebox.askyesno("Exit", "🚪 Are you sure you want to exit?"):
            self.close()
    
    def run(self):
        """Run the menu"""
        print("🎮 Starting Fixed Simple Menu...")
        
        if not self.ui_manager:
            print("❌ UI manager not available")
            return
        
        try:
            # Create menu definition
            menu_def = self.create_menu()
            
            # Create application
            print("🚀 Creating application...")
            self.current_app = self.ui_manager.create_application(menu_def)
            
            print("🌟 Launching menu...")
            
            # Run the application
            self.current_app.run()
            
            print("👋 Menu closed")
            
        except Exception as e:
            print(f"❌ Error running menu: {e}")
            import traceback
            traceback.print_exc()
    
    def close(self):
        """Close the menu"""
        if self.current_app:
            self.current_app.destroy()
            self.current_app = None

def main():
    """Main function"""
    try:
        menu = FixedStartMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\nMenu interrupted")
    except Exception as e:
        print(f"Startup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
