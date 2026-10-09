"""
Custom Widgets - Game-specific UI components
Provides pre-built components for common game UI elements

Features:
- Character stat displays
- Health/mana bars
- Inventory grids
- Skill trees
- Achievement panels
- Combat log
- Minimap
- Chat system
"""
import tkinter as tk
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, colorchooser
from typing import Dict, Any, Optional, Callable, List, Union
import logging
from dataclasses import dataclass
import math

from .modular_ui_system import WidgetFactory, WidgetConfig, ModularUIManager

logger = logging.getLogger(__name__)

# ============================================================================
# Game-Specific Widget Factories
# ============================================================================

class CharacterStatDisplayFactory(WidgetFactory):
    """Factory for character stat display widgets"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create character stat display"""
        frame = ttk.LabelFrame(parent, text=config.text or "Character Stats")
        
        # Create stat displays
        stats = config.value or {}
        row = 0
        
        for stat_name, stat_value in stats.items():
            # Stat name label
            name_label = ttk.Label(frame, text=f"{stat_name.title()}:")
            name_label.grid(row=row, column=0, sticky='w', padx=5, pady=2)
            
            # Stat value label
            value_label = ttk.Label(frame, text=str(stat_value), font=('Arial', 10, 'bold'))
            value_label.grid(row=row, column=1, sticky='e', padx=5, pady=2)
            
            # Store reference for updates
            setattr(frame, f"{stat_name}_label", value_label)
            
            row += 1
        
        # Configure column weights
        frame.grid_columnconfigure(1, weight=1)
        
        return frame

class HealthBarFactory(WidgetFactory):
    """Factory for health/mana bars"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create health/mana bar"""
        frame = ttk.Frame(parent)
        
        # Label
        label_text = config.text or "Health"
        label = ttk.Label(frame, text=label_text)
        label.pack(anchor='w')
        
        # Progress bar
        bar_color = config.options.get('color', 'green')
        max_value = config.options.get('max_value', 100)
        current_value = config.value or max_value
        
        # Create custom progress bar with text
        progress_frame = ttk.Frame(frame, relief='sunken', borderwidth=1)
        progress_frame.pack(fill='x', pady=2)
        
        # Canvas for custom drawing
        canvas_widget = tk.Canvas(progress_frame, height=20, bg='white')
        canvas_widget.pack(fill='x')
        
        # Draw initial bar
        self._update_bar(canvas_widget, current_value, max_value, bar_color)
        
        # Store references
        frame.canvas = canvas_widget
        frame.max_value = max_value
        frame.current_value = current_value
        frame.color = bar_color
        frame.update_bar = lambda current, maximum=None: self._update_bar(
            canvas_widget, current, maximum or max_value, bar_color
        )
        
        return frame
    
    def _update_bar(self, canvas: tk.Canvas, current: float, maximum: float, color: str) -> None:
        """Update the progress bar"""
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:  # Not yet drawn
            canvas.after(100, lambda: self._update_bar(canvas, current, maximum, color))
            return
        
        # Calculate fill percentage
        percentage = max(0, min(1, current / maximum)) if maximum > 0 else 0
        fill_width = width * percentage
        
        # Draw background
        canvas.create_rectangle(0, 0, width, height, fill='lightgray', outline='')
        
        # Draw fill
        if fill_width > 0:
            canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline='')
        
        # Draw text
        text = f"{int(current)}/{int(maximum)}"
        canvas.create_text(width/2, height/2, text=text, font=('Arial', 8, 'bold'))

