# game_sys/jobs/rogue.py

from game_sys.jobs.base import Job

class Rogue(Job):
    name = "Rogue"
    base_stats = {
        "attack": 4,
        "defense": 3,
        "speed": 8,
        "health": 8,
        "mana": 3,
        "stamina": 6
    }
    starting_item_ids = [
        "iron_sword",
        "emerald_loop"
    ]

    def description(self) -> str:
        return "A nimble combatant excelling in speed and critical strikes."
