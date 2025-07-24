#!/usr/bin/env python3
"""
Game UI Components
================

This module defines game-specific UI components built on the base widgets.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, List, Optional, Callable, Any, Tuple

from .base_widget import BaseWidget
from .basic_widgets import Button, Label, Panel, TextInput
from game_sys.hooks.event_types import UIEventType, UIEvent

from game_sys.character.actor import Actor
from game_sys.combat.engine import CombatEngine


class CharacterPanel(Panel):
    """A panel to display character information."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize a character panel.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments:
                title: Panel title (default: "Character")
                actor: The actor to display
        """
        title = kwargs.pop('title', "Character")
        super().__init__(parent, title=title, **kwargs)
        self.actor = kwargs.get('actor', None)
        self.stats_labels = {}
        self.health_bar = None
        self.mana_bar = None
        self.stamina_bar = None
        self.equipment_labels = {}
        
    def create_widget(self, tk_parent) -> ttk.LabelFrame:
        """Create the character panel widget."""
        # Create the base panel
        panel = super().create_widget(tk_parent)
        
        # Create the UI components
        self._create_stats_ui(panel)
        self._create_bars_ui(panel)
        self._create_equipment_ui(panel)
        
        # Update with initial data
        self.update()
        
        return panel
        
    def _create_stats_ui(self, panel):
        """Create the stats UI elements."""
        stats_frame = ttk.LabelFrame(panel, text="Stats")
        stats_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Core stats
        stat_names = [
            ("strength", "Strength"),
            ("dexterity", "Dexterity"),
            ("intelligence", "Intelligence"),
            ("constitution", "Constitution"),
            ("attack", "Attack"),
            ("defense", "Defense"),
            ("crit_chance", "Crit Chance"),
            ("speed", "Speed")
        ]
        
        for i, (stat_id, stat_label) in enumerate(stat_names):
            row = i // 2
            col = (i % 2) * 2  # Each stat takes 2 columns (label + value)
            
            # Label
            ttk.Label(stats_frame, text=f"{stat_label}:").grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=2
            )
            
            # Value label
            value_label = ttk.Label(stats_frame, text="--")
            value_label.grid(
                row=row, column=col+1, sticky=tk.W, padx=5, pady=2
            )
            
            self.stats_labels[stat_id] = value_label
    
    def _create_bars_ui(self, panel):
        """Create the health/mana/stamina bars UI elements."""
        bars_frame = ttk.LabelFrame(panel, text="Status")
        bars_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Health bar
        ttk.Label(bars_frame, text="Health:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=2
        )
        health_frame = ttk.Frame(bars_frame)
        health_frame.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        self.health_bar = ttk.Progressbar(health_frame, length=100)
        self.health_bar.pack(side=tk.LEFT)
        
        self.health_text = ttk.Label(health_frame, text="--/--")
        self.health_text.pack(side=tk.LEFT, padx=5)
        
        # Mana bar
        ttk.Label(bars_frame, text="Mana:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2
        )
        mana_frame = ttk.Frame(bars_frame)
        mana_frame.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        self.mana_bar = ttk.Progressbar(mana_frame, length=100)
        self.mana_bar.pack(side=tk.LEFT)
        
        self.mana_text = ttk.Label(mana_frame, text="--/--")
        self.mana_text.pack(side=tk.LEFT, padx=5)
        
        # Stamina bar
        ttk.Label(bars_frame, text="Stamina:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=2
        )
        stamina_frame = ttk.Frame(bars_frame)
        stamina_frame.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        self.stamina_bar = ttk.Progressbar(stamina_frame, length=100)
        self.stamina_bar.pack(side=tk.LEFT)
        
        self.stamina_text = ttk.Label(stamina_frame, text="--/--")
        self.stamina_text.pack(side=tk.LEFT, padx=5)
    
    def _create_equipment_ui(self, panel):
        """Create the equipment UI elements."""
        equipment_frame = ttk.LabelFrame(panel, text="Equipment")
        equipment_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Weapon
        ttk.Label(equipment_frame, text="Weapon:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=2
        )
        weapon_label = ttk.Label(equipment_frame, text="None")
        weapon_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.equipment_labels["weapon"] = weapon_label
        
        # Offhand
        ttk.Label(equipment_frame, text="Offhand:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2
        )
        offhand_label = ttk.Label(equipment_frame, text="None")
        offhand_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        self.equipment_labels["offhand"] = offhand_label
    
    def set_actor(self, actor: Actor):
        """Set the actor for this panel and update the display."""
        self.actor = actor
        self.update()
    
    def update(self):
        """Update all display elements based on current actor state."""
        if not self.actor:
            return
            
        # Update stats
        for stat_id, label in self.stats_labels.items():
            stat_value = self.actor.get_stat(stat_id)
            if stat_id == "crit_chance":
                label.configure(text=f"{stat_value:.1f}%")
            else:
                label.configure(text=f"{stat_value:.1f}")
                
        # Update health bar
        health_pct = (self.actor.current_health / self.actor.max_health * 100 
                     if self.actor.max_health > 0 else 0)
        self.health_bar["value"] = health_pct
        self.health_text.configure(
            text=f"{self.actor.current_health:.1f}/{self.actor.max_health:.1f}"
        )
        
        # Update mana bar
        mana_pct = (self.actor.current_mana / self.actor.max_mana * 100 
                   if self.actor.max_mana > 0 else 0)
        self.mana_bar["value"] = mana_pct
        self.mana_text.configure(
            text=f"{self.actor.current_mana:.1f}/{self.actor.max_mana:.1f}"
        )
        
        # Update stamina bar
        stamina_pct = (self.actor.current_stamina / self.actor.max_stamina * 100 
                      if self.actor.max_stamina > 0 else 0)
        self.stamina_bar["value"] = stamina_pct
        self.stamina_text.configure(
            text=f"{self.actor.current_stamina:.1f}/{self.actor.max_stamina:.1f}"
        )
        
        # Update equipment
        self.equipment_labels["weapon"].configure(
            text=self.actor.weapon.name if self.actor.weapon else "None"
        )
        self.equipment_labels["offhand"].configure(
            text=self.actor.offhand.name if self.actor.offhand else "None"
        )


class StatusEffectsPanel(Panel):
    """A panel to display active status effects."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize a status effects panel.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments:
                title: Panel title (default: "Status Effects")
                actor: The actor to display
        """
        title = kwargs.pop('title', "Status Effects")
        super().__init__(parent, title=title, **kwargs)
        self.actor = kwargs.get('actor', None)
        self.tree = None
        
    def create_widget(self, tk_parent) -> ttk.LabelFrame:
        """Create the status effects panel widget."""
        # Create the base panel
        panel = super().create_widget(tk_parent)
        
        # Create a treeview for status effects
        columns = ("Effect", "Duration", "Strength")
        self.tree = ttk.Treeview(panel, columns=columns, show="headings", height=5)
        
        # Configure columns
        self.tree.heading("Effect", text="Effect")
        self.tree.heading("Duration", text="Duration")
        self.tree.heading("Strength", text="Strength")
        
        self.tree.column("Effect", width=150)
        self.tree.column("Duration", width=80)
        self.tree.column("Strength", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(panel, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Update with initial data
        self.update()
        
        return panel
    
    def set_actor(self, actor: Actor):
        """Set the actor for this panel and update the display."""
        self.actor = actor
        self.update()
    
    def update(self):
        """Update the status effects display."""
        if not self.actor or not self.tree:
            return
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add current status effects
        for effect_name, (effect, duration) in self.actor.active_statuses.items():
            strength = getattr(effect, "strength", "N/A")
            self.tree.insert("", tk.END, values=(effect_name, f"{duration:.1f}s", strength))


class GameLogPanel(Panel):
    """A panel to display game log messages."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize a game log panel.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments:
                title: Panel title (default: "Game Log")
                height: Height in lines (default: 10)
        """
        title = kwargs.pop('title', "Game Log")
        super().__init__(parent, title=title, **kwargs)
        self.height = kwargs.get('height', 10)
        self.text_widget = None
        
    def create_widget(self, tk_parent) -> ttk.LabelFrame:
        """Create the game log panel widget."""
        # Create the base panel
        panel = super().create_widget(tk_parent)
        
        # Create text widget with scrollbar
        self.text_widget = scrolledtext.ScrolledText(
            panel, wrap=tk.WORD, height=self.height
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_widget.config(state=tk.DISABLED)
        
        # Configure text tags
        self.text_widget.tag_configure("hit", foreground="blue")
        self.text_widget.tag_configure("critical", foreground="red")
        self.text_widget.tag_configure("miss", foreground="gray")
        self.text_widget.tag_configure("blocked", foreground="orange")
        self.text_widget.tag_configure("heal", foreground="green")
        self.text_widget.tag_configure("special", foreground="purple")
        self.text_widget.tag_configure("action", foreground="black", 
                                      font=("Helvetica", 10, "bold"))
        self.text_widget.tag_configure("enemy", foreground="brown", 
                                      font=("Helvetica", 10, "bold"))
        self.text_widget.tag_configure("equip", foreground="teal")
        self.text_widget.tag_configure("warning", foreground="red")
        
        return panel
    
    def log(self, message: str, tag: str = None):
        """Add a message to the log with optional tag."""
        if not self.text_widget:
            return
            
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, message + "\n")
        if tag:
            self.text_widget.tag_add(tag, "end-2l", "end-1c")
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
    
    def clear(self):
        """Clear the log."""
        if not self.text_widget:
            return
            
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)


class ActionPanel(Panel):
    """A panel for combat actions."""
    
    def __init__(self, parent=None, **kwargs):
        """Initialize an action panel.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments:
                title: Panel title (default: "Actions")
                player: The player actor
                enemy: The enemy actor
                game_log: The game log panel
        """
        title = kwargs.pop('title', "Actions")
        super().__init__(parent, title=title, **kwargs)
        self.player = kwargs.get('player', None)
        self.enemy = kwargs.get('enemy', None)
        self.game_log = kwargs.get('game_log', None)
        self.combat_engine = CombatEngine()
        self.buttons = {}
        
    def create_widget(self, tk_parent) -> ttk.LabelFrame:
        """Create the action panel widget."""
        # Create the base panel
        panel = super().create_widget(tk_parent)
        
        # Create action buttons
        self._create_action_buttons(panel)
        
        # Create equipment section
        self._create_equipment_section(panel)
        
        # Update button states
        self.update_button_states()
        
        return panel
    
    def _create_action_buttons(self, panel):
        """Create the action buttons."""
        buttons_frame = ttk.Frame(panel)
        buttons_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Attack button
        attack_btn = ttk.Button(
            buttons_frame, text="Attack", command=self.attack
        )
        attack_btn.pack(side=tk.LEFT, padx=5)
        self.buttons["attack"] = attack_btn
        
        # Heal button
        heal_btn = ttk.Button(
            buttons_frame, text="Heal", command=self.heal
        )
        heal_btn.pack(side=tk.LEFT, padx=5)
        self.buttons["heal"] = heal_btn
        
        # Block button
        block_btn = ttk.Button(
            buttons_frame, text="Block", command=self.block
        )
        block_btn.pack(side=tk.LEFT, padx=5)
        self.buttons["block"] = block_btn
        
        # Special attack button
        special_btn = ttk.Button(
            buttons_frame, text="Special Attack", command=self.special_attack
        )
        special_btn.pack(side=tk.LEFT, padx=5)
        self.buttons["special"] = special_btn
    
    def _create_equipment_section(self, panel):
        """Create the equipment section."""
        equip_frame = ttk.LabelFrame(panel, text="Equipment")
        equip_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Weapon selection
        ttk.Label(equip_frame, text="Weapon:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=2
        )
        self.weapon_var = tk.StringVar(value="sword")
        weapon_options = ["sword", "axe", "mace", "staff", "dagger"]
        self.weapon_combo = ttk.Combobox(
            equip_frame, textvariable=self.weapon_var, 
            values=weapon_options, state="readonly"
        )
        self.weapon_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Equip weapon button
        self.equip_weapon_btn = ttk.Button(
            equip_frame, text="Equip", command=self.equip_weapon
        )
        self.equip_weapon_btn.grid(row=0, column=2, padx=5, pady=2)
        self.buttons["equip_weapon"] = self.equip_weapon_btn
        
        # Offhand selection
        ttk.Label(equip_frame, text="Offhand:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2
        )
        self.offhand_var = tk.StringVar(value="shield")
        offhand_options = ["shield", "dagger", "spell_focus", "none"]
        self.offhand_combo = ttk.Combobox(
            equip_frame, textvariable=self.offhand_var, 
            values=offhand_options, state="readonly"
        )
        self.offhand_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Equip offhand button
        self.equip_offhand_btn = ttk.Button(
            equip_frame, text="Equip", command=self.equip_offhand
        )
        self.equip_offhand_btn.grid(row=1, column=2, padx=5, pady=2)
        self.buttons["equip_offhand"] = self.equip_offhand_btn
    
    def set_actors(self, player: Actor, enemy: Actor):
        """Set the player and enemy actors."""
        self.player = player
        self.enemy = enemy
        self.update_button_states()
    
    def update_button_states(self):
        """Update the state of action buttons based on actor state."""
        enabled = self.player is not None and self.enemy is not None
        player_alive = enabled and self.player.current_health > 0
        enemy_alive = enabled and self.enemy.current_health > 0
        
        for button_name, button in self.buttons.items():
            if button_name in ["attack", "heal", "block", "special"]:
                button["state"] = "normal" if (player_alive and enemy_alive) else "disabled"
            else:
                button["state"] = "normal" if player_alive else "disabled"
    
    # Action methods
    def attack(self):
        """Execute a basic attack."""
        if not self.player or not self.enemy or not self.game_log:
            return
            
        # Use the combat engine to execute the attack
        result = self.combat_engine.execute_attack(self.player, self.enemy)
        
        # Log the result
        if result.hit:
            if result.critical:
                self.game_log.log(
                    f"Critical hit! {self.player.name} deals {result.damage:.1f} damage!",
                    "critical"
                )
            else:
                self.game_log.log(
                    f"{self.player.name} hits for {result.damage:.1f} damage!",
                    "hit"
                )
        else:
            self.game_log.log(f"{self.player.name}'s attack misses!", "miss")
            
        # Schedule enemy action
        self.schedule_enemy_action()
    
    def heal(self):
        """Execute a healing action."""
        if not self.player or not self.enemy or not self.game_log:
            return
            
        # Check if player has enough mana
        mana_cost = 10.0
        if self.player.current_mana < mana_cost:
            self.game_log.log(f"Not enough mana for healing!", "warning")
            return
            
        # Consume mana
        self.player.current_mana -= mana_cost
        
        # Calculate healing amount (based on intelligence)
        heal_amount = self.player.get_stat("intelligence") * 0.5 + 10
        
        # Apply healing
        old_health = self.player.current_health
        self.player.current_health = min(
            self.player.current_health + heal_amount,
            self.player.max_health
        )
        actual_heal = self.player.current_health - old_health
        
        # Log the healing
        self.game_log.log(
            f"{self.player.name} heals for {actual_heal:.1f} health!",
            "heal"
        )
        
        # Schedule enemy action
        self.schedule_enemy_action()
    
    def block(self):
        """Execute a blocking action."""
        if not self.player or not self.enemy or not self.game_log:
            return
            
        # Add a temporary blocking buff
        from game_sys.effects.factory import EffectFactory
        
        # Create a blocking effect definition
        block_effect_def = {
            "type": "block",
            "params": {"strength": 50.0, "duration": 3.0}
        }
        
        # Create the effect
        block_effect = EffectFactory.create(block_effect_def)
        
        # Apply the status
        self.player.apply_status(block_effect)
        
        self.game_log.log(
            f"{self.player.name} enters a defensive stance!",
            "blocked"
        )
        
        # Schedule enemy action
        self.schedule_enemy_action()
    
    def special_attack(self):
        """Execute a special attack."""
        if not self.player or not self.enemy or not self.game_log:
            return
            
        # Check if player has enough stamina
        stamina_cost = 15.0
        if self.player.current_stamina < stamina_cost:
            self.game_log.log(f"Not enough stamina for special attack!", "warning")
            return
            
        # Consume stamina
        self.player.current_stamina -= stamina_cost
        
        # Execute special attack (higher damage multiplier)
        self.game_log.log(
            f"{self.player.name} performs a special attack!",
            "special"
        )
        
        # Create a custom damage packet with higher damage
        damage_mod = self.player.get_stat("strength") * 1.5
        
        # Apply the damage directly to the enemy
        self.enemy.current_health -= damage_mod
        self.game_log.log(f"Special attack deals {damage_mod:.1f} damage!", "special")
        
        # Schedule enemy action
        self.schedule_enemy_action()
    
    def equip_weapon(self):
        """Equip the selected weapon."""
        if not self.player or not self.game_log:
            return
            
        from game_sys.items.factory import ItemFactory
        
        weapon_type = self.weapon_var.get()
        weapon = ItemFactory.create(weapon_type)
        
        success = self.player.equip_weapon(weapon)
        
        if success:
            self.game_log.log(
                f"{self.player.name} equipped {weapon.name}.",
                "equip"
            )
        else:
            self.game_log.log(
                f"Could not equip {weapon.name}.",
                "warning"
            )
    
    def equip_offhand(self):
        """Equip the selected offhand item."""
        if not self.player or not self.game_log:
            return
            
        from game_sys.items.factory import ItemFactory
        
        offhand_type = self.offhand_var.get()
        
        if offhand_type == "none":
            # Unequip offhand
            self.player.offhand = None
            self.game_log.log(
                f"{self.player.name} unequipped offhand item.",
                "equip"
            )
            return
            
        # Create and equip the offhand item
        offhand = ItemFactory.create(offhand_type)
        success = self.player.equip_offhand(offhand)
        
        if success:
            self.game_log.log(
                f"{self.player.name} equipped {offhand.name} in offhand.",
                "equip"
            )
        else:
            self.game_log.log(
                f"Could not equip {offhand.name} in offhand.",
                "warning"
            )
    
    def schedule_enemy_action(self):
        """Schedule an enemy action after a short delay."""
        if not self.enemy or not self.player:
            return
            
        if self.enemy.current_health <= 0:
            return
            
        # Implement enemy AI here (simple example)
        from game_sys.managers.time_manager import time_manager
        import random
        
        def enemy_action():
            if not self.enemy or not self.player or not self.game_log:
                return
                
            if self.enemy.current_health <= 0 or self.player.current_health <= 0:
                return
                
            # Enemy has a few action choices
            action_type = random.choice(["attack", "special", "block"])
            
            if action_type == "attack":
                # Basic attack
                result = self.combat_engine.execute_attack(self.enemy, self.player)
                
                if result.hit:
                    if result.critical:
                        self.game_log.log(
                            f"Critical hit! {self.enemy.name} deals {result.damage:.1f} damage!",
                            "critical"
                        )
                    else:
                        self.game_log.log(
                            f"{self.enemy.name} hits for {result.damage:.1f} damage!",
                            "enemy"
                        )
                else:
                    self.game_log.log(
                        f"{self.enemy.name}'s attack misses!",
                        "miss"
                    )
                    
            elif action_type == "special" and self.enemy.current_stamina >= 15.0:
                # Special attack
                self.enemy.current_stamina -= 15.0
                damage_mod = self.enemy.get_stat("strength") * 1.3  # Slightly weaker than player
                
                self.game_log.log(
                    f"{self.enemy.name} performs a special attack!",
                    "special"
                )
                
                # Apply damage directly
                self.player.current_health -= damage_mod
                self.game_log.log(
                    f"Enemy special attack deals {damage_mod:.1f} damage!",
                    "special"
                )
                
            elif action_type == "block":
                # Block
                from game_sys.effects.factory import EffectFactory
                
                block_effect_def = {
                    "type": "block",
                    "params": {"strength": 40.0, "duration": 3.0}  # Slightly weaker than player
                }
                
                block_effect = EffectFactory.create(block_effect_def)
                self.enemy.apply_status(block_effect)
                
                self.game_log.log(
                    f"{self.enemy.name} enters a defensive stance!",
                    "blocked"
                )
            
            else:
                # Fallback to basic attack if other action couldn't be performed
                result = self.combat_engine.execute_attack(self.enemy, self.player)
                
                if result.hit:
                    self.game_log.log(
                        f"{self.enemy.name} hits for {result.damage:.1f} damage!",
                        "enemy"
                    )
                else:
                    self.game_log.log(
                        f"{self.enemy.name}'s attack misses!",
                        "miss"
                    )
            
            # Update UI after enemy action
            self.update_button_states()
        
        # Schedule the enemy action with a delay
        time_manager.queue_action(enemy_action, delay=1.0)