class InventoryGridFactory(WidgetFactory):
    """Factory for inventory grid widgets"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create inventory grid"""
        frame = ttk.LabelFrame(parent, text=config.text or "Inventory")
        
        # Grid configuration
        rows = config.options.get('rows', 5)
        cols = config.options.get('cols', 5)
        slot_size = config.options.get('slot_size', 40)
        
        # Create grid canvas
        canvas_width = cols * slot_size + (cols + 1) * 2
        canvas_height = rows * slot_size + (rows + 1) * 2
        
        canvas_widget = tk.Canvas(frame, width=canvas_width, height=canvas_height, bg='white')
        canvas_widget.pack(padx=5, pady=5)
        
        # Draw grid
        self._draw_inventory_grid(canvas_widget, rows, cols, slot_size)
        
        # Store grid data
        frame.grid_data = {}
        frame.rows = rows
        frame.cols = cols
        frame.slot_size = slot_size
        frame.canvas = canvas_widget
        
        # Bind click events
        canvas_widget.bind("<Button-1>", lambda e: self._on_grid_click(e, frame))
        
        return frame
    
    def _draw_inventory_grid(self, canvas: tk.Canvas, rows: int, cols: int, slot_size: int) -> None:
        """Draw the inventory grid"""
        canvas.delete("all")
        
        padding = 2
        
        for row in range(rows):
            for col in range(cols):
                x1 = col * slot_size + (col + 1) * padding
                y1 = row * slot_size + (row + 1) * padding
                x2 = x1 + slot_size
                y2 = y1 + slot_size
                
                # Draw slot
                canvas.create_rectangle(x1, y1, x2, y2, fill='lightblue', outline='darkblue')
                
                # Tag for identification
                canvas.create_rectangle(x1, y1, x2, y2, fill='', outline='',
                                      tags=f"slot_{row}_{col}")
    
    def _on_grid_click(self, event, frame) -> None:
        """Handle grid click"""
        canvas = frame.canvas
        x, y = event.x, event.y
        
        # Find clicked slot
        slot_size = frame.slot_size
        padding = 2
        
        col = int((x - padding) / (slot_size + padding))
        row = int((y - padding) / (slot_size + padding))
        
        if 0 <= row < frame.rows and 0 <= col < frame.cols:
            logger.info(f"Clicked inventory slot: {row}, {col}")
            # Emit event or call callback

class SkillTreeFactory(WidgetFactory):
    """Factory for skill tree widgets"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create skill tree"""
        frame = ttk.LabelFrame(parent, text=config.text or "Skills")
        
        # Create scrollable canvas
        canvas_widget = tk.Canvas(frame, bg='white')
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas_widget.yview)
        scrollable_frame = ttk.Frame(canvas_widget)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_widget.configure(scrollregion=canvas_widget.bbox("all"))
        )
        
        canvas_widget.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        canvas_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create skill nodes
        skills = config.value or []
        self._create_skill_nodes(scrollable_frame, skills)
        
        return frame
    
    def _create_skill_nodes(self, parent: ttk.Frame, skills: List[Dict[str, Any]]) -> None:
        """Create skill nodes"""
        for i, skill in enumerate(skills):
            skill_frame = ttk.Frame(parent, relief='raised', borderwidth=1)
            skill_frame.pack(fill='x', padx=5, pady=2)
            
            # Skill icon (placeholder)
            icon_label = ttk.Label(skill_frame, text="[📜]", font=('Arial', 16))
            icon_label.pack(side='left', padx=5)
            
            # Skill info
            info_frame = ttk.Frame(skill_frame)
            info_frame.pack(side='left', fill='x', expand=True, padx=5)
            
            name_label = ttk.Label(info_frame, text=skill.get('name', 'Unknown Skill'), 
                                 font=('Arial', 10, 'bold'))
            name_label.pack(anchor='w')
            
            desc_label = ttk.Label(info_frame, text=skill.get('description', ''), 
                                 font=('Arial', 8))
            desc_label.pack(anchor='w')
            
            # Level indicator
            level = skill.get('level', 0)
            max_level = skill.get('max_level', 5)
            level_label = ttk.Label(skill_frame, text=f"{level}/{max_level}")
            level_label.pack(side='right', padx=5)

class CombatLogFactory(WidgetFactory):
    """Factory for combat log widgets"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create combat log"""
        frame = ttk.LabelFrame(parent, text=config.text or "Combat Log")
        
        # Create text widget with scrollbar
        text_widget = tk.Text(frame, height=10, state='disabled', wrap='word')
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure text tags for different message types
        text_widget.tag_configure("damage", foreground="red")
        text_widget.tag_configure("healing", foreground="green")
        text_widget.tag_configure("system", foreground="blue")
        text_widget.tag_configure("player", foreground="black", font=('Arial', 9, 'bold'))
        
        # Add methods for adding messages
        def add_message(message: str, msg_type: str = "system"):
            text_widget.config(state='normal')
            text_widget.insert(tk.END, f"{message}\n", msg_type)
            text_widget.config(state='disabled')
            text_widget.see(tk.END)
        
        frame.add_message = add_message
        frame.text_widget = text_widget
        
        return frame

class MinimapFactory(WidgetFactory):
    """Factory for minimap widgets"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create minimap"""
        frame = ttk.LabelFrame(parent, text=config.text or "Map")
        
        # Create canvas for map
        size = config.options.get('size', 150)
        canvas_widget = tk.Canvas(frame, width=size, height=size, bg='darkgreen')
        canvas_widget.pack(padx=5, pady=5)
        
        # Draw basic map
        self._draw_minimap(canvas_widget, size)
        
        frame.canvas = canvas_widget
        frame.size = size
        
        return frame
    
    def _draw_minimap(self, canvas: tk.Canvas, size: int) -> None:
        """Draw basic minimap"""
        canvas.delete("all")
        
        # Draw border
        canvas.create_rectangle(2, 2, size-2, size-2, outline='black', width=2)
        
        # Draw player position (center)
        center = size // 2
        canvas.create_oval(center-3, center-3, center+3, center+3, 
                          fill='red', outline='darkred')
        
        # Draw some example features
        canvas.create_rectangle(20, 20, 40, 40, fill='brown', outline='')  # Building
        canvas.create_oval(size-40, size-40, size-20, size-20, fill='blue', outline='')  # Water

