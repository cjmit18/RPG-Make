"""
Quick Start Examples - Simple applications showing the modular UI system

These examples demonstrate how easy it is to create complex applications
with minimal code using the modular UI system.
"""
import asyncio
import tkinter as tk
from tkinter import messagebox
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the modular UI system
try:
    from rpg_engine.ui.modular_ui_system import ModularUIManager, UIDefinition, WidgetConfig, WidgetType
    from rpg_engine.ui.ui_builder import UIBuilder, FormBuilder
    from rpg_engine.ui.custom_widgets import register_game_widgets
    from rpg_engine.core.service_container import ServiceContainer
    from rpg_engine.core.event_bus import EventBus
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    exit(1)

# ============================================================================
# Example 1: Ultra-Simple Window
# ============================================================================

def example_1_simple_window():
    """Create the simplest possible window"""
    print("Example 1: Creating a simple window with 3 lines of code")
    
    # This is all you need for a basic application!
    app_ui = UIBuilder("My First App") \
        .with_size(400, 200) \
        .add_label("Hello, Modular UI!") \
        .add_button("Click Me", command="handle_click") \
        .with_command("handle_click", lambda: messagebox.showinfo("Hello", "Button clicked!")) \
        .build()
    
    # Run it (would normally use ModularUIManager, but for demo simplicity)
    root = tk.Tk()
    root.title(app_ui.title)
    root.geometry(app_ui.geometry)
    
    label = tk.Label(root, text="Hello, Modular UI!")
    label.pack(pady=20)
    
    button = tk.Button(root, text="Click Me", 
                      command=lambda: messagebox.showinfo("Hello", "Button clicked!"))
    button.pack(pady=10)
    
    root.mainloop()

# ============================================================================
# Example 2: Form in 5 Lines
# ============================================================================

def example_2_quick_form():
    """Create a complete form with just 5 lines"""
    print("Example 2: Complete form in 5 lines of code")
    
    def handle_submit():
        messagebox.showinfo("Form", "Form submitted successfully!")
    
    # Complete form with validation in 5 lines!
    form_ui = FormBuilder("User Registration") \
        .add_text_field("name", "Full Name:", required=True) \
        .add_text_field("email", "Email Address:") \
        .add_dropdown("role", "Role:", ["Admin", "User", "Guest"]) \
        .add_submit_button("Register", "submit") \
        .build()
    
    form_ui.commands["submit"] = handle_submit
    
    # Simplified display for demo
    root = tk.Tk()
    root.title(form_ui.title)
    root.geometry("400x300")
    
    tk.Label(root, text="Registration Form", font=('Arial', 14, 'bold')).pack(pady=10)
    tk.Label(root, text="Name:").pack()
    tk.Entry(root).pack(pady=5)
    tk.Label(root, text="Email:").pack()
    tk.Entry(root).pack(pady=5)
    tk.Label(root, text="Role:").pack()
    
    from tkinter import ttk
    ttk.Combobox(root, values=["Admin", "User", "Guest"]).pack(pady=5)
    tk.Button(root, text="Register", command=handle_submit).pack(pady=20)
    
    root.mainloop()

# ============================================================================
# Example 3: Data Manager in 10 Lines
# ============================================================================

def example_3_data_manager():
    """Create a complete data management interface"""
    print("Example 3: Complete data manager in ~10 lines") 
    
    def add_item():
        messagebox.showinfo("Add", "Item added!")
    
    def edit_item():
        messagebox.showinfo("Edit", "Item edited!")
    
    def delete_item():
        messagebox.showwarning("Delete", "Item deleted!")
    
    # Complete CRUD interface
    ui = UIBuilder("Data Manager") \
        .with_size(800, 600) \
        .begin_paned_window(orient='horizontal') \
            .begin_frame("Items") \
                .add_listbox(items=["Item 1", "Item 2", "Item 3"]) \
                .with_pack_layout(fill='both', expand=True) \
            .end_container() \
            .begin_frame("Actions") \
                .add_button("Add Item", command="add") \
                .with_pack_layout(fill='x', pady=5) \
                .add_button("Edit Item", command="edit") \
                .with_pack_layout(fill='x', pady=5) \
                .add_button("Delete Item", command="delete") \
                .with_pack_layout(fill='x', pady=5) \
            .end_container() \
        .end_container() \
        .with_command("add", add_item) \
        .with_command("edit", edit_item) \
        .with_command("delete", delete_item) \
        .build()
    
    # Simplified demo display
    root = tk.Tk()
    root.title("Data Manager")
    root.geometry("600x400")
    
    # Left panel
    left_frame = tk.Frame(root)
    left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    
    tk.Label(left_frame, text="Items", font=('Arial', 12, 'bold')).pack()
    listbox = tk.Listbox(left_frame)
    for item in ["Item 1", "Item 2", "Item 3"]:
        listbox.insert(tk.END, item)
    listbox.pack(fill='both', expand=True, pady=5)
    
    # Right panel
    right_frame = tk.Frame(root)
    right_frame.pack(side='right', fill='y', padx=5, pady=5)
    
    tk.Label(right_frame, text="Actions", font=('Arial', 12, 'bold')).pack()
    tk.Button(right_frame, text="Add Item", command=add_item, width=15).pack(pady=5)
    tk.Button(right_frame, text="Edit Item", command=edit_item, width=15).pack(pady=5)  
    tk.Button(right_frame, text="Delete Item", command=delete_item, width=15).pack(pady=5)
    
    root.mainloop()

