"""
Integration tests for game system features.

This module tests:
- Equipment system integration
- Job assignment and equipment
- Combat system integration
- Resource management
"""

import pytest
from game_sys.character.job_manager import JobManager
from game_sys.character.actor import Actor
from game_sys.combat.combat import CombatCapabilities


class TestEquipmentIntegration:
    """Test equipment system integration."""

    def test_warrior_equipment_integration(self):
        """Test the fully integrated warrior equipment system."""
        # Create a warrior
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

        # Assign warrior job (should auto-equip items)
        JobManager.assign(warrior, 'warrior')

        # Check equipped items
        assert warrior.weapon is not None
        
        # Stats should potentially be enhanced by equipment
        final_attack = warrior.get_stat('attack')
        final_defense = warrior.get_stat('defense')
        
        # At minimum, stats shouldn't decrease
        assert final_attack >= initial_attack
        assert final_defense >= initial_defense

    def test_mage_equipment_integration(self):
        """Test the fully integrated mage equipment system."""
        # Create a mage
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

        # Assign mage job
        JobManager.assign(mage, 'mage')

        # Should have weapon equipped
        assert mage.weapon is not None

        # Check two-handed weapon restrictions
        if (mage.weapon and
                hasattr(mage.weapon, 'two_handed') and
                mage.weapon.two_handed):
            # Offhand should be restricted
            assert (mage.offhand is None or
                    not hasattr(mage.offhand, 'stats'))


class TestCombatIntegration:
    """Test combat system integration."""

    def test_warrior_combat_effectiveness(self):
        """Test that warriors are effective in combat."""
        # Create warrior
        warrior = Actor(
            name="Test Warrior",
            base_stats={
                'health': 100,
                'attack': 20,
                'defense': 10
            }
        )
        JobManager.assign(warrior, 'warrior')

        # Create enemy
        enemy = Actor(
            name="Test Enemy",
            base_stats={
                'health': 80,
                'attack': 15,
                'defense': 5
            }
        )

        # Test combat
        combat = CombatCapabilities(character=warrior, enemy=enemy)
        initial_enemy_hp = enemy.current_health

        outcome = combat.calculate_damage(warrior, enemy)

        # Warrior should deal damage
        assert enemy.current_health < initial_enemy_hp
        assert isinstance(outcome, str)

    def test_damage_calculation_integration(self):
        """Test integrated damage calculation system."""
        attacker = Actor(
            name="Attacker",
            base_stats={'attack': 30, 'defense': 0}
        )
        defender = Actor(
            name="Defender",
            base_stats={'attack': 0, 'defense': 10}
        )

        combat = CombatCapabilities(character=attacker, enemy=defender)
        
        initial_hp = defender.current_health
        combat.calculate_damage(attacker, defender)
        
        # Damage should be dealt
        assert defender.current_health < initial_hp


class TestResourceManagement:
    """Test resource management integration."""

    def test_health_management_integration(self):
        """Test health management in combat scenarios."""
        actor = Actor(
            name="Test Actor",
            base_stats={'health': 100}
        )

        # Test damage and restoration
        actor.take_damage(40)
        assert actor.current_health == 60

        # Test restoration
        actor.restore_all()
        assert actor.current_health == actor.max_health

    def test_stat_calculation_integration(self):
        """Test that stat calculations work with equipment."""
        actor = Actor(
            name="Test Actor",
            base_stats={
                'health': 100,
                'attack': 15,
                'defense': 8
            }
        )

        # Test basic calculations
        total_damage = actor.get_total_damage()
        total_defense = actor.get_total_defense()

        assert total_damage >= 0
        assert total_defense >= 0

        # Test with job equipment
        JobManager.assign(actor, 'warrior')
        
        equipped_damage = actor.get_total_damage()
        equipped_defense = actor.get_total_defense()

        # Should at least maintain or improve stats
        assert equipped_damage >= total_damage
        assert equipped_defense >= total_defense


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    pytest.main([__file__, "-v"])
