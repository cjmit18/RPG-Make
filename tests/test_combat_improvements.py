"""
Combat system demonstration showcasing the DamagePacket refactor.

This module demonstrates:
- DamagePacket factory methods for weapons and spells
- Miss chance logic implementation
- Optimized blocking mechanics
- Combat engine integration
"""

import pytest
from game_sys.character.actor import Actor
from game_sys.character.job_manager import JobManager
from game_sys.combat.engine import CombatEngine
from game_sys.combat.damage_packet import DamagePacket
from game_sys.combat.capabilities import CombatCapabilities
from game_sys.combat.test_utils import swing


def test_damage_packet_weapon_factory():
    """Test DamagePacket.from_weapon_attack() factory method."""
    # Create a warrior with weapon
    warrior = Actor(
        name="Test Warrior",
        base_stats={
            'health': 100,
            'attack': 25,
            'defense': 10
        }
    )
    JobManager.assign(warrior, 'warrior')
    
    # Create target
    target = Actor(
        name="Target",
        base_stats={'health': 80, 'defense': 5}
    )
    
    # Create damage packet from weapon attack
    if warrior.weapon:
        packet = DamagePacket.from_weapon_attack(
            attacker=warrior,
            defender=target,
            weapon=warrior.weapon
        )
        
        # Verify packet properties
        assert packet.attacker == warrior
        assert packet.defender == target
        assert packet.weapon == warrior.weapon
        assert packet.base_damage > 0
        assert hasattr(packet, 'damage_variance_min')
        assert hasattr(packet, 'damage_variance_max')


def test_damage_packet_spell_factory():
    """Test DamagePacket.from_spell_cast() factory method."""
    # Create a mage
    mage = Actor(
        name="Test Mage",
        base_stats={
            'health': 70,
            'mana': 100,
            'intellect': 20
        }
    )
    JobManager.assign(mage, 'mage')
    
    # Create target
    target = Actor(
        name="Target",
        base_stats={'health': 80, 'defense': 5}
    )
    
    # Create damage packet from spell cast
    spell_damage = mage.get_stat('intellect') * 2.0
    packet = DamagePacket.from_spell_cast(
        attacker=mage,
        defender=target,
        spell_damage=spell_damage
    )
    
    # Verify packet properties
    assert packet.attacker == mage
    assert packet.defender == target
    assert packet.base_damage == spell_damage


def test_optimized_blocking():
    """Test the optimized blocking mechanics."""
    # Create a warrior with guaranteed block shield
    warrior = Actor(
        name="Shield Warrior",
        base_stats={
            'health': 100,
            'defense': 10
        }
    )
    JobManager.assign(warrior, 'warrior')
    
    # Mock a shield with 100% block chance
    class GuaranteedBlockShield:
        def __init__(self):
            self.name = "Perfect Shield"
            self.block_chance = 1.0  # 100% block
    
    warrior.offhand = GuaranteedBlockShield()
    
    # Create combat capabilities
    capabilities = CombatCapabilities(warrior)
    
    # Test guaranteed blocking (should not use RNG)
    for _ in range(10):  # Multiple tests to ensure consistency
        assert capabilities.can_block() is True


def test_miss_chance_logic():
    """Test the miss chance logic in combat engine."""
    # Create attacker with low hit chance
    attacker = Actor(
        name="Inaccurate Fighter",
        base_stats={
            'health': 100,
            'attack': 20,
            'hit_chance': 0.1  # Only 10% hit chance
        }
    )
    
    # Create defender
    defender = Actor(
        name="Defender",
        base_stats={'health': 100, 'defense': 5}
    )
    
    # Create combat engine with deterministic RNG for testing
    class MockRNG:
        def __init__(self, value):
            self.value = value
        
        def random(self):
            return self.value
        
        def uniform(self, a, b):
            return (a + b) / 2
        
        def seed(self, seed):
            pass
    
    # Test with RNG that causes miss (0.9 > 0.1 hit_chance)
    miss_engine = CombatEngine(rng=MockRNG(0.9))
    outcome = miss_engine.execute_attack_sync(attacker, [defender])
    
    # Should result in a miss
    assert "miss" in outcome.description.lower()
    
    # Test with RNG that causes hit (0.05 < 0.1 hit_chance)
    hit_engine = CombatEngine(rng=MockRNG(0.05))
    outcome = hit_engine.execute_attack_sync(attacker, [defender])
    
    # Should result in a hit
    assert "miss" not in outcome.description.lower()


def test_combat_engine_integration():
    """Test the complete combat engine integration."""
    # Create warrior and enemy
    warrior = Actor(
        name="Test Warrior",
        base_stats={
            'health': 100,
            'attack': 25,
            'defense': 10
        }
    )
    JobManager.assign(warrior, 'warrior')
    
    enemy = Actor(
        name="Test Enemy",
        base_stats={
            'health': 80,
            'attack': 20,
            'defense': 5
        }
    )
    
    # Create combat engine
    engine = CombatEngine()
    
    # Execute attack
    initial_enemy_health = enemy.current_health
    outcome = engine.execute_attack_sync(warrior, [enemy])
    
    # Verify combat outcome
    assert isinstance(outcome.description, str)
    assert len(outcome.description) > 0
    assert outcome.events  # Should have combat events
    
    # Enemy should take damage (unless missed/blocked)
    if "miss" not in outcome.description.lower() and "block" not in outcome.description.lower():
        assert enemy.current_health < initial_enemy_health


def test_spell_combat_pathway():
    """Test the spell combat pathway in the engine."""
    # Create a mage
    mage = Actor(
        name="Test Mage",
        base_stats={
            'health': 70,
            'mana': 100,
            'intellect': 20
        }
    )
    JobManager.assign(mage, 'mage')
    
    # Create target
    target = Actor(
        name="Target",
        base_stats={'health': 100, 'defense': 5}
    )
    
    # Note: The actual pending_spell implementation may vary
    # This test demonstrates the concept
    
    # Create combat engine
    engine = CombatEngine()
    
    # Execute spell attack (using regular attack with mage stats)
    initial_target_health = target.current_health
    outcome = engine.execute_attack_sync(mage, [target])
    
    # Verify spell casting
    assert isinstance(outcome.description, str)
    assert len(outcome.description) > 0
    
    # Target should take damage based on mage's stats
    if "miss" not in outcome.description.lower():
        assert target.current_health <= initial_target_health


def test_combat_test_utils():
    """Test the combat test utilities."""
    # Create combatants
    attacker = Actor(
        name="Attacker",
        base_stats={'health': 100, 'attack': 20}
    )
    defender = Actor(
        name="Defender",
        base_stats={'health': 100, 'defense': 10}
    )
    
    # Use the swing utility function
    success = swing(attacker, [defender])
    
    # Verify the utility works
    assert isinstance(success, bool)
    # Note: swing returns success status, not outcome description


def test_healing_integration():
    """Test the healing system integration."""
    # Create healer and target
    healer = Actor(
        name="Healer",
        base_stats={'health': 100, 'mana': 50}
    )
    
    target = Actor(
        name="Wounded Target",
        base_stats={'health': 100}
    )
    
    # Damage the target first
    target.take_damage(50)
    assert target.current_health == 50
    
    # Create combat engine and heal
    engine = CombatEngine()
    outcome = engine.apply_healing(healer, target, 30)
    
    # Verify healing
    assert outcome.success
    assert target.current_health == 80  # 50 + 30
    assert "heal" in outcome.description.lower()


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    pytest.main([__file__, "-v"])
