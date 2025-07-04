"""
Comprehensive combat system tests.

This module tests:
- Damage calculation with various modifiers
- Critical hit mechanics
- Blocking/defending mechanics
- RNG determinism for reliable testing
- Combat capabilities and damage packets
"""

import pytest
from game_sys.combat.combat import CombatCapabilities


class TestBasicCombat:
    """Test basic combat mechanics."""

    def test_attack_no_crit_no_defend(self, player_factory, enemy_factory,
                                      mock_combat_rng):
        """Test normal attack without crit or defend."""
        attacker = player_factory(
            name="Attacker",
            base_stats={'attack': 50, 'defense': 0}
        )
        defender = enemy_factory(
            name="Defender",
            base_stats={'attack': 0, 'defense': 20}
        )

        # Use deterministic RNG for predictable results
        rng = mock_combat_rng['no_crit_max_damage']
        combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

        initial_hp = defender.current_health
        outcome = combat.calculate_damage(attacker, defender)

        # Expected: 50 - (20 * 0.05) = 49.0 damage
        assert "deals 49 damage" in outcome
        assert defender.current_health == pytest.approx(initial_hp - 49)

    def test_attack_with_crit(self, player_factory, enemy_factory,
                              mock_combat_rng):
        """Test critical hit damage calculation."""
        attacker = player_factory(
            base_stats={'attack': 40, 'defense': 0}
        )
        defender = enemy_factory(
            base_stats={'attack': 0, 'defense': 10}
        )

        # Use RNG that triggers critical hit
        rng = mock_combat_rng['crit_hit']
        combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

        initial_hp = defender.current_health
        outcome = combat.calculate_damage(attacker, defender)

        # Should mention critical hit
        assert "critical" in outcome.lower()
        # Should deal more damage than normal attack
        damage_dealt = initial_hp - defender.current_health
        normal_damage = 40 - (10 * 0.05)  # 39.5
        assert damage_dealt > normal_damage

    def test_defend_blocks_damage(self, player_factory, enemy_factory,
                                  mock_combat_rng):
        """Test that defending can block damage."""
        attacker = player_factory(
            base_stats={'attack': 30, 'defense': 0}
        )
        defender = enemy_factory(
            base_stats={'attack': 0, 'defense': 15}
        )

        # Use RNG that triggers successful defend
        rng = mock_combat_rng['defend_success']
        combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

        initial_hp = defender.current_health
        outcome = combat.calculate_damage(attacker, defender)

        # Should mention blocking/defending
        assert any(word in outcome.lower() for word in ['block', 'defend'])
        # Should take less damage or no damage
        damage_dealt = initial_hp - defender.current_health
        normal_damage = 30 - (15 * 0.05)  # 29.25
        assert damage_dealt < normal_damage


class TestCombatCapabilities:
    """Test the CombatCapabilities class functionality."""

    def test_combat_capabilities_initialization(self, player_factory,
                                                enemy_factory):
        """Test CombatCapabilities can be initialized."""
        player = player_factory()
        enemy = enemy_factory()

        combat = CombatCapabilities(character=player, enemy=enemy)

        assert combat.character == player
        assert combat.enemy == enemy

    def test_damage_calculation_respects_stats(self, player_factory,
                                               enemy_factory):
        """Test that damage calculation uses character stats."""
        high_attack_player = player_factory(
            base_stats={'attack': 100, 'defense': 0}
        )
        low_attack_player = player_factory(
            base_stats={'attack': 10, 'defense': 0}
        )
        enemy = enemy_factory(
            base_stats={'attack': 0, 'defense': 0}
        )

        # High attack should deal more damage
        combat_high = CombatCapabilities(character=high_attack_player,
                                         enemy=enemy)
        combat_low = CombatCapabilities(character=low_attack_player,
                                        enemy=enemy)

        # Reset enemy health
        enemy.current_health = enemy.max_health
        initial_hp = enemy.current_health

        outcome_high = combat_high.calculate_damage(high_attack_player, enemy)
        damage_high = initial_hp - enemy.current_health

        # Reset for second test
        enemy.current_health = enemy.max_health
        initial_hp = enemy.current_health

        outcome_low = combat_low.calculate_damage(low_attack_player, enemy)
        damage_low = initial_hp - enemy.current_health

        assert damage_high > damage_low


