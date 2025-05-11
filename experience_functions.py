import combat_settings
import character_creation
class Levels:
    def __init__(self, lvl = 1, experience = 0):
        self.lvl = lvl
        self.experience = experience
    def __str__(self):
        return f"Level: {self.lvl}, Experience: {self.experience}"
    def __repr__(self):
        return f"Levels(lvl={self.lvl}, experience={self.experience})"
    def add_experience(self, exp):
        if not isinstance(exp, int):
            raise TypeError("Experience must be an integer.")
        else:
            self.experience += exp
        if self.experience >= self.required_experience():
            self.level_up()
    def level_up(self):
        while self.experience >= self.required_experience():
            self.experience -= self.required_experience()
            self.lvl += 1
            print(f"Level up! You are now level {self.lvl}!")
        else:
            print(f"You have {self.experience} experience points left.")
            print(f"Next level requires {self.required_experience()} experience points.")
    def required_experience(self):
        return (self.lvl * 100) * 2
    def change_level(self, new_level):
        if new_level < 1:
            raise ValueError("Level must be at least 1.")
        self.lvl = new_level
        print(f"Level changed to {self.lvl}.")
    def reset_experience(self):
        self.experience = 0
        print("Experience points have been reset.")
    def reset_level(self):
        self.lvl = 1
        print("Level has been reset to 1.")
    def reset(self):
        self.reset_experience()
        self.reset_level()
        print("Experience and level have been reset.")
    def experience_calc(self, enemy):
       if isinstance(enemy, character_creation.Enemy) or isinstance(enemy, character_creation.NPC):
            if enemy.lvl.experience > 0:
                self.add_experience(enemy.lvl.experience)