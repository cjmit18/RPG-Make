from enum import Enum, auto
class DamageType(Enum):
    NONE = auto()
    PHYSICAL = auto()
    FIRE = auto()
    COLD = auto()
    LIGHTNING = auto()
    POISON = auto()
    ARCANE = auto()
    HOLY =  auto()
    DARK = auto()
    MAGIC =  auto()
    # Add more damage types as needed

    @classmethod
    def get_all_types(cls):
        return [member for member in cls]