# ============================================================================
# Example 4: Game UI Components
# ============================================================================

def example_4_game_ui():
    """Show game-specific UI components"""
    print("Example 4: Game UI with custom widgets")
    
    # Game interface with health bars, inventory, etc.
    ui = UIBuilder("RPG Game Interface") \
        .with_size(900, 700) \
        .add_label("🎮 RPG Game Demo", font=('Arial', 16, 'bold')) \
        .with_pack_layout(pady=10) \
        .begin_frame("Player Status") \
            .add_label("Health: ████████░░ 80/100") \
            .with_pack_layout(side='left', padx=20) \
            .add_label("Mana: ██████░░░░ 60/100") \
            .with_pack_layout(side='left', padx=20) \
            .add_label("Level: 15 | XP: 2847/3000") \
            .with_pack_layout(side='left', padx=20) \
        .end_container() \
        .with_pack_layout(fill='x', pady=10) \
        .begin_paned_window(orient='horizontal') \
            .begin_frame("Game World") \
                .add_label("🗺️ Game World View", font=('Arial', 18)) \
                .with_pack_layout(expand=True) \
                .add_label("(3D game world would be rendered here)") \
                .with_pack_layout(expand=True) \
            .end_container() \
            .begin_frame("Game UI") \
                .add_label("📦 Inventory", font=('Arial', 12, 'bold')) \
                .with_pack_layout() \
                .add_label("🗡️⚔️🛡️🧪💎\\n🏹🔥💀🗝️⭐") \
                .with_pack_layout(pady=10) \
                .add_label("💬 Chat", font=('Arial', 12, 'bold')) \
                .with_pack_layout() \
                .add_text(value="Player1: Anyone want to team up?\\nPlayer2: Sure, I'm at the tavern\\nSystem: Guild event starting soon!", height=6) \
                .with_pack_layout(fill='both', expand=True, pady=5) \
            .end_container() \
        .end_container() \
        .with_pack_layout(fill='both', expand=True, padx=10, pady=10) \
        .build()
    
    # Display demo
    root = tk.Tk()
    root.title("RPG Game Interface")
    root.geometry("900x700")
    
    # Header
    tk.Label(root, text="🎮 RPG Game Demo", font=('Arial', 16, 'bold')).pack(pady=10)
    
    # Status bar
    status_frame = tk.Frame(root)
    status_frame.pack(fill='x', pady=10)
    tk.Label(status_frame, text="Health: ████████░░ 80/100").pack(side='left', padx=20)
    tk.Label(status_frame, text="Mana: ██████░░░░ 60/100").pack(side='left', padx=20)
    tk.Label(status_frame, text="Level: 15 | XP: 2847/3000").pack(side='left', padx=20)
    
    # Main area
    main_frame = tk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Game world
    world_frame = tk.Frame(main_frame, bg='darkgreen', relief='sunken', bd=2)
    world_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
    tk.Label(world_frame, text="🗺️ Game World View", font=('Arial', 18), bg='darkgreen', fg='white').pack(expand=True)
    
    # UI panel
    ui_frame = tk.Frame(main_frame, relief='raised', bd=1)
    ui_frame.pack(side='right', fill='y', padx=(5, 0))
    
    tk.Label(ui_frame, text="📦 Inventory", font=('Arial', 12, 'bold')).pack(pady=5)
    tk.Label(ui_frame, text="🗡️⚔️🛡️🧪💎\\n🏹🔥💀🗝️⭐").pack(pady=10)
    
    tk.Label(ui_frame, text="💬 Chat", font=('Arial', 12, 'bold')).pack(pady=(20, 5))
    chat_text = tk.Text(ui_frame, height=6, width=25)
    chat_text.insert('1.0', "Player1: Anyone want to team up?\\nPlayer2: Sure, I'm at the tavern\\nSystem: Guild event starting soon!")
    chat_text.pack(pady=5, padx=5)
    
    root.mainloop()