class ChatSystemFactory(WidgetFactory):
    """Factory for chat system widgets"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create chat system"""
        frame = ttk.LabelFrame(parent, text=config.text or "Chat")
        
        # Chat display
        chat_text = tk.Text(frame, height=8, state='disabled', wrap='word')
        chat_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=chat_text.yview)
        chat_text.configure(yscrollcommand=chat_scrollbar.set)
        
        # Chat input
        input_frame = ttk.Frame(frame)
        chat_entry = ttk.Entry(input_frame)
        send_button = ttk.Button(input_frame, text="Send")
        
        # Pack components
        chat_text.pack(side="top", fill="both", expand=True)
        chat_scrollbar.pack(side="right", fill="y")
        
        input_frame.pack(side="bottom", fill="x", pady=(5, 0))
        chat_entry.pack(side="left", fill="x", expand=True)
        send_button.pack(side="right", padx=(5, 0))
        
        # Configure text tags
        chat_text.tag_configure("system", foreground="blue", font=('Arial', 8, 'italic'))
        chat_text.tag_configure("player", foreground="green", font=('Arial', 9, 'bold'))
        chat_text.tag_configure("npc", foreground="purple")
        
        # Add methods
        def add_chat_message(sender: str, message: str, msg_type: str = "player"):
            chat_text.config(state='normal')
            chat_text.insert(tk.END, f"{sender}: {message}\n", msg_type)
            chat_text.config(state='disabled')
            chat_text.see(tk.END)
        
        def send_message():
            message = chat_entry.get().strip()
            if message:
                add_chat_message("Player", message)
                chat_entry.delete(0, tk.END)
        
        frame.add_message = add_chat_message
        frame.send_message = send_message
        frame.chat_text = chat_text
        frame.chat_entry = chat_entry
        
        # Bind events
        send_button.configure(command=send_message)
        chat_entry.bind("<Return>", lambda e: send_message())
        
        return frame

class AchievementPanelFactory(WidgetFactory):
    """Factory for achievement panels"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create achievement panel"""
        frame = ttk.LabelFrame(parent, text=config.text or "Achievements")
        
        # Create scrollable frame
        canvas_widget = tk.Canvas(frame, bg='white')
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas_widget.yview)
        scrollable_frame = ttk.Frame(canvas_widget)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_widget.configure(scrollregion=canvas_widget.bbox("all"))
        )
        
        canvas_widget.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        canvas_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create achievement items
        achievements = config.value or []
        self._create_achievement_items(scrollable_frame, achievements)
        
        return frame
    
    def _create_achievement_items(self, parent: ttk.Frame, achievements: List[Dict[str, Any]]) -> None:
        """Create achievement items"""
        for achievement in achievements:
            item_frame = ttk.Frame(parent, relief='raised', borderwidth=1)
            item_frame.pack(fill='x', padx=5, pady=2)
            
            # Achievement icon
            completed = achievement.get('completed', False)
            icon = "🏆" if completed else "🔒"
            icon_label = ttk.Label(item_frame, text=icon, font=('Arial', 16))
            icon_label.pack(side='left', padx=5)
            
            # Achievement info
            info_frame = ttk.Frame(item_frame)
            info_frame.pack(side='left', fill='x', expand=True, padx=5)
            
            name_label = ttk.Label(info_frame, text=achievement.get('name', 'Unknown'), 
                                 font=('Arial', 10, 'bold'))
            name_label.pack(anchor='w')
            
            desc_label = ttk.Label(info_frame, text=achievement.get('description', ''), 
                                 font=('Arial', 8))
            desc_label.pack(anchor='w')
            
            # Progress bar for incomplete achievements
            if not completed and 'progress' in achievement:
                progress = achievement['progress']
                max_progress = achievement.get('max_progress', 100)
                
                progress_bar = ttk.Progressbar(info_frame, length=100, mode='determinate')
                progress_bar['value'] = (progress / max_progress) * 100
                progress_bar.pack(anchor='w', pady=2)
                
                progress_label = ttk.Label(info_frame, text=f"{progress}/{max_progress}", 
                                         font=('Arial', 8))
                progress_label.pack(anchor='w')

