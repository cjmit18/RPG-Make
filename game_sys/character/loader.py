from pathlib import Path
import json
from game_sys.character.character_creation import Player, Enemy

_TEMPLATES_PATH = Path(__file__).parent / 'data' / 'character_templates.json'
with open(_TEMPLATES_PATH) as f:
    templates = json.load(f)

player = Player.from_dict(templates["Player"])
enemy  = Enemy.from_dict(templates["Enemy"])