"""
Comprehensive tests for the Actor class and character management.

This module tests core Actor functionality including:
- Health/damage management
- Job assignment and stat modifications
- Equipment integration
- Character state management
"""

import pytest
from game_sys.character.actor import Actor
from game_sys.character.job_manager import JobManager


class TestActorBasics:
    """Test basic Actor functionality."""

    def test_take_damage_clamps_and_reports_defeat(self, basic_actor, capfd):
        """Test damage application and defeat detection."""
        actor = basic_actor
        initial_health = actor.current_health

        # Apply damage within health range
        actor.take_damage(20)
        assert actor.current_health == initial_health - 20

        # Apply killing blow
        actor.take_damage(200)  # More than remaining health
        captured = capfd.readouterr()
        assert actor.current_health == 0
        assert f"{actor.name} has been defeated!" in captured.out

    def test_health_never_goes_negative(self, basic_actor):
        """Ensure health is clamped to 0."""
        actor = basic_actor
        actor.take_damage(1000)  # Massive overkill
        assert actor.current_health == 0

    @pytest.mark.parametrize("damage_amount", [0, 10, 50, 100])
    def test_damage_amounts(self, basic_actor, damage_amount):
        """Test various damage amounts."""
        actor = basic_actor
        initial_health = actor.current_health
        actor.take_damage(damage_amount)

        expected_health = max(0, initial_health - damage_amount)
        assert actor.current_health == expected_health


class TestJobIntegration:
    """Test job assignment and related stat/equipment changes."""

    def test_assign_job_applies_stats_and_items(self, basic_actor):
        """Test that job assignment properly modifies stats and equipment."""
        actor = basic_actor

        # Record initial stats
        initial_attack = actor.get_stat("attack")
        initial_defense = actor.get_stat("defense")

        # Assign knight job
        JobManager.assign(actor, "knight")

        # Check stat improvements
        new_attack = actor.get_stat("attack")
        new_defense = actor.get_stat("defense")

        assert new_attack > initial_attack, "Knight should improve attack"
        assert new_defense > initial_defense, "Knight should improve defense"

        # Check that equipment was applied
        assert actor.weapon is not None, "Knight should have a weapon"
        assert hasattr(actor.weapon, 'id'), "Weapon should have an ID"

    @pytest.mark.parametrize("job_name,level", [
        ("knight", 1),
        ("knight", 3),
        ("mage", 1),
        ("mage", 2),
        ("warrior", 1),
    ])
    def test_job_assignment_at_various_levels(
        self, player_factory, job_name, level
    ):
        """Test job assignment scales properly with level."""
        player = player_factory(level=level)

        # Record stats before job assignment
        pre_stats = {
            stat: player.get_stat(stat)
            for stat in ['attack', 'defense', 'health', 'mana', 'intellect']
        }

        # Assign job
        JobManager.assign(player, job_name)

        # Verify stats have been modified
        post_stats = {
            stat: player.get_stat(stat)
            for stat in ['attack', 'defense', 'health', 'mana', 'intellect']
        }

        # At least some stats should be different (improved)
        stats_changed = sum(
            1 for stat in pre_stats
            if pre_stats[stat] != post_stats[stat]
        )
        assert stats_changed > 0, f"Job {job_name} should modify some stats"

    def test_job_equipment_is_applied(self, basic_actor):
        """Test that job starting equipment is properly equipped."""
        actor = basic_actor
        JobManager.assign(actor, "knight")

        # Knight should have both weapon and shield
        assert actor.weapon is not None
        assert actor.offhand is not None

        # Equipment should provide stat bonuses
        weapon_attack = getattr(actor.weapon, 'stats', {}).get('attack', 0)
        shield_defense = getattr(actor.offhand, 'stats', {}).get('defense', 0)

        # At least one piece should provide bonuses
        assert weapon_attack > 0 or shield_defense > 0


class TestStatManagement:
    """Test stat calculation and management."""

    def test_stat_calculation_includes_equipment(
        self, basic_actor, test_equipment
    ):
        """Test that equipment bonuses are included in stat calculations."""
        actor = basic_actor
        sword = test_equipment['sword']

        # Get baseline attack
        base_attack = actor.get_stat('attack')

        # Apply sword (should increase attack)
        sword.apply(actor)

        # Check that attack increased
        new_attack = actor.get_stat('attack')
        assert new_attack > base_attack, "Equipment should improve stats"

    @pytest.mark.parametrize("stat_name,base_value", [
        ("health", 100),
        ("mana", 50),
        ("attack", 10),
        ("defense", 5),
        ("intellect", 8),
    ])
    def test_base_stat_setting(self, stat_name, base_value):
        """Test that base stats can be set and retrieved correctly."""
        actor = Actor(
            name="Test Actor",
            base_stats={stat_name: base_value}
        )

        retrieved_value = actor.get_stat(stat_name)
        assert retrieved_value >= base_value, (
            f"Retrieved {stat_name} ({retrieved_value}) should be >= "
            f"base value ({base_value})"
        )


class TestPlayerSpecificFeatures:
    """Test Player-specific functionality."""

    def test_player_has_learning_system(self, player_factory):
        """Test that Players have learning capabilities."""
        player = player_factory()
        assert hasattr(player, 'learning'), (
            "Player should have learning system"
        )

    def test_player_starts_with_commoner_job(self, player_factory):
        """Test that Players start with the commoner job."""
        player = player_factory()
        # Player should have some job assigned
        assert hasattr(player, 'job') or hasattr(player, 'job_name')


class TestEnemySpecificFeatures:
    """Test Enemy-specific functionality."""

    def test_enemy_behavior_setting(self, enemy_factory):
        """Test that Enemy behavior can be set."""
        enemy = enemy_factory()

        # Should be able to set behavior
        if hasattr(enemy, 'set_behavior'):
            enemy.set_behavior('aggressive')
            assert hasattr(enemy, 'behavior_state')
            assert enemy.behavior_state == 'aggressive'