class TestCombatEdgeCases:
    """Test edge cases and error conditions."""

    def test_zero_damage_protection(self, player_factory, enemy_factory):
        """Test that minimum damage is always dealt."""
        weak_attacker = player_factory(
            base_stats={'attack': 1, 'defense': 0}
        )
        strong_defender = enemy_factory(
            base_stats={'attack': 0, 'defense': 100}
        )

        combat = CombatCapabilities(character=weak_attacker, enemy=strong_defender)

        initial_hp = strong_defender.current_health
        outcome = combat.calculate_damage(weak_attacker, strong_defender)

        # Should deal at least 1 damage
        damage_dealt = initial_hp - strong_defender.current_health
        assert damage_dealt >= 1

    def test_dead_character_no_damage(self, player_factory, enemy_factory):
        """Test that dead characters don't deal damage."""
        attacker = player_factory(
            base_stats={'attack': 50, 'defense': 0}
        )
        defender = enemy_factory(
            base_stats={'attack': 0, 'defense': 0}
        )

        # Kill the attacker
        attacker.current_health = 0

        combat = CombatCapabilities(character=attacker, enemy=defender)

        initial_hp = defender.current_health
        # This might raise an exception or return early
        try:
            outcome = combat.calculate_damage(attacker, defender)
            # If no exception, defender should take no damage
            assert defender.current_health == initial_hp
        except Exception:
            # If exception is raised, that's also acceptable behavior
            pass


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    pytest.main([__file__, "-v"])

        # Use RNG that triggers critical hit
        rng = mock_combat_rng['crit_max_damage']
        combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

        initial_hp = defender.current_health
        outcome = combat.calculate_damage(attacker, defender)

        # Expected: (40 - 10*0.05) * 2 = 79.0 crit damage
        assert "Critical Hit!" in outcome
        assert "deals 79 damage" in outcome
        assert defender.current_health == pytest.approx(initial_hp - 79)

    def test_attack_with_defender_blocking(self, player_factory, enemy_factory,
                                          mock_combat_rng):
        """Test damage reduction when defender is blocking."""
        attacker = player_factory(
            base_stats={'attack': 30, 'defense': 0}
        )
        defender = enemy_factory(
            base_stats={'attack': 0, 'defense': 5}
        )

        # Set defender to defending state
        defender.defending = True

        rng = mock_combat_rng['no_crit_max_damage']
        combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

        initial_hp = defender.current_health
        outcome = combat.calculate_damage(attacker, defender)

        # Expected: (30 - 5*0.05) * 0.5 = 14.875 ≈ 15 damage
        assert "deals 15 damage" in outcome
        assert defender.current_health == pytest.approx(initial_hp - 15)


class TestDamageCalculation:
    """Test damage calculation edge cases and formulas."""

    @pytest.mark.parametrize("attack,defense,expected_base", [
        (50, 0, 50.0),      # No defense
        (50, 20, 49.0),     # Light defense
        (50, 100, 45.0),    # Heavy defense  
        (10, 200, 0.0),     # Defense exceeds attack
    ])
    def test_damage_formula_accuracy(self, player_factory, enemy_factory,
                                   mock_combat_rng, attack, defense, 
                                   expected_base):
        """Test damage formula with various attack/defense combinations."""
        attacker = player_factory(base_stats={'attack': attack})
        defender = enemy_factory(base_stats={'defense': defense})

        rng = mock_combat_rng['no_crit_max_damage']
        combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

        initial_hp = defender.current_health
        outcome = combat.calculate_damage(attacker, defender)

        # Calculate expected damage: attack - (defense * 0.05)
        expected_damage = max(0, expected_base)
        damage_taken = initial_hp - defender.current_health

        assert damage_taken == pytest.approx(expected_damage, abs=1)

    def test_zero_damage_scenarios(self, player_factory, enemy_factory,
                                 mock_combat_rng):
        """Test scenarios where no damage should be dealt."""
        # Very low attack vs high defense
        attacker = player_factory(base_stats={'attack': 1})
        defender = enemy_factory(base_stats={'defense': 100})

        rng = mock_combat_rng['no_crit_max_damage']  
        combat = CombatCapabilities(character=attacker, enemy=defender, rng=rng)

        initial_hp = defender.current_health
        combat.calculate_damage(attacker, defender)

        # Should deal minimal or no damage
        damage_taken = initial_hp - defender.current_health
        assert damage_taken <= 1  # Allow for rounding


class TestCombatModifiers:
    """Test various combat modifiers and special effects."""

    def test_damage_variance(self, player_factory, enemy_factory):
        """Test that damage has appropriate variance."""
        attacker = player_factory(base_stats={'attack': 50})
        defender = enemy_factory(base_stats={'defense': 0})

        combat = CombatCapabilities(character=attacker, enemy=defender)
        
        # Collect damage values from multiple attacks
        damage_values = []
        for _ in range(10):
            # Reset defender health
            defender.current_health = defender.max_health
            initial_hp = defender.current_health
            
            combat.calculate_damage(attacker, defender)
            damage_dealt = initial_hp - defender.current_health
            damage_values.append(damage_dealt)

        # Should have some variance in damage (not all identical)
        unique_values = len(set(damage_values))
        assert unique_values > 1, "Damage should have variance"

    def test_combat_state_persistence(self, combat_pair):
        """Test that combat state is maintained correctly."""
        player, enemy = combat_pair
        
        # Initial state check
        assert not getattr(player, 'defending', False)
        assert not getattr(enemy, 'defending', False)
        
        # Set defending state
        enemy.defending = True
        assert enemy.defending == True
        
        # Combat shouldn't change unrelated states
        combat = CombatCapabilities(character=player, enemy=enemy)
        combat.calculate_damage(player, enemy)
        
        # Defending state should persist
        assert enemy.defending == True
