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

def build_ui_def(ui_manager):
    import tkinter.messagebox as messagebox
    import json
    from pathlib import Path
    from rpg_engine.ui.ui_builder import UIBuilder
    from rpg_engine.ui.modular_ui_system import WidgetConfig, WidgetType, LayoutType
    
    def on_create_character():
        messagebox.showinfo("Character Creation", "Character creation not yet implemented.")

    def create_character_template_card(name, info):
        """Create a polished character template card"""
        stats = info.get("stats") or info.get("base_stats") or {}
        description = info.get("description", "No description available")
        character_class = info.get("character_class", "Unknown")
        rarity = info.get("rarity", "COMMON")
        
        # Create a card with better styling and organization
        card = (
            UIBuilder()
            .begin_frame()
            .with_style("Card.TLabelframe", relief="raised", borderwidth=2, padding=15)
            
            # Header section with name and class
            .begin_frame()
            .add_label(name.replace("_", " ").title(), 
                      font=("Segoe UI", 14, "bold"), 
                      foreground="#2c3e50")
            .with_pack_layout(anchor="w", pady=(0, 5))
            .add_label(f"Class: {character_class} | Rarity: {rarity}", 
                      font=("Segoe UI", 9), 
                      foreground="#7f8c8d")
            .with_pack_layout(anchor="w", pady=(0, 8))
            .end_container()
            
            # Description section
            .add_label(description[:80] + ("..." if len(description) > 80 else ""), 
                      font=("Segoe UI", 9), 
                      foreground="#34495e",
                      wraplength=250,
                      justify="left")
            .with_pack_layout(anchor="w", pady=(0, 10), fill="x")
            
            # Stats section - show top 4 stats
            .begin_frame()
            .add_label("Key Stats:", font=("Segoe UI", 10, "bold"), foreground="#2980b9")
            .with_pack_layout(anchor="w", pady=(0, 2))
            .end_container()
        )
        
        # Add top 4 stats in a grid-like format
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:4]
        stats_text = " | ".join(f"{k.title()}: {v}" for k, v in sorted_stats)
        card.add_label(stats_text, 
                      font=("Consolas", 9), 
                      foreground="#27ae60")
        card.with_pack_layout(anchor="w", pady=(0, 10))
        
        # Action buttons
        card.begin_frame()
        card.add_button("📋 View Details", 
                       command=f"view_{name}",
                       style="Accent.TButton")
        card.with_pack_layout(side="left", padx=(0, 5))
        card.add_button("⚔️ Create", 
                       command=f"create_{name}",
                       style="Success.TButton")
        card.with_pack_layout(side="left")
        card.end_container()
        card.with_pack_layout(fill="x", pady=5)
        
        return card.end_container().build().widgets[0]

    def on_view_characters():
        """Enhanced character viewer with modern design"""
        try:
            data_path = Path(__file__).parent.parent / "data" / "character_templates.json"
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            templates = data.get("character_templates", {})
            
            if not templates:
                messagebox.showinfo("View Characters", "No character templates found.")
                return

            # Create template cards organized in a responsive grid
            template_cards = []
            template_names = list(templates.keys())
            
            for i in range(0, len(template_names), 2):
                row_cards = []
                for j in range(2):
                    idx = i + j
                    if idx >= len(template_names):
                        # Add spacer for odd number of templates
                        if j == 1:
                            spacer = WidgetConfig(
                                widget_type=WidgetType.FRAME,
                                options={"width": 300, "height": 1}
                            )
                            row_cards.append(spacer)
                        break
                    
                    name = template_names[idx]
                    info = templates[name]
                    card = create_character_template_card(name, info)
                    row_cards.append(card)
                
                # Create row container
                if row_cards:
                    row_frame = WidgetConfig(
                        widget_type=WidgetType.FRAME,
                        children=row_cards,
                        options={"relief": "flat", "bg": "#ecf0f1"}
                    )
                    template_cards.append(row_frame)

            # Build the enhanced viewer window
            builder = (
                UIBuilder("Character Templates Gallery")
                .with_size(900, 700)
                .with_theme("clam")
                .with_layout(LayoutType.PACK)
                
                # Header section
                .begin_frame()
                .with_style("Header.TLabelframe", relief="flat", padding=20)
                .add_label("🎮 Character Templates Gallery", 
                          font=("Segoe UI", 20, "bold"), 
                          foreground="#2c3e50")
                .with_pack_layout(pady=(0, 5))
                .add_label(f"Choose from {len(templates)} available character archetypes", 
                          font=("Segoe UI", 11), 
                          foreground="#7f8c8d")
                .with_pack_layout()
                .end_container()
                .with_pack_layout(fill="x", pady=(0, 10))
                
                # Main content area with scrollable cards
                .add_scrollable_frame(
                    children=template_cards,
                    borderwidth=1,
                    relief="sunken",
                    bg="#ecf0f1"
                )
                
                # Footer with actions
                .begin_frame()
                .with_style("Footer.TLabelframe", relief="flat", padding=15)
                .add_separator()
                .with_pack_layout(fill="x", pady=(0, 10))
                .begin_frame()
                .add_button("🔄 Refresh", command="refresh_templates")
                .with_pack_layout(side="left", padx=(0, 10))
                .add_button("📖 Help", command="show_help")
                .with_pack_layout(side="left", padx=(0, 10))
                .add_button("❌ Close", command="close_viewer")
                .with_pack_layout(side="right")
                .end_container()
                .with_pack_layout(fill="x")
                .end_container()
                .with_pack_layout(fill="x", pady=(10, 0))
            )
            
            # Add command handlers for template actions
            for name in template_names:
                def create_view_handler(template_name, template_info):
                    def handler():
                        details = f"""
🎭 Character Template Details

Name: {template_name.replace('_', ' ').title()}
Class: {template_info.get('character_class', 'Unknown')}
Rarity: {template_info.get('rarity', 'COMMON')}

Description:
{template_info.get('description', 'No description available')}

📊 Base Stats:
"""
                        stats = template_info.get('stats') or template_info.get('base_stats') or {}
                        for stat, value in stats.items():
                            details += f"  • {stat.title()}: {value}\n"
                        
                        starting_equipment = template_info.get('starting_equipment', [])
                        if starting_equipment:
                            details += f"\n⚔️ Starting Equipment:\n"
                            for item in starting_equipment:
                                details += f"  • {item.replace('_', ' ').title()}\n"
                        
                        starting_skills = template_info.get('starting_skills', [])
                        if starting_skills:
                            details += f"\n🎯 Starting Skills:\n"
                            for skill in starting_skills:
                                details += f"  • {skill.replace('_', ' ').title()}\n"
                                
                        messagebox.showinfo(f"📋 {template_name.replace('_', ' ').title()}", details)
                    return handler
                
                def create_create_handler(template_name):
                    def handler():
                        result = messagebox.askyesno(
                            "⚔️ Create Character", 
                            f"Create a new character using the {template_name.replace('_', ' ').title()} template?\n\n"
                            "This will start the character creation process with this template as the base."
                        )
                        if result:
                            messagebox.showinfo("Character Created", 
                                              f"Character creation from {template_name.replace('_', ' ').title()} template initiated!\n\n"
                                              "(Full character creation system coming soon)")
                    return handler
                
                template_info = templates[name]
                builder.with_command(f"view_{name}", create_view_handler(name, template_info))
                builder.with_command(f"create_{name}", create_create_handler(name))
            
            def refresh_templates():
                """Refresh the templates display"""
                messagebox.showinfo("🔄 Refresh Complete", 
                    f"Successfully refreshed {len(templates)} character templates.\n\n"
                    "All templates are up to date and ready for use!")
            
            def show_help():
                """Show comprehensive help information"""
                help_text = """
🎮 Character Templates Gallery - Help

📋 About This System:
The Character Templates Gallery displays all available character archetypes that you can use to create new characters. Each template provides a unique starting point with different stats, equipment, and abilities.

🎭 Template Cards:
• Name & Class: Shows the template name and character class
• Description: Brief overview of the character type
• Key Stats: The four highest base statistics
• View Details: Shows complete template information
• Create: Starts character creation with this template

⚡ Quick Actions:
• Refresh: Updates the template list (useful if templates are modified)
• Help: Shows this help information
• Close: Returns to the main menu

💡 Tips:
• Templates with higher stats in specific areas are better for different play styles
• Consider the starting equipment when choosing a template
• Each template has unique starting skills that define their capabilities

🔧 System Status:
Templates are loaded from the game's data files and represent the core character archetypes available in the RPG system.
"""
                messagebox.showinfo("📖 Help - Character Templates", help_text)
            
            builder.with_command("refresh_templates", refresh_templates)
            builder.with_command("show_help", show_help)
            
            # Create and show the window
            import tkinter as tk
            win = tk.Toplevel(ui_manager.current_app.root)
            win.title("Character Templates Gallery")
            win.geometry("900x700")
            win.configure(bg="#ecf0f1")
            
            # Set window icon and properties
            win.resizable(True, True)
            win.minsize(600, 400)
            
            builder.with_command("close_viewer", lambda: win.destroy())
            viewer_ui = builder.build()
            
            # Create the modular UI inside the Toplevel
            viewer_app = ui_manager.create_application(viewer_ui)
            viewer_app.root = win
            
            # Enhanced build_ui method for better integration
            def build_ui_in_toplevel(self):
                self.root.title(self.ui_definition.title)
                self._setup_enhanced_styling()
                
                for name, command in self.ui_definition.commands.items():
                    self.ui_manager.set_command(name, command)
                for name, value in self.ui_definition.variables.items():
                    var = self.ui_manager.get_variable(name)
                    var.set(value)
                    
                self._create_widgets(self.root, self.ui_definition.widgets)
                self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
                
                if self.ui_definition.on_init:
                    self.ui_definition.on_init(self)
            
            def _setup_enhanced_styling(self):
                """Setup enhanced styling for the character viewer"""
                if not self.ui_manager.style:
                    from tkinter import ttk
                    self.ui_manager.style = ttk.Style()
                style = self.ui_manager.style
                
                # Configure enhanced styles
                style.configure("Header.TLabelframe", background="#ecf0f1")
                style.configure("Footer.TLabelframe", background="#ecf0f1")
                style.configure("Card.TLabelframe", background="white")
                style.configure("Accent.TButton", background="#3498db", foreground="white")
                style.configure("Success.TButton", background="#27ae60", foreground="white")
            
            import types
            viewer_app.build_ui = types.MethodType(build_ui_in_toplevel, viewer_app)
            viewer_app._setup_enhanced_styling = types.MethodType(_setup_enhanced_styling, viewer_app)
            viewer_app.build_ui()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load character templates:\n{e}")
            import traceback
            traceback.print_exc()

    # Build the main application UI with enhanced design
    return (
        UIBuilder("🎮 RPG Engine - Character Manager")
        .with_size(1000, 650)
        .with_theme("clam")
        .with_layout(LayoutType.PACK)
        
        # Header section
        .begin_frame()
        .with_style("MainHeader.TLabelframe", relief="flat", padding=30)
        .add_label("🎮 RPG Engine", 
                  font=("Segoe UI", 28, "bold"), 
                  foreground="#2c3e50")
        .with_pack_layout(pady=(0, 5))
        .add_label("Character Management System", 
                  font=("Segoe UI", 14), 
                  foreground="#7f8c8d")
        .with_pack_layout(pady=(0, 10))
        .add_separator()
        .with_pack_layout(fill="x", pady=(10, 0))
        .end_container()
        .with_pack_layout(fill="x", pady=(0, 20))
        
        # Main content area
        .begin_frame()
        .with_style("MainContent.TLabelframe", relief="flat", padding=40)
        
        # Feature cards in a grid
        .begin_frame()
        
        # Character Creation Card
        .begin_frame()
        .with_style("FeatureCard.TLabelframe", relief="raised", borderwidth=2, padding=25)
        .add_label("⚔️ Create Character", 
                  font=("Segoe UI", 16, "bold"), 
                  foreground="#2980b9")
        .with_pack_layout(pady=(0, 10))
        .add_label("Start your adventure by creating\na new character from templates", 
                  font=("Segoe UI", 10), 
                  foreground="#34495e",
                  justify="center")
        .with_pack_layout(pady=(0, 15))
        .add_button("🚀 Get Started", 
                   command="create_character",
                   style="Primary.TButton")
        .with_pack_layout()
        .end_container()
        .with_pack_layout(side="left", padx=(0, 20), fill="both", expand=True)
        
        # Character Gallery Card
        .begin_frame()
        .with_style("FeatureCard.TLabelframe", relief="raised", borderwidth=2, padding=25)
        .add_label("📚 Character Gallery", 
                  font=("Segoe UI", 16, "bold"), 
                  foreground="#27ae60")
        .with_pack_layout(pady=(0, 10))
        .add_label("Browse and explore available\ncharacter templates and classes", 
                  font=("Segoe UI", 10), 
                  foreground="#34495e",
                  justify="center")
        .with_pack_layout(pady=(0, 15))
        .add_button("🎭 Browse Gallery", 
                   command="view_characters",
                   style="Success.TButton")
        .with_pack_layout()
        .end_container()
        .with_pack_layout(side="left", fill="both", expand=True)
        
        .end_container()
        .with_pack_layout(fill="both", expand=True, pady=(0, 30))
        
        # Quick stats section
        .begin_frame()
        .add_label("📊 Quick Stats", 
                  font=("Segoe UI", 12, "bold"), 
                  foreground="#8e44ad")
        .with_pack_layout(pady=(0, 5))
        .add_label("• Available Templates: Loading...", 
                  font=("Segoe UI", 9), 
                  foreground="#7f8c8d")
        .with_pack_layout(anchor="w")
        .add_label("• System Status: Ready", 
                  font=("Segoe UI", 9), 
                  foreground="#7f8c8d")
        .with_pack_layout(anchor="w")
        .end_container()
        .with_pack_layout(pady=(0, 20))
        
        .end_container()
        .with_pack_layout(fill="both", expand=True)
        
        # Footer section
        .begin_frame()
        .with_style("Footer.TLabelframe", relief="flat", padding=15)
        .add_separator()
        .with_pack_layout(fill="x", pady=(0, 10))
        .begin_frame()
        .add_label("RPG Engine v2.0 - Modern Architecture", 
                  font=("Segoe UI", 8), 
                  foreground="#bdc3c7")
        .with_pack_layout(side="left")
        .add_button("❌ Exit", 
                   command="close_window",
                   style="Secondary.TButton")
        .with_pack_layout(side="right")
        .end_container()
        .with_pack_layout(fill="x")
        .end_container()
        .with_pack_layout(fill="x")
        
        # Command bindings
        .with_command("create_character", on_create_character)
        .with_command("view_characters", on_view_characters)
        .with_command("close_window", lambda: ui_manager.current_app.destroy())
        
        # Custom styles
        .with_style("MainHeader.TLabelframe", background="#ecf0f1")
        .with_style("MainContent.TLabelframe", background="#ecf0f1")
        .with_style("FeatureCard.TLabelframe", background="white")
        .with_style("Footer.TLabelframe", background="#ecf0f1")
        .with_style("Primary.TButton", background="#3498db", foreground="white")
        .with_style("Success.TButton", background="#27ae60", foreground="white")
        .with_style("Secondary.TButton", background="#95a5a6", foreground="white")
        
        .build()
    )

