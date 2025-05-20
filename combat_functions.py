"""Combat functions for the game.
This module contains the Combat class, which handles the combat mechanics between characters."""
import character_creation
from typing import List, Dict, Tuple
import gen
import random
import logging
logging.basicConfig(level=logging.INFO)
log: logging = logging.getLogger()
class Combat:
    """Combat class to handle combat between characters."""
    def __init__(self, character: character_creation, enemy: character_creation) -> None:
        """Initialize the Combat class."""
        self.character: character_creation = character
        self.enemy: character_creation = enemy
        self.turn_count: int = 1
    def start_combat_loop(self) -> None:
        """Start the combat loop."""
        for attacker, defender in self.get_turn_order():
            action = self.get_action(attacker)
            result = self.resolve_action(action, attacker, defender)
            # Handle the result of the action
            if self.check_defeat(defender):
                return f"{attacker.name} wins!"
            self.turn_count += 1
    def get_turn_order(self) -> List[Tuple['character_creation.Player', 'character_creation.Player']]:
        """Determine the turn order based on speed."""
        # Get the turn order based on speed
        if self.character.speed >= self.enemy.speed:
            return [(self.character, self.enemy), (self.enemy, self.character)]
        return [(self.enemy, self.character), (self.character, self.enemy)]
    def get_action(self, attacker: character_creation) -> str:
        """Get the action for the attacker."""
        # Placeholder for user input or AI decision
        if isinstance(attacker, character_creation.Player):
            action = input(f"{attacker.name}, choose your action (attack/defend): ").strip().lower()
        else:
            action = "attack"
        return action
    def resolve_action(self, action: str, attacker: character_creation, defender: character_creation) -> None:
        """Resolve the action taken by the attacker."""
        if action == "attack":
            self.calculate_dmg(attacker, defender)
        elif action == "defend":
            # Placeholder for defend logic
            log.info(f"{attacker.name} defends!")
        elif action == "cast":
            # Placeholder for cast logic
            log.info(f"{attacker.name} casts a spell!")
        elif action == "item":
            # Placeholder for item logic
            log.info(f"{attacker.name} uses an item!")
        elif action == "run":
            # Placeholder for run logic
            log.info(f"{attacker.name} runs away!")
        else:
            log.info("Invalid action. Please choose 'attack' or 'defend'.")
   #Figure out how to make this work with the rest of the code
    def turns(self, attacker: character_creation, defender: character_creation) -> str:
        """Handle the turns in combat between attacker and defender."""
        log.info("Testing combat settings...")
        log.info(f"{attacker.name} vs {defender.name}")
        log.info("Combat test initiated.")
        while True:
            user: str = "attack"
            if user == "attack" and attacker.speed >= defender.speed:
                log.info(f"{attacker.name} attacks {defender.name}!")
                self.calculate_dmg(attacker, defender)
                if defender.health <= 0:
                    return (f"{attacker.name} wins!")
                else:
                    log.info(f"{defender.name} attacks {attacker.name}!")
                    self.calculate_dmg(defender, attacker)
                    if attacker.health <= 0:
                        return (f"{defender.name} wins!")
            elif user == "attack" and attacker.speed < defender.speed:
                log.info(f"{defender.name} attacks {attacker.name}!")
                self.calculate_dmg(defender, attacker)
                if attacker.health <= 0:
                    return (f"{defender.name} wins!")
                else:
                    log.info(f"{attacker.name} attacks {defender.name}!")
                    self.calculate_dmg(attacker, defender)
                    if defender.health <= 0:
                        return (f"{attacker.name} wins!")
            elif user == "exit":
                return ("Exiting combat test.")
            else:
                log.info("Invalid command. Please enter 'attack' or 'exit'.")
            self.turn_count += 1
    
    def calc_dmg(self, attacker: character_creation, defender: character_creation) -> None:
        """Calculate the damage dealt by the attacker to the defender."""
        multiplier: float = gen.generate_random_float(0.8, 1.2) # Random multiplier for damage
        base__dmg: int = max(0, attacker.attack_power - defender.defense * .05) * multiplier # Base damage calculation
        if random.random() < .1: # 10% chance to deal critical damage
            base__dmg *= 2
            crit_text: str = "Critical Hit!" # Critical hit message
        else:
            crit_text: str = "" # Normal hit
        if hasattr(defender, "defending") and defender.defending:
            base__dmg *= 0.5 # Halve damage if defending
        defender.health -= base__dmg # Subtract damage from defender's health
        return f"{attacker.name} deals {base__dmg} damage to {defender.name}. {crit_text}"
    def check_defeat(self, character: character_creation) -> bool:
        """Check if the character is defeated."""
        if character.health <= 0:
            return True
        return False
    
    def loot(self, winner, loser) -> None:
        """Transfer all items from loser (enemy) to winner (player) after combat."""
        for item_data in loser.inventory.items.values():
            item = item_data["item"]
            quantity: int = gen.generate_random_number(1,item_data["quantity"])
            winner.inventory.add_item(item, quantity)
            log.info(f"{winner.name} loots {quantity} {item.name}(s) from {loser.name}.")
        loser.inventory.drop_all()


if __name__ == "__main__":
    pass