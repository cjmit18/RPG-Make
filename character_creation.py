import inventory_functions
class Character():
    def __init__(self, name: str = ""):
        self.name = name
        self.lvl = 1
        self.attack = 10
        self.defense = 10
        self.speed = 10
        self.health = 100
        self.mana = 100
        self.stamina = 100
        self.experience = 0
        self.equippable = { "weapon": None, "armor": None, "accessory": None}
        self.inventory = inventory_functions.Inventory(self.name)
    def __str__(self):
        return (f"{self.name}:\n"
                f"Lvl: {self.lvl}\n"
                f"Attack: {self.attack}\n"
                f"Defense: {self.defense}\n"
                f"Speed: {self.speed}\n"
                f"Health: {self.health}\n"
                f"Mana: {self.mana}\n"
                f"Stamina: {self.stamina}\n"
                f"Experience: {self.experience}\n"
                f"Inventory: {self.inventory.get_items()}")
    def __repr__(self):
        return (f"{self.__class__.__name__}(") + \
               (f"name={self.name!r}, lvl={self.lvl}, attack={self.attack}, defense={self.defense}, ") + \
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
        if not isinstance(lvl, int):
            raise TypeError("Level must be an integer.")
        elif lvl < 0:
            self.lvl = 0
        else:
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
    def experience(self):
        return self._experience
    @experience.setter
    def experience(self, experience):
        if not isinstance(experience, int):
            raise TypeError("Experience must be an integer.")
        elif experience < 0:
            self.experience = 0
        else:
            self._experience = experience
    @property
    def inventory(self):
        return self._inventory
    @inventory.setter
    def inventory(self, inventory):
        if not isinstance(inventory, inventory_functions.Inventory):
            raise TypeError("Inventory must be an Inventory object.")
        self._inventory = inventory
class NPC(Character):
    def __init__(self, name: str = str):
        super().__init__(name)
    def __str__(self):
        return super().__str__()
    def __repr__(self):
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, NPC):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class Enemy(Character):
    def __init__(self, name: str = str ):
        super().__init__(name)
    def __str__(self):
        return super().__str__()
    def __repr__(self):
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, Enemy):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class Player(Character):
    def __init__(self, name: str = str):
        super().__init__(name)
    def __str__(self):
        return super().__str__()
    def __repr__(self):
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, Player):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False