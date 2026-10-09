"""
Modular UI Demo - Complete demonstration of the modular UI system
Shows how to create complex applications with minimal code using declarative syntax

This demo includes:
1. Simple applications using UIBuilder
2. Form creation with FormBuilder
3. Dialog systems
4. Custom game widgets
5. Template-based UIs
6. JSON-driven UI definitions
"""
import asyncio
import tkinter as tk
from tkinter import messagebox
import logging
from typing import Dict, Any, Optional
import json

# Import our modular UI components
from rpg_engine.ui.modular_ui_system import ModularUIManager, UIDefinition, WidgetConfig, WidgetType, LayoutType
from rpg_engine.ui.ui_builder import UIBuilder, FormBuilder, DialogBuilder, UITemplate, create_form_dialog
from rpg_engine.ui.custom_widgets import register_game_widgets, update_character_stats, add_combat_message
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ModularUIDemo:
    """Complete demonstration of the modular UI system"""
    
    def __init__(self):
        self.service_container = ServiceContainer()
        self.ui_manager: Optional[ModularUIManager] = None
        self.current_app = None
        
        # Demo data
        self.character_stats = {
            'strength': 15,
            'dexterity': 12,
            'intelligence': 18,
            'constitution': 14,
            'health': 140,
            'mana': 180
        }
        
        self.sample_skills = [
            {'name': 'Fireball', 'description': 'Casts a ball of fire', 'level': 3, 'max_level': 5},
            {'name': 'Heal', 'description': 'Restores health points', 'level': 2, 'max_level': 5},
            {'name': 'Shield', 'description': 'Creates a protective barrier', 'level': 1, 'max_level': 3}
        ]
        
        self.sample_achievements = [
            {'name': 'First Steps', 'description': 'Complete the tutorial', 'completed': True},
            {'name': 'Monster Slayer', 'description': 'Defeat 100 monsters', 'completed': False, 'progress': 45, 'max_progress': 100},
            {'name': 'Treasure Hunter', 'description': 'Find 50 treasure chests', 'completed': False, 'progress': 12, 'max_progress': 50}
        ]
    
    async def initialize(self):
        """Initialize the demo"""
        logger.info("Initializing Modular UI Demo...")
        
        # Set up service container
        self.service_container.register_singleton(EventBus, EventBus)
        self.service_container.register_singleton(ModularUIManager, ModularUIManager)
        
        # Initialize services
        event_bus = await self.service_container.get_service(EventBus)
        self.ui_manager = await self.service_container.get_service(ModularUIManager)
        
        # Register custom game widgets
        register_game_widgets(self.ui_manager)
        
        logger.info("Demo initialized successfully")
    
    def create_main_menu(self) -> UIDefinition:
        """Create the main demo menu"""
        return UIBuilder("Modular UI System Demo") \
            .with_size(600, 500) \
            .with_theme("clam") \
            .add_label("🎮 Modular UI System Demonstration", font=('Arial', 16, 'bold')) \
            .with_grid_layout(0, 0, columnspan=2, pady=20) \
            .add_label("Choose a demo to explore the capabilities:") \
            .with_grid_layout(1, 0, columnspan=2, pady=10) \
            .begin_frame("Basic Examples") \
                .add_button("Simple Window Demo", command="show_simple_window") \
                .with_pack_layout(fill='x', pady=2) \
                .add_button("Form Builder Demo", command="show_form_demo") \
                .with_pack_layout(fill='x', pady=2) \
                .add_button("Dialog System Demo", command="show_dialog_demo") \
                .with_pack_layout(fill='x', pady=2) \
            .end_container() \
            .with_grid_layout(2, 0, sticky='ew', padx=5, pady=10) \
            .begin_frame("Game Widgets") \
                .add_button("Character Stats Demo", command="show_character_demo") \
                .with_pack_layout(fill='x', pady=2) \
                .add_button("Game HUD Demo", command="show_hud_demo") \
                .with_pack_layout(fill='x', pady=2) \
                .add_button("Inventory System Demo", command="show_inventory_demo") \
                .with_pack_layout(fill='x', pady=2) \
            .end_container() \
            .with_grid_layout(2, 1, sticky='ew', padx=5, pady=10) \
            .begin_frame("Advanced Features") \
                .add_button("Template System Demo", command="show_template_demo") \
                .with_pack_layout(fill='x', pady=2) \
                .add_button("JSON Configuration Demo", command="show_json_demo") \
                .with_pack_layout(fill='x', pady=2) \
                .add_button("Event Integration Demo", command="show_event_demo") \
                .with_pack_layout(fill='x', pady=2) \
            .end_container() \
            .with_grid_layout(3, 0, sticky='ew', padx=5, pady=10) \
            .add_separator() \
            .with_grid_layout(4, 0, columnspan=2, sticky='ew', pady=10) \
            .add_button("Exit Demo", command="exit_demo") \
            .with_grid_layout(5, 1, sticky='e', pady=10) \
            .with_command("show_simple_window", self.show_simple_window) \
            .with_command("show_form_demo", self.show_form_demo) \
            .with_command("show_dialog_demo", self.show_dialog_demo) \
            .with_command("show_character_demo", self.show_character_demo) \
            .with_command("show_hud_demo", self.show_hud_demo) \
            .with_command("show_inventory_demo", self.show_inventory_demo) \
            .with_command("show_template_demo", self.show_template_demo) \
            .with_command("show_json_demo", self.show_json_demo) \
            .with_command("show_event_demo", self.show_event_demo) \
            .with_command("exit_demo", self.exit_demo) \
            .build()
    
    def show_simple_window(self):
        """Show simple window demo"""
        logger.info("Showing simple window demo")
        
        # Create a simple window with various widgets
        ui_def = UIBuilder("Simple Window Demo") \
            .with_size(500, 400) \
            .add_label("Simple Window Created with UIBuilder", font=('Arial', 14, 'bold')) \
            .with_pack_layout(pady=10) \
            .begin_frame("Input Controls") \
                .add_label("Enter your name:") \
                .with_pack_layout(anchor='w') \
                .add_entry(variable="user_name") \
                .with_pack_layout(fill='x', pady=5) \
                .add_label("Choose your favorite color:") \
                .with_pack_layout(anchor='w') \
                .add_combobox(values=["Red", "Green", "Blue", "Yellow"], variable="favorite_color") \
                .with_pack_layout(fill='x', pady=5) \
                .add_checkbutton("Subscribe to newsletter", variable="subscribe") \
                .with_pack_layout(anchor='w', pady=5) \
            .end_container() \
            .with_pack_layout(fill='x', padx=20, pady=10) \
            .begin_frame("Actions") \
                .add_button("Show Info", command="show_info") \
                .with_pack_layout(side='left', padx=5) \
                .add_button("Clear Form", command="clear_form") \
                .with_pack_layout(side='left', padx=5) \
                .add_button("Close", command="close_window") \
                .with_pack_layout(side='right', padx=5) \
            .end_container() \
            .with_pack_layout(fill='x', padx=20, pady=10) \
            .add_text(value="This is a multi-line text area.\\nYou can type here...") \
            .with_pack_layout(fill='both', expand=True, padx=20, pady=10) \
            .with_variable("user_name", "John Doe") \
            .with_variable("favorite_color", "Blue") \
            .with_variable("subscribe", False) \
            .with_command("show_info", lambda: self.show_user_info()) \
            .with_command("clear_form", lambda: self.clear_simple_form()) \
            .with_command("close_window", lambda: self.close_current_app()) \
            .build()
        
        self.run_application(ui_def)
    
    def show_form_demo(self):
        """Show form builder demo"""
        logger.info("Showing form demo")
        
        # Create a registration form
        form_def = FormBuilder("User Registration Form") \
            .add_text_field("username", "Username:", required=True) \
            .add_password_field("password", "Password:") \
            .add_text_field("email", "Email Address:") \
            .add_dropdown("country", "Country:", ["USA", "Canada", "UK", "Germany", "France"]) \
            .add_checkbox_field("terms", "I agree to the terms and conditions") \
            .add_text_area("bio", "Biography:", rows=4) \
            .add_button_row([ \
                {'text': 'Register', 'command': 'handle_register'}, \
                {'text': 'Cancel', 'command': 'handle_cancel'} \
            ]) \
            .build()
        
        # Add commands
        form_def.commands['handle_register'] = lambda: self.handle_registration()
        form_def.commands['handle_cancel'] = lambda: self.close_current_app()
        
        self.run_application(form_def)
    
    def show_dialog_demo(self):
        """Show dialog system demo"""
        logger.info("Showing dialog demo")
        
        # Create a dialog demo window
        ui_def = UIBuilder("Dialog System Demo") \
            .with_size(400, 300) \
            .add_label("Dialog System Demonstration", font=('Arial', 14, 'bold')) \
            .with_pack_layout(pady=20) \
            .add_label("Click buttons to show different types of dialogs:") \
            .with_pack_layout(pady=10) \
            .begin_frame() \
                .add_button("Message Dialog", command="show_message") \
                .with_pack_layout(pady=5, fill='x') \
                .add_button("Confirmation Dialog", command="show_confirm") \
                .with_pack_layout(pady=5, fill='x') \
                .add_button("Input Dialog", command="show_input") \
                .with_pack_layout(pady=5, fill='x') \
                .add_button("Custom Dialog", command="show_custom") \
                .with_pack_layout(pady=5, fill='x') \
            .end_container() \
            .with_pack_layout(padx=50, pady=20, fill='x') \
            .add_button("Close", command="close_window") \
            .with_pack_layout(pady=20) \
            .with_command("show_message", lambda: messagebox.showinfo("Message", "This is a message dialog!")) \
            .with_command("show_confirm", lambda: messagebox.askyesno("Confirm", "Are you sure?")) \
            .with_command("show_input", lambda: self.show_input_dialog()) \
            .with_command("show_custom", lambda: self.show_custom_dialog()) \
            .with_command("close_window", lambda: self.close_current_app()) \
            .build()
        
        self.run_application(ui_def)
    
    def show_character_demo(self):
        """Show character stats demo"""
        logger.info("Showing character demo")
        
        # Create character demo with custom widgets
        ui_def = UIBuilder("Character Stats Demo") \
            .with_size(600, 500) \
            .add_label("Character Information", font=('Arial', 16, 'bold')) \
            .with_pack_layout(pady=10) \
            .begin_paned_window(orient='horizontal') \
                .begin_frame() \
                    .add_label("Character Stats", style={'font': ('Arial', 12, 'bold')}) \
                    .with_pack_layout(pady=5) \
                    .add_text(value="Name: Gandalf the Grey\\nClass: Wizard\\nLevel: 42\\n\\nA powerful wizard with extensive knowledge of magic and lore.") \
                    .with_pack_layout(fill='both', expand=True, padx=10, pady=5) \
                .end_container() \
                .begin_frame() \
                    .add_label("Skills", style={'font': ('Arial', 12, 'bold')}) \
                    .with_pack_layout(pady=5) \
                    .add_text(value="Active Skills:\\n• Fireball (Level 5)\\n• Lightning Bolt (Level 4)\\n• Heal (Level 3)\\n\\nPassive Skills:\\n• Magic Mastery\\n• Wisdom of Ages") \
                    .with_pack_layout(fill='both', expand=True, padx=10, pady=5) \
                .end_container() \
            .end_container() \
            .with_pack_layout(fill='both', expand=True, padx=20, pady=10) \
            .begin_frame() \
                .add_button("Level Up", command="level_up") \
                .with_pack_layout(side='left', padx=5) \
                .add_button("Reset Stats", command="reset_stats") \
                .with_pack_layout(side='left', padx=5) \
                .add_button("Close", command="close_window") \
                .with_pack_layout(side='right', padx=5) \
            .end_container() \
            .with_pack_layout(fill='x', padx=20, pady=10) \
            .with_command("level_up", lambda: messagebox.showinfo("Level Up!", "Character leveled up! Stats increased.")) \
            .with_command("reset_stats", lambda: messagebox.showinfo("Reset", "Character stats reset to default values.")) \
            .with_command("close_window", lambda: self.close_current_app()) \
            .build()
        
        self.run_application(ui_def)
    
    def show_hud_demo(self):
        """Show game HUD demo"""
        logger.info("Showing HUD demo")
        
        # This would use the custom GameHUDFactory
        ui_def = UIBuilder("Game HUD Demo") \
            .with_size(800, 600) \
            .add_label("Game HUD Demonstration", font=('Arial', 16, 'bold')) \
            .with_pack_layout(pady=10) \
            .add_label("This demonstrates a typical game interface with health bars, minimap, and chat.") \
            .with_pack_layout(pady=5) \
            .begin_frame("Health & Mana") \
                .add_progressbar(length=200, mode='determinate') \
                .with_pack_layout(side='left', padx=5) \
                .add_label("Health: 85/100") \
                .with_pack_layout(side='left', padx=10) \
                .add_progressbar(length=200, mode='determinate') \
                .with_pack_layout(side='left', padx=5) \
                .add_label("Mana: 60/100") \
                .with_pack_layout(side='left', padx=10) \
            .end_container() \
            .with_pack_layout(pady=20) \
            .begin_paned_window(orient='horizontal') \
                .begin_frame("Game Area") \
                    .add_label("🎮 Main Game View", font=('Arial', 24)) \
                    .with_pack_layout(expand=True) \
                    .add_label("(Game world would be rendered here)") \
                    .with_pack_layout(expand=True) \
                .end_container() \
                .begin_frame("Minimap & Chat") \
                    .add_label("📍 Minimap", font=('Arial', 12, 'bold')) \
                    .with_pack_layout() \
                    .add_label("[Map visualization]\\n\\n👤 You are here") \
                    .with_pack_layout(pady=10) \
                    .add_separator() \
                    .with_pack_layout(fill='x', pady=10) \
                    .add_label("💬 Chat", font=('Arial', 12, 'bold')) \
                    .with_pack_layout() \
                    .add_text(value="Player1: Hello everyone!\\nPlayer2: Hi there!\\nSystem: Welcome to the game!", height=8) \
                    .with_pack_layout(fill='both', expand=True, pady=5) \
                    .add_entry() \
                    .with_pack_layout(fill='x') \
                .end_container() \
            .end_container() \
            .with_pack_layout(fill='both', expand=True, padx=20, pady=10) \
            .add_button("Close", command="close_window") \
            .with_pack_layout(pady=10) \
            .with_command("close_window", lambda: self.close_current_app()) \
            .build()
        
        self.run_application(ui_def)
    
    def show_inventory_demo(self):
        """Show inventory system demo"""
        logger.info("Showing inventory demo")
        
        ui_def = UIBuilder("Inventory System Demo") \
            .with_size(700, 500) \
            .add_label("Inventory Management System", font=('Arial', 16, 'bold')) \
            .with_pack_layout(pady=10) \
            .begin_paned_window(orient='horizontal') \
                .begin_frame("Inventory Grid") \
                    .add_label("Equipment Slots (5x5 Grid)") \
                    .with_pack_layout(pady=5) \
                    .add_label("🎒 [Simulated inventory grid would be here]\\n\\nItems:\\n⚔️ Iron Sword\\n🛡️ Leather Armor\\n🧪 Health Potion x3\\n🗝️ Rusty Key") \
                    .with_pack_layout(padx=20, pady=20) \
                .end_container() \
                .begin_frame("Item Details") \
                    .add_label("Selected Item Details", font=('Arial', 12, 'bold')) \
                    .with_pack_layout(pady=5) \
                    .add_text(value="Item: Iron Sword\\nType: Weapon\\nDamage: 15-20\\nDurability: 85/100\\n\\nDescription:\\nA well-crafted iron sword. Shows signs of use but remains sharp and reliable.") \
                    .with_pack_layout(fill='both', expand=True, padx=10, pady=5) \
                    .begin_frame() \
                        .add_button("Equip", command="equip_item") \
                        .with_pack_layout(side='left', padx=5) \
                        .add_button("Drop", command="drop_item") \
                        .with_pack_layout(side='left', padx=5) \
                        .add_button("Repair", command="repair_item") \
                        .with_pack_layout(side='left', padx=5) \
                    .end_container() \
                    .with_pack_layout(pady=10) \
                .end_container() \
            .end_container() \
            .with_pack_layout(fill='both', expand=True, padx=20, pady=10) \
            .add_button("Close", command="close_window") \
            .with_pack_layout(pady=10) \
            .with_command("equip_item", lambda: messagebox.showinfo("Equip", "Item equipped successfully!")) \
            .with_command("drop_item", lambda: messagebox.showwarning("Drop", "Item dropped from inventory.")) \
            .with_command("repair_item", lambda: messagebox.showinfo("Repair", "Item repaired for 50 gold.")) \
            .with_command("close_window", lambda: self.close_current_app()) \
            .build()
        
        self.run_application(ui_def)
    
    def show_template_demo(self):
        """Show template system demo"""
        logger.info("Showing template demo")
        
        # Use a built-in template
        ui_def = UITemplate.create_crud_interface("Item")
        
        # Add commands
        ui_def.commands = {
            'save_item': lambda: messagebox.showinfo("Save", "Item saved successfully!"),
            'delete_item': lambda: messagebox.showwarning("Delete", "Item deleted!"),
            'new_item': lambda: messagebox.showinfo("New", "New item created!"),
        }
        
        ui_def.on_close = lambda app: self.close_current_app() or False
        
        self.run_application(ui_def)
    
    def show_json_demo(self):
        """Show JSON configuration demo"""
        logger.info("Showing JSON demo")
        
        # Create a UI definition from dictionary (simulating JSON)
        json_data = {
            "title": "JSON-Configured Interface",
            "geometry": "500x400",
            "widgets": [
                {
                    "type": "label",
                    "text": "This UI was created from JSON configuration!",
                    "options": {"font": ("Arial", 14, "bold")},
                    "layout": {"row": 0, "column": 0, "pady": 20, "columnspan": 2}
                },
                {
                    "type": "labelframe",
                    "text": "JSON Configuration Example",
                    "layout": {"row": 1, "column": 0, "columnspan": 2, "sticky": "ew", "padx": 20, "pady": 10},
                    "children": [
                        {
                            "type": "label",
                            "text": "Field 1:",
                            "layout": {"row": 0, "column": 0, "sticky": "w", "padx": 5, "pady": 5}
                        },
                        {
                            "type": "entry",
                            "variable": "field1",
                            "value": "Default value",
                            "layout": {"row": 0, "column": 1, "sticky": "ew", "padx": 5, "pady": 5}
                        },
                        {
                            "type": "label",
                            "text": "Field 2:",
                            "layout": {"row": 1, "column": 0, "sticky": "w", "padx": 5, "pady": 5}
                        },
                        {
                            "type": "combobox",
                            "variable": "field2",
                            "value": ["Option 1", "Option 2", "Option 3"],
                            "layout": {"row": 1, "column": 1, "sticky": "ew", "padx": 5, "pady": 5}
                        }
                    ]
                },
                {
                    "type": "button",
                    "text": "Process Data",
                    "command": "process_data",
                    "layout": {"row": 2, "column": 0, "pady": 20}
                },
                {
                    "type": "button", 
                    "text": "Close",
                    "command": "close_window",
                    "layout": {"row": 2, "column": 1, "pady": 20}
                }
            ]
        }
        
        ui_def = self.ui_manager.load_ui_from_dict(json_data)
        ui_def.commands = {
            'process_data': lambda: messagebox.showinfo("Process", "Data processed from JSON configuration!"),
            'close_window': lambda: self.close_current_app()
        }
        
        self.run_application(ui_def)
    
    def show_event_demo(self):
        """Show event integration demo"""
        logger.info("Showing event demo")
        
        ui_def = UIBuilder("Event Integration Demo") \
            .with_size(600, 400) \
            .add_label("Event System Integration", font=('Arial', 16, 'bold')) \
            .with_pack_layout(pady=10) \
            .add_label("This demonstrates integration with the RPG Engine event system.") \
            .with_pack_layout(pady=5) \
            .begin_frame("Event Publishers") \
                .add_button("Trigger Character Event", command="trigger_char_event") \
                .with_pack_layout(pady=5, fill='x') \
                .add_button("Trigger Game Event", command="trigger_game_event") \
                .with_pack_layout(pady=5, fill='x') \
                .add_button("Trigger UI Update", command="trigger_ui_event") \
                .with_pack_layout(pady=5, fill='x') \
            .end_container() \
            .with_pack_layout(fill='x', padx=50, pady=20) \
            .add_label("Event Log:", font=('Arial', 12, 'bold')) \
            .with_pack_layout(anchor='w', padx=20) \
            .add_text(value="Events will appear here when triggered...\\n", height=8) \
            .with_pack_layout(fill='both', expand=True, padx=20, pady=10) \
            .add_button("Close", command="close_window") \
            .with_pack_layout(pady=10) \
            .with_command("trigger_char_event", lambda: self.trigger_character_event()) \
            .with_command("trigger_game_event", lambda: self.trigger_game_event()) \
            .with_command("trigger_ui_event", lambda: self.trigger_ui_update()) \
            .with_command("close_window", lambda: self.close_current_app()) \
            .build()
        
        self.run_application(ui_def)
    
    # Helper methods for demo functionality
    def show_user_info(self):
        """Show user info from simple form"""
        if self.ui_manager:
            name = self.ui_manager.get_variable("user_name").get()
            color = self.ui_manager.get_variable("favorite_color").get()
            subscribe = self.ui_manager.get_variable("subscribe").get()
            
            info = f"Name: {name}\\nFavorite Color: {color}\\nSubscribed: {'Yes' if subscribe else 'No'}"
            messagebox.showinfo("User Information", info)
    
    def clear_simple_form(self):
        """Clear the simple form"""
        if self.ui_manager:
            self.ui_manager.get_variable("user_name").set("")
            self.ui_manager.get_variable("favorite_color").set("")
            self.ui_manager.get_variable("subscribe").set(False)
    
    def handle_registration(self):
        """Handle form registration"""
        if self.ui_manager:
            username = self.ui_manager.get_variable("username").get()
            email = self.ui_manager.get_variable("email").get()
            country = self.ui_manager.get_variable("country").get()
            
            if not username:
                messagebox.showerror("Error", "Username is required!")
                return
            
            messagebox.showinfo("Registration", f"Welcome {username}!\\nEmail: {email}\\nCountry: {country}")
    
    def show_input_dialog(self):
        """Show custom input dialog"""
        from tkinter import simpledialog
        result = simpledialog.askstring("Input Dialog", "Enter your favorite game genre:")
        if result:
            messagebox.showinfo("Input Received", f"Your favorite genre is: {result}")
    
    def show_custom_dialog(self):
        """Show custom dialog using our builder"""
        dialog_def = DialogBuilder("Custom Dialog") \
            .with_message("This is a custom dialog created with DialogBuilder!") \
            .with_input("Enter something interesting:", "custom_input") \
            .with_buttons([ \
                {'text': 'OK', 'command': 'dialog_ok'}, \
                {'text': 'Cancel', 'command': 'dialog_cancel'} \
            ]) \
            .build()
        
        # This would show in a separate window - simplified for demo
        messagebox.showinfo("Custom Dialog", "Custom dialog would appear here!")
    
    def trigger_character_event(self):
        """Trigger a character-related event"""
        messagebox.showinfo("Character Event", "Character leveled up! Event published to system.")
    
    def trigger_game_event(self):
        """Trigger a game-related event"""
        messagebox.showinfo("Game Event", "Combat initiated! Game state updated.")
    
    def trigger_ui_update(self):
        """Trigger a UI update event"""
        messagebox.showinfo("UI Event", "UI refresh requested! All displays updated.")
    
    def run_application(self, ui_definition: UIDefinition):
        """Run a UI application"""
        if self.current_app:
            self.current_app.destroy()
        
        self.current_app = self.ui_manager.create_application(ui_definition)
        self.current_app.run()
    
    def close_current_app(self):
        """Close the current application"""
        if self.current_app:
            self.current_app.destroy()
            self.current_app = None
    
    def exit_demo(self):
        """Exit the demo"""
        logger.info("Exiting demo...")
        if self.current_app:
            self.current_app.destroy()
        exit()
    
    async def run_demo(self):
        """Run the main demo"""
        try:
            await self.initialize()
            
            # Create and run main menu
            main_menu = self.create_main_menu()
            self.run_application(main_menu)
            
        except Exception as e:
            logger.error(f"Demo error: {e}")
            messagebox.showerror("Demo Error", f"An error occurred: {e}")

# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point for the demo"""
    demo = ModularUIDemo()
    await demo.run_demo()

if __name__ == "__main__":
    print("🎮 Modular UI System Demo")
    print("=" * 50)
    print("This demo showcases the comprehensive modular UI system")
    print("for the RPG Engine, featuring:")
    print("• Declarative UI creation with simple syntax")
    print("• Form builders and dialog systems")
    print("• Custom game widgets")
    print("• Template-based UI generation")
    print("• JSON-driven configuration")
    print("• Event system integration")
    print("=" * 50)
    print()
    
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo failed: {e}")
        logging.exception("Demo exception")
