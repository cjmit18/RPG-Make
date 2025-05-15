import inventory_functions
import experience_functions
import Item_functions
class Character():
    def __init__(self, name: str = "Template", level: int = 1, experience: int = 0):
        self.name = name
        self.attack = 10
        self.defense = 5
        self.speed = 10
        self.health = 100
        self.mana = 100
        self.stamina = 100
        self.lvl = experience_functions.Levels(self, level, experience)
        self.inventory = inventory_functions.Inventory(self)
    def __str__(self):
        return (f"{self.__class__.__name__}:\n"
                f"{self.lvl}\n"
                f"{"-"*10}\n"
                f"Attack: {self.attack} ({self.inventory.equipped_items['weapon'].attack_power if self.inventory.equipped_items['weapon'] else 0})\n"
                f"Defense: {self.defense} ({self.inventory.equipped_items['armor'].defense_power if self.inventory.equipped_items['armor'] else 0})\n"
                f"Speed: {self.speed}\n"
                f"Health: {self.health}\n"
                f"Mana: {self.mana}\n"
                f"Stamina: {self.stamina}\n"
                f"{"-"*10}\n"
                f"{self.inventory}")
    def __repr__(self):
        return (f"{self.__class__.__name__}(") + \
               (f"name={self.name}, lvl={self.lvl}, attack={self.attack}, defense={self.defense}, ") + \
               (f"speed={self.speed}, health={self.health}, mana={self.mana}, ") + \
               (f"stamina={self.stamina}, inventory={self.inventory})")    
    def __eq__(self, other):
        if isinstance(other, Character):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        self._name = name
    @property
    def lvl(self):
        return self._lvl
    @lvl.setter
    def lvl(self, lvl):
        if not isinstance(lvl, experience_functions.Levels):
            raise TypeError("Level must be a Levels object.")
        self._lvl = lvl
    @property
    def attack(self):
        if self.inventory.equipped_items["weapon"] is not None:
            return self._attack + self.inventory.equipped_items["weapon"].attack_power
        return self._attack
    
    @attack.setter
    def attack(self, attack):
        if not isinstance(attack, int):
            raise TypeError("Attack must be an integer.")
        elif attack < 0:
            self._attack = 0
        else:
            self._attack = attack
    @property
    def defense(self):
        if self.inventory.equipped_items["armor"] is not None:
            return self._defense + self.inventory.equipped_items["armor"].defense_power
        return self._defense
    @defense.setter
    def defense(self, defense):
        if not isinstance(defense, int):
            raise TypeError("Defense must be an integer.")
        elif defense < 1:
            self.defense = 1
        else:
            self._defense = defense
    @property
    def speed(self):
        if self.inventory.equipped_items["consumable"] is not None and self.inventory.equipped_items["consumable"].effect == "speed:":
                return self._speed + self.inventory.equipped_items["consumable"].amount
        else:
            return self._speed
    @speed.setter
    def speed(self, speed):
        if not isinstance(speed, int):
            raise TypeError("Speed must be an integer.")
        elif speed < 0:
            self._speed = 0
        else:
            self._speed = speed
    @property
    def health(self):
        if self.inventory.equipped_items["consumable"] is not None and self.inventory.equipped_items["consumable"].effect == "health:":
            return self._health + self.inventory.equipped_items["consumable"].amount
        else:
            return self._health
    @health.setter
    def health(self, health):
        if not isinstance(health, int):
            raise TypeError("Health must be an integer.")
        elif health < 0:
            self._health = 0
        else:
            self._health = health
    @property
    def mana(self):
        if self.inventory.equipped_items["consumable"] is not None and self.inventory.equipped_items["consumable"].effect == "mana:":
            return self._mana + self.inventory.equipped_items["consumable"].amount
        else:
            return self._mana
    @mana.setter
    def mana(self, mana):
        if not isinstance(mana, int):
            raise TypeError("Mana must be an integer.")
        elif mana < 0:
            self._mana = 0
        else:
            self._mana = mana
    @property
    def stamina(self):
        if self.inventory.equipped_items["consumable"] is not None and self.inventory.equipped_items["consumable"].effect == "stamina:":
            return self._stamina + self.inventory.equipped_items["consumable"].amount
        else:
            return self._stamina
    @stamina.setter
    def stamina(self, stamina):
        if not isinstance(stamina, int):
            raise TypeError("Stamina must be an integer.")
        elif stamina < 0:
            self._stamina = 0
        else:
            self._stamina = stamina
    @property
    def inventory(self):
        return self._inventory
    @inventory.setter
    def inventory(self, inventory):
        if not isinstance(inventory, inventory_functions.Inventory):
            raise TypeError("Inventory must be an Inventory object.")
        self._inventory = inventory
class NPC(Character):
    def __init__(self, name: str = "NPC", level: int = 1):
        super().__init__(name, level)
    def __str__(self):
        return super().__str__()
    def __repr__(self):
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, NPC):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class Enemy(Character):
    def __init__(self, name: str = "Enemy", level: int = 1):
        super().__init__(name, level)
        self.attack = self.lvl.lvl * 10
        self.defense = self.lvl.lvl * 5
        self.speed = self.lvl.lvl * 3
        self.health = self.lvl.lvl * 50
        self.mana = self.lvl.lvl * 20
        self.stamina = self.lvl.lvl * 30
    def __str__(self):
        return super().__str__()
    def __repr__(self):
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, Enemy):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class Player(Character):
    def __init__(self, name: str = "Hero", level: int = 1):
        super().__init__(name, level)
        self.attack = 15 * self.lvl.lvl
        self.defense = 10 * self.lvl.lvl
        self.speed = 5 * self.lvl.lvl
        self.health = 100 + (self.lvl.lvl * 20)
        self.mana = 100 + (self.lvl.lvl * 10)
        self.stamina = 100 + (self.lvl.lvl * 15)
    def __str__(self):
        return super().__str__()
    def __repr__(self):
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, Player):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False