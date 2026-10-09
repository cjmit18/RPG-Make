"""
RPG Game Start Menu - Main menu interface using AsyncUIManager bridge
Uses the proper async-sync bridge to integrate with the RPG Engine

Features:
- Uses AsyncUIManager for proper async/sync bridging
- Event-driven communication through EventBus
- Modular UI component integration
- Professional game menu interface
"""
import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from pathlib import Path

# Import the proper async UI bridge
from .ui_system import AsyncUIManager
from ..core.service_container import ServiceContainer
from ..core.event_bus import EventBus, UIUpdateEvent

logger = logging.getLogger(__name__)

class StartMenuManager:
    """Start menu manager using the proper async-sync bridge"""
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.ui_manager: Optional[AsyncUIManager] = None
        
        # Game state
        self.game_title = "🎮 RPG Adventure"
        self.version = "v2.0"
        self.save_directory = Path("saves")
        
        # Ensure save directory exists
        self.save_directory.mkdir(exist_ok=True)
        
        # Menu callbacks
        self.on_new_game: Optional[Callable] = None
        self.on_load_game: Optional[Callable] = None
        self.on_settings: Optional[Callable] = None
        self.on_exit: Optional[Callable] = None
    
    async def initialize(self):
        """Initialize the start menu system using the async bridge"""
        logger.info("Initializing start menu with async-sync bridge...")
        
        # Get the AsyncUIManager (handles the bridge automatically)
        self.ui_manager = await self.service_container.get_service(AsyncUIManager)
        
        logger.info("Start menu initialized with bridge")
    
    async def show_menu(self):
        """Show the start menu using the bridge"""
        if not self.ui_manager:
            logger.error("UI manager not initialized")
            return
        
        logger.info("Displaying start menu through async bridge...")
        
        # Send UI update event to display the menu
        # The AsyncUIManager handles the threading automatically
        menu_data = {
            "title": self.game_title,
            "version": self.version,
            "buttons": [
                {"id": "new_game", "text": "🎯 New Game", "action": "new_game"},
                {"id": "load_game", "text": "📁 Load Game", "action": "load_game"},
                {"id": "settings", "text": "⚙️ Settings", "action": "settings"},
                {"id": "exit", "text": "🚪 Exit", "action": "exit"}
            ]
        }
        
        update_event = UIUpdateEvent(
            source="start_menu",
            component_id="main_menu",
            update_type="show_start_menu",
            data=menu_data
        )
        
        # Publish through the event bus - AsyncUIManager will handle it
        if self.ui_manager.event_bus:
            await self.ui_manager.event_bus.publish(update_event)
            logger.info("Start menu displayed through bridge")
        else:
            logger.error("Event bus not available")
    
    async def handle_menu_action(self, action: str):
        """Handle menu actions through the bridge"""
        logger.info(f"Menu action received: {action}")
        
        if action == "new_game":
            if self.on_new_game:
                self.on_new_game()
            else:
                await self._default_new_game()
        elif action == "load_game":
            if self.on_load_game:
                self.on_load_game()
            else:
                await self._default_load_game()
        elif action == "settings":
            if self.on_settings:
                self.on_settings()
            else:
                await self._default_settings()
        elif action == "exit":
            if self.on_exit:
                self.on_exit()
            else:
                await self._default_exit()
    
    async def _default_new_game(self):
        """Default new game handler"""
        logger.info("Starting new game...")
        # Send event to show character creation
        
    async def _default_load_game(self):
        """Default load game handler"""
        logger.info("Loading game...")
        # Send event to show load dialog
        
    async def _default_settings(self):
        """Default settings handler"""
        logger.info("Opening settings...")
        # Send event to show settings dialog
        
    async def _default_exit(self):
        """Default exit handler"""
        logger.info("Exiting game...")
        # Send event to close application
        
    async def wait_for_close(self):
        """Wait for the menu to close"""
        if self.ui_manager:
            # Wait while the UI is running
            while self.ui_manager.ui_running:
                await asyncio.sleep(0.1)

# ============================================================================
# Demo Function Using Proper Bridge
# ============================================================================

