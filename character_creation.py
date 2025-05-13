import inventory_functions
import experience_functions
import Item_functions
class Character():
    def __init__(self, name: str = "Template", level: int = 1, experience: int = 0):
        self.name = name
        self.attack = 10
        self.defense = 10
        self.speed = 10
        self.health = 100
        self.mana = 100
        self.stamina = 100
        self.lvl = experience_functions.Levels(name, level, experience)
        self.inventory = inventory_functions.Inventory(self.name)
    def __str__(self):
        return (f"{self.__class__.__name__}:\n"
                f"{self.lvl}\n"
                f"{"-"*10}\n"
                f"Attack: {self.attack}\n"
                f"Defense: {self.defense}\n"
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
               (f"stamina={self.stamina}, experience={self.experience})")    
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
            raise TypeError("Level must be an Experience object.")
        elif lvl.lvl < 0:
            self.lvl.lvl = 0
        self._lvl = lvl
    @property
    def attack(self):
        return self._attack
    @attack.setter
    def attack(self, attack):
        if not isinstance(attack, int):
            raise TypeError("Attack must be an integer.")
        elif attack < 0:
            self.attack = 0
        else:
            self._attack = attack
    @property
    def defense(self):
        return self._defense
    @defense.setter
    def defense(self, defense):
        if not isinstance(defense, int):
            raise TypeError("Defense must be an integer.")
        elif defense < 0:
            self.defense = 0
        else:
            self._defense = defense
    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self, speed):
        if not isinstance(speed, int):
            raise TypeError("Speed must be an integer.")
        elif speed < 0:
            self.speed = 0
        else:
            self._speed = speed
    @property
    def health(self):
        return self._health
    @health.setter
    def health(self, health):
        if not isinstance(health, int):
            raise TypeError("Health must be an integer.")
        elif health < 0:
            self.health = 0
        else:
            self._health = health
    @property
    def mana(self):
        return self._mana
    @mana.setter
    def mana(self, mana):
        if not isinstance(mana, int):
            raise TypeError("Mana must be an integer.")
        elif mana < 0:
            self.mana = 0
        else:
            self._mana = mana
    @property
    def stamina(self):
        return self._stamina
    @stamina.setter
    def stamina(self, stamina):
        if not isinstance(stamina, int):
            raise TypeError("Stamina must be an integer.")
        elif stamina < 0:
            self.stamina = 0
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
    @property
    def slots(self):
        return self._slots
    @slots.setter
    def slots(self, slots):
        if not isinstance(slots, dict):
            raise TypeError("slots must be a dictionary.")
        for key, value in slots.items():
            if key not in ["weapon", "armor", "consumable"]:
                raise ValueError("slots must contain 'weapon', 'armor', and 'consumable' keys.")
            if not isinstance(value, Item_functions.Items) and value is not None:
                raise TypeError("slots items must be of type Items.")
        self._slots = slots
class NPC(Character):
    def __init__(self, name: str = "NPC", level: int = 1, experience: int = 0):
        super().__init__(name, level, experience)
    def __str__(self):
        return super().__str__()
    def __repr__(self):
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, NPC):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class Enemy(Character):
    def __init__(self, name: str = "Enemy", level: int = 1, experience: int = 0):
        super().__init__(name, level, experience)
        self.lvl.experience = self.lvl.lvl * 100
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
    def __init__(self, name: str = "Hero", level: int = 1, experience: int = 0):
        super().__init__(name, level, experience)
        self.attack = 15 * self.lvl.lvl
        self.defense = 10 * self.lvl.lvl
        self.speed = 5 * self.lvl.lvl
        self.health = 100 + (self.lvl.lvl * 20)
        self.mana = 100 + (self.lvl.lvl * 10)
        self.stamina = 100 + (self.lvl.lvl * 15)
    def __str__(self,name: str = "", level: int = 1, experience: int = 0):
        return super().__str__()
    def __repr__(self):
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, Player):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False