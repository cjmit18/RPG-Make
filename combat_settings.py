import main
class Combat:
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
    def user_input(self, prompt: str = str) -> str:
        return input(prompt)
    def turns(self):
        print("Testing combat settings...")
        print(f"{self.character.get_name()} vs {self.enemy.get_name()}")
        print("Combat test initiated.")
        while True:
            user = self.user_input("Attack, Exit: ").lower()
            if user == "attack" and self.character.get_speed() >= self.enemy.get_speed():
                print(f"{self.character.get_name()} attacks {self.enemy.get_name()}!")
                self.damage_calc(self.character, self.enemy)
                if self.enemy.get_health() <= 0:
                    print(f"{self.character.get_name()} wins!")
                    break
            elif user == "attack" and self.character.get_speed() < self.enemy.get_speed():
                print(f"{self.enemy.get_name()} attacks {self.character.get_name()}!")
                self.damage_calc(self.enemy, self.character)
                if self.character.get_health() <= 0:
                    print(f"{self.enemy.get_name()} wins!")
                    break
            elif user == "exit":
                print("Exiting combat test.")
                break
            else:
                print("Invalid command. Please enter 'attack' or 'exit'.")
    
    def damage_calc(self, attacker, defender):
        damage = attacker.get_attack() - defender.get_defense()
        if damage > 0:
            defender.set_health(defender.get_health() - damage)
            print(f"{defender.get_name()} takes {damage} damage!")
            print(f"{defender.get_name()} has {defender.get_health() if defender.get_health() >= 1 else "0"}  health left.")
        else:
            print(f"{defender.get_name()} blocks the attack!")
        if defender.get_health() <= 0:
            print(f"{defender.get_name()} is defeated!")
if __name__ == "__main__":
    character = main.character_creation.player("Hero")
    enemy = main.character_creation.enemy("Monster")
    combat = Combat(character, enemy)
    enemy.set_defense(6)
    enemy.set_health(10)
    combat.turns()