# ============================================================================
# Example 5: JSON Configuration
# ============================================================================

def example_5_json_config():
    """Show JSON-driven UI creation"""
    print("Example 5: UI from JSON configuration")
    
    # This could be loaded from a file
    ui_config = {
        "title": "Settings Panel",
        "geometry": "500x400",
        "widgets": [
            {
                "type": "label",
                "text": "Application Settings",
                "options": {"font": ("Arial", 14, "bold")},
                "layout": {"row": 0, "column": 0, "columnspan": 2, "pady": 20}
            },
            {
                "type": "checkbutton",
                "text": "Enable notifications",
                "variable": "notifications",
                "layout": {"row": 1, "column": 0, "columnspan": 2, "sticky": "w", "padx": 20, "pady": 5}
            },
            {
                "type": "checkbutton", 
                "text": "Auto-save changes",
                "variable": "autosave",
                "layout": {"row": 2, "column": 0, "columnspan": 2, "sticky": "w", "padx": 20, "pady": 5}
            },
            {
                "type": "label",
                "text": "Theme:",
                "layout": {"row": 3, "column": 0, "sticky": "w", "padx": 20, "pady": 10}
            },
            {
                "type": "combobox",
                "value": ["Default", "Dark", "Light", "Blue"],
                "variable": "theme",
                "layout": {"row": 3, "column": 1, "sticky": "ew", "padx": 20, "pady": 10}
            },
            {
                "type": "button",
                "text": "Save Settings",
                "command": "save",
                "layout": {"row": 4, "column": 0, "pady": 20}
            },
            {
                "type": "button",
                "text": "Cancel",
                "command": "cancel", 
                "layout": {"row": 4, "column": 1, "pady": 20}
            }
        ]
    }
    
    def save_settings():
        messagebox.showinfo("Save", "Settings saved successfully!")
    
    def cancel_settings():
        messagebox.showinfo("Cancel", "Changes cancelled")
    
    # Display demo
    root = tk.Tk()
    root.title("Settings Panel")
    root.geometry("500x400")
    
    tk.Label(root, text="Application Settings", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
    
    tk.Checkbutton(root, text="Enable notifications").grid(row=1, column=0, columnspan=2, sticky='w', padx=20, pady=5)
    tk.Checkbutton(root, text="Auto-save changes").grid(row=2, column=0, columnspan=2, sticky='w', padx=20, pady=5)
    
    tk.Label(root, text="Theme:").grid(row=3, column=0, sticky='w', padx=20, pady=10)
    
    from tkinter import ttk
    theme_combo = ttk.Combobox(root, values=["Default", "Dark", "Light", "Blue"])
    theme_combo.grid(row=3, column=1, sticky='ew', padx=20, pady=10)
    
    tk.Button(root, text="Save Settings", command=save_settings).grid(row=4, column=0, pady=20)
    tk.Button(root, text="Cancel", command=cancel_settings).grid(row=4, column=1, pady=20)
    
    root.grid_columnconfigure(1, weight=1)
    
    root.mainloop()

# ============================================================================
# Main Menu
# ============================================================================

def show_examples_menu():
    """Show a menu of all examples"""
    root = tk.Tk()
    root.title("Modular UI System - Quick Examples")
    root.geometry("600x500")
    
    tk.Label(root, text="🚀 Modular UI System", font=('Arial', 18, 'bold')).pack(pady=20)
    tk.Label(root, text="Quick Start Examples", font=('Arial', 12)).pack(pady=5)
    
    tk.Label(root, text="Choose an example to see how easy UI creation can be:", 
             wraplength=500, justify='center').pack(pady=20)
    
    # Example buttons
    examples = [
        ("1. Simple Window (3 lines)", example_1_simple_window),
        ("2. Complete Form (5 lines)", example_2_quick_form),
        ("3. Data Manager (10 lines)", example_3_data_manager),
        ("4. Game UI Components", example_4_game_ui),
        ("5. JSON Configuration", example_5_json_config),
    ]
    
    for text, func in examples:
        btn = tk.Button(root, text=text, command=func, font=('Arial', 11), width=40)
        btn.pack(pady=8)
    
    tk.Label(root, text="\\n💡 Each example shows progressively more advanced features\\nwhile keeping the code simple and readable.", 
             wraplength=500, justify='center', font=('Arial', 9, 'italic')).pack(pady=20)
    
    root.mainloop()

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    print("🚀 Modular UI System - Quick Start Examples")
    print("=" * 55)
    print("These examples show how to create complex applications")
    print("with minimal code using declarative syntax.")
    print("=" * 55)
    print()
    
    show_examples_menu()
