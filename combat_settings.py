import inventory_functions
import experience_functions
import character_creation
class Combat:
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
    def user_input(self, prompt: str = "") -> str:
        return input(prompt)
    def turns(self, attacker, defender):
        print("Testing combat settings...")
        print(f"{attacker.name} vs {defender.name}")
        print("Combat test initiated.")
        while True:
            user = self.user_input("Attack, Exit: ").lower()
            if user == "attack" and attacker.speed >= defender.speed:
                print(f"{attacker.name} attacks {defender.name}!")
                self.damage_calc(attacker, defender)
                if defender.health <= 0:
                    print(f"{attacker.name} wins!")
                    break
                else:
                    print(f"{defender.name} attacks {attacker.name}!")
                    self.damage_calc(defender, attacker)
                    if attacker.health <= 0:
                        print(f"{defender.name} wins!")
                        break
            elif user == "attack" and attacker.speed < defender.speed:
                print(f"{defender.name} attacks {attacker.name}!")
                self.damage_calc(defender, attacker)
                if attacker.health <= 0:
                    print(f"{defender.name} wins!")
                else:
                    print(f"{attacker.name} attacks {defender.name}!")
                    self.damage_calc(attacker, defender)
                    if defender.health <= 0:
                        print(f"{attacker.name} wins!")
                        break
            elif user == "exit":
                print("Exiting combat test.")
                break
            else:
                print("Invalid command. Please enter 'attack' or 'exit'.")
    
    def damage_calc(self, attacker, defender):
        damage = attacker.attack - defender.defense
        if damage > 0:
            defender.health = (defender.health - damage)
            print(f"{defender.name} takes {damage} damage!")
        else:
            print(f"{defender.name} blocks the attack!")
        if defender.health <= 0:
            print(f"{defender.name} is defeated!")
            print(f"{attacker.name} gains {defender.lvl.experience} experience points!")
            attacker.lvl.experience_calc(defender)
        elif attacker.health <= 0:
            print(f"{attacker.name} is defeated!")
            print(f"{defender.name} gains {attacker.lvl.experience} experience points!")
            defender.lvl.experience_calc(attacker)
        else:
            print(f"{attacker.name} has {attacker.health if attacker.health >= 1 else "0"} health left.")
            print(f"{defender.name} has {defender.health if defender.health >= 1 else "0"} health left.")
if __name__ == "__main__":
    pass