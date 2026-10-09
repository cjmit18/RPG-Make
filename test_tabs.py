#!/usr/bin/env python3
"""
Simple test of the dynamic tab system
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

import tkinter as tk
from tkinter import ttk
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from rpg_engine.ui.dynamic_tab_manager import DynamicTabManager
    from tabs.browse_templates_provider import BrowseTemplatesTabProvider
    from tabs.character_creation_provider import CharacterCreationTabProvider
    
    logger.info("✅ All imports successful")
    
    # Create simple test window
    root = tk.Tk()
    root.title("Dynamic Tab System Test")
    root.geometry("800x600")
    
    # Create tab manager
    tab_manager = DynamicTabManager(root, ui_manager=None)
    
    # Create providers
    browse_provider = BrowseTemplatesTabProvider(ui_manager=None)
    creation_provider = CharacterCreationTabProvider(ui_manager=None)
    
    # Register tabs
    tab_manager.register_tab_provider('browse', browse_provider)
    tab_manager.register_tab_provider('create', creation_provider)
    
    logger.info("✅ Tab system initialized successfully")
    
    # Run the application
    root.mainloop()
    
except Exception as e:
    logger.error(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