# ============================================================================
# Compound Game UI Components
# ============================================================================

class GameHUDFactory(WidgetFactory):
    """Factory for complete game HUD"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: ModularUIManager) -> tk.Widget:
        """Create complete game HUD"""
        main_frame = ttk.Frame(parent)
        
        # Top panel - health, mana, etc.
        top_panel = ttk.Frame(main_frame)
        top_panel.pack(side='top', fill='x', padx=5, pady=5)
        
        # Health bar
        health_config = WidgetConfig(
            widget_type='health_bar',
            text='Health',
            value=100,
            options={'max_value': 100, 'color': 'red'}
        )
        health_bar = HealthBarFactory().create_widget(top_panel, health_config, ui_manager)
        health_bar.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Mana bar
        mana_config = WidgetConfig(
            widget_type='health_bar',
            text='Mana',
            value=50,
            options={'max_value': 100, 'color': 'blue'}
        )
        mana_bar = HealthBarFactory().create_widget(top_panel, mana_config, ui_manager)
        mana_bar.pack(side='left', fill='x', expand=True, padx=5)
        
        # Experience bar
        exp_config = WidgetConfig(
            widget_type='health_bar',
            text='Experience',
            value=75,
            options={'max_value': 100, 'color': 'gold'}
        )
        exp_bar = HealthBarFactory().create_widget(top_panel, exp_config, ui_manager)
        exp_bar.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Bottom panel - minimap and chat
        bottom_panel = ttk.Frame(main_frame)
        bottom_panel.pack(side='bottom', fill='x', padx=5, pady=5)
        
        # Minimap
        minimap_config = WidgetConfig(
            widget_type='minimap',
            options={'size': 120}
        )
        minimap = MinimapFactory().create_widget(bottom_panel, minimap_config, ui_manager)
        minimap.pack(side='right', padx=(5, 0))
        
        # Chat system
        chat_config = WidgetConfig(widget_type='chat_system')
        chat = ChatSystemFactory().create_widget(bottom_panel, chat_config, ui_manager)
        chat.pack(side='left', fill='both', expand=True)
        
        # Store references
        main_frame.health_bar = health_bar
        main_frame.mana_bar = mana_bar
        main_frame.exp_bar = exp_bar
        main_frame.minimap = minimap
        main_frame.chat = chat
        
        return main_frame

# ============================================================================
# Registration Helper
# ============================================================================

def register_game_widgets(ui_manager: ModularUIManager) -> None:
    """Register all game-specific widgets with the UI manager"""
    ui_manager.register_custom_factory('character_stats', CharacterStatDisplayFactory())
    ui_manager.register_custom_factory('health_bar', HealthBarFactory())
    ui_manager.register_custom_factory('inventory_grid', InventoryGridFactory())
    ui_manager.register_custom_factory('skill_tree', SkillTreeFactory())
    ui_manager.register_custom_factory('combat_log', CombatLogFactory())
    ui_manager.register_custom_factory('minimap', MinimapFactory())
    ui_manager.register_custom_factory('chat_system', ChatSystemFactory())
    ui_manager.register_custom_factory('achievement_panel', AchievementPanelFactory())
    ui_manager.register_custom_factory('game_hud', GameHUDFactory())
    
    logger.info("Game-specific widgets registered")

# ============================================================================
# Widget Update Helpers
# ============================================================================

def update_character_stats(widget: tk.Widget, stats: Dict[str, Any]) -> None:
    """Update character stat display"""
    for stat_name, stat_value in stats.items():
        label_attr = f"{stat_name}_label"
        if hasattr(widget, label_attr):
            label = getattr(widget, label_attr)
            label.configure(text=str(stat_value))

def update_health_bar(widget: tk.Widget, current: float, maximum: Optional[float] = None) -> None:
    """Update health/mana bar"""
    if hasattr(widget, 'update_bar'):
        widget.update_bar(current, maximum)

def add_inventory_item(widget: tk.Widget, row: int, col: int, item_data: Dict[str, Any]) -> None:
    """Add item to inventory grid"""
    if hasattr(widget, 'grid_data'):
        widget.grid_data[(row, col)] = item_data
        # Visual update would go here

def add_combat_message(widget: tk.Widget, message: str, msg_type: str = "system") -> None:
    """Add message to combat log"""
    if hasattr(widget, 'add_message'):
        widget.add_message(message, msg_type)

def add_chat_message(widget: tk.Widget, sender: str, message: str, msg_type: str = "player") -> None:
    """Add message to chat"""
    if hasattr(widget, 'add_message'):
        widget.add_message(sender, message, msg_type)
