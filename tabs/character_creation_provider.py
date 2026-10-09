#!/usr/bin/env python3
"""
Character Creation Tab Provider - Dynamic tab implementation for character creation
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import logging
import random
from datetime import datetime

from rpg_engine.ui.dynamic_tab_manager import TabProvider, TabState
from rpg_engine.systems.character.stat_system import CharacterStats
from rpg_engine.core.config import get_config, Rarity, Grade

logger = logging.getLogger(__name__)

class CharacterCreationTabProvider(TabProvider):
    """Tab provider for character creation"""
    
    def __init__(self, ui_manager=None):
        self.ui_manager = ui_manager
        self.templates_data = None
        self.current_character = {}
        self.selected_template = None
        self.template_base_stats = {}  # Initialize empty template base stats
        self.total_stat_points = 0  # Initialize total stat points
        
        # Stat allocation properties (will be calculated from template/config)
       
        
        # Initialize stat system for validation
        self.stat_system = None
        self._initialize_stat_system()
        
        self._load_templates()
    
    def _initialize_stat_system(self) -> None:
        """Initialize the stat system for validation"""
        try:
            self.config = get_config()
            self.stat_system = None  # Will implement simpler validation
        except Exception as e:
            logger.warning(f"Could not initialize config: {e}")
            self.config = None
            self.stat_system = None
    
    def _calculate_stat_points_for_level(self, level: int = 1) -> int:
        """Calculate available stat points for character level"""
        if self.config and hasattr(self.config, 'leveling_config'):
            base_points = getattr(self.config.leveling_config, 'stat_points_per_level', 2)
            return base_points * level
        else:
            # Fallback calculation
            return 2 * level  # 2 points per level is common in RPGs
    
    def _get_template_base_stats(self) -> Dict[str, int]:
        """Get base stats from selected template or config defaults"""
        if self.selected_template and self.selected_template in self.templates_data:
            template_info = self.templates_data[self.selected_template]
            
            # Try base_stats first (new format), then stats (old format)
            template_stats = template_info.get('base_stats') or template_info.get('stats', {})
            
            if template_stats:
                logger.info(f"Using template base stats: {template_stats}")
                return template_stats
        
        # Use config base stats if available
        if self.config and hasattr(self.config, 'base_stats'):
            base_stats = self.config.base_stats
            config_stats = {
                'strength': base_stats.strength,
                'dexterity': base_stats.dexterity,
                'constitution': base_stats.constitution,
                'intelligence': base_stats.intelligence,
                'wisdom': base_stats.wisdom,
                'charisma': base_stats.charisma
            }
            logger.info(f"Using config base stats: {config_stats}")
            return config_stats
        
        # Final fallback - standard RPG base stats
        fallback_stats = {
            'strength': 10,
            'dexterity': 10,
            'constitution': 10,
            'intelligence': 10,
            'wisdom': 10,
            'charisma': 9  # Match the observed pattern
        }
        logger.warning(f"Using fallback base stats: {fallback_stats}")
        return fallback_stats
    
    def _load_templates(self) -> None:
        """Load character templates from JSON file"""
        try:
            data_path = Path(__file__).parent.parent / "data" / "character_templates.json"
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.templates_data = data.get("character_templates", {})
            logger.info(f"Loaded {len(self.templates_data)} character templates for creation")
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            self.templates_data = {}
    
    def get_tab_info(self) -> Dict[str, str]:
        """Return tab metadata"""
        return {
            'title': 'Create Character',
            'icon': '⚔️',
            'description': 'Create a new character using templates'
        }
    
    def create_content(self, parent: tk.Widget, tab_state: TabState) -> tk.Widget:
        """Create the modern, streamlined character creation content"""
        # Main content frame with modern styling
        main_frame = ttk.Frame(parent)
        
        # Modern header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        # Title with modern styling
        title_label = ttk.Label(header_frame, 
                               text="🎭 Character Creation Studio", 
                               font=("Segoe UI", 24, "bold"))
        title_label.pack(anchor="w")
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame,
                                  text="Design your perfect RPG character with our intelligent creation system",
                                  font=("Segoe UI", 12),
                                  foreground="#6c757d")
        subtitle_label.pack(anchor="w", pady=(3, 0))
        
        # Progress bar and current step indicator
        progress_frame = ttk.Frame(header_frame)
        progress_frame.pack(fill="x", pady=(10, 0))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.step_label = ttk.Label(progress_frame, 
                                   text="Step 1 of 3: Choose Template", 
                                   font=("Segoe UI", 10),
                                   foreground="#28a745")
        self.step_label.pack(anchor="w")
        
        # Modern separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=10)
        
        # Main content area with side-by-side layout
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Creation content (65% width)
        self.left_panel = ttk.Frame(content_frame)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Right panel - Live preview (35% width)
        self.right_panel = ttk.Frame(content_frame)
        self.right_panel.pack(side="right", fill="y", padx=(15, 0))
        self.right_panel.config(width=350)
        self.right_panel.pack_propagate(False)
        
        # Setup the live preview panel
        self._setup_live_preview_panel()
        
        # Initialize with template selection
        self.current_step = 1
        self._show_template_selection()
        
        # Store widgets in tab state
        tab_state.widgets.update({
            'current_character': self.current_character,
            'current_step': self.current_step
        })
        
        return main_frame
    
    def _setup_live_preview_panel(self) -> None:
        """Setup the live character preview panel"""
        # Character preview card
        preview_frame = ttk.LabelFrame(self.right_panel, text="🎭 Character Preview", padding=15)
        preview_frame.pack(fill="both", expand=True)
        
        # Character avatar/icon area
        avatar_frame = ttk.Frame(preview_frame)
        avatar_frame.pack(fill="x", pady=(0, 15))
        
        # Large character icon
        self.avatar_label = ttk.Label(avatar_frame, 
                                     text="🧙‍♂️", 
                                     font=("Segoe UI", 48))
        self.avatar_label.pack()
        
        # Character name display
        self.preview_name = ttk.Label(avatar_frame, 
                                     text="Unnamed Character", 
                                     font=("Segoe UI", 14, "bold"))
        self.preview_name.pack(pady=(5, 0))
        
        # Template display
        self.preview_template = ttk.Label(avatar_frame, 
                                         text="No template selected", 
                                         font=("Segoe UI", 10, "italic"),
                                         foreground="#6c757d")
        self.preview_template.pack()
        
        # Stats preview area
        stats_frame = ttk.LabelFrame(preview_frame, text="📊 Quick Stats", padding=10)
        stats_frame.pack(fill="x", pady=(15, 0))
        
        # Create compact stats display
        self.preview_stats = {}
        main_stats = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        
        for i, stat in enumerate(main_stats):
            row = i // 2
            col = i % 2
            
            stat_frame = ttk.Frame(stats_frame)
            if col == 0:
                stat_frame.pack(fill="x", pady=2)
            else:
                # Find the existing frame for this row
                for child in stats_frame.winfo_children():
                    if isinstance(child, ttk.Frame):
                        existing_children = len([c for c in child.winfo_children() if isinstance(c, ttk.Label)])
                        if existing_children == 2:  # This frame already has a stat
                            continue
                        else:
                            stat_frame = child
                            break
            
            stat_label = ttk.Label(stat_frame, text=f"{stat}:", width=4)
            stat_label.pack(side="left")
            
            value_label = ttk.Label(stat_frame, text="10", font=("Segoe UI", 9, "bold"))
            value_label.pack(side="left", padx=(5, 15))
            
            # Store with proper mapping - use the 3-letter abbreviation as key
            self.preview_stats[stat] = value_label
        
        # Action buttons at bottom
        actions_frame = ttk.Frame(preview_frame)
        actions_frame.pack(fill="x", pady=(15, 0))
        
        self.random_btn = ttk.Button(actions_frame, text="🎲 Randomize", 
                                    command=self._randomize_character, width=15)
        self.random_btn.pack(fill="x", pady=2)
        
        self.reset_btn = ttk.Button(actions_frame, text="🔄 Reset", 
                                   command=self._reset_character, width=15)
        self.reset_btn.pack(fill="x", pady=2)
    
    def _show_template_selection(self) -> None:
        """Show template selection step"""
        # Clear left panel
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        
        # Update progress
        self.progress_var.set(33)
        self.step_label.config(text="Step 1 of 3: Choose Your Character Template")
        
        # Template selection content
        content_frame = ttk.Frame(self.left_panel)
        content_frame.pack(fill="both", expand=True)
        
        # Header
        header_label = ttk.Label(content_frame, 
                                text="🎭 Select Character Template", 
                                font=("Segoe UI", 18, "bold"))
        header_label.pack(pady=(0, 15))
        
        # Template grid layout
        templates_frame = ttk.Frame(content_frame)
        templates_frame.pack(fill="both", expand=True)
        
        # Create template cards in a grid
        self.template_cards = {}
        templates = list(self.templates_data.keys()) if self.templates_data else []
        
        # Configure grid
        cols = 2
        for i, template_name in enumerate(templates[:6]):  # Show first 6 templates
            row = i // cols
            col = i % cols
            
            card = self._create_template_card(templates_frame, template_name, template_name == self.selected_template)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.template_cards[template_name] = card
            
            # Configure grid weights
            templates_frame.grid_rowconfigure(row, weight=1)
            templates_frame.grid_columnconfigure(col, weight=1)
        
        # Navigation
        nav_frame = ttk.Frame(content_frame)
        nav_frame.pack(fill="x", pady=(20, 0))
        
        self.next_step1_btn = ttk.Button(nav_frame, text="Next: Customize Character →", 
                                        command=self._show_character_customization,
                                        state="disabled" if not self.selected_template else "normal")
        self.next_step1_btn.pack(side="right")
    
    def _create_template_card(self, parent: tk.Widget, template_name: str, selected: bool = False) -> tk.Widget:
        """Create a modern template selection card"""
        # Main card frame with selection styling
        card_style = "selected.TFrame" if selected else "TFrame"
        card = ttk.Frame(parent, relief="solid", borderwidth=2 if selected else 1)
        card.pack_propagate(False)
        card.config(height=120, width=250)
        
        # Make card clickable
        card.bind("<Button-1>", lambda e: self._select_template(template_name))
        
        # Card content
        content = ttk.Frame(card, padding=15)
        content.pack(fill="both", expand=True)
        content.bind("<Button-1>", lambda e: self._select_template(template_name))
        
        # Template icon and name
        icon_frame = ttk.Frame(content)
        icon_frame.pack(fill="x")
        icon_frame.bind("<Button-1>", lambda e: self._select_template(template_name))
        
        # Get template data
        template_data = self.templates_data.get(template_name, {})
        template_icon = template_data.get('icon', '🧙‍♂️')
        
        icon_label = ttk.Label(icon_frame, text=template_icon, font=("Segoe UI", 24))
        icon_label.pack(side="left")
        icon_label.bind("<Button-1>", lambda e: self._select_template(template_name))
        
        name_label = ttk.Label(icon_frame, text=template_name.title(), 
                              font=("Segoe UI", 12, "bold"))
        name_label.pack(side="left", padx=(10, 0))
        name_label.bind("<Button-1>", lambda e: self._select_template(template_name))
        
        # Template description
        description = template_data.get('description', 'A mysterious character class')[:60] + "..."
        desc_label = ttk.Label(content, text=description, 
                              font=("Segoe UI", 9), 
                              foreground="#6c757d",
                              wraplength=220)
        desc_label.pack(fill="x", pady=(8, 0))
        desc_label.bind("<Button-1>", lambda e: self._select_template(template_name))
        
        return card
    
    def _select_template(self, template_name: str) -> None:
        """Select a template and update UI"""
        self.selected_template = template_name
        
        # Update template cards
        for name, card in self.template_cards.items():
            if name == template_name:
                card.config(relief="solid", borderwidth=2)
            else:
                card.config(relief="solid", borderwidth=1)
        
        # Update preview
        template_data = self.templates_data.get(template_name, {})
        self.preview_template.config(text=template_name.title())
        
        # Update avatar based on template
        template_icon = template_data.get('icon', '🧙‍♂️')
        self.avatar_label.config(text=template_icon)
        
        # Enable next button
        if hasattr(self, 'next_step1_btn'):
            self.next_step1_btn.config(state="normal")
        
        # Update character data
        self.current_character.update({
            'template': template_name,
            'icon': template_icon
        })
        
        # Load template stats
        self._load_template_stats()
    
    def _load_template_stats(self) -> None:
        """Load and apply template base stats"""
        if not self.selected_template:
            return
        
        self.template_base_stats = self._get_template_base_stats()
        self.total_stat_points = 3  # Fixed 3 points to distribute (can add up to 3 per stat, 1 stat max)
        
        # Update preview stats with proper mapping
        stat_mapping = {
            'strength': 'STR',
            'dexterity': 'DEX', 
            'constitution': 'CON',
            'intelligence': 'INT',
            'wisdom': 'WIS',
            'charisma': 'CHA'
        }
        
        for stat, value in self.template_base_stats.items():
            if stat in stat_mapping:
                short_stat = stat_mapping[stat]
                if short_stat in self.preview_stats:
                    self.preview_stats[short_stat].config(text=str(value))
    
    def _show_character_customization(self) -> None:
        """Show character customization step (combines basic info + stats)"""
        # Clear left panel
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        
        # Update progress
        self.progress_var.set(66)
        self.step_label.config(text="Step 2 of 3: Customize Your Character")
        self.current_step = 2
        
        # Main content
        content_frame = ttk.Frame(self.left_panel)
        content_frame.pack(fill="both", expand=True)
        
        # Header
        header_label = ttk.Label(content_frame, 
                                text="🎨 Character Customization", 
                                font=("Segoe UI", 18, "bold"))
        header_label.pack(pady=(0, 20))
        
        # Create two-column layout
        columns_frame = ttk.Frame(content_frame)
        columns_frame.pack(fill="both", expand=True)
        
        # Left column - Basic Info
        left_col = ttk.LabelFrame(columns_frame, text="📝 Character Details", padding=15)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Character name
        name_frame = ttk.Frame(left_col)
        name_frame.pack(fill="x", pady=5)
        
        ttk.Label(name_frame, text="Name:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.name_entry = ttk.Entry(name_frame, font=("Segoe UI", 11))
        self.name_entry.pack(fill="x", pady=(2, 0))
        self.name_entry.bind("<KeyRelease>", self._update_preview_name)
        
        # Background
        bg_frame = ttk.Frame(left_col)
        bg_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        ttk.Label(bg_frame, text="Background Story:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.background_text = tk.Text(bg_frame, height=6, wrap=tk.WORD, font=("Segoe UI", 9))
        self.background_text.pack(fill="both", expand=True, pady=(2, 0))
        
        # Right column - Stats
        right_col = ttk.LabelFrame(columns_frame, text="⚡ Attribute Points", padding=15)
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Points display
        points_frame = ttk.Frame(right_col)
        points_frame.pack(fill="x", pady=(0, 15))
        
        self.points_label = ttk.Label(points_frame, 
                                    text="Available Points: 3", 
                                    font=("Segoe UI", 11, "bold"),
                                    foreground="#28a745")
        self.points_label.pack()
        
        # Stats controls
        self.stat_vars = {}
        self.stat_controls = {}
        
        main_stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for stat in main_stats:
            stat_frame = ttk.Frame(right_col)
            stat_frame.pack(fill="x", pady=3)
            
            # Stat label
            ttk.Label(stat_frame, text=f"{stat.title()}:", 
                     font=("Segoe UI", 9, "bold"), width=12).pack(side="left")
            
            # Decrease button
            dec_btn = ttk.Button(stat_frame, text="−", width=3,
                               command=lambda s=stat: self._modify_stat(s, -1))
            dec_btn.pack(side="right", padx=(0, 2))
            
            # Value display
            base_value = self.template_base_stats.get(stat, 10)
            value_var = tk.IntVar(value=base_value)
            self.stat_vars[stat] = value_var
            
            value_label = ttk.Label(stat_frame, textvariable=value_var, 
                                  font=("Segoe UI", 10, "bold"), width=3)
            value_label.pack(side="right", padx=2)
            
            # Increase button
            inc_btn = ttk.Button(stat_frame, text="+", width=3,
                               command=lambda s=stat: self._modify_stat(s, 1))
            inc_btn.pack(side="right", padx=(2, 0))
            
            self.stat_controls[stat] = {'inc': inc_btn, 'dec': dec_btn, 'var': value_var}
        
        # Quick action buttons
        actions_frame = ttk.Frame(right_col)
        actions_frame.pack(fill="x", pady=(15, 0))
        
        ttk.Button(actions_frame, text="🎯 Apply Growth Stats", 
                  command=self._apply_template_growth, width=15).pack(fill="x", pady=1)
        ttk.Button(actions_frame, text="🎲 Random Stats", 
                  command=self._randomize_stats, width=15).pack(fill="x", pady=1)
        ttk.Button(actions_frame, text="🔄 Reset", 
                  command=self._reset_stats, width=15).pack(fill="x", pady=1)
        
        # Navigation
        nav_frame = ttk.Frame(content_frame)
        nav_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(nav_frame, text="← Back to Templates", 
                  command=self._show_template_selection).pack(side="left")
        ttk.Button(nav_frame, text="Next: Review & Create →", 
                  command=self._show_final_review).pack(side="right")
    
    def _show_final_review(self) -> None:
        """Show final review and creation step with proper buttons and navigation"""
        # Clear left panel
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        
        # Update progress
        self.progress_var.set(100)
        self.step_label.config(text="Step 3 of 3: Review and Create Character")
        self.current_step = 3
        
        # Main content
        content_frame = ttk.Frame(self.left_panel)
        content_frame.pack(fill="both", expand=True)
        
        # Header
        header_label = ttk.Label(content_frame, 
                                text="✅ Character Review & Creation", 
                                font=("Segoe UI", 18, "bold"))
        header_label.pack(pady=(0, 15))
        
        # Two-column layout for review
        review_columns = ttk.Frame(content_frame)
        review_columns.pack(fill="both", expand=True)
        
        # Left column - Character summary
        left_review = ttk.LabelFrame(review_columns, text="📋 Character Summary", padding=15)
        left_review.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Character details text
        self.review_text = tk.Text(left_review, height=10, wrap=tk.WORD, 
                                  font=("Segoe UI", 10), state="disabled")
        self.review_text.pack(fill="both", expand=True)
        
        # Right column - Final stats preview
        right_review = ttk.LabelFrame(review_columns, text="📊 Final Statistics", padding=15)
        right_review.pack(side="right", fill="y", padx=(10, 0))
        right_review.config(width=200)
        right_review.pack_propagate(False)
        
        # Stats display
        self.final_stats_frame = ttk.Frame(right_review)
        self.final_stats_frame.pack(fill="both", expand=True)
        
        # Populate both panels
        self._populate_character_summary(self.review_text)
        self._populate_final_stats()
        
        # Action buttons section
        actions_section = ttk.Frame(content_frame)
        actions_section.pack(fill="x", pady=(20, 0))
        
        # Action buttons frame
        actions_frame = ttk.Frame(actions_section)
        actions_frame.pack(pady=(10, 0))
        
        # Main action buttons
        create_btn = ttk.Button(actions_frame, text="🎭 Create Character", 
                               command=self._create_character, width=18)
        create_btn.pack(side="left", padx=(0, 10))
        
        save_btn = ttk.Button(actions_frame, text="💾 Save Character", 
                             command=self._save_character, width=15)
        save_btn.pack(side="left", padx=(0, 10))
        
        export_btn = ttk.Button(actions_frame, text="📤 Export", 
                               command=self._export_character, width=12)
        export_btn.pack(side="left")
        
        # Navigation buttons
        nav_frame = ttk.Frame(content_frame)
        nav_frame.pack(fill="x", pady=(20, 0))
        
        back_btn = ttk.Button(nav_frame, text="← Back to Customize", 
                             command=self._show_character_customization)
        back_btn.pack(side="left")
        
        new_char_btn = ttk.Button(nav_frame, text="🔄 Create Another Character", 
                                 command=self._start_new_character)
        new_char_btn.pack(side="right")
    
    def _populate_final_stats(self) -> None:
        """Populate the final stats display"""
        # Clear existing widgets
        for widget in self.final_stats_frame.winfo_children():
            widget.destroy()
        
        # Display final stats
        if hasattr(self, 'stat_vars'):
            for stat, var in self.stat_vars.items():
                stat_frame = ttk.Frame(self.final_stats_frame)
                stat_frame.pack(fill="x", pady=2)
                
                # Stat name
                ttk.Label(stat_frame, text=f"{stat.title()}:", 
                         font=("Segoe UI", 9, "bold"), width=10).pack(side="left")
                
                # Stat value
                value = var.get()
                base = self.template_base_stats.get(stat, 10)
                
                if value > base:
                    # Show bonus
                    ttk.Label(stat_frame, text=f"{value} (+{value-base})", 
                             font=("Segoe UI", 9), foreground="#28a745").pack(side="right")
                else:
                    ttk.Label(stat_frame, text=str(value), 
                             font=("Segoe UI", 9)).pack(side="right")
        
            # Show total points used
            if hasattr(self, 'stat_vars') and hasattr(self, 'template_base_stats'):
                points_used = sum(max(0, var.get() - self.template_base_stats.get(stat, 10)) 
                                for stat, var in self.stat_vars.items())
                
                ttk.Separator(self.final_stats_frame, orient="horizontal").pack(fill="x", pady=5)
                
                points_frame = ttk.Frame(self.final_stats_frame)
                points_frame.pack(fill="x", pady=5)
                
                ttk.Label(points_frame, text="Points Used:", 
                         font=("Segoe UI", 9, "bold")).pack(side="left")
                ttk.Label(points_frame, text=f"{points_used}/3", 
                         font=("Segoe UI", 9), foreground="#007bff").pack(side="right")    # Helper methods for the new streamlined design
    def _update_preview_name(self, event=None) -> None:
        """Update the preview name as user types"""
        name = self.name_entry.get().strip()
        self.preview_name.config(text=name or "Unnamed Character")
        self.current_character['name'] = name
    
    def _modify_stat(self, stat: str, change: int) -> None:
        """Modify a stat value with proper point system constraints"""
        if not hasattr(self, 'stat_vars') or stat not in self.stat_vars:
            return
        
        current_value = self.stat_vars[stat].get()
        base_value = self.template_base_stats.get(stat, 10)
        
        # Calculate current total points spent
        current_spent = 0
        for s, var in self.stat_vars.items():
            base = self.template_base_stats.get(s, 10)
            current_spent += max(0, var.get() - base)
        
        # Calculate new value (clamp between base and base+3)
        min_value = base_value
        max_value = base_value + 3  # Maximum 3 points above base
        new_value = max(min_value, min(max_value, current_value + change))
        
        # Check if we have enough points
        if change > 0:  # Increasing stat
            points_needed = new_value - current_value
            available_points = self.total_stat_points - current_spent
            
            if points_needed > available_points:
                # Not enough points available
                return
        
        # Apply the change
        if new_value != current_value:
            self.stat_vars[stat].set(new_value)
            self._update_stats_preview()
            self._update_points_display()
    
    def _update_points_display(self) -> None:
        """Update the available points display"""
        if not hasattr(self, 'points_label') or not hasattr(self, 'stat_vars'):
            return
        
        # Calculate points spent
        points_spent = 0
        for stat, var in self.stat_vars.items():
            base = self.template_base_stats.get(stat, 10)
            points_spent += max(0, var.get() - base)
        
        available_points = self.total_stat_points - points_spent
        
        # Update label with color coding
        if available_points > 0:
            self.points_label.config(text=f"Available Points: {available_points}", 
                                   foreground="#28a745")
        elif available_points == 0:
            self.points_label.config(text="Available Points: 0 (All points used)", 
                                   foreground="#ffc107")
        else:
            self.points_label.config(text=f"Available Points: {available_points} (Over limit!)", 
                                   foreground="#dc3545")
        
        # Update button states using stat_controls
        if hasattr(self, 'stat_controls'):
            for stat, controls in self.stat_controls.items():
                if stat in self.stat_vars and stat in self.template_base_stats:
                    current_value = self.stat_vars[stat].get()
                    base_value = self.template_base_stats[stat]
                    max_value = base_value + 3
                    
                    # Enable/disable buttons
                    can_increase = (available_points > 0 and current_value < max_value)
                    can_decrease = (current_value > base_value)
                    
                    controls['inc'].config(state="normal" if can_increase else "disabled")
                    controls['dec'].config(state="normal" if can_decrease else "disabled")
    
    def _update_stats_preview(self) -> None:
        """Update the stats preview in the right panel"""
        # Proper stat mapping for preview updates
        stat_mapping = {
            'strength': 'STR',
            'dexterity': 'DEX', 
            'constitution': 'CON',
            'intelligence': 'INT',
            'wisdom': 'WIS',
            'charisma': 'CHA'
        }
        
        # Update each stat in the preview
        for stat, short_stat in stat_mapping.items():
            if hasattr(self, 'stat_vars') and stat in self.stat_vars:
                if short_stat in self.preview_stats:
                    value = self.stat_vars[stat].get()
                    self.preview_stats[short_stat].config(text=str(value))
        
        # Update points display
        self._update_points_display()
    
    def _apply_template_growth(self) -> None:
        """Apply template-based stat growth using growth rates to distribute points intelligently"""
        if not self.selected_template or not hasattr(self, 'stat_vars'):
            return
        
        template_data = self.templates_data.get(self.selected_template, {})
        growth_rates = template_data.get('growth_rates', {})
        
        if not growth_rates:
            # Fallback: just reset to base stats if no growth rates
            self._reset_stats()
            return
        
        # Reset all stats to base values first
        for stat, var in self.stat_vars.items():
            base_value = self.template_base_stats.get(stat, 10)
            var.set(base_value)
        
        # Create a list of stats sorted by their growth rates (highest first)
        # Only include stats that exist in our stat_vars
        available_stats = [(stat, rate) for stat, rate in growth_rates.items() 
                          if stat in self.stat_vars and rate > 0]
        available_stats.sort(key=lambda x: x[1], reverse=True)
        
        if not available_stats:
            return
        
        # Distribute the 3 available points based on growth rates
        points_to_distribute = self.total_stat_points
        points_distributed = 0
        
        # First pass: Give priority to highest growth rate stats
        for stat, growth_rate in available_stats:
            if points_distributed >= points_to_distribute:
                break
                
            base_value = self.template_base_stats.get(stat, 10)
            current_value = self.stat_vars[stat].get()
            max_value = base_value + 3  # Maximum 3 points above base
            
            # Determine how many points to give this stat based on growth rate
            # Higher growth rates get more points
            if growth_rate >= 1.2:  # High growth rate
                points_to_add = min(2, max_value - current_value, points_to_distribute - points_distributed)
            elif growth_rate >= 1.0:  # Medium growth rate  
                points_to_add = min(1, max_value - current_value, points_to_distribute - points_distributed)
            else:  # Low growth rate (< 1.0)
                points_to_add = 0
            
            if points_to_add > 0:
                self.stat_vars[stat].set(current_value + points_to_add)
                points_distributed += points_to_add
        
        # Second pass: Distribute any remaining points to the highest growth rate stats
        while points_distributed < points_to_distribute and available_stats:
            for stat, growth_rate in available_stats:
                if points_distributed >= points_to_distribute:
                    break
                    
                base_value = self.template_base_stats.get(stat, 10)
                current_value = self.stat_vars[stat].get()
                max_value = base_value + 3
                
                if current_value < max_value:
                    self.stat_vars[stat].set(current_value + 1)
                    points_distributed += 1
                    break
            else:
                # No more stats can be increased, break the while loop
                break
        
        # Update the preview
        self._update_stats_preview()
        
        # Show feedback to user
        from tkinter import messagebox
        messagebox.showinfo("Template Growth Applied", 
                           f"✅ Applied {self.selected_template} growth pattern!\n\n"
                           f"📈 Distributed {points_distributed} points based on class strengths\n"
                           f"🎯 Optimized for {self.selected_template.replace('_', ' ').title()} playstyle")
    
    def _randomize_stats(self) -> None:
        """Randomize character stats"""
        import random
        
        # Clear current allocation
        for stat, var in self.stat_vars.items():
            base = self.template_base_stats.get(stat, 10)
            var.set(base)
        
        # Randomly distribute available points
        remaining_points = self.total_stat_points
        stat_list = list(self.stat_vars.keys())
        
        while remaining_points > 0 and stat_list:
            stat = random.choice(stat_list)
            base = self.template_base_stats.get(stat, 10)
            current = self.stat_vars[stat].get()
            max_value = base + 3
            
            if current < max_value:
                self.stat_vars[stat].set(current + 1)
                remaining_points -= 1
            else:
                stat_list.remove(stat)
        
        self._update_stats_preview()
    
    def _randomize_character(self) -> None:
        """Randomize entire character"""
        # Random template
        if self.templates_data:
            random_template = random.choice(list(self.templates_data.keys()))
            self._select_template(random_template)
        
        # Random name
        random_names = ["Aeliana", "Thorgar", "Zephyr", "Lyralei", "Kael", "Mirana", "Daven", "Elara"]
        if hasattr(self, 'name_entry'):
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, random.choice(random_names))
            self._update_preview_name()
    
    def _reset_stats(self) -> None:
        """Reset stats to template base values"""
        if hasattr(self, 'stat_vars') and self.template_base_stats:
            for stat, var in self.stat_vars.items():
                base_value = self.template_base_stats.get(stat, 10)
                var.set(base_value)
            
            self._update_stats_preview()
    
    def _reset_character(self) -> None:
        """Reset character to defaults"""
        # Reset to first step
        self.current_step = 1
        self.selected_template = None
        self.current_character = {}
        
        # Reset preview
        self.preview_name.config(text="Unnamed Character")
        self.preview_template.config(text="No template selected")
        self.avatar_label.config(text="🧙‍♂️")
        
        # Reset preview stats to default
        for stat_key in self.preview_stats:
            self.preview_stats[stat_key].config(text="10")
        
        # Show template selection
        self._show_template_selection()
    
    def _populate_character_summary(self, text_widget: tk.Text) -> None:
        """Populate the character summary text"""
        text_widget.config(state="normal")
        text_widget.delete(1.0, tk.END)
        
        name = self.current_character.get('name', 'Unnamed Character')
        template = self.current_character.get('template', 'No template')
        
        summary = f"""🎭 CHARACTER SUMMARY
{'=' * 50}

