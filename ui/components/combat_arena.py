"""
Combat Arena Component
======================

A reusable combat testing and demonstration component.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Protocol
from dataclasses import dataclass

from game_sys.logging import get_logger
from game_sys.combat.combat_service import CombatService
from game_sys.character.character_creation_service import CharacterCreationService


class CombatArenaCallbacks(Protocol):
    """Protocol for combat arena callbacks."""
    
    def on_combat_started(self, attacker: Any, defender: Any) -> None:
        """Called when combat starts."""
        ...
    
    def on_combat_finished(self, result: Dict[str, Any]) -> None:
        """Called when combat finishes."""
        ...
    
    def on_status_update(self, message: str, msg_type: str = "info") -> None:
        """Called to update status display."""
        ...


@dataclass
class ArenaConfig:
    """Configuration for the combat arena."""
    show_detailed_log: bool = True
    auto_scroll_log: bool = True
    show_statistics: bool = True
    enable_auto_combat: bool = True
    combat_delay: float = 1.0


class CombatArena:
    """
    Combat Arena Component
    
    A comprehensive combat testing interface that allows users to:
    - Select combatants from available characters
    - Configure combat settings
    - Watch combat unfold with detailed logging
    - View combat statistics and results
    """
    
    def __init__(self, parent: tk.Widget, combat_service: CombatService, 
                 character_service: CharacterCreationService, callbacks: Optional[CombatArenaCallbacks] = None,
                 config: Optional[ArenaConfig] = None):
        """Initialize the combat arena."""
        self.parent = parent
        self.combat_service = combat_service
        self.character_service = character_service
        self.callbacks = callbacks
        self.config = config or ArenaConfig()
        self.logger = get_logger(f"{__name__}.CombatArena")
        
        # UI elements
        self.main_frame: Optional[tk.Frame] = None
        self.log_text: Optional[tk.Text] = None
        self.stats_frame: Optional[tk.Frame] = None
        
        # State
        self.current_combat: Optional[Dict[str, Any]] = None
        self.combat_history: list = []
        
        self._create_interface()
        self.logger.info("Combat arena component initialized")
    
    def _create_interface(self) -> None:
        """Create the combat arena interface."""
        # Main container
        self.main_frame = tk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="⚔️ Combat Arena",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Control panel
        self._create_control_panel()
        
        # Combat log
        if self.config.show_detailed_log:
            self._create_combat_log()
        
        # Statistics panel
        if self.config.show_statistics:
            self._create_statistics_panel()
    
    def _create_control_panel(self) -> None:
        """Create the combat control panel."""
        control_frame = tk.LabelFrame(self.main_frame, text="Combat Controls", font=("Arial", 12, "bold"))
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Combatant selection
        selection_frame = tk.Frame(control_frame)
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Attacker selection
        attacker_frame = tk.Frame(selection_frame)
        attacker_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Label(attacker_frame, text="Attacker:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.attacker_var = tk.StringVar()
        attacker_combo = ttk.Combobox(attacker_frame, textvariable=self.attacker_var, width=20)
        attacker_combo['values'] = ["Hero", "Warrior", "Mage", "Rogue"]  # Placeholder values
        attacker_combo.pack(fill=tk.X, pady=(2, 0))
        
        # VS label
        vs_frame = tk.Frame(selection_frame)
        vs_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(vs_frame, text="VS", font=("Arial", 14, "bold"), fg="red").pack(pady=20)
        
        # Defender selection
        defender_frame = tk.Frame(selection_frame)
        defender_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        tk.Label(defender_frame, text="Defender:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.defender_var = tk.StringVar()
        defender_combo = ttk.Combobox(defender_frame, textvariable=self.defender_var, width=20)
        defender_combo['values'] = ["Goblin", "Orc", "Dragon", "Skeleton"]  # Placeholder values
        defender_combo.pack(fill=tk.X, pady=(2, 0))
        
        # Action buttons
        button_frame = tk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(
            button_frame,
            text="🏟️ Start Combat",
            command=self._start_combat,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            button_frame,
            text="⏸️ Pause",
            command=self._pause_combat,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            button_frame,
            text="🛑 Stop",
            command=self._stop_combat,
            font=("Arial", 10),
            bg="#F44336",
            fg="white"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            button_frame,
            text="🗑️ Clear Log",
            command=self._clear_log,
            font=("Arial", 10)
        ).pack(side=tk.RIGHT)
    
    def _create_combat_log(self) -> None:
        """Create the combat log display."""
        log_frame = tk.LabelFrame(self.main_frame, text="Combat Log", font=("Arial", 12, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Text widget with scrollbar
        text_frame = tk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Consolas', 9),
            height=15
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial message
        self._log_message("Combat Arena ready. Select combatants and start combat!", "info")
    
    def _create_statistics_panel(self) -> None:
        """Create the statistics display panel."""
        self.stats_frame = tk.LabelFrame(self.main_frame, text="Combat Statistics", font=("Arial", 12, "bold"))
        self.stats_frame.pack(fill=tk.X)
        
        # Placeholder statistics
        stats_text = tk.Label(
            self.stats_frame,
            text="No combat statistics available. Start a combat to see statistics.",
            font=("Arial", 10),
            fg="gray"
        )
        stats_text.pack(pady=10)
    
    def _start_combat(self) -> None:
        """Start a combat encounter."""
        try:
            attacker = self.attacker_var.get()
            defender = self.defender_var.get()
            
            if not attacker or not defender:
                messagebox.showwarning("Combat Arena", "Please select both attacker and defender!")
                return
            
            if attacker == defender:
                messagebox.showwarning("Combat Arena", "Attacker and defender cannot be the same!")
                return
            
            self._log_message(f"🏟️ COMBAT STARTING: {attacker} vs {defender}", "combat")
            self._log_message("=" * 50, "separator")
            
            # Simulate combat (placeholder)
            self._simulate_combat(attacker, defender)
            
            if self.callbacks:
                self.callbacks.on_status_update(f"Combat started: {attacker} vs {defender}")
                
        except Exception as e:
            self.logger.error(f"Combat start error: {e}")
            self._log_message(f"❌ Error starting combat: {e}", "error")
    
    def _simulate_combat(self, attacker: str, defender: str) -> None:
        """Simulate a combat encounter (placeholder implementation)."""
        import random
        
        # Simulate combat rounds
        attacker_hp = 100
        defender_hp = 100
        round_num = 1
        
        while attacker_hp > 0 and defender_hp > 0 and round_num <= 10:
            self._log_message(f"--- Round {round_num} ---", "round")
            
            # Attacker's turn
            damage = random.randint(10, 25)
            defender_hp -= damage
            self._log_message(f"{attacker} attacks {defender} for {damage} damage! ({defender}: {max(0, defender_hp)}/100 HP)", "attack")
            
            if defender_hp <= 0:
                self._log_message(f"🏆 {attacker} wins the combat!", "victory")
                break
            
            # Defender's turn
            damage = random.randint(8, 20)
            attacker_hp -= damage
            self._log_message(f"{defender} attacks {attacker} for {damage} damage! ({attacker}: {max(0, attacker_hp)}/100 HP)", "attack")
            
            if attacker_hp <= 0:
                self._log_message(f"🏆 {defender} wins the combat!", "victory")
                break
            
            round_num += 1
        
        if round_num > 10:
            self._log_message("⏱️ Combat ended in a draw (maximum rounds reached)", "draw")
        
        self._log_message("=" * 50, "separator")
        self._log_message("Combat finished!", "info")
        
        if self.callbacks:
            self.callbacks.on_combat_finished({"winner": attacker if attacker_hp > 0 else defender if defender_hp > 0 else "Draw"})
    
    def _pause_combat(self) -> None:
        """Pause the current combat."""
        self._log_message("⏸️ Combat paused", "info")
        if self.callbacks:
            self.callbacks.on_status_update("Combat paused")
    
    def _stop_combat(self) -> None:
        """Stop the current combat."""
        self._log_message("🛑 Combat stopped", "info")
        if self.callbacks:
            self.callbacks.on_status_update("Combat stopped")
    
    def _clear_log(self) -> None:
        """Clear the combat log."""
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            self._log_message("Combat log cleared", "info")
    
    def _log_message(self, message: str, msg_type: str = "info") -> None:
        """Add a message to the combat log."""
        if not self.log_text:
            return
        
        self.log_text.config(state=tk.NORMAL)
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on message type
        colors = {
            "info": "black",
            "combat": "blue",
            "attack": "red",
            "victory": "green",
            "error": "red",
            "round": "purple",
            "separator": "gray",
            "draw": "orange"
        }
        
        color = colors.get(msg_type, "black")
        
        # Insert message
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Auto-scroll if enabled
        if self.config.auto_scroll_log:
            self.log_text.see(tk.END)
        
        self.log_text.config(state=tk.DISABLED)
    
    def refresh(self) -> None:
        """Refresh the combat arena."""
        self.logger.debug("Combat arena refreshed")
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the combat arena."""
        return {
            'current_combat': self.current_combat,
            'combat_history': len(self.combat_history),
            'attacker': self.attacker_var.get() if hasattr(self, 'attacker_var') else None,
            'defender': self.defender_var.get() if hasattr(self, 'defender_var') else None
        }
