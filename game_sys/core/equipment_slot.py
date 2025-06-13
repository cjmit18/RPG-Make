from enum import Enum, auto


class EquipmentSlot(Enum):
    """
    Enum representing different equipment slots for characters.
    """
    HEAD = auto()
    ARMOR = auto()
    LEGS = auto()
    FEET = auto()
    HANDS = auto()
    WEAPON = auto()
    OFFHAND = auto()
    RING = auto()
    AMULET = auto()
    ACCESSORY = auto()

    def __str__(self):
        return self.name.capitalize()
