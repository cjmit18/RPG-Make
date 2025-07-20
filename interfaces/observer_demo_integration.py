#!/usr/bin/env python3
"""
Observer Pattern Integration Example
====================================

Shows how to integrate the observer pattern with demo.py for improved
decoupling and automatic UI updates.
"""

from interfaces.observer_interfaces import GameEventType, GameEvent
from interfaces.ui_observer import UIObserver, GameEventPublisher


class ObserverDemoMixin:
    """
    Mixin that can be added to SimpleGameDemo to demonstrate observer pattern integration.
    This shows how to decouple UI updates from game logic.
    """
    
    def setup_observer_pattern(self):
        """Initialize the observer pattern for the demo."""
        # Create UI observer and connect it to the demo UI
        self.ui_observer = UIObserver(self.demo_ui)
        
        # The UI observer is now automatically subscribed to relevant events
        # and will handle UI updates when events are published
        
        self.log_message("🔍 Observer pattern initialized", "info")
    
    def learn_spell_dialog_with_observer(self):
        """
        Enhanced version of learn_spell_dialog that uses observer pattern.
        Compare this with the original version to see the improvements.
        """
        try:
            # Define spells with level requirements (same as original)
            spell_requirements = {
                "magic_missile": {"level": 1, "intelligence": 10},
                "heal": {"level": 2, "wisdom": 12},
                "fireball": {"level": 3, "intelligence": 15},
                "ice_shard": {"level": 4, "intelligence": 18},
                "lightning_bolt": {"level": 5, "intelligence": 20, "wisdom": 15}
            }

            if not hasattr(self.player, 'known_spells'):
                self.player.known_spells = []

            # Find spells available for learning (same logic as original)
            available_for_learning = []
            for spell, requirements in spell_requirements.items():
                if spell not in self.player.known_spells:
                    if self.player.level >= requirements["level"]:
                        can_learn = True
                        for stat, required_value in requirements.items():
                            if stat != "level":
                                current_value = getattr(self.player, stat, 0)
                                if current_value < required_value:
                                    can_learn = False
                                    break
                        if can_learn:
                            available_for_learning.append(spell)

            if not available_for_learning:
                self.log_message("No spells available to learn at your current level/stats!", "info")
                return

            # Learn the first available spell (same as original)
            spell_id = available_for_learning[0]
            self.player.known_spells.append(spell_id)
            
            # 🎯 OBSERVER PATTERN IMPROVEMENT:
            # Instead of manually calling self.update_progression_display(),
            # we publish an event and let the observer handle UI updates
            GameEventPublisher.publish_spell_learned(spell_id, source=self)
            
            # The UI observer will automatically:
            # 1. Update the progression display
            # 2. Log the learning message with proper formatting
            # 3. Handle any errors gracefully
            # 4. Update any other relevant UI components
            
            # No need for manual UI updates - the observer handles it all!

        except Exception as e:
            # 🎯 OBSERVER PATTERN IMPROVEMENT:
            # Instead of just logging locally, publish an error event
            GameEventPublisher.publish_error(f"Error learning spell: {e}", source=self)
    
    def learn_skill_dialog_with_observer(self):
        """
        Enhanced version of learn_skill_dialog that uses observer pattern.
        """
        try:
            skill_requirements = {
                "power_attack": {"level": 2, "strength": 15},
                "defensive_stance": {"level": 3, "constitution": 12},
                "quick_strike": {"level": 4, "dexterity": 18},
                "berserker_rage": {"level": 5, "strength": 20, "constitution": 15}
            }

            if not hasattr(self.player, 'known_skills'):
                self.player.known_skills = []

            available_for_learning = []
            for skill, requirements in skill_requirements.items():
                if skill not in self.player.known_skills:
                    if self.player.level >= requirements["level"]:
                        can_learn = True
                        for stat, required_value in requirements.items():
                            if stat != "level":
                                current_value = getattr(self.player, stat, 0)
                                if current_value < required_value:
                                    can_learn = False
                                    break
                        if can_learn:
                            available_for_learning.append(skill)

            if not available_for_learning:
                self.log_message("No skills available to learn at your current level/stats!", "info")
                return

            skill_id = available_for_learning[0]
            self.player.known_skills.append(skill_id)
            
            # 🎯 OBSERVER PATTERN IMPROVEMENT: Event-driven UI updates
            GameEventPublisher.publish_skill_learned(skill_id, source=self)

        except Exception as e:
            GameEventPublisher.publish_error(f"Error learning skill: {e}", source=self)
    
    def gain_test_xp_with_observer(self):
        """
        Enhanced XP gain that demonstrates stat change events.
        """
        try:
            old_level = self.player.level
            old_xp = self.player.experience
            
            # Add XP (same logic as original)
            xp_gain = 100
            self.player.experience += xp_gain
            
            # 🎯 OBSERVER PATTERN IMPROVEMENT: Publish XP change event
            GameEventPublisher.publish_stat_change('experience', old_xp, self.player.experience, source=self)
            
            # Check for level up
            if self.player.level > old_level:
                # 🎯 OBSERVER PATTERN IMPROVEMENT: Publish level up event
                GameEventPublisher.publish_level_up(self.player.level, source=self)
            
            # The observer will automatically handle all UI updates!

        except Exception as e:
            GameEventPublisher.publish_error(f"Error gaining XP: {e}", source=self)
    
    def equip_item_with_observer(self, item):
        """
        Enhanced item equipping that publishes events.
        """
        try:
            # Perform the equipment logic (same as original)
            success = self.player.equip_weapon(item) if hasattr(item, 'item_type') and item.item_type == 'weapon' else False
            
            if success:
                # 🎯 OBSERVER PATTERN IMPROVEMENT: Publish equipment event
                item_name = getattr(item, 'name', str(item))
                GameEventPublisher.publish_inventory_change('equip', item_name, source=self)
                
                # Also publish specific equipment event if needed
                from interfaces.observer_interfaces import GameEvent, GameEventType, event_manager
                equip_event = GameEvent(
                    GameEventType.ITEM_EQUIPPED,
                    {'item_name': item_name, 'item': item},
                    source=self
                )
                event_manager.publish(equip_event)
            else:
                GameEventPublisher.publish_error("Failed to equip item", source=self)

        except Exception as e:
            GameEventPublisher.publish_error(f"Error equipping item: {e}", source=self)


# 🎯 BENEFITS OF OBSERVER PATTERN INTEGRATION:

"""
1. **Decoupled UI Updates**: 
   - Game logic doesn't need to know about UI components
   - UI updates happen automatically when events occur
   - Easy to add new UI components that respond to events

2. **Centralized Event Handling**:
   - All events flow through the observer system
   - Consistent logging and error handling
   - Easy to add new event types

3. **Improved Maintainability**:
   - Separation of concerns between game logic and UI
   - Easier to test game logic without UI dependencies
   - Less code duplication

4. **Extensibility**:
   - New observers can be added easily
   - Events can trigger multiple actions automatically
   - Plugin architecture becomes possible

5. **Integration with Existing Hooks**:
   - Works alongside the existing event bus
   - No need to rewrite existing code
   - Gradual migration path

6. **Error Handling**:
   - Centralized error event handling
   - UI observers can respond to errors gracefully
   - Better user experience

USAGE EXAMPLE:

# In demo.py __init__ method:
self.setup_observer_pattern()

# Replace existing methods:
self.learn_spell_dialog = self.learn_spell_dialog_with_observer
self.learn_skill_dialog = self.learn_skill_dialog_with_observer
# etc.

# Or integrate gradually:
# Keep existing methods but add observer events for new features
"""