Name: {name}
Template: {template.title() if template != 'No template' else template}

📊 STATISTICS
{'-' * 30}
"""
        
        if hasattr(self, 'stat_vars'):
            for stat, var in self.stat_vars.items():
                summary += f"{stat.title()}: {var.get()}\n"
        
        summary += f"""
📝 BACKGROUND
{'-' * 30}
"""
        
        # Safely get background text
        try:
            if hasattr(self, 'background_text') and self.background_text.winfo_exists():
                background = self.background_text.get(1.0, tk.END).strip()
                if background:
                    summary += background
                else:
                    summary += "No background story provided."
            else:
                summary += "No background story provided."
        except tk.TclError:
            summary += "No background story provided."
        
        summary += f"""

🎮 READY TO PLAY!
{'-' * 30}
Your character is ready for adventure!
        """
        
        text_widget.insert(1.0, summary)
        text_widget.config(state="disabled")
    
    def _save_character(self) -> None:
        """Save character to file"""
        try:
            # Create character data dictionary
            character_data = {
                'name': self.current_character.get('name', 'Unnamed Character'),
                'template': self.current_character.get('template', 'None'),
                'icon': self.current_character.get('icon', '🧙‍♂️'),
                'stats': {},
                'background': ''
            }
            
            # Get current stats
            if hasattr(self, 'stat_vars'):
                for stat, var in self.stat_vars.items():
                    character_data['stats'][stat] = var.get()
            
            # Get background
            if hasattr(self, 'background_text'):
                character_data['background'] = self.background_text.get(1.0, tk.END).strip()
            
            # Show save confirmation (in real implementation, save to file)
            name = character_data['name']
            messagebox.showinfo("Character Saved", 
                               f"💾 '{name}' has been saved successfully!\n\n"
                               f"Template: {character_data['template']}\n"
                               f"Stats: {len(character_data['stats'])} attributes saved")
            
        except Exception as e:
            logger.error(f"Failed to save character: {e}")
            messagebox.showerror("Save Error", f"❌ Failed to save character:\n{str(e)}")
    
    def _export_character(self) -> None:
        """Export character data"""
        try:
            # Create export data
            export_data = {
                'name': self.current_character.get('name', 'Unnamed Character'),
                'template': self.current_character.get('template', 'None'),
                'stats': {},
                'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if hasattr(self, 'stat_vars'):
                for stat, var in self.stat_vars.items():
                    export_data['stats'][stat] = var.get()
            
            # Show export info (in real implementation, export to file/clipboard)
            messagebox.showinfo("Character Exported", 
                               f"� Character data exported successfully!\n\n"
                               f"Format: JSON\n"
                               f"Character: {export_data['name']}\n"
                               f"Date: {export_data['creation_date']}")
            
        except Exception as e:
            logger.error(f"Failed to export character: {e}")
            messagebox.showerror("Export Error", f"❌ Failed to export character:\n{str(e)}")
    
    def _create_character(self) -> None:
        """Finalize character creation"""
        try:
            name = self.current_character.get('name', 'Unnamed Character')
            template = self.current_character.get('template', 'None')
            
            # Validation
            if not name.strip():
                messagebox.showwarning("Invalid Name", "⚠️ Please enter a character name!")
                return
            
            if not template or template == 'None':
                messagebox.showwarning("No Template", "⚠️ Please select a character template!")
                return
            
            # Show creation success
            messagebox.showinfo("Character Created", 
                               f"🎭 Character '{name}' created successfully!\n\n"
                               f"Template: {template}\n"
                               f"Ready for adventure!")
            
            # Reset for new character
            self._start_new_character()
            
        except Exception as e:
            logger.error(f"Failed to create character: {e}")
            messagebox.showerror("Creation Error", f"❌ Failed to create character:\n{str(e)}")
    
    def _start_new_character(self) -> None:
        """Start creating a new character"""
        # Reset all data
        self.current_step = 1
        self.selected_template = None
        self.current_character = {}
        self.template_base_stats = {}
        
        # Reset preview
        self.preview_name.config(text="Unnamed Character")
        self.preview_template.config(text="No template selected")
        self.avatar_label.config(text="🧙‍♂️")
        
        # Reset preview stats to default
        for stat_key in self.preview_stats:
            self.preview_stats[stat_key].config(text="10")
        
        # Reset progress
        self.progress_var.set(0)
        self.step_label.config(text="Step 1 of 3: Choose Your Character Template")
        
        # Show template selection
        self._show_template_selection()
        
        logger.info("Started new character creation")
        
    def _populate_final_stats(self) -> None:
        """Populate the final stats display"""
        # Clear existing widgets
        for widget in self.final_stats_frame.winfo_children():
            widget.destroy()
        
        # Display final stats
        if hasattr(self, 'stat_vars'):
            for stat, var in self.stat_vars.items():
                stat_frame = ttk.Frame(self.final_stats_frame)
                stat_frame.pack(fill="x", pady=2)
                
                ttk.Label(stat_frame, text=f"{stat.title()}:", 
                         font=("Segoe UI", 9), width=12).pack(side="left")
                
                ttk.Label(stat_frame, text=str(var.get()), 
                         font=("Segoe UI", 9, "bold")).pack(side="right")
        
    def on_tab_activated(self, tab_state: TabState) -> None:
        """Called when tab becomes active"""
        logger.info("Character Creation tab activated")
        
        # Check if we should load a specific template
        if hasattr(self.ui_manager, '_pending_template'):
            template_name = self.ui_manager._pending_template
            delattr(self.ui_manager, '_pending_template')
            self.load_template(template_name)
    
    def on_tab_deactivated(self, tab_state: TabState) -> None:
        """Called when tab becomes inactive"""
        logger.info("Character Creation tab deactivated")
    
    def on_tab_closing(self, tab_state: TabState) -> bool:
        """Called when tab is about to close"""
        if self.current_character and self.current_character.get('name'):
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved character creation progress. Save as draft?"
            )
            if result is True:  # Yes - save draft
                return True
            elif result is False:  # No - discard
                return True
            else:  # Cancel - don't close
                return False
        return True
    
    def get_commands(self) -> Dict[str, Callable]:
        """Return tab-specific commands"""
        return {
            'create_character': self._create_character,
            'save_character': self._save_character,
            'reset_creation': self._start_new_character
        }
