"""
Demo AI Integration Example
==========================

Example showing how to integrate the AI system into demo.py for responsive enemy combat.
This file shows the changes needed in demo.py to enable AI functionality.
"""

# Example integration code for demo.py

# 1. ADD THESE IMPORTS AT THE TOP OF demo.py:
"""
from game_sys.ai.demo_integration import (
    create_ai_integration, setup_enemy_ai, update_enemy_ai, get_ai_status
)
"""

# 2. ADD THIS TO __init__ method in SimpleGameDemo class:
"""
def __init__(self):
    # ...existing code...
    
    # Initialize AI system
    self.ai_manager = None
    self.ai_enabled = True
    self.ai_update_timer = 0.0
"""

# 3. ADD THIS TO setup_game_state method:
"""
def setup_game_state(self):
    # ...existing code...
    
    # Initialize AI system
    if self.ai_enabled:
        try:
            self.ai_manager = create_ai_integration(self.combat_service)
            self.log_message("AI system initialized!", "info")
        except Exception as e:
            self.log_message(f"AI system failed to initialize: {e}", "combat")
            self.ai_enabled = False
"""

# 4. MODIFY spawn_enemy method to include AI:
"""
def spawn_enemy(self):
    enemy_types = ["goblin", "orc", "dragon"]
    enemy_type = random.choice(enemy_types)

    logger.info(f"Spawning {enemy_type}")

    # Create enemy with random stats
    self.enemy = create_character_with_random_stats(enemy_type)

    if self.enemy:
        logger.info(f"Created enemy: {self.enemy.name}")
        
        # Set up AI control for the enemy
        if self.ai_enabled and self.ai_manager:
            try:
                # Choose behavior based on enemy type
                behavior_type = "basic_enemy"
                if "dragon" in enemy_type.lower():
                    behavior_type = "aggressive_enemy"
                elif "goblin" in enemy_type.lower():
                    behavior_type = "defensive_enemy"
                
                self.enemy = setup_enemy_ai(self.ai_manager, self.enemy, behavior_type)
                self.log_message(f"AI enabled for {self.enemy.name} ({behavior_type})", "info")
            except Exception as e:
                self.log_message(f"AI setup failed: {e}", "combat")
        
        # ...rest of existing spawn_enemy code...
"""

# 5. ADD THIS NEW METHOD FOR AI UPDATES:
"""
def update_ai_enemies(self):
    '''Update AI for all enemy actors.'''
    if not self.ai_enabled or not self.ai_manager or not hasattr(self, 'player'):
        return
        
    try:
        # Get AI actions
        ai_actions = update_enemy_ai(self.ai_manager, self.player)
        
        # Process and display AI actions
        for action_data in ai_actions:
            enemy = action_data['enemy']
            action = action_data['action']
            result = action_data['result']
            
            if result['success']:
                # Display AI action in combat log
                self.log_message(result['message'], "combat")
                
                # Create visual effects for AI actions
                if result['type'] == 'attack':
                    self.create_particles(150, 200, "red", 10)
                elif result['type'] == 'cast_spell':
                    color = "orange" if "fire" in result.get('spell_id', '') else "cyan"
                    self.create_particles(150, 200, color, 15)
                elif result['type'] == 'heal':
                    self.create_particles(450, 200, "green", 12)
                    
        # Update displays if any actions occurred
        if ai_actions:
            self.update_char_info()
            self.update_enemy_info()
            self.draw_game_state()
            
    except Exception as e:
        self.log_message(f"AI update error: {e}", "combat")
"""

# 6. ADD AI UPDATE CALLS TO COMBAT METHODS:
"""
def attack(self):
    # ...existing attack code...
    
    # After player attack, trigger AI response
    if result['success']:
        # ...existing code...
        
        # Give AI a chance to respond
        self.root.after(1500, self.update_ai_enemies)  # AI responds after 1.5 seconds
"""

