from enum import Enum

class Rarity(Enum):
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    EPIC = 3
    LEGENDARY = 4
    MYTHIC = 5

    @classmethod
    def get_all_rarities(cls):
        return [member for member in cls]
    
    @classmethod
    def get_rarity_by_value(cls, value):
        for rarity in cls:
            if rarity.value == value:
                return rarity
        return None