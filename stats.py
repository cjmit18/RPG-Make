from dataclasses import dataclass

@dataclass
class Stats:
    attack: int = 0
    defense: int = 0
    speed: int = 0
    health: int = 0
    mana: int = 0
    stamina: int = 0
    max_health: int = 0
    max_mana: int = 0
    max_stamina: int = 0

    def __add__(self, other):
        if not isinstance(other, Stats):
            raise TypeError("Can only add Stats to Stats.")
        return Stats(
            attack=self.attack + other.attack,
            defense=self.defense + other.defense,
            speed=self.speed + other.speed,
            health=self.health + other.health,
            mana=self.mana + other.mana,
            stamina=self.stamina + other.stamina,
            max_health=self.max_health + other.max_health,
            max_mana=self.max_mana + other.max_mana,
            max_stamina=self.max_stamina + other.max_stamina,
        )
