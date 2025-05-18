import inventory_functions
import experience_functions
import class_creation
import items_list
import unit_test
class Character():
    def __init__(self, name: str = "Template", level: int = 1, experience: int = 0) -> None:
        self.name: str = name
        self.attack: int = 10
        self.defense: int = 5
        self.speed: int = 10
        self.health: int = 100
        self.mana: int = 100
        self.stamina: int = 100
        self.lvls: experience_functions.Levels = experience_functions.Levels(self, level, experience)
        self.lvl: int = self.lvls.lvl
        self.experience: int = self.lvls.experience
        self.inventory: inventory_functions.Inventory = inventory_functions.Inventory(self)
        self.class_ = class_creation.c_class(self)
        self.cls = None
        self.update_stats()

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}:\n"
                f"{self.lvls}\n"
                f"Class: {self.class_.class_}\n"
                f"{'-'*10}\n"
                f"Attack: {self.attack} ({self.inventory.equipped_items['weapon'].attack_power if self.inventory.equipped_items['weapon'] else 0})\n"
                f"Defense: {self.defense} ({self.inventory.equipped_items['armor'].defense_power if self.inventory.equipped_items['armor'] else 0})\n"
                f"Speed: {self.speed}\n"
                f"Health: {self.health}\n"
                f"Mana: {self.mana}\n"
                f"Stamina: {self.stamina}\n"
                f"{'-'*10}\n"
                f"{self.inventory}")
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}") + \
               (f"name={self.name}, lvl={self.lvl}, attack={self.attack}, defense={self.defense}, ") + \
               (f"speed={self.speed}, health={self.health}, mana={self.mana}, ") + \
               (f"stamina={self.stamina}, inventory={self.inventory})")    
    def __eq__(self, other) -> bool:
        if isinstance(other, Character):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    def update_stats(self):
        # Default stat calculation, override in subclasses if needed
        self.attack = 10 + (self.lvls.lvl - 1) * 2
        self.defense = 5 + (self.lvls.lvl - 1) * 2
        self.speed = 10 + (self.lvls.lvl - 1)
        self.health = 100 + (self.lvls.lvl - 1) * 10
        self.mana = 100 + (self.lvls.lvl - 1) * 10
        self.stamina = 100 + (self.lvls.lvl - 1) * 10

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.") 
        self._name: str = name
    @property
    def lvl(self) -> int:
        return self._lvl
    @lvl.setter
    def lvl(self, lvl) -> None:
        if not isinstance(lvl, int):
            raise TypeError("Level must be an integer.")
        elif lvl < 1:
            self._lvl: int = 1
        else:
            self._lvl: int = lvl
        self.lvls.change_level(self._lvl)
        self.update_stats()
    @property
    def attack(self) -> int:
        if self.inventory.equipped_items["weapon"]:
            return self._attack + self.inventory.equipped_items["weapon"].attack_power
        return self._attack
    @attack.setter
    def attack(self, attack):
        if not isinstance(attack, int):
            raise TypeError("Attack must be an integer.")
        elif attack < 0:
            self._attack: int = 0
        else:
            self._attack: int = attack
    @property
    def defense(self) -> int:
        if self.inventory.equipped_items["armor"] is not None:
            return self._defense + self.inventory.equipped_items["armor"].defense_power
        return self._defense
    @defense.setter
    def defense(self, defense) -> None:
        if not isinstance(defense, int):
            raise TypeError("Defense must be an integer.")
        elif defense < 1:
            self.defense: int = 1
        else:
            self._defense: int = defense
    @property
    def speed(self) -> int:
        return self._speed
    @speed.setter
    def speed(self, speed) -> None:
        if not isinstance(speed, int):
            raise TypeError("Speed must be an integer.")
        elif speed < 0:
            self._speed: int = 0
        else:
            self._speed: int = speed
    @property
    def health(self) -> int:
        return self._health
    @health.setter
    def health(self, health) -> None:
        if not isinstance(health, int):
            raise TypeError("Health must be an integer.")
        elif health < 0:
            self._health: int = 0
        else:
            self._health: int = health
    @property
    def mana(self) -> int:
        return self._mana
    @mana.setter
    def mana(self, mana) -> None:
        if not isinstance(mana, int):
            raise TypeError("Mana must be an integer.")
        elif mana < 0:
            self._mana: int = 0
        else:
            self._mana: int = mana
    @property
    def stamina(self) -> int:
        return self._stamina
    @stamina.setter
    def stamina(self, stamina) -> None:
        if not isinstance(stamina, int):
            raise TypeError("Stamina must be an integer.")
        elif stamina < 0:
            self._stamina: int = 0
        else:
            self._stamina: int = stamina
    @property
    def inventory(self) -> inventory_functions.Inventory:
        return self._inventory
    @inventory.setter
    def inventory(self, inventory) -> None:
        if not isinstance(inventory, inventory_functions.Inventory):
            raise TypeError("Inventory must be an Inventory object.")
        self._inventory: inventory_functions.Inventory = inventory
    @property
    def class_(self) -> class_creation.c_class:
        return self._class_
    @class_.setter
    def class_(self, class_) -> None:
        if not isinstance(class_, class_creation.c_class):
            raise TypeError("Class must be a c_class object.")
        self._class_: class_creation.c_class = class_
        
class NPC(Character) :
    def __init__(self, name: str = "NPC", level: int = 1) -> None:
        super().__init__(name, level)
    def __str__(self) -> str:
        return super().__str__()
    def __repr__(self)-> str:
        return super().__repr__()
    def __eq__(self, other)-> bool:
        if isinstance(other, NPC):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class Enemy(Character):
    def __init__(self, name: str = "Enemy", level: int = 1) -> None:
        super().__init__(name, level)
        cls = class_creation.c_class(self)
        level = 1 if level == 0 else level
        if level == 1:
            potion = items_list.Health_Potion(lvl=1)
            self.inventory.add_item(potion, unit_test.generate_random_number(1, 3))
        elif level == 2:
            potion = items_list.Health_Potion(lvl=2)
            self.inventory.add_item(potion, unit_test.generate_random_number(1, 3))
        elif level == 3:
            potion = items_list.Health_Potion(lvl=3)
            self.inventory.add_item(potion, unit_test.generate_random_number(1, 3))
    def __str__(self) -> str:   
        return super().__str__()
    def __repr__(self) -> str:
        return super().__repr__()
    def __eq__(self, other) -> bool:
        if isinstance(other, Enemy):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    def update_stats(self):
        self.attack = self.lvls.lvl * 10
        self.defense = self.lvls.lvl * 5
        self.speed = self.lvls.lvl * 3
        self.health = (self.lvls.lvl * 2) * 10
        self.mana = round((self.lvls.lvl * 2) * 20)
        self.stamina = self.lvls.lvl * 5
class Player(Character):
    def __init__(self, name: str = "Hero", level: int = 1)  -> None:
        super().__init__(name, level)
        cls = class_creation.c_class(self)
    def __str__(self) -> str:
        return super().__str__()
    def __repr__(self) -> str:
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, Player) or isinstance(other, Enemy):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    def update_stats(self):
        self.attack = self.lvls.lvl * 15
        self.defense = self.lvls.lvl * 10
        self.speed = self.lvls.lvl * 5
        self.health = (self.lvls.lvl * 2) * 5
        self.mana = round((self.lvls.lvl * 2) * 25)
        self.stamina = self.lvls.lvl * 10