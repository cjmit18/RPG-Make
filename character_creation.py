import inventory
class character():
    def __init__(self, name: str = str):
        self.name = name
        self.lvl = 1
        self.attack = 10
        self.defense = 10
        self.speed = 10
        self.health = 100
        self.mana = 100
        self.stamina = 100
        self.experience = 0
        self.inventory = inventory.inventory(self.name)
    def __str__(self):
        return f"{self.name}:\nLvl: {self.lvl}\nattack: {self.attack}\ndefense: {self.defense}\nspeed: {self.speed} \nhealth: {self.health}\nmana: {self.mana}\nstamina: {self.stamina}\nexperience: {self.experience} \nInventory: {self.inventory.get_items()}"
    def __repr__(self):
        return f"Character Template: {self.name}:\nLvl: {self.lvl}\nattack: {self.attack}\ndefense: {self.defense}\nspeed: {self.speed} \nhealth: {self.health}\nmana: {self.mana}\nstamina: {self.stamina}\nexperience: {self.experience} \nInventory: {self.inventory.get_items()}"
    def __eq__(self, other):
        if isinstance(other, character):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    def set_name(self, name: str = str) -> None:
        self.name = name
    def set_lvl(self, lvl: int = int) -> None:
        self.lvl = lvl
    def set_attack(self, attack: int = int) -> None:
        self.attack = attack
    def set_defense(self, defense: int = int) -> None:
        self.defense = defense
    def set_speed(self, speed: int = int) -> None:
        self.speed = speed
    def set_health(self, health: int = int) -> None:
        self.health = health
    def set_mana(self, mana: int = int) -> None:
        self.mana = mana
    def set_stamina(self, stamina: int = int) -> None:
        self.stamina = stamina
    def set_experience(self, experience: int = int) -> None:
        self.experience = experience
    def get_name(self) -> str:
        return self.name
    def get_lvl(self) -> int:
        return self.lvl
    def get_attack(self) -> int:
        return self.attack
    def get_defense(self) -> int:
        return self.defense
    def get_speed(self) -> int:
        return self.speed
    def get_health(self) -> int:
        return self.health
    def get_mana(self) -> int:
        return self.mana
    def get_stamina(self) -> int:
        return self.stamina
    def get_experience(self) -> int:
        return self.experience
    def get_inventory(self) -> inventory.inventory:
        return self.inventory
    @property
    def inventory(self):
        return self._inventory
    @inventory.setter
    def inventory(self, value):
        self._inventory = value
class npc(character):
    def __init__(self, name: str = str):
        super().__init__(name)
    def __str__(self):
        return f"{self.name}:\nLvl: {self.lvl}\nattack: {self.attack}\ndefense: {self.defense}\nspeed: {self.speed} \nhealth: {self.health}\nmana: {self.mana}\nstamina: {self.stamina}\nexperience: {self.experience}"
    def __repr__(self):
        return f"NPC: {self.name}:\nLvl: {self.lvl}\nattack: {self.attack}\ndefense: {self.defense}\nspeed: {self.speed} \nhealth: {self.health}\nmana: {self.mana}\nstamina: {self.stamina}\nexperience: {self.experience}"
    def __eq__(self, other):
        if isinstance(other, npc):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class enemy(character):
    def __init__(self, name: str = str ):
        super().__init__(name)
    def __str__(self):
        return f"{self.name}:\nLvl: {self.lvl}\nattack: {self.attack}\ndefense: {self.defense}\nspeed: {self.speed} \nhealth: {self.health}\nmana: {self.mana}\nstamina: {self.stamina}\nexperience: {self.experience}"
    def __repr__(self):
        return f"Enemy: {self.name}:\nLvl: {self.lvl}\nattack: {self.attack}\ndefense: {self.defense}\nspeed: {self.speed} \nhealth: {self.health}\nmana: {self.mana}\nstamina: {self.stamina}\nexperience: {self.experience}"
    def __eq__(self, other):
        if isinstance(other, enemy):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class player(character):
    def __init__(self, name: str = str):
        super().__init__(name)
    def __str__(self):
        return f"{self.name}:\nLvl: {self.lvl}\nattack: {self.attack}\ndefense: {self.defense}\nspeed: {self.speed} \nhealth: {self.health}\nmana: {self.mana}\nstamina: {self.stamina}\nexperience: {self.experience}"
    def __repr__(self):
        return f"Player: {self.name}:\nLvl: {self.lvl}\nattack: {self.attack}\ndefense: {self.defense}\nspeed: {self.speed} \nhealth: {self.health}\nmana: {self.mana}\nstamina: {self.stamina}\nexperience: {self.experience}"
    def __eq__(self, other):
        if isinstance(other, player):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False