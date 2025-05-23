import json
from item_factory import item_from_dict
from character_creation import Character

def save_character(character: Character, filename: str):
    with open(filename, "w") as f:
        json.dump(character.to_dict(), f, indent=4)

def load_character(filename: str) -> Character:
    with open(filename, "r") as f:
        data = json.load(f)
    return Character.from_dict(data, item_from_dict)