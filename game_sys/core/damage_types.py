from enum import Enum
class DamageType(Enum):
    NONE = 0
    PHYSICAL = 1
    FIRE = 2
    COLD = 3
    LIGHTNING = 4
    POISON = 5
    ARCANE = 6
    HOLY = 7
    DARK = 8
    MAGIC = 9
    # Add more damage types as needed

    @classmethod
    def get_all_types(cls):
        return [member for member in cls]