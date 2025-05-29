# game_sys/jobs/healer.py

from game_sys.jobs.base import Job

class Healer(Job):
    name = "Healer"
    base_stats = {
        "attack": 1,
        "defense": 4,
        "speed": 4,
        "health": 7,
        "mana": 8,
        "stamina": 4
    }
    starting_item_ids = [
        "health_potion",
        "mana_potion"
    ]

    def description(self) -> str:
        return "A supportive class specializing in healing and buffs."
