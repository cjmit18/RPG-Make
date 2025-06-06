from enum import Enum, auto

class Rarity(Enum):
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()
    MYTHIC = auto()
    EXOTIC = auto()
    DIVINE = auto()

    @classmethod
    def get_all_rarities(cls):
        return [member for member in cls]
    
    @classmethod
    def get_rarity_by_value(cls, value):
        for rarity in cls:
            if rarity.value == value:
                return rarity
        return None