async def demo_bridged_start_menu():
    """Demo the start menu using the proper async-sync bridge"""
    print("🌉 RPG Start Menu - Async Bridge Demo")
    print("=" * 40)
    
    # Set up service container with proper bridge
    service_container = ServiceContainer()
    service_container.register_singleton(EventBus, lambda container: EventBus())
    service_container.register_singleton(AsyncUIManager, lambda container: AsyncUIManager(container))
    
    # Create start menu
    start_menu = StartMenuManager(service_container)
    await start_menu.initialize()
    
    # Set up callbacks
    start_menu.on_new_game = lambda: print("🎮 New game callback triggered!")
    start_menu.on_load_game = lambda: print("📁 Load game callback triggered!")
    start_menu.on_settings = lambda: print("⚙️ Settings callback triggered!")
    start_menu.on_exit = lambda: print("🚪 Exit callback triggered!")
    
    # Show the menu (runs in background thread via bridge)
    await start_menu.show_menu()
    
    print("✅ Menu is now running through async-sync bridge")
    print("🔄 Async code continues while UI runs in separate thread")
    
    # Wait for menu to close
    await start_menu.wait_for_close()
    
    print("👋 Menu closed")

if __name__ == "__main__":
    """Run the bridged start menu demo"""
    import asyncio
    
    try:
        asyncio.run(demo_bridged_start_menu())
    except KeyboardInterrupt:
        print("\\nDemo interrupted")
    except Exception as e:
        print(f"Demo error: {e}")
        logger.exception("Bridged start menu demo failed")
    
    def create_main_menu(self) -> UIDefinition:
        """Create the main start menu"""
        return UIBuilder(f"{self.game_title} - Main Menu") \
            .with_size(800, 600) \
            .with_theme("clam") \
            .add_label("", name="spacer_top") \
            .with_pack_layout(pady=50) \
            .add_label(self.game_title) \
            .with_pack_layout(pady=20) \
            .add_label(self.version) \
            .with_pack_layout(pady=(0, 40)) \
            .add_button("🎯 New Game", command="new_game", width=20) \
            .with_pack_layout(pady=10) \
            .add_button("📁 Load Game", command="load_game", width=20) \
            .with_pack_layout(pady=10) \
            .add_button("⚙️ Settings", command="settings", width=20) \
            .with_pack_layout(pady=10) \
            .add_button("🚪 Exit", command="exit_game", width=20) \
            .with_pack_layout(pady=10) \
            .add_label("", name="spacer_bottom") \
            .with_pack_layout(pady=30) \
            .add_label("© 2025 RPG Adventure Game") \
            .with_pack_layout(side='bottom', pady=10) \
            .with_command("new_game", self.handle_new_game) \
            .with_command("load_game", self.handle_load_game) \
            .with_command("settings", self.handle_settings) \
            .with_command("exit_game", self.handle_exit) \
            .on_init(self.on_menu_init) \
            .build()
    
    def create_new_game_dialog(self) -> UIDefinition:
        """Create new game setup dialog"""
        return DialogBuilder("New Game Setup") \
            .with_size(450, 350) \
            .with_message("Create your character and start your adventure!") \
            .begin_frame("Character Creation") \
                .add_label("Character Name:") \
                .with_pack_layout(anchor='w', padx=20, pady=(10, 5)) \
                .add_entry(variable="character_name") \
                .with_pack_layout(fill='x', padx=20, pady=(0, 10)) \
                .add_label("Choose Class:") \
                .with_pack_layout(anchor='w', padx=20, pady=(10, 5)) \
                .add_combobox(values=["Warrior", "Mage", "Rogue", "Paladin", "Archer"], 
                             variable="character_class") \
                .with_pack_layout(fill='x', padx=20, pady=(0, 10)) \
                .add_label("Difficulty:") \
                .with_pack_layout(anchor='w', padx=20, pady=(10, 5)) \
                .add_combobox(values=["Easy", "Normal", "Hard", "Expert"], 
                             variable="difficulty") \
                .with_pack_layout(fill='x', padx=20, pady=(0, 20)) \
            .end_container() \
            .with_pack_layout(fill='both', expand=True, padx=10, pady=10) \
            .with_buttons([
                {'text': '🎮 Start Adventure', 'command': 'start_game'},
                {'text': '❌ Cancel', 'command': 'cancel_new_game'}
            ]) \
            .with_variable("character_name", "Hero") \
            .with_variable("character_class", "Warrior") \
            .with_variable("difficulty", "Normal") \
            .with_command("start_game", self.start_new_game) \
            .with_command("cancel_new_game", self.cancel_new_game) \
            .build()
    
    def create_load_game_dialog(self) -> UIDefinition:
        """Create load game dialog"""
        # Get list of save files
        save_files = self.get_save_files()
        
        return UIBuilder("Load Game") \
            .with_size(500, 400) \
            .add_label("Select a saved game to continue:", font=('Arial', 12, 'bold')) \
            .with_pack_layout(pady=10) \
            .add_listbox(items=save_files, variable="selected_save") \
            .with_pack_layout(fill='both', expand=True, padx=20, pady=10) \
            .begin_frame() \
                .add_button("📁 Load Selected", command="load_selected", font=('Arial', 11, 'bold')) \
                .with_pack_layout(side='left', padx=5) \
                .add_button("🗑️ Delete Save", command="delete_save") \
                .with_pack_layout(side='left', padx=5) \
                .add_button("📂 Browse Files", command="browse_saves") \
                .with_pack_layout(side='left', padx=5) \
                .add_button("❌ Cancel", command="cancel_load") \
                .with_pack_layout(side='right', padx=5) \
            .end_container() \
            .with_pack_layout(fill='x', padx=20, pady=10) \
            .with_command("load_selected", self.load_selected_game) \
            .with_command("delete_save", self.delete_save_file) \
            .with_command("browse_saves", self.browse_save_files) \
            .with_command("cancel_load", self.cancel_load_game) \
            .build()
    
    def create_settings_dialog(self) -> UIDefinition:
        """Create settings/options dialog"""
        return UIBuilder("Game Settings") \
            .with_size(600, 500) \
            .begin_notebook() \
                .begin_frame("🎮 Gameplay") \
                    .add_label("Gameplay Options", font=('Arial', 12, 'bold')) \
                    .with_pack_layout(pady=10) \
                    .add_checkbutton("Auto-save enabled", variable="auto_save") \
                    .with_pack_layout(anchor='w', padx=20, pady=5) \
                    .add_checkbutton("Show damage numbers", variable="show_damage") \
                    .with_pack_layout(anchor='w', padx=20, pady=5) \
                    .add_checkbutton("Pause on focus loss", variable="pause_on_focus_loss") \
                    .with_pack_layout(anchor='w', padx=20, pady=5) \
                    .add_separator() \
                    .with_pack_layout(fill='x', padx=20, pady=15) \
                    .add_label("Auto-save interval (minutes):") \
                    .with_pack_layout(anchor='w', padx=20) \
                    .add_scale(from_=1, to=30, variable="autosave_interval", orient='horizontal') \
                    .with_pack_layout(fill='x', padx=20, pady=5) \
                .end_container() \
                .begin_frame("🔊 Audio") \
                    .add_label("Audio Settings", font=('Arial', 12, 'bold')) \
                    .with_pack_layout(pady=10) \
                    .add_checkbutton("Master audio enabled", variable="audio_enabled") \
                    .with_pack_layout(anchor='w', padx=20, pady=5) \
                    .add_checkbutton("Music enabled", variable="music_enabled") \
                    .with_pack_layout(anchor='w', padx=20, pady=5) \
                    .add_checkbutton("Sound effects enabled", variable="sfx_enabled") \
                    .with_pack_layout(anchor='w', padx=20, pady=5) \
                    .add_separator() \
                    .with_pack_layout(fill='x', padx=20, pady=15) \
                    .add_label("Master Volume:") \
                    .with_pack_layout(anchor='w', padx=20) \
                    .add_scale(from_=0, to=100, variable="master_volume", orient='horizontal') \
                    .with_pack_layout(fill='x', padx=20, pady=5) \
                    .add_label("Music Volume:") \
                    .with_pack_layout(anchor='w', padx=20) \
                    .add_scale(from_=0, to=100, variable="music_volume", orient='horizontal') \
                    .with_pack_layout(fill='x', padx=20, pady=5) \
                    .add_label("SFX Volume:") \
                    .with_pack_layout(anchor='w', padx=20) \
                    .add_scale(from_=0, to=100, variable="sfx_volume", orient='horizontal') \
                    .with_pack_layout(fill='x', padx=20, pady=5) \
                .end_container() \
                .begin_frame("🖥️ Display") \
                    .add_label("Display Settings", font=('Arial', 12, 'bold')) \
                    .with_pack_layout(pady=10) \
                    .add_checkbutton("Fullscreen mode", variable="fullscreen") \
                    .with_pack_layout(anchor='w', padx=20, pady=5) \
                    .add_checkbutton("V-Sync enabled", variable="vsync") \
                    .with_pack_layout(anchor='w', padx=20, pady=5) \
                    .add_separator() \
                    .with_pack_layout(fill='x', padx=20, pady=15) \
                    .add_label("Resolution:") \
                    .with_pack_layout(anchor='w', padx=20) \
                    .add_combobox(values=["1920x1080", "1600x900", "1366x768", "1280x720", "1024x768"], 
                                 variable="resolution") \
                    .with_pack_layout(fill='x', padx=20, pady=5) \
                    .add_label("UI Scale:") \
                    .with_pack_layout(anchor='w', padx=20) \
                    .add_scale(from_=0.5, to=2.0, variable="ui_scale", orient='horizontal', resolution=0.1) \
                    .with_pack_layout(fill='x', padx=20, pady=5) \
                .end_container() \
            .end_container() \
            .with_pack_layout(fill='both', expand=True, padx=10, pady=10) \
            .begin_frame() \
                .add_button("💾 Save Settings", command="save_settings", font=('Arial', 11, 'bold')) \
                .with_pack_layout(side='left', padx=5) \
                .add_button("🔄 Reset to Defaults", command="reset_settings") \
                .with_pack_layout(side='left', padx=5) \
                .add_button("❌ Cancel", command="cancel_settings") \
                .with_pack_layout(side='right', padx=5) \
            .end_container() \
            .with_pack_layout(fill='x', padx=20, pady=10) \
            .with_variable("auto_save", True) \
            .with_variable("show_damage", True) \
            .with_variable("pause_on_focus_loss", False) \
            .with_variable("autosave_interval", 5) \
            .with_variable("audio_enabled", True) \
            .with_variable("music_enabled", True) \
            .with_variable("sfx_enabled", True) \
            .with_variable("master_volume", 80) \
            .with_variable("music_volume", 70) \
            .with_variable("sfx_volume", 85) \
            .with_variable("fullscreen", False) \
            .with_variable("vsync", True) \
            .with_variable("resolution", "1920x1080") \
            .with_variable("ui_scale", 1.0) \
            .with_command("save_settings", self.save_settings) \
            .with_command("reset_settings", self.reset_settings) \
            .with_command("cancel_settings", self.cancel_settings) \
            .build()
    
    # Event handlers
    def handle_new_game(self):
        """Handle new game button click"""
        logger.info("New game requested")
        
        if self.on_new_game:
            self.on_new_game()
        else:
            # Show new game dialog
            new_game_dialog = self.create_new_game_dialog()
            self.show_dialog(new_game_dialog)
    
    def handle_load_game(self):
        """Handle load game button click"""
        logger.info("Load game requested")
        
        if self.on_load_game:
            self.on_load_game()
        else:
            # Show load game dialog
            load_dialog = self.create_load_game_dialog()
            self.show_dialog(load_dialog)
    
    def handle_settings(self):
        """Handle settings button click"""
        logger.info("Settings requested")
        
        if self.on_settings:
            self.on_settings()
        else:
            # Show settings dialog
            settings_dialog = self.create_settings_dialog()
            self.show_dialog(settings_dialog)
    
    def handle_exit(self):
        """Handle exit button click"""
        logger.info("Exit requested")
        
        # Confirm exit
        if messagebox.askyesno("Exit Game", "Are you sure you want to exit?"):
            if self.on_exit:
                self.on_exit()
            else:
                self.close_menu()
    
    def start_new_game(self):
        """Start a new game with selected character"""
        if not self.ui_manager:
            return
        
        character_name = self.ui_manager.get_variable("character_name").get().strip()
        character_class = self.ui_manager.get_variable("character_class").get()
        difficulty = self.ui_manager.get_variable("difficulty").get()
        
        if not character_name:
            messagebox.showerror("Error", "Please enter a character name!")
            return
        
        # Close dialog and start game
        self.close_current_dialog()
        
        logger.info(f"Starting new game: {character_name} ({character_class}) on {difficulty}")
        messagebox.showinfo("New Game", 
                           f"Starting new adventure!\\n\\n"
                           f"Character: {character_name}\\n"
                           f"Class: {character_class}\\n"
                           f"Difficulty: {difficulty}\\n\\n"
                           f"Good luck on your quest!")
        
        # Here you would initialize the actual game
        # For now, we'll just show a message
        self.close_menu()
    
    def cancel_new_game(self):
        """Cancel new game creation"""
        self.close_current_dialog()
    
    def load_selected_game(self):
        """Load the selected save game"""
        if not self.ui_manager:
            return
        
        # Get selected save (this would need proper implementation)
        selected = "Demo Save Game"  # Placeholder
        
        self.close_current_dialog()
        logger.info(f"Loading game: {selected}")
        messagebox.showinfo("Load Game", f"Loading: {selected}\\n\\nGame loaded successfully!")
        self.close_menu()
    
    def delete_save_file(self):
        """Delete selected save file"""
        if messagebox.askyesno("Delete Save", "Are you sure you want to delete this save file?"):
            messagebox.showinfo("Delete Save", "Save file deleted.")
    
    def browse_save_files(self):
        """Browse for save files"""
        filename = filedialog.askopenfilename(
            title="Select Save File",
            filetypes=[("Save files", "*.sav"), ("All files", "*.*")]
        )
        if filename:
            logger.info(f"Selected save file: {filename}")
    
    def cancel_load_game(self):
        """Cancel load game"""
        self.close_current_dialog()
    
    def save_settings(self):
        """Save game settings"""
        logger.info("Saving settings...")
        
        # Here you would save settings to file
        messagebox.showinfo("Settings", "Settings saved successfully!")
        self.close_current_dialog()
    
    def reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Reset all settings to default values?"):
            logger.info("Resetting settings to defaults")
            # Reset variables to defaults
            messagebox.showinfo("Settings", "Settings reset to defaults.")
    
    def cancel_settings(self):
        """Cancel settings changes"""
        self.close_current_dialog()
    
    def on_menu_init(self, app):
        """Called when menu is initialized"""
        logger.info("Start menu displayed")
        
        # Play menu music (placeholder)
        # self.play_menu_music()
    
    # Utility methods
    def get_save_files(self) -> list:
        """Get list of available save files"""
        save_files = []
        
        if self.save_directory.exists():
            for save_file in self.save_directory.glob("*.sav"):
                save_files.append(save_file.stem)
        
        # Add some demo saves if no real saves exist
        if not save_files:
            save_files = [
                "Demo Save - Level 15 Warrior",
                "Demo Save - Level 8 Mage", 
                "Demo Save - Level 22 Rogue"
            ]
        
        return save_files
    
    def show_dialog(self, dialog_def: UIDefinition):
        """Show a dialog window"""
        if self.ui_manager:
            dialog_app = self.ui_manager.create_application(dialog_def)
            dialog_app.show()
            self.current_dialog = dialog_app
    
    def close_current_dialog(self):
        """Close the current dialog"""
        if hasattr(self, 'current_dialog') and self.current_dialog:
            self.current_dialog.destroy()
            self.current_dialog = None
    
    def run_menu(self):
        """Run the start menu"""
        if not self.ui_manager:
            logger.error("UI manager not initialized")
            return
        
        main_menu = self.create_main_menu()
        self.current_app = self.ui_manager.create_application(main_menu)
        self.current_app.run()
    
    def close_menu(self):
        """Close the start menu"""
        if self.current_app:
            self.current_app.destroy()
            self.current_app = None

