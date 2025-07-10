import pytest
from game_sys.character.actor import Actor
from game_sys.combat.engine import CombatEngine
from game_sys.config.config_manager import ConfigManager

@pytest.fixture
def simple_actors():
    class TestActor(Actor):
        def is_alive(self):
            return True
    attacker = TestActor(name="Test Attacker", base_stats={"strength": 10, "stamina": 20})
    defender = TestActor(name="Test Defender", base_stats={"defense": 5, "stamina": 20})
    attacker.current_stamina = 10
    defender.current_stamina = 10
    return attacker, defender

def test_attack_stamina_deduction(simple_actors):
    attacker, defender = simple_actors
    engine = CombatEngine()
    cfg = ConfigManager()
    stamina_cost = cfg.get('constants.combat.stamina_costs.attack', 5)
    # Should succeed and deduct stamina
    outcome = engine.execute_attack_sync(attacker, [defender])
    assert outcome.success
    assert attacker.current_stamina == 10 - stamina_cost

def test_attack_fails_when_exhausted(simple_actors):
    attacker, defender = simple_actors
    engine = CombatEngine()
    attacker.current_stamina = 2  # Less than cost
    outcome = engine.execute_attack_sync(attacker, [defender])
    assert not outcome.success
    assert "exhausted" in outcome.description.lower()
    assert attacker.current_stamina == 2
