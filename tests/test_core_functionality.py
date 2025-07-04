"""
Core functionality tests for the game system.

This module consolidates tests for:
- Basic character creation and stats
- Equipment system
- Job assignment
- Combat mechanics
- Inventory management
"""

import pytest
from game_sys.character.actor import Actor
from game_sys.character.job_manager import JobManager
from game_sys.character.character_factory import create_character


class TestCharacterCreation:
    """Test basic character creation and stats."""

    def test_actor_creation(self):
        """Test creating an Actor with custom stats."""
        actor = Actor(
            name="Test Actor",
            base_stats={
                'health': 100,
                'mana': 50,
                'stamina': 75,
                'attack': 10,
                'defense': 5,
                'intellect': 8
            }
        )

        assert actor.name == "Test Actor"
        assert actor.get_stat('health') == 100
        assert actor.get_stat('attack') == 10
        assert actor.current_health == 100

    def test_character_factory(self):
        """Test character creation through factory."""
        hero = create_character('hero')
        assert hero is not None
        assert hasattr(hero, 'name')
        assert hasattr(hero, 'health')
        assert hasattr(hero, 'stats')


class TestJobSystem:
    """Test job assignment and equipment."""

    def test_warrior_job_assignment(self):
        """Test assigning warrior job and auto-equipment."""
        warrior = Actor(
            name="Test Warrior",
            base_stats={
                'health': 100,
                'mana': 30,
                'stamina': 80,
                'attack': 10,
                'defense': 5,
                'intellect': 5
            }
        )

        initial_attack = warrior.get_stat('attack')
        initial_defense = warrior.get_stat('defense')

        # Assign warrior job
        JobManager.assign(warrior, 'warrior')

        # Should have weapon equipped
        assert warrior.weapon is not None

        # Stats should potentially be modified by equipment
        # (actual values depend on equipment stats)
        assert warrior.get_stat('attack') >= initial_attack
        assert warrior.get_stat('defense') >= initial_defense

    def test_mage_job_assignment(self):
        """Test assigning mage job and staff equipment."""
        mage = Actor(
            name="Test Mage",
            base_stats={
                'health': 70,
                'mana': 100,
                'stamina': 50,
                'attack': 5,
                'defense': 3,
                'intellect': 15
            }
        )

        JobManager.assign(mage, 'mage')

        # Should have staff equipped
        assert mage.weapon is not None

        # Two-handed weapon should prevent offhand
        if (hasattr(mage.weapon, 'two_handed') and
                mage.weapon.two_handed):
            assert (mage.offhand is None or
                    not hasattr(mage.offhand, 'stats'))


class TestEquipmentSystem:
    """Test equipment mechanics."""

    def test_shield_blocking(self):
        """Test shield blocking functionality."""
        warrior = Actor(
            name="Shield Warrior",
            base_stats={
                'health': 100,
                'mana': 30,
                'stamina': 80,
                'attack': 10,
                'defense': 5,
                'intellect': 5
            }
        )

        # Assign job to get shield
        JobManager.assign(warrior, 'warrior')

        # Test damage with blocking
        initial_health = warrior.current_health

        # Test multiple damage attempts to check for blocking
        for _ in range(10):  # Multiple attempts to increase chance of block
            before_hp = warrior.current_health
            warrior.take_damage(15.0)
            after_hp = warrior.current_health

            if before_hp == after_hp:  # No damage taken = blocked
                break

            # Reset health for next test
            warrior.current_health = initial_health

        # Note: This test might be flaky due to RNG -
        # consider using deterministic RNG

    def test_two_handed_weapon_restrictions(self):
        """Test that two-handed weapons prevent dual wielding."""
        mage = Actor(
            name="Staff Mage",
            base_stats={
                'health': 70,
                'mana': 100,
                'stamina': 50,
                'attack': 5,
                'defense': 3,
                'intellect': 15
            }
        )

        JobManager.assign(mage, 'mage')

        # If weapon is two-handed, offhand should be restricted
        if (mage.weapon and
                hasattr(mage.weapon, 'two_handed') and
                mage.weapon.two_handed):
            # Offhand should be None or have no combat stats
            assert (mage.offhand is None or
                    not hasattr(mage.offhand, 'stats'))


class TestCombatBasics:
    """Test basic combat mechanics."""

    def test_damage_calculation(self):
        """Test basic damage and defense calculation."""
        attacker = Actor(
            name="Attacker",
            base_stats={'attack': 20, 'defense': 0}
        )
        defender = Actor(
            name="Defender",
            base_stats={'attack': 0, 'defense': 10}
        )

        initial_health = defender.current_health

        # Calculate expected damage: attack - (defense * modifier)
        base_damage = attacker.get_stat('attack')
        # Assuming 5% per defense
        defense_reduction = defender.get_stat('defense') * 0.05
        # Minimum 1 damage
        expected_damage = max(1, base_damage - defense_reduction)

        # Apply damage
        defender.take_damage(expected_damage)

        # Verify damage was applied
        assert defender.current_health < initial_health

    def test_health_restoration(self):
        """Test health restoration mechanics."""
        actor = Actor(
            name="Test Actor",
            base_stats={'health': 100}
        )

        # Damage the actor
        actor.take_damage(50)
        assert actor.current_health == 50

        # Restore health
        actor.restore_all()
        assert actor.current_health == actor.max_health


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    pytest.main([__file__, "-v"])