# ============================================================================
# Demo/Testing Functions
# ============================================================================

async def demo_start_menu():
    """Demo the start menu system"""
    print("🎮 RPG Start Menu Demo")
    print("=" * 30)
    
    # Set up service container
    service_container = ServiceContainer()
    service_container.register_singleton(EventBus, EventBus)
    service_container.register_singleton(ModularUIManager, ModularUIManager)
    
    # Initialize services
    event_bus = await service_container.get_service(EventBus)
    ui_manager = await service_container.get_service(ModularUIManager)
    
    # Create start menu
    start_menu = StartMenuManager(service_container)
    await start_menu.initialize()
    
    # Set up callbacks (optional)
    start_menu.on_new_game = lambda: print("New game callback triggered!")
    start_menu.on_load_game = lambda: print("Load game callback triggered!")
    start_menu.on_settings = lambda: print("Settings callback triggered!")
    start_menu.on_exit = lambda: print("Exit callback triggered!")
    
    # Run the menu
    start_menu.run_menu()

if __name__ == "__main__":
    """Run the start menu demo"""
    import asyncio
    
    try:
        asyncio.run(demo_start_menu())
    except KeyboardInterrupt:
        print("\\nDemo interrupted")
    except Exception as e:
        print(f"Demo error: {e}")
        logger.exception("Start menu demo failed")
