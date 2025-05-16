import inventory_functions
import experience_functions
import character_creation
import Item_functions
import main, random,logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
class Combat:
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
    def user_input(self, prompt: str = "") -> str:
        return input(prompt)
    def turns(self, attacker, defender):
        log.info("Testing combat settings...")
        log.info(f"{attacker.name} vs {defender.name}")
        log.info("Combat test initiated.")
        while True:
            user = "attack" #self.user_input("Attack, Exit: ").lower()
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
    
    def damage_calc(self, attacker, defender):
        self.turn = 1
        random_float = random.uniform(1.0, 2.0)
        damage = attacker.attack - round(defender.defense / random_float)
        if damage > 0:
            defender.health = (defender.health - damage)
            log.info(f"{defender.name} takes {damage} damage!")
        else:
            log.info(f"{defender.name} blocks the attack!")
        if defender.health <= 0:
            if defender.__class__ == character_creation.Enemy:
                log.info(f"{defender.name} is defeated!")
                if random.randint(1, 10) > 5:
                    log.info(f"{attacker.name} found a health potion!")
                    attacker.inventory.add_item(Item_functions.Items.generate(lvl = 2,item_type = "consumable",effect = "health"), main.generate_random_number(1, 4))
                return attacker.lvl.experience_calc(defender), f"{attacker.name} gains {defender.lvl.experience} experience points!"
            elif defender.__class__ == character_creation.Player:
                log.info(f"{defender.name} is defeated!")
                return attacker.lvl.experience_calc(defender)
        elif attacker.health <= 0:
            if attacker.__class__ == character_creation.Enemy:
                log.info(f"{attacker.name} is defeated!")
                if random.randint(1, 10) > 5:
                    log.info(f"{defender.name} found a health potion!")
                    defender.inventory.add_item(Item_functions.Items.generate(lvl = 2,item_type = "consumable",effect = "health"), main.generate_random_number(1, 4))
                return defender.lvl.experience_calc(attacker), f"{defender.name} gains {attacker.lvl.experience} experience points!"
            elif attacker.__class__ == character_creation.Player:
                log.info(f"{attacker.name} is defeated!")
                return attacker.lvl.experience_calc(defender)
            else:
                if random.randint(1, 10) > 5:
                    log.info(f"{defender.name} found a health potion!")
                    defender.inventory.add_item(Item_functions.Items.generate(lvl = 2,item_type = "consumable",effect = "health"), main.generate_random_number(1, 4))
                return f"{attacker.name} is defeated!\n\
                {defender.name} gains {attacker.lvl.experience} experience points!\n\
                {defender.lvl.experience_calc(attacker)}"
        else:
            log.info(f"{attacker.name} has {attacker.health if attacker.health >= 1 else '0'} health left.")
            log.info(f"{defender.name} has {defender.health if defender.health >= 1 else '0'} health left.")
            self.turn += 1
            
if __name__ == "__main__":
    pass