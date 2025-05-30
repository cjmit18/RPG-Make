import json
from game_sys.items.item_factory import item_from_dict
from game_sys.core.character.character_creation import Character

def save_character(character: Character, filename: str):
    """Save a character to a JSON file."""
    try:
        with open(filename, "x") as f:
            pass  # Ensure the file does not already exist
    except FileExistsError:
        raise FileExistsError(f"File '{filename}' already exists. Please choose a different name or delete the existing file.")
    with open(filename, "w") as f:
        json.dump(character.to_dict(), f, indent=4)
def load_character(filename: str) -> Character:
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        # Reconstruct the character from the loaded data
        character = Character(
            name=data["name"],
            level=data["level"],
            experience=data["experience"],
            job=data["class"]
        )
        # Load inventory items
        for item_data in data["inventory"]:
            item = item_from_dict(item_data)
            character.inventory.add_item(item)
        # Load equipped items
        for slot, item_data in data["equipped"].items():
            item = item_from_dict(item_data)
            character.inventory.equip_item(item, slot)
        return character
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found. Please check the file path.")
    except json.JSONDecodeError:
        raise ValueError(f"File '{filename}' is not a valid JSON file or is corrupted.")
    