# 7. ADD AI STATUS DISPLAY TO COMBAT TAB:
"""
def setup_combat_tab(self):
    # ...existing code...
    
    # Add AI status display
    ai_status_frame = tk.Frame(self.combat_tab, bg="gray")
    ai_status_frame.pack(fill=tk.X, padx=10, pady=5)
    
    self.ai_status_label = tk.Label(
        ai_status_frame,
        text="AI Status: Initializing...",
        bg="gray",
        fg="white",
        font=("Arial", 10)
    )
    self.ai_status_label.pack(anchor="w")
    
    # AI control buttons
    ai_control_frame = tk.Frame(self.combat_tab, bg="gray")
    ai_control_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ai_buttons = [
        ("Toggle AI", self.toggle_ai),
        ("AI Status", self.show_ai_status),
        ("Force Easy", lambda: self.force_difficulty("easy")),
        ("Force Hard", lambda: self.force_difficulty("hard"))
    ]
    
    for text, command in ai_buttons:
        btn = tk.Button(ai_control_frame, text=text, command=command)
        btn.pack(side=tk.LEFT, padx=5)
"""

# 8. ADD THESE NEW METHODS FOR AI CONTROL:
"""
def toggle_ai(self):
    '''Toggle AI on/off.'''
    if self.ai_manager:
        self.ai_enabled = not self.ai_enabled
        status = "enabled" if self.ai_enabled else "disabled"
        self.log_message(f"AI {status}", "info")
        self.update_ai_status_display()
    else:
        self.log_message("AI system not available", "combat")

def show_ai_status(self):
    '''Show detailed AI status.'''
    if self.ai_manager:
        status = get_ai_status(self.ai_manager)
        self.log_message(status, "info")
    else:
        self.log_message("AI system not available", "combat")

def force_difficulty(self, difficulty):
    '''Force a specific difficulty level.'''
    if self.ai_manager:
        self.ai_manager.force_difficulty(difficulty)
        self.log_message(f"Difficulty forced to {difficulty}", "info")
        self.update_ai_status_display()
    else:
        self.log_message("AI system not available", "combat")

def update_ai_status_display(self):
    '''Update AI status display.'''
    if hasattr(self, 'ai_status_label') and self.ai_manager:
        try:
            status = "AI: "
            if not self.ai_enabled:
                status += "DISABLED"
            else:
                difficulty_info = self.ai_manager.get_difficulty_info()
                status += f"{difficulty_info['current_level'].upper()}"
                performance = difficulty_info['performance']
                status += f" | Battles: {performance['total_battles']}"
                status += f" | Win Rate: {performance['win_rate']:.0%}"
                
            self.ai_status_label.config(text=status)
        except Exception as e:
            self.ai_status_label.config(text=f"AI Status Error: {e}")
"""

# 9. MODIFY BATTLE RESULT RECORDING:
"""
# In your combat methods, add battle result recording:
def cast_fireball(self):
    # ...existing code...
    
    if result['defeated']:
        # Record battle result for AI
        if self.ai_manager:
            # Calculate battle metrics
            battle_duration = time.time() - getattr(self, 'battle_start_time', time.time())
            damage_dealt = result.get('damage', 0)
            damage_received = getattr(self, 'damage_received_this_battle', 0)
            
            self.ai_manager.record_battle_result(
                player_won=True,
                battle_duration=battle_duration,
                damage_dealt=damage_dealt,
                damage_received=damage_received
            )
            self.update_ai_status_display()
"""

# 10. ADD PERIODIC AI UPDATES:
"""
def run(self):
    '''Run the demo with AI updates.'''
    logger.info("Starting demo")

    # Add quit button to main window
    quit_btn = tk.Button(self.root, text="Quit Game", command=self.quit)
    quit_btn.pack(side=tk.BOTTOM, pady=5)

    # Start AI update loop
    if self.ai_enabled:
        self.schedule_ai_update()

    self.root.mainloop()
    logger.info("Demo ended")

def schedule_ai_update(self):
    '''Schedule periodic AI updates.'''
    if self.ai_enabled and self.ai_manager:
        self.update_ai_enemies()
        self.update_ai_status_display()
        
    # Schedule next update
    self.root.after(3000, self.schedule_ai_update)  # Update every 3 seconds
"""

# SUMMARY OF INTEGRATION:
"""
This integration adds:
1. Responsive enemy AI that makes decisions based on game state
2. Dynamic difficulty scaling based on player performance  
3. Visual feedback for AI actions
4. AI control interface in the combat tab
5. Performance tracking and battle result recording
6. Multiple AI behavior types (basic, aggressive, defensive)
7. Automatic difficulty adjustment to maintain challenge

The AI system uses the same service layer APIs that the player uses,
ensuring consistent game mechanics and balance.
"""
