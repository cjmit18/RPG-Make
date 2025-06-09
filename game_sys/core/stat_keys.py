# game_sys/core/stat_keys.py
from enum import Enum


class StatKey(str, Enum):

    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    INTELLECT = "intellect"
    WISDOM = "wisdom"
    AGILITY = "agility"
    LUCK = "luck"
    ENDURANCE = "endurance"
    ATTACK = "attack"
    DEFENSE = "defense"
    MAGIC_ATTACK = "magic_attack"
    STAMINA = "stamina"
    HEALTH = "health"
    MANA = "mana"
    SPEED = "speed"
