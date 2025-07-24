#!/usr/bin/env python3
"""
Combat Arena Manager for Demo v3
================================

Advanced combat testing and demonstration system with:
- Real-time combat simulation
- Visual combat logs
- Damage calculation breakdown
- Performance metrics
- AI behavior testing
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass

from game_sys.logging import get_logger
from game_sys.combat.combat_service import CombatService
from game_sys.character.character_factory import create_character
from game_sys.character.character_service import create_character_with_random_stats


@dataclass
class CombatScenario:
    """Configuration for a combat scenario."""
    name: str
    description: str
    player_template: str
    enemy_template: str
    enemy_count: int = 1
    auto_combat: bool = False
    difficulty_multiplier: float = 1.0


class CombatArenaManager:
    """Manager for the Combat Arena tab - comprehensive combat testing."""
    
    def __init__(self, parent: ttk.Frame, combat_service: CombatService, character_service, demo_app):
        """Initialize the Combat Arena manager."""
        self.parent = parent
        self.combat_service = combat_service
        self.character_service = character_service
        self.demo_app = demo_app
        self.logger = get_logger(f"{__name__}.CombatArena")
        
        # Combat state
        self.current_player = None
        self.current_enemies = []
        self.combat_active = False
        self.combat_log = []
        self.combat_stats = {
            'rounds': 0,
            'damage_dealt': 0,
            'damage_taken': 0,
            'hits': 0,
            'misses': 0,
            'crits': 0
        }
        
        # UI components
        self.main_frame = None
        self.control_panel = None
        self.combat_display = None
        self.log_display = None
        self.stats_display = None
        
        # Combat scenarios
        self.scenarios = self._create_combat_scenarios()
        self.selected_scenario = tk.StringVar()
        
        self._setup_arena()
    
    def _create_combat_scenarios(self) -> List[CombatScenario]:
        """Create predefined combat scenarios."""
        return [
            CombatScenario(
                name="Hero vs Goblin",
                description="Basic combat test - Hero against a single Goblin",
                player_template="hero",
                enemy_template="goblin",
                enemy_count=1
            ),
            CombatScenario(
                name="Mage vs Orc",
                description="Magic vs Brute strength - Mage against an Orc",
                player_template="mage",
                enemy_template="orc",
                enemy_count=1
            ),
            CombatScenario(
                name="Warrior vs Pack",
                description="Endurance test - Warrior against multiple enemies",
                player_template="warrior",
                enemy_template="goblin",
                enemy_count=3
            ),
            CombatScenario(
                name="Elite Challenge",
                description="High difficulty - Hero vs Elite enemy",
                player_template="hero",
                enemy_template="orc",
                enemy_count=1,
                difficulty_multiplier=2.0
            ),
            CombatScenario(
                name="Auto Combat Demo",
                description="Automated combat demonstration",
                player_template="hero",
                enemy_template="goblin",
                enemy_count=2,
                auto_combat=True
            )
        ]
    
    def _setup_arena(self) -> None:
        """Set up the combat arena interface."""
        try:
            # Create main layout with paned window
            self.main_frame = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create left panel for controls
            self._create_control_panel()
            
            # Create right panel for combat display
            self._create_combat_display()
            
            self.logger.info("Combat arena setup completed")
            
        except Exception as e:
            self.logger.error(f"Arena setup error: {e}")
    
    def _create_control_panel(self) -> None:
        """Create the combat control panel."""
        control_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(control_frame, weight=1)
        
        # Scenario selection
        scenario_frame = ttk.LabelFrame(control_frame, text="Combat Scenarios")
        scenario_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.scenario_combo = ttk.Combobox(
            scenario_frame,
            textvariable=self.selected_scenario,
            values=[s.name for s in self.scenarios],
            state="readonly"
        )
        self.scenario_combo.pack(fill=tk.X, padx=5, pady=5)
        self.scenario_combo.bind("<<ComboboxSelected>>", self._on_scenario_selected)
        
        # Scenario description
        self.scenario_desc = tk.Text(scenario_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        self.scenario_desc.pack(fill=tk.X, padx=5, pady=5)
        
        # Combat controls
        controls_frame = ttk.LabelFrame(control_frame, text="Combat Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = ttk.Button(button_frame, text="🚀 Start Combat", command=self._start_combat)
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.step_btn = ttk.Button(button_frame, text="➡️ Next Turn", command=self._next_turn, state=tk.DISABLED)
        self.step_btn.pack(side=tk.LEFT, padx=2)
        
        self.auto_btn = ttk.Button(button_frame, text="⚡ Auto Combat", command=self._toggle_auto_combat)
        self.auto_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(button_frame, text="🛑 Stop", command=self._stop_combat, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Character setup
        char_frame = ttk.LabelFrame(control_frame, text="Character Setup")
        char_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(char_frame, text="🎲 Random Player", command=self._create_random_player).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(char_frame, text="📥 Use Current Character", command=self._use_current_character).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(char_frame, text="👤 Character Info", command=self._show_character_info).pack(fill=tk.X, padx=5, pady=2)
        
        # Combat statistics
        self.stats_frame = ttk.LabelFrame(control_frame, text="Combat Statistics")
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = tk.Text(self.stats_frame, height=8, font=('Consolas', 9), state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._update_stats_display()
    
    def _create_combat_display(self) -> None:
        """Create the combat display area."""
        display_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(display_frame, weight=2)
        
        # Combat visualization
        viz_frame = ttk.LabelFrame(display_frame, text="Combat Visualization")
        viz_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.combat_canvas = tk.Canvas(viz_frame, height=200, bg='#f0f0f0')
        self.combat_canvas.pack(fill=tk.X, padx=5, pady=5)
        
        # Combat log
        log_frame = ttk.LabelFrame(display_frame, text="Combat Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrolled text widget for log
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_container, wrap=tk.WORD, font=('Consolas', 9), state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Combat status
        status_frame = ttk.Frame(display_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.combat_status = ttk.Label(status_frame, text="Ready - Select scenario and start combat", font=('Arial', 10, 'bold'))
        self.combat_status.pack()
        
        # Initialize with welcome message
        self._log_combat_message("🏟️ Welcome to the Combat Arena!")
        self._log_combat_message("Select a combat scenario and click 'Start Combat' to begin.")
    
    def _on_scenario_selected(self, event=None) -> None:
        """Handle scenario selection."""
        scenario_name = self.selected_scenario.get()
        scenario = next((s for s in self.scenarios if s.name == scenario_name), None)
        
        if scenario:
            # Update description
            self.scenario_desc.config(state=tk.NORMAL)
            self.scenario_desc.delete(1.0, tk.END)
            self.scenario_desc.insert(tk.END, scenario.description)
            self.scenario_desc.config(state=tk.DISABLED)
            
            self.demo_app.status_label.config(text=f"Scenario selected: {scenario.name}")
    
    def _start_combat(self) -> None:
        """Start a combat scenario."""
        try:
            scenario_name = self.selected_scenario.get()
            if not scenario_name:
                messagebox.showwarning("No Scenario", "Please select a combat scenario first!")
                return
            
            scenario = next((s for s in self.scenarios if s.name == scenario_name), None)
            if not scenario:
                messagebox.showerror("Error", "Invalid scenario selected!")
                return
            
            self._log_combat_message(f"🚀 Starting scenario: {scenario.name}")
            
            # Create or use existing player character
            if not self.current_player:
                self._create_player_from_template(scenario.player_template)
            
            # Create enemies
            self._create_enemies_from_scenario(scenario)
            
            # Initialize combat
            self.combat_active = True
            self.combat_stats = {
                'rounds': 0,
                'damage_dealt': 0,
                'damage_taken': 0,
                'hits': 0,
                'misses': 0,
                'crits': 0,
                'start_time': datetime.now()
            }
            
            # Update UI state
            self.start_btn.config(state=tk.DISABLED)
            self.step_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.combat_status.config(text=f"Combat Active - {scenario.name}")
            
            # Draw initial combat visualization
            self._draw_combat_scene()
            
            # Start auto combat if enabled
            if scenario.auto_combat:
                self._start_auto_combat()
            
            self._log_combat_message(f"⚔️ Combat begins! {self.current_player.name} vs {len(self.current_enemies)} enemies")
            self._update_stats_display()
            
        except Exception as e:
            self.logger.error(f"Start combat error: {e}")
            messagebox.showerror("Combat Error", f"Failed to start combat: {e}")
    
    def _create_player_from_template(self, template_id: str) -> None:
        """Create a player character from template."""
        try:
            # Use character creation service if available
            if hasattr(self.character_service, 'create_character_preview'):
                result = self.character_service.create_character_preview(template_id)
                if result['success']:
                    self.current_player = self.character_service.current_character
                else:
                    raise Exception(result.get('message', 'Failed to create character'))
            else:
                # Fallback to direct creation
                self.current_player = create_character(template_id)
            
            self._log_combat_message(f"👤 Player created: {self.current_player.name} (Level {self.current_player.level})")
            
        except Exception as e:
            self.logger.error(f"Player creation error: {e}")
            raise
    
    def _create_enemies_from_scenario(self, scenario: CombatScenario) -> None:
        """Create enemies for the scenario."""
        try:
            self.current_enemies = []
            
            for i in range(scenario.enemy_count):
                # Create enemy with difficulty multiplier
                enemy = create_character(scenario.enemy_template)
                
                # Apply difficulty multiplier
                if scenario.difficulty_multiplier != 1.0:
                    self._apply_difficulty_multiplier(enemy, scenario.difficulty_multiplier)
                
                # Make enemy name unique if multiple
                if scenario.enemy_count > 1:
                    enemy.name = f"{enemy.name} #{i+1}"
                
                self.current_enemies.append(enemy)
                self._log_combat_message(f"👹 Enemy created: {enemy.name} (Level {enemy.level})")
            
        except Exception as e:
            self.logger.error(f"Enemy creation error: {e}")
            raise
    
    def _apply_difficulty_multiplier(self, character, multiplier: float) -> None:
        """Apply difficulty multiplier to character stats."""
        try:
            # Increase key stats based on multiplier
            character.max_hp = int(character.max_hp * multiplier)
            character.hp = character.max_hp
            character.attack = int(character.attack * multiplier)
            character.defense = int(character.defense * multiplier)
            
            # Slightly increase level for display
            character.level = max(1, int(character.level * (multiplier * 0.7)))
            
        except Exception as e:
            self.logger.error(f"Difficulty multiplier error: {e}")
    
    def _draw_combat_scene(self) -> None:
        """Draw the combat visualization."""
        try:
            self.combat_canvas.delete("all")
            
            if not self.current_player or not self.current_enemies:
                return
            
            canvas_width = self.combat_canvas.winfo_width()
            canvas_height = self.combat_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas not ready yet
                self.demo_app.root.after(100, self._draw_combat_scene)
                return
            
            # Draw player on the left
            player_x = canvas_width * 0.2
            player_y = canvas_height * 0.5
            
            # Player health bar background
            bar_width = 80
            bar_height = 10
            self.combat_canvas.create_rectangle(
                player_x - bar_width//2, player_y - 40,
                player_x + bar_width//2, player_y - 40 + bar_height,
                fill="red", outline="black"
            )
            
            # Player health bar fill
            health_percent = self.current_player.hp / max(self.current_player.max_hp, 1)
            fill_width = int(bar_width * health_percent)
            self.combat_canvas.create_rectangle(
                player_x - bar_width//2, player_y - 40,
                player_x - bar_width//2 + fill_width, player_y - 40 + bar_height,
                fill="green", outline=""
            )
            
            # Player character
            self.combat_canvas.create_oval(
                player_x - 20, player_y - 20,
                player_x + 20, player_y + 20,
                fill="blue", outline="darkblue", width=2
            )
            
            # Player name and HP
            self.combat_canvas.create_text(
                player_x, player_y + 30,
                text=f"{self.current_player.name}\nHP: {self.current_player.hp}/{self.current_player.max_hp}",
                font=('Arial', 8), justify=tk.CENTER
            )
            
            # Draw enemies on the right
            enemy_count = len(self.current_enemies)
            for i, enemy in enumerate(self.current_enemies):
                if enemy.hp <= 0:
                    continue
                
                enemy_x = canvas_width * 0.8
                enemy_y = canvas_height * (0.3 + (i * 0.4 / max(enemy_count - 1, 1)))
                
                # Enemy health bar
                self.combat_canvas.create_rectangle(
                    enemy_x - bar_width//2, enemy_y - 40,
                    enemy_x + bar_width//2, enemy_y - 40 + bar_height,
                    fill="red", outline="black"
                )
                
                enemy_health_percent = enemy.hp / max(enemy.max_hp, 1)
                enemy_fill_width = int(bar_width * enemy_health_percent)
                self.combat_canvas.create_rectangle(
                    enemy_x - bar_width//2, enemy_y - 40,
                    enemy_x - bar_width//2 + enemy_fill_width, enemy_y - 40 + bar_height,
                    fill="green", outline=""
                )
                
                # Enemy character
                self.combat_canvas.create_oval(
                    enemy_x - 15, enemy_y - 15,
                    enemy_x + 15, enemy_y + 15,
                    fill="red", outline="darkred", width=2
                )
                
                # Enemy name and HP
                self.combat_canvas.create_text(
                    enemy_x, enemy_y + 25,
                    text=f"{enemy.name}\nHP: {enemy.hp}/{enemy.max_hp}",
                    font=('Arial', 8), justify=tk.CENTER
                )
            
        except Exception as e:
            self.logger.error(f"Combat visualization error: {e}")
    
    def _next_turn(self) -> None:
        """Execute the next combat turn."""
        try:
            if not self.combat_active:
                return
            
            self.combat_stats['rounds'] += 1
            
            # Player turn
            if self.current_player.hp > 0:
                alive_enemies = [e for e in self.current_enemies if e.hp > 0]
                if alive_enemies:
                    target = random.choice(alive_enemies)
                    self._execute_attack(self.current_player, target, is_player=True)
            
            # Enemy turns
            alive_enemies = [e for e in self.current_enemies if e.hp > 0]
            for enemy in alive_enemies:
                if self.current_player.hp > 0:
                    self._execute_attack(enemy, self.current_player, is_player=False)
            
            # Check combat end conditions
            if self.current_player.hp <= 0:
                self._end_combat("💀 Defeat! Player has fallen.")
            elif all(e.hp <= 0 for e in self.current_enemies):
                self._end_combat("🎉 Victory! All enemies defeated.")
            else:
                # Update displays
                self._draw_combat_scene()
                self._update_stats_display()
            
        except Exception as e:
            self.logger.error(f"Combat turn error: {e}")
    
    def _execute_attack(self, attacker, defender, is_player: bool) -> None:
        """Execute an attack between two characters."""
        try:
            # Simple combat calculation
            base_damage = attacker.attack
            defense = defender.defense
            
            # Calculate hit chance (simplified)
            hit_chance = 0.85  # Base 85% hit chance
            hit_roll = random.random()
            
            if hit_roll <= hit_chance:
                # Hit! Calculate damage
                damage = max(1, base_damage - defense + random.randint(-3, 3))
                
                # Check for critical hit
                crit_chance = 0.1  # 10% crit chance
                crit_roll = random.random()
                is_critical = crit_roll <= crit_chance
                
                if is_critical:
                    damage = int(damage * 1.5)
                    self.combat_stats['crits'] += 1
                
                # Apply damage
                defender.hp = max(0, defender.hp - damage)
                
                # Log attack
                crit_text = " CRITICAL!" if is_critical else ""
                self._log_combat_message(
                    f"⚔️ {attacker.name} hits {defender.name} for {damage} damage{crit_text} "
                    f"({defender.hp}/{defender.max_hp} HP remaining)"
                )
                
                # Update stats
                if is_player:
                    self.combat_stats['damage_dealt'] += damage
                else:
                    self.combat_stats['damage_taken'] += damage
                self.combat_stats['hits'] += 1
                
            else:
                # Miss!
                self._log_combat_message(f"💨 {attacker.name} misses {defender.name}!")
                self.combat_stats['misses'] += 1
            
        except Exception as e:
            self.logger.error(f"Attack execution error: {e}")
    
    def _end_combat(self, message: str) -> None:
        """End the current combat."""
        try:
            self.combat_active = False
            
            # Update UI state
            self.start_btn.config(state=tk.NORMAL)
            self.step_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.auto_btn.config(text="⚡ Auto Combat")
            
            self.combat_status.config(text="Combat Ended")
            
            # Log final result
            self._log_combat_message(f"🏁 {message}")
            
            # Calculate final stats
            if 'start_time' in self.combat_stats:
                duration = datetime.now() - self.combat_stats['start_time']
                self._log_combat_message(f"⏱️ Combat duration: {duration.total_seconds():.1f} seconds")
            
            self._update_stats_display()
            self._draw_combat_scene()
            
            self.demo_app.status_label.config(text=f"Combat ended: {message}")
            
        except Exception as e:
            self.logger.error(f"End combat error: {e}")
    
    def _stop_combat(self) -> None:
        """Stop the current combat."""
        if messagebox.askyesno("Stop Combat", "Are you sure you want to stop the current combat?"):
            self._end_combat("🛑 Combat stopped by user")
    
    def _toggle_auto_combat(self) -> None:
        """Toggle auto combat mode."""
        try:
            if not self.combat_active:
                messagebox.showinfo("Auto Combat", "Start a combat scenario first!")
                return
            
            if hasattr(self, '_auto_combat_active') and self._auto_combat_active:
                # Stop auto combat
                self._auto_combat_active = False
                self.auto_btn.config(text="⚡ Auto Combat")
                self.step_btn.config(state=tk.NORMAL)
            else:
                # Start auto combat
                self._start_auto_combat()
        
        except Exception as e:
            self.logger.error(f"Auto combat toggle error: {e}")
    
    def _start_auto_combat(self) -> None:
        """Start automated combat."""
        try:
            self._auto_combat_active = True
            self.auto_btn.config(text="⏸️ Pause Auto")
            self.step_btn.config(state=tk.DISABLED)
            
            def auto_combat_loop():
                while self._auto_combat_active and self.combat_active:
                    self.demo_app.root.after(0, self._next_turn)
                    time.sleep(1.5)  # 1.5 second delay between turns
            
            auto_thread = threading.Thread(target=auto_combat_loop, daemon=True)
            auto_thread.start()
            
        except Exception as e:
            self.logger.error(f"Auto combat start error: {e}")
    
    def _create_random_player(self) -> None:
        """Create a random player character."""
        try:
            templates = ['hero', 'mage', 'warrior']
            template = random.choice(templates)
            self._create_player_from_template(template)
            self._log_combat_message(f"🎲 Random player created: {self.current_player.name}")
            self.demo_app.status_label.config(text=f"Random player created: {self.current_player.name}")
            
        except Exception as e:
            self.logger.error(f"Random player creation error: {e}")
            messagebox.showerror("Error", f"Failed to create random player: {e}")
    
    def _use_current_character(self) -> None:
        """Use the current character from the demo."""
        try:
            if hasattr(self.demo_app, 'current_character') and self.demo_app.current_character:
                self.current_player = self.demo_app.current_character
                self._log_combat_message(f"📥 Using current character: {self.current_player.name}")
                self.demo_app.status_label.config(text=f"Using character: {self.current_player.name}")
            else:
                messagebox.showinfo("No Character", "No current character available. Create one in the Character Workshop first!")
        
        except Exception as e:
            self.logger.error(f"Use current character error: {e}")
    
    def _show_character_info(self) -> None:
        """Show detailed character information."""
        try:
            if not self.current_player:
                messagebox.showinfo("No Character", "No player character available!")
                return
            
            # Create character info window
            info_window = tk.Toplevel(self.demo_app.root)
            info_window.title(f"Character Info - {self.current_player.name}")
            info_window.geometry("400x500")
            info_window.transient(self.demo_app.root)
            
            # Character info text
            info_text = tk.Text(info_window, wrap=tk.WORD, font=('Consolas', 10))
            info_scrollbar = ttk.Scrollbar(info_window, orient=tk.VERTICAL, command=info_text.yview)
            info_text.configure(yscrollcommand=info_scrollbar.set)
            
            info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Generate character info
            char = self.current_player
            info_lines = [
                f"Character: {char.name}",
                f"Level: {char.level}",
                f"Template: {getattr(char, 'template_id', 'Unknown')}",
                "",
                "=== COMBAT STATS ===",
                f"Health: {char.hp}/{char.max_hp}",
                f"Mana: {char.mp}/{char.max_mp}",
                f"Attack: {char.attack}",
                f"Defense: {char.defense}",
                f"Accuracy: {getattr(char, 'accuracy', 0.85):.1%}",
                f"Critical Chance: {getattr(char, 'critical_chance', 0.1):.1%}",
                "",
                "=== BASE STATS ===",
                f"Strength: {char.strength}",
                f"Intelligence: {char.intelligence}",
                f"Dexterity: {char.dexterity}",
                f"Constitution: {char.constitution}",
                f"Wisdom: {char.wisdom}",
                f"Luck: {char.luck}",
                f"Agility: {char.agility}"
            ]
            
            info_text.insert(tk.END, "\n".join(info_lines))
            info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Show character info error: {e}")
    
    def _log_combat_message(self, message: str) -> None:
        """Log a message to the combat log."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            
            self.combat_log.append(log_entry)
            
            # Update UI
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_entry + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
            
            # Keep log size manageable
            if len(self.combat_log) > 100:
                self.combat_log.pop(0)
                # Also remove from UI
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete(1.0, 2.0)
                self.log_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Combat log error: {e}")
    
    def _update_stats_display(self) -> None:
        """Update the combat statistics display."""
        try:
            stats_lines = [
                f"=== COMBAT STATISTICS ===",
                f"Rounds: {self.combat_stats['rounds']}",
                f"Damage Dealt: {self.combat_stats['damage_dealt']}",
                f"Damage Taken: {self.combat_stats['damage_taken']}",
                f"Hits: {self.combat_stats['hits']}",
                f"Misses: {self.combat_stats['misses']}",
                f"Critical Hits: {self.combat_stats['crits']}",
                "",
                f"=== CURRENT STATUS ===",
                f"Combat Active: {'Yes' if self.combat_active else 'No'}",
            ]
            
            if self.current_player:
                stats_lines.extend([
                    f"Player: {self.current_player.name}",
                    f"Player HP: {self.current_player.hp}/{self.current_player.max_hp}",
                ])
            
            if self.current_enemies:
                alive_enemies = [e for e in self.current_enemies if e.hp > 0]
                stats_lines.extend([
                    f"Enemies Alive: {len(alive_enemies)}/{len(self.current_enemies)}",
                ])
            
            # Calculate hit rate
            total_attacks = self.combat_stats['hits'] + self.combat_stats['misses']
            if total_attacks > 0:
                hit_rate = (self.combat_stats['hits'] / total_attacks) * 100
                stats_lines.append(f"Hit Rate: {hit_rate:.1f}%")
            
            stats_text = "\n".join(stats_lines)
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, stats_text)
            self.stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Stats display update error: {e}")
    
    def refresh(self) -> None:
        """Refresh the combat arena."""
        try:
            # Update scenario list if needed
            self.scenario_combo['values'] = [s.name for s in self.scenarios]
            
            # Refresh displays
            self._draw_combat_scene()
            self._update_stats_display()
            
        except Exception as e:
            self.logger.error(f"Combat arena refresh error: {e}")
