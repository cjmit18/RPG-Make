#!/usr/bin/env python3
"""
Tabs Module - Contains all tab implementations for the RPG Character Manager
"""

from .character_creation_provider import CharacterCreationTabProvider
from .browse_templates_provider import BrowseTemplatesTabProvider
from .start_screen_provider import StartScreenTabProvider

__all__ = [
    'CharacterCreationTabProvider',
    'BrowseTemplatesTabProvider',
    'StartScreenTabProvider'
]