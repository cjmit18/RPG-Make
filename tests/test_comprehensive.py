#!/usr/bin/env python3
"""
Comprehensive Interactive Test Script for the SimpleGameDemo
===========================================================

This script provides a structured way to manually test all features of the demo
with the consolidated configuration system. It guides the user through each test
case and records the results for reference.

Features:
- Tabbed interface for test steps and notes
- Dark mode support with theme toggle
- Styled Launch Demo button
- Highly visible PASS/FAIL buttons
- Scrollable test steps and notes
- Test result tracking and reporting
- Integrated console output view
"""

import os
import sys
import io
import logging
import datetime
import subprocess
import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Add the parent directory to the path so we can import the game modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import necessary modules
from game_sys.config.config_manager import ConfigManager

class TestResult:
    """Represents a test result with pass/fail status and notes."""
    def __init__(self, name, status=None, notes=""):
        self.name = name
        self.status = status  # "PASS", "FAIL", or None
        self.notes = notes
        self.timestamp = datetime.datetime.now()

class TestCategory:
    """Represents a category of tests."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.tests = []

    def add_test(self, name, description, steps):
        """Add a test to this category."""
        self.tests.append({
            "name": name,
            "description": description,
            "steps": steps,
            "result": TestResult(name)
        })
        return len(self.tests) - 1

class ComprehensiveTestManager:
    """Manages the comprehensive test suite for the SimpleGameDemo."""

    def __init__(self):
        """Initialize the test manager."""
        self.config = ConfigManager()
        self.categories = []
        self.current_category = 0
        self.current_test = 0
        self.test_results = []
        self.demo_process = None
        self.current_theme = "light"

        # Set up the test categories and tests
        self.setup_test_cases()

        # Set up the UI
        self.setup_ui()

        # Set up console logging
        self.setup_console_logging()

        # Log initialization message
        self.log_to_console("Test manager initialized", "info")
        self.log_to_console("Select a test category and test to begin", "info")

    def setup_test_cases(self):
        """Set up all test categories and test cases."""

        # 1. Configuration System Tests
        config_category = TestCategory(
            "Configuration System",
            "Tests for the consolidated configuration system"
        )

        config_category.add_test(
            "Config Loading",
            "Verify that the configuration loads correctly",
            [
                "The test will verify that the config can be loaded.",
                "It will check for required sections and key values.",
                "No user action is needed for this test."
            ]
        )

        config_category.add_test(
            "Config Sections",
            "Verify all required config sections exist",
            [
                "The test will check for the following sections:",
                "- toggles",
                "- modules",
                "- leveling",
                "- skills",
                "- spells",
                "- enchantments",
                "- ui",
                "No user action is needed for this test."
            ]
        )

        self.categories.append(config_category)

        # 2. Character & Stats Tests
        character_category = TestCategory(
            "Character & Stats",
            "Tests for character creation and stats management"
        )

        character_category.add_test(
            "Character Creation",
            "Test creating a new character",
            [
                "1. Start the demo by clicking 'Launch Demo'",
                "2. Verify that a new player character is created",
                "3. Check that the character has starting stats (in Stats tab)",
                "4. Check that HP, MP, and Stamina are initialized correctly"
            ]
        )

        character_category.add_test(
            "Stat Display",
            "Test that stats are displayed correctly",
            [
                "1. Go to the Stats tab",
                "2. Verify all core stats are displayed (Str, Dex, Int, etc.)",
                "3. Verify derived stats are calculated and displayed",
                "4. Check that resource bars are visible and accurate"
            ]
        )

        self.categories.append(character_category)

        # 3. Leveling System Tests
        leveling_category = TestCategory(
            "Leveling System",
            "Tests for experience gain, leveling, and stat allocation"
        )

        leveling_category.add_test(
            "Experience Gain",
            "Test gaining experience points",
            [
                "1. Go to the Leveling tab",
                "2. Note your current XP and level",
                "3. Click 'Gain XP' button several times",
                "4. Verify XP increases each time",
                "5. Continue until you level up"
            ]
        )

        leveling_category.add_test(
            "Level Up",
            "Test leveling up and stat point allocation",
            [
                "1. Continue gaining XP until you level up",
                "2. Verify that you received stat points",
                "3. Go to the Leveling tab if not already there",
                "4. Verify available stat points are displayed"
            ]
        )

        leveling_category.add_test(
            "Stat Allocation",
            "Test allocating stat points",
            [
                "1. In the Leveling tab, note your current stats",
                "2. Allocate points to different stats",
                "3. Verify stats increase when points are allocated",
                "4. Verify available points decrease",
                "5. Check derived stats update accordingly"
            ]
        )

        leveling_category.add_test(
            "Stat Reset",
            "Test resetting stat points",
            [
                "1. After allocating some stat points, click 'Reset Stats'",
                "2. Verify stats are reset to base values",
                "3. Verify all spent points are returned to available pool",
                "4. Try allocating points again to confirm functionality"
            ]
        )

        self.categories.append(leveling_category)

        # 4. Inventory & Items Tests
        inventory_category = TestCategory(
            "Inventory & Items",
            "Tests for inventory management and item functionality"
        )

        inventory_category.add_test(
            "Inventory Display",
            "Test inventory UI display",
            [
                "1. Go to the Inventory tab",
                "2. Verify inventory slots are displayed",
                "3. Check for item filtering or sorting options",
                "4. Verify item tooltips/details work when hovering"
            ]
        )

        inventory_category.add_test(
            "Item Creation",
            "Test creating new items",
            [
                "1. In the Inventory tab, find the 'Create Item' or similar button",
                "2. Create different types of items (weapon, armor, consumable)",
                "3. Verify items appear in inventory",
                "4. Check item properties and attributes"
            ]
        )

        inventory_category.add_test(
            "Item Equipping",
            "Test equipping and unequipping items",
            [
                "1. Create a weapon or armor item if none exists",
                "2. Click to equip the item",
                "3. Verify item is shown as equipped",
                "4. Check that stats are updated based on item bonuses",
                "5. Unequip the item and verify stats return to normal"
            ]
        )

        inventory_category.add_test(
            "Item Use",
            "Test using consumable items",
            [
                "1. Create a consumable item (potion, food, etc.)",
                "2. Reduce a resource (take damage to lower HP)",
                "3. Use the consumable item",
                "4. Verify the item effect works (HP restored, etc.)",
                "5. Check that item is consumed/removed from inventory"
            ]
        )

        self.categories.append(inventory_category)

        # 5. Combat System Tests
        combat_category = TestCategory(
            "Combat System",
            "Tests for combat mechanics and battle system"
        )

        combat_category.add_test(
            "Combat Initiation",
            "Test starting combat with an enemy",
            [
                "1. Go to the Combat tab",
                "2. Click 'Find Enemy' or similar button",
                "3. Verify an enemy is generated",
                "4. Check that enemy stats are displayed"
            ]
        )

        combat_category.add_test(
            "Attack Mechanics",
            "Test basic attack mechanics",
            [
                "1. In combat with an enemy, click 'Attack' button",
                "2. Verify damage is calculated and applied",
                "3. Check that the enemy's health decreases",
                "4. Verify that the enemy counter-attacks",
                "5. Check that player resources (stamina/mana) are consumed appropriately"
            ]
        )

        combat_category.add_test(
            "Special Attacks",
            "Test special attacks or combat skills",
            [
                "1. In combat, look for special attack options",
                "2. Use any available special attacks or skills",
                "3. Verify they consume the correct resources",
                "4. Check that they deal appropriate damage",
                "5. Verify any special effects are applied"
            ]
        )

        combat_category.add_test(
            "Combat Resolution",
            "Test combat ending conditions",
            [
                "1. Defeat an enemy in combat",
                "2. Verify you gain XP and possibly loot",
                "3. Check that you can start a new combat",
                "4. (Optional) Test losing combat if possible"
            ]
        )

        self.categories.append(combat_category)

        # 6. Weapon Mastery & Combat Specialization Tests
        weapon_mastery_category = TestCategory(
            "Weapon Mastery & Combat Specialization",
            "Tests for weapon types, dual-wielding, and combat specializations"
        )

        weapon_mastery_category.add_test(
            "Single Weapon Combat",
            "Test combat with single-handed weapons",
            [
                "1. Equip a single one-handed weapon (sword, axe, etc.)",
                "2. Engage in combat with an enemy",
                "3. Verify attack speed and damage are appropriate",
                "4. Check that weapon stats affect combat performance",
                "5. Test blocking if a shield is equipped in offhand"
            ]
        )

        weapon_mastery_category.add_test(
            "Two-Handed Weapon Combat",
            "Test combat with two-handed weapons",
            [
                "1. Equip a two-handed weapon (great sword, staff, etc.)",
                "2. Verify that offhand slot is blocked/unavailable",
                "3. Engage in combat and test attack patterns",
                "4. Check that two-handed weapons deal more damage",
                "5. Verify attack speed differences from one-handed weapons"
            ]
        )

        weapon_mastery_category.add_test(
            "Dual-Wield Combat",
            "Test dual-wielding two weapons",
            [
                "1. Equip weapons in both main hand and offhand",
                "2. Verify dual-wield is enabled in configuration",
                "3. Engage in combat and test attack patterns",
                "4. Check for alternating attacks or special dual-wield moves",
                "5. Verify damage calculation includes both weapons"
            ]
        )

        weapon_mastery_category.add_test(
            "Blocking and Defense",
            "Test defensive combat mechanics",
            [
                "1. Equip a shield or defensive weapon",
                "2. Engage in combat and try blocking attacks",
                "3. Verify block chance and damage reduction work",
                "4. Test timing-based blocking if available",
                "5. Check that blocking consumes stamina appropriately"
            ]
        )

        weapon_mastery_category.add_test(
            "Critical Hits",
            "Test critical hit mechanics",
            [
                "1. Engage in extended combat to trigger critical hits",
                "2. Verify critical hits deal extra damage",
                "3. Check that critical chance is influenced by stats",
                "4. Look for visual/audio feedback on critical hits",
                "5. Test that critical multiplier is applied correctly"
            ]
        )

        self.categories.append(weapon_mastery_category)

        # 8. Magic & Spells System Tests
        magic_category = TestCategory(
            "Magic & Spells",
            "Tests for spell casting and magic system"
        )

        magic_category.add_test(
            "Spell Learning",
            "Test learning new spells",
            [
                "1. Go to the Progression tab",
                "2. Find the 'Learn Spell' or similar button",
                "3. Learn a basic spell like 'Fireball'",
                "4. Verify the spell appears in your known spells list",
                "5. Check that you meet the stat requirements"
            ]
        )

        magic_category.add_test(
            "Spell Casting - Fireball",
            "Test casting fireball spell",
            [
                "1. Go to the Combat tab",
                "2. Spawn an enemy if needed",
                "3. Click 'Cast Fireball' button",
                "4. Verify mana is consumed (should cost ~10-20 mana)",
                "5. Check that the enemy takes fire damage",
                "6. Verify spell has appropriate range and effects"
            ]
        )

        magic_category.add_test(
            "Spell Casting - Ice Shard",
            "Test casting ice shard spell",
            [
                "1. Learn the Ice Shard spell if not already known",
                "2. In combat, cast Ice Shard on an enemy",
                "3. Verify mana consumption",
                "4. Check that ice damage is dealt",
                "5. Verify any slowing effects are applied"
            ]
        )

        magic_category.add_test(
            "Healing Spells",
            "Test healing magic",
            [
                "1. Learn Healing Touch spell if available",
                "2. Take some damage (attack enemy, let it hit you)",
                "3. Cast healing spell on yourself",
                "4. Verify health is restored",
                "5. Check mana consumption is appropriate"
            ]
        )

        magic_category.add_test(
            "Mana Management",
            "Test mana consumption and regeneration",
            [
                "1. Cast several spells to use up mana",
                "2. Verify mana decreases with each cast",
                "3. Check that you cannot cast when out of mana",
                "4. Use 'Restore Mana' to refill mana pool",
                "5. Verify mana regeneration over time if implemented"
            ]
        )

        self.categories.append(magic_category)

        # 9. Enchanting System Tests
        enchanting_category = TestCategory(
            "Enchanting System",
            "Tests for item enchanting and enhancement"
        )

        enchanting_category.add_test(
            "Learning Enchantments",
            "Test learning new enchantments",
            [
                "1. Go to the Enchanting tab",
                "2. Find available enchantments to learn",
                "3. Learn a basic enchantment (e.g., Fire Enchant)",
                "4. Verify it appears in your known enchantments",
                "5. Check stat requirements are met"
            ]
        )

        enchanting_category.add_test(
            "Applying Enchantments",
            "Test applying enchantments to items",
            [
                "1. Have a weapon or armor item in inventory",
                "2. Go to the Enchanting tab",
                "3. Select an item and an enchantment",
                "4. Apply the enchantment to the item",
                "5. Verify the item properties are enhanced",
                "6. Check that the item shows the enchantment effect"
            ]
        )

        enchanting_category.add_test(
            "Enchantment Effects",
            "Test that enchantments actually work in combat",
            [
                "1. Enchant a weapon with fire damage",
                "2. Equip the enchanted weapon",
                "3. Attack an enemy in combat",
                "4. Verify additional fire damage is dealt",
                "5. Check for any burn or damage-over-time effects"
            ]
        )

        self.categories.append(enchanting_category)

        # 10. Skills System Tests
        skills_category = TestCategory(
            "Skills System",
            "Tests for skill learning and usage"
        )

        skills_category.add_test(
            "Skill Learning",
            "Test learning new skills",
            [
                "1. Go to the Progression tab",
                "2. Find available skills to learn",
                "3. Learn a combat skill (e.g., Power Strike)",
                "4. Verify it appears in your known skills",
                "5. Check level and stat requirements"
            ]
        )

        skills_category.add_test(
            "Skill Usage",
            "Test using learned skills",
            [
                "1. Learn a combat skill if not already known",
                "2. Go to combat and engage an enemy",
                "3. Use the skill in combat",
                "4. Verify skill effects (damage, stamina cost, etc.)",
                "5. Check cooldown mechanics if applicable"
            ]
        )

        skills_category.add_test(
            "Passive Skills",
            "Test passive skill effects",
            [
                "1. Learn a passive skill (e.g., Sword Mastery)",
                "2. Equip appropriate equipment (sword for sword mastery)",
                "3. Check that passive bonuses are applied",
                "4. Verify stats are improved when conditions are met"
            ]
        )

        self.categories.append(skills_category)

        # 11. Resource Management Tests
        resource_category = TestCategory(
            "Resource Management",
            "Tests for health, mana, and stamina systems"
        )

        resource_category.add_test(
            "Health System",
            "Test health damage and restoration",
            [
                "1. Note your current/max health",
                "2. Take damage by fighting an enemy",
                "3. Use 'Restore Health' button",
                "4. Verify health is restored to maximum",
                "5. Test that health cannot exceed maximum"
            ]
        )

        resource_category.add_test(
            "Stamina System",
            "Test stamina consumption and restoration",
            [
                "1. Check your current stamina",
                "2. Use skills or abilities that consume stamina",
                "3. Verify stamina decreases appropriately",
                "4. Use 'Restore Stamina' button",
                "5. Check stamina regeneration over time"
            ]
        )

        resource_category.add_test(
            "Resource Interactions",
            "Test interactions between different resources",
            [
                "1. Use 'Restore All' button",
                "2. Verify all resources (health, mana, stamina) are restored",
                "3. Test resource consumption in different scenarios",
                "4. Check that low resources prevent certain actions"
            ]
        )

        self.categories.append(resource_category)

        # 12. Item Quality & Rarity Tests
        quality_category = TestCategory(
            "Item Quality & Rarity",
            "Tests for item grading and rarity systems"
        )

        quality_category.add_test(
            "Item Creation",
            "Test creating items with different qualities",
            [
                "1. Go to the Inventory tab",
                "2. Use 'Create Item' to make different items",
                "3. Create multiple copies of the same item type",
                "4. Check for different qualities (normal, superior, etc.)",
                "5. Verify quality affects item stats"
            ]
        )

        quality_category.add_test(
            "Rarity System",
            "Test item rarity levels",
            [
                "1. Use 'Add Random Item' multiple times",
                "2. Check for different rarity levels (common, rare, epic, etc.)",
                "3. Verify rare items have better stats",
                "4. Check color coding or visual indicators for rarity"
            ]
        )

        quality_category.add_test(
            "Item Comparison",
            "Test comparing items of different qualities",
            [
                "1. Create or find items of the same type but different qualities",
                "2. Compare their stats and bonuses",
                "3. Equip different quality items",
                "4. Verify that higher quality items provide better bonuses",
                "5. Check tooltip information shows quality differences"
            ]
        )

        self.categories.append(quality_category)

        # 13. Status Effects System Tests
        status_effects_category = TestCategory(
            "Status Effects System",
            "Tests for buffs, debuffs, and temporary effects"
        )

        status_effects_category.add_test(
            "Status Effect Application",
            "Test applying status effects to characters",
            [
                "1. Go to the Combat tab",
                "2. Spawn an enemy if needed",
                "3. Cast a spell that applies effects (like Ice Shard for slow)",
                "4. Verify the status effect is applied to the target",
                "5. Check that effect icons or indicators appear",
                "6. Verify the effect actually modifies behavior (reduced speed, etc.)"
            ]
        )

        status_effects_category.add_test(
            "Status Effect Ticking",
            "Test status effect duration and periodic effects",
            [
                "1. Apply a damage-over-time effect (like burn from fireball)",
                "2. Click 'Tick Status' button repeatedly",
                "3. Verify damage is applied each tick",
                "4. Check that effect duration decreases",
                "5. Verify effect is removed when duration expires"
            ]
        )

        status_effects_category.add_test(
            "Multiple Effects",
            "Test having multiple status effects active",
            [
                "1. Apply multiple different effects to the same target",
                "2. Verify all effects are active simultaneously",
                "3. Check that effects stack appropriately",
                "4. Test that different effects have different durations",
                "5. Verify effects are removed independently"
            ]
        )

        status_effects_category.add_test(
            "Buff vs Debuff",
            "Test positive and negative status effects",
            [
                "1. Apply beneficial effects (healing over time, stat boosts)",
                "2. Apply harmful effects (poison, stat reductions)",
                "3. Verify beneficial effects help the character",
                "4. Verify harmful effects hinder the character",
                "5. Check visual distinctions between buff/debuff types"
            ]
        )

        self.categories.append(status_effects_category)

        # 14. Visual Effects & Graphics Tests
        visual_effects_category = TestCategory(
            "Visual Effects & Graphics",
            "Tests for particle effects, animations, and visual feedback"
        )

        visual_effects_category.add_test(
            "Combat Particle Effects",
            "Test particle effects during combat",
            [
                "1. Go to the Combat tab and engage in combat",
                "2. Use the Attack button to attack an enemy",
                "3. Look for particle effects when damage is dealt",
                "4. Cast spells (Fireball, Ice Shard) and watch for particles",
                "5. Verify different spells have different colored effects"
            ]
        )

        visual_effects_category.add_test(
            "Healing Visual Effects",
            "Test visual feedback for healing",
            [
                "1. Take damage by fighting an enemy",
                "2. Use the Heal button in combat",
                "3. Look for green particle effects during healing",
                "4. Use 'Restore Health' button and check for effects",
                "5. Verify healing effects are visually distinct from damage"
            ]
        )

        visual_effects_category.add_test(
            "Game State Visualization",
            "Test the combat canvas and game state display",
            [
                "1. Go to the Combat tab",
                "2. Verify character and enemy are drawn on the canvas",
                "3. Check that health bars or status indicators are visible",
                "4. Spawn different enemies and verify they appear",
                "5. Look for visual updates when actions are performed"
            ]
        )

        visual_effects_category.add_test(
            "Animation Timing",
            "Test timing and duration of visual effects",
            [
                "1. Perform various actions that trigger effects",
                "2. Observe that particle effects have appropriate duration",
                "3. Verify effects don't overlap inappropriately",
                "4. Check that effects complete before new ones start",
                "5. Test rapid action clicking for effect handling"
            ]
        )

        self.categories.append(visual_effects_category)

        # 15. User Interface & Experience Tests
        ui_experience_category = TestCategory(
            "User Interface & Experience",
            "Tests for UI responsiveness, layout, and user experience"
        )

        ui_experience_category.add_test(
            "Tab Navigation",
            "Test switching between different tabs",
            [
                "1. Click on each tab (Stats, Combat, Inventory, etc.)",
                "2. Verify each tab loads and displays content correctly",
                "3. Check that tab switching updates relevant displays",
                "4. Verify no errors occur when switching tabs rapidly",
                "5. Test that tab content is preserved when switching back"
            ]
        )

        ui_experience_category.add_test(
            "Button Responsiveness",
            "Test that all buttons work correctly",
            [
                "1. Test all buttons in each tab",
                "2. Verify buttons provide immediate visual feedback",
                "3. Check that buttons are disabled when appropriate",
                "4. Test button tooltips if available",
                "5. Verify buttons don't cause crashes or errors"
            ]
        )

        ui_experience_category.add_test(
            "Information Display",
            "Test that information is clearly displayed",
            [
                "1. Check that character stats are readable and accurate",
                "2. Verify resource bars (health, mana, stamina) are clear",
                "3. Check that item tooltips show complete information",
                "4. Verify combat log shows meaningful messages",
                "5. Test that all text is legible and properly formatted"
            ]
        )

        ui_experience_category.add_test(
            "Layout and Sizing",
            "Test UI layout and window behavior",
            [
                "1. Try resizing the main window",
                "2. Verify content scales appropriately",
                "3. Check that scrollbars appear when needed",
                "4. Test that all UI elements remain accessible",
                "5. Verify layout doesn't break with different window sizes"
            ]
        )

        ui_experience_category.add_test(
            "Error Handling",
            "Test error messages and edge cases",
            [
                "1. Try to perform invalid actions (e.g., cast spells without mana)",
                "2. Verify appropriate error messages are shown",
                "3. Check that the application doesn't crash on errors",
                "4. Test recovery from error states",
                "5. Verify error messages are helpful and clear"
            ]
        )

        self.categories.append(ui_experience_category)

        # 16. Performance & Stability Tests
        performance_category = TestCategory(
            "Performance & Stability",
            "Tests for application performance and stability"
        )

        performance_category.add_test(
            "Rapid Action Testing",
            "Test application stability with rapid user actions",
            [
                "1. Rapidly click various buttons in sequence",
                "2. Quickly switch between tabs multiple times",
                "3. Perform many actions in rapid succession",
                "4. Verify the application remains responsive",
                "5. Check that no errors or crashes occur"
            ]
        )

        performance_category.add_test(
            "Resource Usage",
            "Test memory and CPU usage over time",
            [
                "1. Leave the application running for an extended period",
                "2. Perform various actions repeatedly",
                "3. Monitor for memory leaks or excessive resource usage",
                "4. Check that the application doesn't slow down over time",
                "5. Verify particle effects are cleaned up properly"
            ]
        )

        performance_category.add_test(
            "Long Session Testing",
            "Test application behavior during extended use",
            [
                "1. Use the application for an extended session (30+ minutes)",
                "2. Perform a variety of different actions",
                "3. Level up multiple times and use many features",
                "4. Check that the application remains stable",
                "5. Verify no performance degradation occurs"
            ]
        )

        self.categories.append(performance_category)

        # 17. Logging & Debug Systems Tests
        logging_debug_category = TestCategory(
            "Logging & Debug Systems",
            "Tests for game logging, debug output, and development features"
        )

        logging_debug_category.add_test(
            "Combat Logging",
            "Test that combat actions are properly logged",
            [
                "1. Engage in combat and perform various actions",
                "2. Check the log area at the bottom of the demo window",
                "3. Verify attack messages appear with damage values",
                "4. Check that spell casting is logged with effects",
                "5. Verify error messages appear for invalid actions"
            ]
        )

        logging_debug_category.add_test(
            "Resource Change Logging",
            "Test logging of resource changes (health, mana, etc.)",
            [
                "1. Use 'Restore Health', 'Restore Mana', 'Restore Stamina'",
                "2. Check that resource changes are logged",
                "3. Verify healing spells log their effects",
                "4. Check that level-up events are logged",
                "5. Test that resource depletion is logged"
            ]
        )

        logging_debug_category.add_test(
            "Item and Inventory Logging",
            "Test logging of inventory and item actions",
            [
                "1. Create, equip, and use items",
                "2. Check that item creation is logged",
                "3. Verify equipment changes are logged",
                "4. Check that item usage is logged",
                "5. Test that enchantment application is logged"
            ]
        )

        logging_debug_category.add_test(
            "Debug Information Display",
            "Test debug settings and information display",
            [
                "1. Check if debug mode can be enabled",
                "2. Look for debug information in the UI",
                "3. Verify that debug toggles work if available",
                "4. Check for developer options or cheat codes",
                "5. Test that debug info doesn't interfere with normal play"
            ]
        )

        self.categories.append(logging_debug_category)

        # 18. Advanced Systems Integration Tests
        integration_category = TestCategory(
            "Advanced Integration",
            "Tests for complex system interactions"
        )

        integration_category.add_test(
            "Full Character Build",
            "Test creating a complete character build",
            [
                "1. Level up your character several times",
                "2. Allocate stat points strategically",
                "3. Learn complementary skills and spells",
                "4. Equip appropriate gear",
                "5. Apply enchantments to your equipment",
                "6. Test the complete build in combat"
            ]
        )

        integration_category.add_test(
            "Configuration Integration",
            "Test that all systems use the config system",
            [
                "1. Check that item rarities come from config",
                "2. Verify spell data is loaded from config",
                "3. Test that stat calculations use config values",
                "4. Confirm UI colors and settings are from config"
            ]
        )

        integration_category.add_test(
            "Save/Load State",
            "Test game state persistence",
            [
                "1. Make significant changes to your character",
                "2. Equip items, learn skills, allocate stats",
                "3. Test if any save/load functionality exists",
                "4. Verify character state persists between sessions",
                "5. Check that all progress is maintained"
            ]
        )

        self.categories.append(integration_category)

        # Add more test categories here...
        # (For brevity, I'll skip the remaining categories since they follow the same pattern)

    def setup_ui(self):
        """Set up the test manager UI."""
        # Create main window
        self.root = tk.Tk()
        self.root.title("Comprehensive Test Manager")
        self.root.geometry("900x750")

        # Configure window resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=3)
        self.main_frame.rowconfigure(2, weight=1)

        # Create header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=10)

        ttk.Label(header_frame, text="SimpleGameDemo Comprehensive Test",
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(header_frame,
                 text="Test all features of the demo with consolidated configuration").pack()

        # Create content frame with split view
        content_frame = ttk.Frame(self.main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Left panel - Test categories
        left_panel = ttk.LabelFrame(content_frame, text="Test Categories")
        left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 5), pady=5)

        # Add scrollbar to category listbox
        category_frame = ttk.Frame(left_panel)
        category_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        category_scrollbar = ttk.Scrollbar(category_frame)
        category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.category_listbox = tk.Listbox(
            category_frame, width=30, height=20,
            yscrollcommand=category_scrollbar.set
        )
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        category_scrollbar.config(command=self.category_listbox.yview)

        for category in self.categories:
            self.category_listbox.insert(tk.END, category.name)
        self.category_listbox.bind('<<ListboxSelect>>',
                                  self.on_category_select)

        # Right panel - Test details
        self.right_panel = ttk.LabelFrame(content_frame, text="Test Details")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        # Test info frame
        test_info_frame = ttk.Frame(self.right_panel)
        test_info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(test_info_frame, text="Test Category:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.category_label = ttk.Label(test_info_frame, text="", font=("Arial", 10, "bold"))
        self.category_label.grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(test_info_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.category_desc_label = ttk.Label(test_info_frame, text="", wraplength=500)
        self.category_desc_label.grid(row=1, column=1, sticky=tk.W, pady=2)

        # Tests in category frame
        tests_frame = ttk.LabelFrame(self.right_panel, text="Tests in Category")
        tests_frame.pack(fill=tk.X, padx=10, pady=5)

        # Add scrollbar to tests listbox
        tests_list_frame = ttk.Frame(tests_frame)
        tests_list_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)

        tests_scrollbar = ttk.Scrollbar(tests_list_frame)
        tests_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tests_listbox = tk.Listbox(tests_list_frame, height=8,
                                       yscrollcommand=tests_scrollbar.set)
        self.tests_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tests_scrollbar.config(command=self.tests_listbox.yview)
        self.tests_listbox.bind('<<ListboxSelect>>', self.on_test_select)

        # Current test frame
        current_test_frame = ttk.LabelFrame(self.right_panel, text="Current Test")
        current_test_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Label(current_test_frame, text="Test Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.test_name_label = ttk.Label(current_test_frame, text="", font=("Arial", 10, "bold"))
        self.test_name_label.grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(current_test_frame, text="Description:").grid(row=1, column=0, sticky=tk.NW, pady=2)
        self.test_desc_label = ttk.Label(current_test_frame, text="", wraplength=500)
        self.test_desc_label.grid(row=1, column=1, sticky=tk.W, pady=2)

        # Create a notebook with tabs for test details, notes, and console
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, sticky="nsew", pady=5, padx=10)

        # Tab 1: Test Steps
        steps_tab = ttk.Frame(self.notebook)
        self.notebook.add(steps_tab, text="Test Steps")
        self.setup_steps_tab(steps_tab)

        # Tab 2: Notes
        notes_tab = ttk.Frame(self.notebook)
        self.notebook.add(notes_tab, text="Test Notes")
        self.setup_notes_tab(notes_tab)

        # Tab 3: Console Output
        console_tab = ttk.Frame(self.notebook)
        self.notebook.add(console_tab, text="Console Output")
        self.setup_console_tab(console_tab)

        # Bottom frame - Results
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.grid(row=3, column=0, sticky="ew", pady=10)
        bottom_frame.columnconfigure(1, weight=1)

        ttk.Button(bottom_frame, text="Save Results",
                  command=self.save_results).grid(row=0, column=0, padx=5)

        # Theme toggle button in the center
        self.theme_button = tk.Button(
            bottom_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            width=15,
            bg="#555555",
            fg="#FFFFFF",
            relief=tk.RAISED,
            bd=2,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        self.theme_button.grid(row=0, column=1, padx=5)

        ttk.Button(bottom_frame, text="Exit",
                  command=self.root.destroy).grid(row=0, column=2, padx=5)

        # Auto-run config tests
        self.root.after(1000, self.run_config_tests)

        # Select first category
        if self.categories:
            self.category_listbox.selection_set(0)
            self.on_category_select(None)

        # Apply initial theme
        self.apply_theme("light")

    def setup_steps_tab(self, parent):
        """Set up the test steps tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # Add the steps display to this tab
        steps_display_frame = ttk.LabelFrame(parent, text="Test Instructions")
        steps_display_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create a scrollable frame for steps
        steps_container = ttk.Frame(steps_display_frame)
        steps_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas for scrolling
        self.steps_canvas = tk.Canvas(steps_container, width=500, height=150,
                                      highlightthickness=0, borderwidth=1, relief="sunken")
        steps_scrollbar = ttk.Scrollbar(steps_container, orient="vertical",
                                       command=self.steps_canvas.yview)

        # Frame inside canvas that will hold the steps
        self.steps_frame = ttk.Frame(self.steps_canvas)

        # Configure scrolling
        self.steps_canvas.configure(yscrollcommand=steps_scrollbar.set)
        self.steps_canvas.pack(side="left", fill="both", expand=True)
        steps_scrollbar.pack(side="right", fill="y")

        # Add keyboard bindings for scrolling
        self.steps_canvas.bind("<Up>", lambda e: self.steps_canvas.yview_scroll(-1, "units"))
        self.steps_canvas.bind("<Down>", lambda e: self.steps_canvas.yview_scroll(1, "units"))
        self.steps_canvas.bind("<MouseWheel>", lambda e: self.steps_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Create window inside canvas for the steps frame
        self.steps_window = self.steps_canvas.create_window((0, 0), window=self.steps_frame,
                                                    anchor="nw")

        # Update scroll region when steps frame changes size
        def _configure_steps_scroll(event):
            self.steps_canvas.configure(scrollregion=self.steps_canvas.bbox("all"))
            self.steps_canvas.itemconfig(self.steps_window, width=self.steps_canvas.winfo_width())

        self.steps_frame.bind("<Configure>", _configure_steps_scroll)
        self.steps_canvas.bind("<Configure>", lambda e: self.steps_canvas.itemconfig(
            self.steps_window, width=self.steps_canvas.winfo_width()))

    def setup_notes_tab(self, parent):
        """Set up the notes tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # Create a scrollable notes text area
        notes_frame = ttk.LabelFrame(parent, text="Test Observations")
        notes_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)

        # Create text widget with scrollbar
        notes_container = ttk.Frame(notes_frame)
        notes_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        notes_container.columnconfigure(0, weight=1)
        notes_container.rowconfigure(0, weight=1)

        notes_scroll = ttk.Scrollbar(notes_container)
        notes_scroll.grid(row=0, column=1, sticky="ns")

        self.result_notes_text = tk.Text(
            notes_container,
            height=10,
            width=70,
            font=("Arial", 10),
            wrap=tk.WORD,
            yscrollcommand=notes_scroll.set
        )
        self.result_notes_text.grid(row=0, column=0, sticky="nsew")
        notes_scroll.config(command=self.result_notes_text.yview)

        # Add instructions
        ttk.Label(
            parent,
            text="After completing the test steps, use the buttons below to record the result:",
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky="ew", pady=(15, 10))

        # Pass/Fail/Demo buttons container
        self.pass_fail_frame = tk.Frame(parent, bd=2, relief=tk.GROOVE, bg="#F0F0F0")
        self.pass_fail_frame.grid(row=2, column=0, sticky="ew", pady=(5, 15), padx=20)
        self.pass_fail_frame.columnconfigure(0, weight=1)
        self.pass_fail_frame.columnconfigure(1, weight=1)
        self.pass_fail_frame.columnconfigure(2, weight=1)

        # PASS button
        self.pass_btn = tk.Button(
            self.pass_fail_frame,
            text="✓ PASS",
            command=lambda: self.record_result("PASS"),
            bg="#00CC00",
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.RAISED,
            bd=2,
            width=12,
            height=1
        )
        self.pass_btn.grid(row=0, column=0, sticky="e", padx=5, pady=10)

        # FAIL button
        self.fail_btn = tk.Button(
            self.pass_fail_frame,
            text="✗ FAIL",
            command=lambda: self.record_result("FAIL"),
            bg="#FF0000",
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.RAISED,
            bd=2,
            width=12,
            height=1
        )
        self.fail_btn.grid(row=0, column=1, padx=5, pady=10)

        # Launch Demo button
        self.launch_demo_btn = tk.Button(
            self.pass_fail_frame,
            text="▶ Demo",
            command=self.launch_demo,
            bg="#4B89DC",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.RAISED,
            bd=2,
            width=12,
            height=1,
            cursor="hand2"
        )
        self.launch_demo_btn.grid(row=0, column=2, sticky="w", padx=5, pady=10)

    def setup_console_tab(self, parent):
        """Set up the console output tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # Create console output area
        console_frame = ttk.LabelFrame(parent, text="Console Output")
        console_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)

        # Console text widget with scrollbar
        console_container = ttk.Frame(console_frame)
        console_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        console_container.columnconfigure(0, weight=1)
        console_container.rowconfigure(0, weight=1)

        console_scroll = ttk.Scrollbar(console_container)
        console_scroll.grid(row=0, column=1, sticky="ns")

        # Create a text widget for console output
        self.console_text = tk.Text(
            console_container,
            height=15,
            width=80,
            font=("Consolas", 9),
            wrap=tk.WORD,
            yscrollcommand=console_scroll.set,
            background="#f0f0f0",
            foreground="#000000"
        )
        self.console_text.grid(row=0, column=0, sticky="nsew")
        console_scroll.config(command=self.console_text.yview)

        # Create tags for different message types
        self.console_text.tag_configure("info", foreground="#000000")
        self.console_text.tag_configure("success", foreground="#008800")
        self.console_text.tag_configure("warning", foreground="#AA6600")
        self.console_text.tag_configure("error", foreground="#CC0000")
        self.console_text.tag_configure("debug", foreground="#666666")

        # Add a clear console button
        clear_console_btn = ttk.Button(
            console_frame,
            text="Clear Console",
            command=self.clear_console
        )
        clear_console_btn.grid(row=1, column=0, sticky="e", padx=5, pady=5)

    def setup_console_logging(self):
        """Set up console logging to redirect Python logging to the console widget."""
        # Create a custom logging handler that redirects to our console widget
        class ConsoleHandler(logging.Handler):
            def __init__(self, console_widget, log_func):
                super().__init__()
                self.console_widget = console_widget
                self.log_func = log_func

            def emit(self, record):
                try:
                    msg = self.format(record)
                    level = record.levelname.lower()
                    if level == 'critical':
                        level = 'error'  # Map critical to error for display
                    self.log_func(msg, level)
                except Exception:
                    self.handleError(record)

        # Set up the handler
        self.console_handler = ConsoleHandler(self.console_text, self.log_to_console)
        self.console_handler.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                     datefmt='%H:%M:%S')
        self.console_handler.setFormatter(formatter)

        # Add the handler to the root logger
        logging.getLogger().addHandler(self.console_handler)

        # Also redirect stdout and stderr to the console
        class StdoutRedirector:
            def __init__(self, log_func):
                self.log_func = log_func
                self.buffer = ""

            def write(self, string):
                self.buffer += string
                if string.endswith('\n'):
                    self.log_func(self.buffer.strip(), "info")
                    self.buffer = ""

            def flush(self):
                if self.buffer:
                    self.log_func(self.buffer, "info")
                    self.buffer = ""

        class StderrRedirector:
            def __init__(self, log_func):
                self.log_func = log_func
                self.buffer = ""

            def write(self, string):
                self.buffer += string
                if string.endswith('\n'):
                    self.log_func(self.buffer.strip(), "error")
                    self.buffer = ""

            def flush(self):
                if self.buffer:
                    self.log_func(self.buffer, "error")
                    self.buffer = ""

        # Save original stdout and stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        # Redirect stdout and stderr
        sys.stdout = StdoutRedirector(self.log_to_console)
        sys.stderr = StderrRedirector(self.log_to_console)

        # Log a message confirming redirection is set up
        logging.info("Console logging redirection set up")

    def log_to_console(self, message, level="info"):
        """Log a message to the console with appropriate formatting.

        Args:
            message: The message to log
            level: The level of the message (info, success, warning, error, debug)
        """
        if not hasattr(self, 'console_text'):
            return  # Console not initialized yet

        # Get current time for timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Format the message
        formatted_message = f"[{timestamp}] {message}\n"

        # Ensure we're on the main thread
        self.console_text.after(0, lambda: self._append_to_console(formatted_message, level))

    def _append_to_console(self, message, level):
        """Actually append text to the console (called on main thread)."""
        # Insert the message at the end
        self.console_text.insert(tk.END, message, level)

        # Scroll to the end
        self.console_text.see(tk.END)

        # Update the widget immediately
        self.console_text.update_idletasks()

    def clear_console(self):
        """Clear the console text."""
        self.console_text.delete("1.0", tk.END)
        self.log_to_console("Console cleared", "info")

    def launch_demo(self):
        """Launch the game demo."""
        try:
            # Check if a demo is already running
            if self.demo_process and self.demo_process.poll() is None:
                messagebox.showinfo("Demo Running", "The demo is already running.")
                self.log_to_console("Demo is already running", "warning")
                return

            self.log_to_console("Launching demo...", "info")

            # Get the path to the demo script
            demo_script = Path(parent_dir) / "demo.py"

            if not demo_script.exists():
                error_msg = f"Demo script not found: {demo_script}"
                messagebox.showerror("Error", error_msg)
                self.log_to_console(error_msg, "error")
                return

            # Clear any previous console output
            self.clear_console()

            # Switch to the console tab
            self.notebook.select(2)  # 0-based index, console is the third tab

            # Launch the demo process
            python_exe = sys.executable
            cmd = [python_exe, str(demo_script)]

            self.log_to_console(f"Running command: {' '.join(cmd)}", "info")

            # Create the process with pipes for stdout and stderr
            self.demo_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )

            # Set up threads to read output
            def read_output(pipe, level):
                for line in iter(pipe.readline, ''):
                    self.log_to_console(line.strip(), level)
                pipe.close()

            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=read_output,
                args=(self.demo_process.stdout, "info"),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=read_output,
                args=(self.demo_process.stderr, "error"),
                daemon=True
            )

            stdout_thread.start()
            stderr_thread.start()

            # Set up a background task to check if the process has ended
            def check_process():
                if self.demo_process and self.demo_process.poll() is not None:
                    returncode = self.demo_process.poll()
                    if returncode == 0:
                        self.log_to_console("Demo process completed successfully", "success")
                    else:
                        self.log_to_console(f"Demo process ended with return code {returncode}", "error")
                    return

                # Process still running, check again in 1 second
                self.root.after(1000, check_process)

            # Start checking the process
            self.root.after(1000, check_process)

            self.log_to_console("Demo launched successfully", "success")

        except Exception as e:
            error_msg = f"Failed to launch demo: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.log_to_console(error_msg, "error")
            traceback.print_exc()
            self.log_to_console(traceback.format_exc(), "error")

    def restore_stdout_stderr(self):
        """Restore the original stdout and stderr."""
        if hasattr(self, 'original_stdout') and hasattr(self, 'original_stderr'):
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

    def apply_theme(self, theme):
        """Apply a theme to the UI."""
        # Define color schemes for light and dark modes
        light_colors = {
            "bg": "#FFFFFF",
            "fg": "#000000",
            "highlight": "#FF00EE",
            "button_bg": "#FFFFFF",
            "button_fg": "#000000",
            "pass_bg": "#00CC00",
            "pass_fg": "#FFFFFF",
            "fail_bg": "#FF0000",
            "fail_fg": "#FFFFFF",
            "demo_bg": "#4B89DC",
            "demo_fg": "#000000",
            "frame_bg": "#F5F5F5",
            "header_fg": "#000066",
            "accent": "#E0E0E0",
            "console_bg": "#F0F0F0",
            "console_fg": "#000000",
            "console_info": "#000000",
            "console_success": "#008800",
            "console_warning": "#AA6600",
            "console_error": "#CC0000",
            "console_debug": "#666666"
        }

        dark_colors = {
            "bg": "#2D2D30",
            "fg": "#FFFFFF",
            "highlight": "#FFFFFF",
            "button_bg": "#3E3E42",
            "button_fg": "#000000",
            "pass_bg": "#008800",
            "pass_fg": "#FFFFFF",
            "fail_bg": "#CC0000",
            "fail_fg": "#FFFFFF",
            "demo_bg": "#007ACC",
            "demo_fg": "#000000",
            "frame_bg": "#252526",
            "header_fg": "#CCCCFF",
            "accent": "#3E3E42",
            "console_bg": "#1E1E1E",
            "console_fg": "#CCCCCC",
            "console_info": "#CCCCCC",
            "console_success": "#6A9955",
            "console_warning": "#CE9178",
            "console_error": "#F14C4C",
            "console_debug": "#909090"
        }

        colors = light_colors if theme == "light" else dark_colors

        # Store the current theme
        self.current_theme = theme

        # Update theme button text
        if theme == "light":
            self.theme_button.config(text="🌙 Dark Mode", bg="#555555", fg="#FFFFFF")
        else:
            self.theme_button.config(text="☀️ Light Mode", bg="#007ACC", fg="#FFFFFF")

        # Apply colors to the main window and frames
        self.root.config(bg=colors["bg"])

        # Apply theme to notebook and its tabs
        style = ttk.Style()
        style.configure("TNotebook", background=colors["bg"])
        style.configure("TNotebook.Tab", background=colors["button_bg"], foreground=colors["button_fg"])
        style.map("TNotebook.Tab", background=[("selected", colors["highlight"])],
                 foreground=[("selected", colors["demo_fg"])])

        # Configure styles for different widgets
        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("TButton", background=colors["button_bg"], foreground=colors["button_fg"])
        style.configure("TLabelframe", background=colors["bg"], foreground=colors["fg"])
        style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["header_fg"])

        # Update the console colors
        if hasattr(self, 'console_text'):
            self.console_text.config(
                background=colors["console_bg"],
                foreground=colors["console_fg"]
            )

            # Update console tag colors
            self.console_text.tag_configure("info", foreground=colors["console_info"])
            self.console_text.tag_configure("success", foreground=colors["console_success"])
            self.console_text.tag_configure("warning", foreground=colors["console_warning"])
            self.console_text.tag_configure("error", foreground=colors["console_error"])
            self.console_text.tag_configure("debug", foreground=colors["console_debug"])

        # Update PASS/FAIL/Demo buttons
        self.pass_btn.config(bg=colors["pass_bg"], fg=colors["pass_fg"])
        self.fail_btn.config(bg=colors["fail_bg"], fg=colors["fail_fg"])
        self.launch_demo_btn.config(bg=colors["demo_bg"], fg=colors["demo_fg"])

        # Set the canvas background for steps
        self.steps_canvas.config(background=colors["frame_bg"])

        # Update text areas
        if hasattr(self, 'result_notes_text'):
            self.result_notes_text.config(bg=colors["frame_bg"], fg=colors["fg"])

        # Update list boxes
        self.category_listbox.config(bg=colors["frame_bg"], fg=colors["fg"])
        self.tests_listbox.config(bg=colors["frame_bg"], fg=colors["fg"])

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

        # Log theme change to console
        theme_name = "Dark" if new_theme == "dark" else "Light"
        self.log_to_console(f"Switched to {theme_name} theme", "info")

    def run_config_tests(self):
        """Automatically run the configuration tests."""
        if self.categories[0].name == "Configuration System":
            cat = self.categories[0]
            config = None

            # Config Loading Test
            test_idx = 0
            test = cat.tests[test_idx]

            try:
                config = ConfigManager()
                if config and len(config._data) > 0:
                    test["result"].status = "PASS"
                    test["result"].notes = f"Config loaded successfully with {len(config._data)} sections"
                    self.log_to_console(f"Config test PASS: {test['result'].notes}", "success")
                else:
                    test["result"].status = "FAIL"
                    test["result"].notes = "Config loaded but appears empty"
                    self.log_to_console(f"Config test FAIL: {test['result'].notes}", "error")
            except Exception as e:
                test["result"].status = "FAIL"
                test["result"].notes = f"Config failed to load: {str(e)}"
                self.log_to_console(f"Config test FAIL: {test['result'].notes}", "error")

            # Config Sections Test
            test_idx = 1
            test = cat.tests[test_idx]

            try:
                required_sections = ["toggles", "modules", "leveling", "skills", "spells", "enchantments", "ui"]
                missing_sections = []

                if config:
                    for section in required_sections:
                        if section not in config._data:
                            missing_sections.append(section)

                    if not missing_sections:
                        test["result"].status = "PASS"
                        test["result"].notes = f"All required config sections found: {', '.join(required_sections)}"
                        self.log_to_console(f"Config sections test PASS: {test['result'].notes}", "success")
                    else:
                        test["result"].status = "FAIL"
                        test["result"].notes = f"Missing config sections: {', '.join(missing_sections)}"
                        self.log_to_console(f"Config sections test FAIL: {test['result'].notes}", "error")

                    # Additional validation for new systems
                    extra_checks = []

                    # Check item rarities and grades
                    if 'defaults' in config._data:
                        defaults = config._data['defaults']
                        if 'rarities' in defaults and isinstance(defaults['rarities'], list):
                            extra_checks.append(f"Item rarities: {len(defaults['rarities'])} types")
                        if 'grades' in defaults and isinstance(defaults['grades'], list):
                            extra_checks.append(f"Item grades: {len(defaults['grades'])} levels")

                    # Check spells configuration
                    if 'spells' in config._data and len(config._data['spells']) > 0:
                        spell_count = len(config._data['spells'])
                        extra_checks.append(f"Spells configured: {spell_count}")

                    # Check skills configuration
                    if 'skills' in config._data and len(config._data['skills']) > 0:
                        skill_count = len(config._data['skills'])
                        extra_checks.append(f"Skills configured: {skill_count}")

                    # Check enchantments configuration
                    if 'enchantments' in config._data and len(config._data['enchantments']) > 0:
                        enchant_count = len(config._data['enchantments'])
                        extra_checks.append(f"Enchantments configured: {enchant_count}")

                    if extra_checks:
                        additional_info = "; ".join(extra_checks)
                        test["result"].notes += f". Additional validation: {additional_info}"
                        self.log_to_console(f"Additional config validation: {additional_info}", "info")

                else:
                    test["result"].status = "FAIL"
                    test["result"].notes = "Cannot check config sections: Config not loaded"
                    self.log_to_console(f"Config sections test FAIL: {test['result'].notes}", "error")
            except Exception as e:
                test["result"].status = "FAIL"
                test["result"].notes = f"Error checking config sections: {str(e)}"
                self.log_to_console(f"Config sections test FAIL: {test['result'].notes}", "error")

            # Update UI to show results
            self.update_test_display()

    def on_category_select(self, event):
        """Handle category selection."""
        if not self.categories:
            return

        selection = self.category_listbox.curselection()
        if selection:
            self.current_category = selection[0]

            # Update category info
            category = self.categories[self.current_category]
            self.category_label.config(text=category.name)
            self.category_desc_label.config(text=category.description)

            # Update tests list
            self.tests_listbox.delete(0, tk.END)
            for test in category.tests:
                status = test["result"].status
                status_display = f" [{status}]" if status else ""
                self.tests_listbox.insert(tk.END, f"{test['name']}{status_display}")

            # Select first test
            if category.tests:
                self.tests_listbox.selection_set(0)
                self.current_test = 0
                self.on_test_select(None)

    def on_test_select(self, event):
        """Handle test selection."""
        selection = self.tests_listbox.curselection()
        if selection:
            prev_test = self.current_test
            self.current_test = selection[0]

            if prev_test != self.current_test:
                self.update_test_display()

    def update_test_display(self):
        """Update the display for the current test."""
        try:
            if not self.categories or self.current_category >= len(self.categories):
                return

            category = self.categories[self.current_category]

            if not category.tests or self.current_test >= len(category.tests):
                return

            test = category.tests[self.current_test]

            # Update test info
            self.test_name_label.config(text=test["name"])
            self.test_desc_label.config(text=test["description"])

            # Clear and update steps
            for widget in self.steps_frame.winfo_children():
                widget.destroy()

            # Reset scroll position
            self.steps_canvas.yview_moveto(0)

            # Add test status if it has one
            test_status = test["result"].status
            if test_status:
                status_color = "green" if test_status == "PASS" else "red"
                status_label = ttk.Label(
                    self.steps_frame,
                    text=f"Test Status: {test_status}",
                    font=("Arial", 10, "bold"),
                    foreground=status_color
                )
                status_label.pack(anchor=tk.W, pady=(0, 5))

                ttk.Separator(self.steps_frame, orient=tk.HORIZONTAL).pack(
                    fill=tk.X, pady=5
                )

            # Add the test steps
            steps_header = ttk.Label(
                self.steps_frame,
                text="Test Steps:",
                font=("Arial", 10, "bold"),
                foreground="#000066"
            )
            steps_header.pack(anchor=tk.W, pady=(2, 5))

            if not test["steps"]:
                ttk.Label(
                    self.steps_frame,
                    text="No steps provided for this test.",
                    font=("Arial", 9, "italic"),
                    foreground="#666666"
                ).pack(anchor=tk.W, pady=5, padx=10)

            # Display each step
            for i, step in enumerate(test["steps"]):
                cat_num = self.current_category + 1
                test_num = self.current_test + 1
                step_num = i + 1

                step_text = f"{cat_num}.{test_num}.{step_num}. {step}"

                step_label = ttk.Label(
                    self.steps_frame,
                    text=step_text,
                    wraplength=480,
                    justify=tk.LEFT,
                    font=("Arial", 9)
                )
                step_label.pack(anchor=tk.W, pady=1, padx=(10, 5), fill=tk.X)

            # Update notes
            if hasattr(self, 'result_notes_text'):
                self.result_notes_text.delete("1.0", tk.END)
                if test["result"].notes:
                    self.result_notes_text.insert("1.0", test["result"].notes)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update test display: {str(e)}")
            self.log_to_console(f"Error updating test display: {str(e)}", "error")

    def record_result(self, status):
        """Record the result of the current test."""
        try:
            self.log_to_console(f"Recording test result: {status}", "info")

            if not self.categories:
                messagebox.showwarning("Warning", "No test categories available")
                self.log_to_console("No test categories available", "error")
                return

            if self.current_category >= len(self.categories):
                messagebox.showwarning("Warning", "Invalid category index")
                self.log_to_console("Invalid category index", "error")
                return

            category = self.categories[self.current_category]

            if not category.tests:
                messagebox.showwarning("Warning", "No tests in this category")
                return

            if self.current_test >= len(category.tests):
                messagebox.showwarning("Warning", "Invalid test index")
                return

            test = category.tests[self.current_test]

            # Get notes from text field
            result_notes = self.result_notes_text.get("1.0", tk.END).strip()

            # Record the result
            test["result"].status = status
            test["result"].notes = result_notes
            test["result"].timestamp = datetime.datetime.now()

            # Update the test list to show status
            if self.current_test < self.tests_listbox.size():
                self.tests_listbox.delete(self.current_test)
                status_display = f" [{status}]" if status else ""
                self.tests_listbox.insert(self.current_test, f"{test['name']}{status_display}")
                self.tests_listbox.selection_set(self.current_test)

                # Update the current test display to show the new status
                self.update_test_display()

            # Show confirmation message and switch back to the first tab
            messagebox.showinfo("Test Result", f"Test marked as {status}")
            self.notebook.select(0)  # Switch back to the first tab

            # Log the result
            self.log_to_console(f"Test '{test['name']}' marked as {status}", "success")

            # Automatically go to next test
            self.next_test()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record result: {str(e)}")
            self.log_to_console(f"Error recording result: {str(e)}", "error")

    def next_test(self):
        """Go to the next test."""
        category = self.categories[self.current_category]
        if self.current_test < len(category.tests) - 1:
            self.current_test += 1
            self.tests_listbox.selection_clear(0, tk.END)
            self.tests_listbox.selection_set(self.current_test)
            self.update_test_display()
        elif self.current_category < len(self.categories) - 1:
            self.current_category += 1
            self.category_listbox.selection_clear(0, tk.END)
            self.category_listbox.selection_set(self.current_category)
            self.on_category_select(None)
            self.current_test = 0
            self.tests_listbox.selection_clear(0, tk.END)
            self.tests_listbox.selection_set(self.current_test)
            self.update_test_display()

    def prev_test(self):
        """Go to the previous test."""
        category = self.categories[self.current_category]
        if self.current_test > 0:
            self.current_test -= 1
            self.tests_listbox.selection_clear(0, tk.END)
            self.tests_listbox.selection_set(self.current_test)
            self.update_test_display()
        elif self.current_category > 0:
            self.current_category -= 1
            self.category_listbox.selection_clear(0, tk.END)
            self.category_listbox.selection_set(self.current_category)
            self.on_category_select(None)
            category = self.categories[self.current_category]
            self.current_test = len(category.tests) - 1
            self.tests_listbox.selection_clear(0, tk.END)
            self.tests_listbox.selection_set(self.current_test)
            self.update_test_display()

    def save_results(self):
        """Save test results to a file."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.txt"
            filepath = Path(__file__).parent / "test_results" / filename

            # Create test_results directory if it doesn't exist
            filepath.parent.mkdir(exist_ok=True)

            with open(filepath, 'w') as f:
                f.write("Comprehensive Test Results\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.datetime.now()}\n\n")

                for category in self.categories:
                    f.write(f"Category: {category.name}\n")
                    f.write("-" * 30 + "\n")

                    for test in category.tests:
                        result = test["result"]
                        f.write(f"Test: {test['name']}\n")
                        f.write(f"Status: {result.status or 'NOT TESTED'}\n")
                        f.write(f"Timestamp: {result.timestamp}\n")
                        if result.notes:
                            f.write(f"Notes: {result.notes}\n")
                        f.write("\n")
                    f.write("\n")

            messagebox.showinfo("Results Saved", f"Test results saved to: {filepath}")
            self.log_to_console(f"Test results saved to: {filepath}", "success")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
            self.log_to_console(f"Error saving results: {str(e)}", "error")

if __name__ == "__main__":
    manager = ComprehensiveTestManager()
    manager.root.mainloop()

    # Restore stdout and stderr before exiting
    manager.restore_stdout_stderr()
