# game_sys/jobs/mage.py

from game_sys.jobs.base import Job

class Mage(Job):
    name = "Mage"
    base_stats = {
        "attack": 2,
        "defense": 3,
        "speed": 5,
        "health": 6,
        "mana": 10,
        "stamina": 3
    }
    starting_item_ids = [
        "mana_potion",
        "ruby_band"
    ]

    def description(self) -> str:
        return "A master of arcane arts, trading physical power for high mana reserves."
