# game_sys/jobs/knight.py

from game_sys.jobs.base import Job

class Knight(Job):
    name = "Knight"
    base_stats = {
        "attack": 5,
        "defense": 7,
        "speed": 3,
        "health": 10,
        "mana": 2,
        "stamina": 5
    }
    starting_item_ids = [
        "iron_sword",      # from items.json
        "leather_armor",
        "ruby_band"
    ]

    def description(self) -> str:
        return "A stalwart defender with high resilience and moderate offense."
