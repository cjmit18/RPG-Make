"""Combat functions for the game.
This module contains the Combat class, which handles the combat mechanics between characters."""
import inventory_functions
import experience_functions
import character_creation
import items_list
import unit_test, random,logging
logging.basicConfig(level=logging.INFO)
log: logging = logging.getLogger()
class Combat:
    def __init__(self, character: character_creation, enemy: character_creation) -> None:
        """Initialize the Combat class."""
        self.character: character_creation = character
        self.enemy: character_creation = enemy
        self.turn: int = 1
    def turns(self, attacker: character_creation, defender: character_creation) -> str:
        """Handle the turns in combat between attacker and defender."""
        log.info("Testing combat settings...")
        log.info(f"{attacker.name} vs {defender.name}")
        log.info("Combat test initiated.")
        while True:
            user: str = "attack"
            if user == "attack" and attacker.speed >= defender.speed:
                log.info(f"{attacker.name} attacks {defender.name}!")
                self.damage_calc(attacker, defender)
                if defender.health <= 0:
                    return (f"{attacker.name} wins!")
                else:
                    log.info(f"{defender.name} attacks {attacker.name}!")
                    self.damage_calc(defender, attacker)
                    if attacker.health <= 0:
                        return (f"{defender.name} wins!")
            elif user == "attack" and attacker.speed < defender.speed:
                log.info(f"{defender.name} attacks {attacker.name}!")
                self.damage_calc(defender, attacker)
                if attacker.health <= 0:
                    return (f"{defender.name} wins!")
                else:
                    log.info(f"{attacker.name} attacks {defender.name}!")
                    self.damage_calc(attacker, defender)
                    if defender.health <= 0:
                        return (f"{attacker.name} wins!")
            elif user == "exit":
                return ("Exiting combat test.")
            else:
                log.info("Invalid command. Please enter 'attack' or 'exit'.")
            self.turn += 1
    
    def damage_calc(self, attacker: character_creation, defender: character_creation) -> None:
        """Calculate the damage dealt by the attacker to the defender."""
        random_float: float = random.uniform(1.0, 2.0)
        damage: int = attacker.attack - round(defender.defense / random_float)
        if damage > 0:
            defender.health = (defender.health - damage)
            log.info(f"{defender.name} takes {damage} damage!")
        else:
            log.info(f"{defender.name} blocks the attack!")
        if defender.health <= 0:
            if defender.__class__ == character_creation.Enemy:
                log.info(f"{defender.name} is defeated!")
                if random.randint(1, 10) > 5:
                    self.loot(attacker, defender)
                attacker.lvls.experience_calc(defender)
                return f"{attacker.name} gains {defender.lvls.experience} experience points!\n"
            elif defender.__class__ == character_creation.Player:
                log.info(f"{defender.name} is defeated!")
                return attacker.lvls.experience_calc(defender)
        elif attacker.health <= 0:
            if attacker.__class__ == character_creation.Enemy:
                log.info(f"{attacker.name} is defeated!")
                if random.randint(1, 10) > 5:
                    self.loot(defender, attacker)
                defender.lvls.experience_calc(attacker)
                return f"{defender.name} gains {attacker.lvls.experience} experience points!"
            elif attacker.__class__ == character_creation.Player:
                log.info(f"{attacker.name} is defeated!")
                return attacker.lvls.experience_calc(defender)
            else:
                if random.randint(1, 10) > 5:
                    self.loot(defender, attacker)
                defender.lvls.experience_calc(attacker)
                return f"{defender.name} gains {attacker.lvls.experience} experience points!\n"
        else:
            log.info(f"{attacker.name} has {attacker.health if attacker.health >= 1 else '0'} health left.")
            log.info(f"{defender.name} has {defender.health if defender.health >= 1 else '0'} health left.")
            self.turn += 1
    def loot(self, winner, loser) -> None:
        """Transfer all items from loser (enemy) to winner (player) after combat."""
        for item_data in loser.inventory.items.values():
            item: items_list.Item = item_data["item"]
            quantity: int = item_data["quantity"]
            loot_amount = unit_test.generate_random_number(1, quantity)
            winner.inventory.add_item(item, loot_amount)
            log.info(f"{winner.name} loots {loot_amount} {item.name}(s) from {loser.name}.")
        loser.inventory.drop_all()


if __name__ == "__main__":
    pass