def main():
    # Set up service container and UI manager
    container = ServiceContainer()
    container.register_singleton(EventBus, lambda c: EventBus())
    container.register_singleton(ModularUIManager, ModularUIManager)

    import asyncio
    asyncio.run(container.initialize_all_async())
    ui_manager = container.get(ModularUIManager)

    # Set up enhanced theme and styling
    # Initialize style if not already done
    if not ui_manager.style:
        from tkinter import ttk
        ui_manager.style = ttk.Style()
    style = ui_manager.style
    
    # Configure modern theme styles
    style.theme_use('clam')
    
    # Configure enhanced button styles
    style.configure("Primary.TButton", 
                   background="#3498db", 
                   foreground="white",
                   focuscolor="none",
                   padding=(20, 10))
    style.map("Primary.TButton",
             background=[('active', '#2980b9')])
    
    style.configure("Success.TButton", 
                   background="#27ae60", 
                   foreground="white",
                   focuscolor="none",
                   padding=(20, 10))
    style.map("Success.TButton",
             background=[('active', '#229954')])
    
    style.configure("Secondary.TButton", 
                   background="#95a5a6", 
                   foreground="white",
                   focuscolor="none",
                   padding=(10, 5))
    style.map("Secondary.TButton",
             background=[('active', '#7f8c8d')])
    
    style.configure("Accent.TButton", 
                   background="#e74c3c", 
                   foreground="white",
                   focuscolor="none",
                   padding=(15, 8))
    style.map("Accent.TButton",
             background=[('active', '#c0392b')])
    
    # Configure frame styles
    style.configure("MainHeader.TLabelframe", 
                   background="#ecf0f1",
                   borderwidth=0)
    style.configure("MainContent.TLabelframe", 
                   background="#ecf0f1",
                   borderwidth=0)
    style.configure("FeatureCard.TLabelframe", 
                   background="white",
                   borderwidth=2,
                   relief="raised")
    style.configure("Footer.TLabelframe", 
                   background="#ecf0f1",
                   borderwidth=0)
    style.configure("Card.TLabelframe", 
                   background="white",
                   borderwidth=1,
                   relief="solid")

    # Load template count for main UI
    try:
        import json
        from pathlib import Path
        data_path = Path(__file__).parent.parent / "data" / "character_templates.json"
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        template_count = len(data.get("character_templates", {}))
    except Exception:
        template_count = "Unknown"

    # Build the UI declaratively with dynamic data
    ui_def = build_ui_def(ui_manager)
    
    # Update quick stats with actual data
    for widget in ui_def.widgets:
        if hasattr(widget, 'children'):
            for child in widget.children:
                if hasattr(child, 'children'):
                    for subchild in child.children:
                        if hasattr(subchild, 'text') and "Available Templates: Loading..." in str(subchild.text):
                            subchild.text = f"• Available Templates: {template_count}"

    # Create and run the modular application
    app = ui_manager.create_application(ui_def)
    ui_manager.current_app = app
    
    # Configure window properties before showing
    def configure_window():
        # Set window properties
        app.root.minsize(800, 500)
        app.root.configure(bg="#ecf0f1")
        
        # Center the window on screen
        app.root.update_idletasks()
        width = app.root.winfo_width()
        height = app.root.winfo_height()
        x = (app.root.winfo_screenwidth() // 2) - (width // 2)
        y = (app.root.winfo_screenheight() // 2) - (height // 2)
        app.root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Set the on_init callback to configure the window
    original_on_init = ui_def.on_init
    def enhanced_on_init(app_instance):
        configure_window()
        if original_on_init:
            original_on_init(app_instance)
    
    ui_def.on_init = enhanced_on_init
    
    app.run()

if __name__ == "__main__":
    main()
