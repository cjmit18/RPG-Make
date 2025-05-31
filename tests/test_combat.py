# game_sys/tests/test_combat.py

import pytest
import random

from game_sys.core.actor import Actor
from game_sys.character.character_creation import Enemy, Player
from game_sys.combat.combat import CombatCapabilities


class DummyRNG(random.Random):
    """A dummy RNG that returns fixed values for uniform(), random(), and randint()."""
    def __init__(self, uniform_val: float, random_val: float, randint_val: int):
        super().__init__()
        self._uniform_val = uniform_val
        self._random_val = random_val
        self._randint_val = randint_val

    def uniform(self, a, b):
        return self._uniform_val

    def random(self):
        return self._random_val

    def randint(self, a, b):
        return self._randint_val


@pytest.fixture
def make_fighter():
    """
    Returns a function (name, level, base_attack, base_defense) -> Player
    with those base stats set, and full health at start.
    """
    def _inner(name: str, level: int, base_attack: int, base_defense: int):
        # Create a Player (Actor subclass)
        hero = Player(name=name, level=level)
        # Override base stats via stats.set_base
        hero.stats.set_base("attack", base_attack)
        hero.stats.set_base("defense", base_defense)
        # Ensure hero.current_health is at max health
        max_hp = hero.stats.effective()["health"]
        hero.health = max_hp
        return hero

    return _inner


def test_attack_no_crit_no_defend(make_fighter):
    """
    If RNG.random() > 0.1 (no crit), uniform() = 1.0 (no variance),
    and defender.defending=False, then final damage = round((attack - defense*0.05) * 1.0).
    """
    attacker = make_fighter("Attacker", level=1, base_attack=50, base_defense=0)
    defender = make_fighter("Defender", level=1, base_attack=0, base_defense=20)

    # uniform()=1.0, random()=0.5 (>0.1 so no crit), randint()=0 (unused here)
    rng = DummyRNG(uniform_val=1.0, random_val=0.5, randint_val=0)
    combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

    # Record defender’s health before
    initial_hp = defender.health

    outcome = combat.calculate_damage(attacker, defender)
    # Base damage = 50 - (20 * 0.05) = 50 - 1 = 49.0; *1.0 = 49.0; no crit → round(49.0) = 49
    assert "deals 49 damage" in outcome

    expected_hp = max(initial_hp - 49, 0)
    assert defender.health == pytest.approx(expected_hp)


def test_attack_with_crit(make_fighter):
    """
    If RNG.random() < 0.1 (crit), uniform()=1.0, and defender.defending=False,
    damage doubles before rounding.
    """
    attacker = make_fighter("Attacker", level=1, base_attack=40, base_defense=0)
    defender = make_fighter("Defender", level=1, base_attack=0, base_defense=10)

    # Base = 40 - (10 * 0.05) = 39.5; uniform()=1.0 → 39.5; random()=0.0 → crit → 79.0 → round(79.0)=79
    rng = DummyRNG(uniform_val=1.0, random_val=0.0, randint_val=0)
    combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

    initial_hp = defender.health

    outcome = combat.calculate_damage(attacker, defender)
    assert "deals 79 damage. Critical Hit!" in outcome

    expected_hp = max(initial_hp - 79, 0)
    assert defender.health == pytest.approx(expected_hp)


def test_attack_with_defender_defending(make_fighter):
    """
    If defender.defending=True, damage is halved AFTER crit/no-crit logic.
    E.g., base = 30 - (5 * 0.05) = 29.75; uniform()=1.0 → 29.75; random()=1.0 (no crit);
    defender.defending → *0.5 = 14.875 → round(14.875) = 15.
    """
    attacker = make_fighter("Attacker", level=1, base_attack=30, base_defense=0)
    defender = make_fighter("Defender", level=1, base_attack=0, base_defense=5)

    # uniform()=1.0, random()=1.0 (no crit), randint()=0 (unused here)
    rng = DummyRNG(uniform_val=1.0, random_val=1.0, randint_val=0)
    combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

    defender.defending = True
    initial_hp = defender.health

    outcome = combat.calculate_damage(attacker, defender)
    assert "deals 15 damage" in outcome

    expected_hp = max(initial_hp - 15, 0)
    assert defender.health == pytest.approx(expected_hp)
