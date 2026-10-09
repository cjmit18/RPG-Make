#!/usr/bin/env python3
"""
Start Screen Tab Provider - Welcome screen with modern design
Provides a beautiful entry point to the RPG Character Engine
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Callable
from pathlib import Path

from rpg_engine.ui.dynamic_tab_manager import TabProvider, TabState

logger = logging.getLogger(__name__)

class StartScreenTabProvider(TabProvider):
    """Tab provider for the start screen with modern welcome design"""
    
    def __init__(self, ui_manager=None):
        self.ui_manager = ui_manager
        self.template_count = 0
        self._load_stats()
    
    def _load_stats(self) -> None:
        """Load application statistics"""
        try:
            # Load template count for display
            import json
            data_path = Path(__file__).parent.parent / "data" / "character_templates.json"
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.template_count = len(data.get("character_templates", {}))
            logger.info(f"Start screen loaded {self.template_count} templates")
        except Exception as e:
            logger.warning(f"Could not load template stats: {e}")
            self.template_count = 7  # Fallback
    
    def get_tab_info(self) -> Dict[str, str]:
        """Return tab information"""
        return {
            "id": "start_screen",
            "title": "🏠 Welcome",
            "tooltip": "Welcome to RPG Character Engine"
        }
    
    def create_content(self, parent: tk.Widget, tab_state: TabState) -> tk.Widget:
        """Create the enhanced start screen with modern design"""
        # Main content frame with modern styling
        main_frame = ttk.Frame(parent)
        
        # Hero section with large welcome message
        hero_frame = ttk.Frame(main_frame)
        hero_frame.pack(fill="x", padx=40, pady=(40, 30))
        
        # Main title
        title_label = ttk.Label(hero_frame, 
                               text="⚔️ RPG CHARACTER ENGINE ⚔️", 
                               font=("Segoe UI", 32, "bold"),
                               foreground="#2c3e50")
        title_label.pack(anchor="center", pady=(0, 15))
        
        # Subtitle
        subtitle_label = ttk.Label(hero_frame,
                                  text="🎭 The Ultimate Character Creation Experience", 
                                  font=("Segoe UI", 16, "italic"),
                                  foreground="#7f8c8d")
        subtitle_label.pack(anchor="center", pady=(0, 10))
        
        # Version/stats line
        
        # Features section
        features_frame = ttk.LabelFrame(main_frame, text="🔥 Key Features", padding=25)
        features_frame.pack(fill="x", padx=40, pady=(0, 25))
        
        # Feature grid
        features_grid = ttk.Frame(features_frame)
        features_grid.pack(fill="x")
        
        # Left column features
        left_features = ttk.Frame(features_grid)
        left_features.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        features_left = [
            ("🎲 Random Stat Distribution", "Intelligent point-by-point allocation system"),
            ("📊 Advanced Analytics", "Real-time stat validation and derived calculations"),
            ("🎨 Dynamic UI", "Modern tabbed interface with seamless navigation")
        ]
        
        for title, desc in features_left:
            feature_frame = ttk.Frame(left_features)
            feature_frame.pack(fill="x", pady=8)
            
            ttk.Label(feature_frame, text=title, 
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
            ttk.Label(feature_frame, text=desc, 
                     font=("Segoe UI", 9), 
                     foreground="#7f8c8d").pack(anchor="w", padx=(20, 0))
        
        # Right column features
        right_features = ttk.Frame(features_grid)
        right_features.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        features_right = [
            ("🧙‍♂️ Smart Templates", f"{self.template_count} character archetypes with intelligent stat recommendations"),
            ("⚡ Enhanced Character Info", "Live character summary with template bonuses and tips"),
            ("🔄 Real-time Updates", "Instant feedback and validation as you build your character")
        ]
        
        for title, desc in features_right:
            feature_frame = ttk.Frame(right_features)
            feature_frame.pack(fill="x", pady=8)
            
            ttk.Label(feature_frame, text=title, 
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
            ttk.Label(feature_frame, text=desc, 
                     font=("Segoe UI", 9), 
                     foreground="#7f8c8d").pack(anchor="w", padx=(20, 0))
        
        # Quick start section
        quickstart_frame = ttk.LabelFrame(main_frame, text="🚀 Quick Start Guide", padding=25)
        quickstart_frame.pack(fill="x", padx=40, pady=(0, 25))
        
        steps = [
            "1️⃣ Browse Templates - Explore available character archetypes and their rich backstories",
            "2️⃣ Create Character - Use the step-by-step wizard to build your perfect character",
            "3️⃣ Customize Stats - Apply templates or manually distribute points with intelligent validation",
            "4️⃣ Review & Export - Finalize your character and export for use in your campaigns"
        ]
        
        for step in steps:
            step_label = ttk.Label(quickstart_frame, text=step, 
                                  font=("Segoe UI", 10))
            step_label.pack(anchor="w", pady=4)
        
        # Action buttons section
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill="x", padx=40, pady=(0, 40))
        
        # Button container for centering
        button_container = ttk.Frame(actions_frame)
        button_container.pack(expand=True)
        
        # Primary action buttons
        browse_button = ttk.Button(button_container,
                                  text="🎨 Browse Templates",
                                  command=self._browse_templates,
                                  width=20)
        browse_button.pack(side="left", padx=10)
        
        create_button = ttk.Button(button_container,
                                  text="⚔️ Create Character",
                                  command=self._create_character,
                                  width=20)
        create_button.pack(side="left", padx=10)
        
        return main_frame
    
    def _browse_templates(self) -> None:
        """Navigate to browse templates tab"""
        if hasattr(self.ui_manager, 'switch_to_browse_templates'):
            self.ui_manager.switch_to_browse_templates()
        elif hasattr(self.ui_manager, 'tab_manager'):
            self.ui_manager.tab_manager.switch_to_tab('browse_templates')
        logger.info("Navigating to browse templates")
    
    def _create_character(self) -> None:
        """Navigate to character creation tab"""
        if hasattr(self.ui_manager, 'switch_to_character_creation'):
            self.ui_manager.switch_to_character_creation()
        elif hasattr(self.ui_manager, 'tab_manager'):
            self.ui_manager.tab_manager.switch_to_tab('character_creation')
        logger.info("Navigating to character creation")
    
    def on_tab_activated(self, tab_state: TabState) -> None:
        """Called when the tab becomes active"""
        logger.info("Start Screen tab activated")
        # Refresh stats if needed
        self._load_stats()
    
    def on_tab_deactivated(self, tab_state: TabState) -> None:
        """Called when the tab becomes inactive"""
        logger.info("Start Screen tab deactivated")
    
    def get_commands(self) -> Dict[str, Callable]:
        """Return available commands"""
        return {
            "browse_templates": self._browse_templates,
            "create_character": self._create_character
        }
