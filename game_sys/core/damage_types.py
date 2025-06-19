from enum import Enum, auto


class DamageType(Enum):
    NONE = auto()
    PHYSICAL = auto()
    FIRE = auto()
    ICE = auto()
    LIGHTNING = auto()
    POISON = auto()
    ARCANE = auto()
    HOLY = auto()
    DARK = auto()
    MAGIC = auto()
    # Add more damage types as needed

    @classmethod
    def get_all_types(cls):
        return [member for member in cls]
    
    def __str__(self):
        return self.name.lower()
    
    def __repr__(self):
        return f"Damage Type: {self.name.upper()}"