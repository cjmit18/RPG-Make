import pytest
from game_sys.core.scaling_manager import ScalingManager
from game_sys.config.config_manager import ConfigManager
from game_sys.character.leveling_manager import LevelingManager

class DummyActor:
    def __init__(self, base_stats=None, grade=None, grade_name=None, rarity=None, 
                 rarity_name=None, job_level=None, level=1, spent_stat_points=0):
        self.base_stats = base_stats or {'strength': 10, 'vitality': 10, 'dexterity': 10, 
                                         'intelligence': 10, 'wisdom': 10, 'constitution': 10, 
                                         'luck': 10}
        self.grade = grade
        self.grade_name = grade_name
        self.rarity = rarity
        self.rarity_name = rarity_name
        self.job_level = job_level
        self.level = level
        self.spent_stat_points = spent_stat_points
        self.name = "TestActor"
        self.leveling_manager = LevelingManager()
        self.experience = 0
    
    def get_stat(self, stat_name):
        return ScalingManager.compute_stat(self, stat_name)

def test_grade_and_rarity_scaling():
    cfg = ConfigManager()
    # Use config values for grade and rarity multipliers
    grade_map = cfg.get('constants.grade.stat_multiplier')
    rarity_map = cfg.get('constants.rarity.stat_multiplier')
    grades = cfg.get('defaults.grades')
    rarities = cfg.get('defaults.rarities')

    # Test all grade/rarity combinations
    for grade_name in grades:
        for rarity_name in rarities:
            actor = DummyActor(grade_name=grade_name, rarity_name=rarity_name)
            base = 10.0
            actor.base_stats['strength'] = base
            # Should apply both grade and rarity multipliers
            expected = base
            if isinstance(grade_map, dict):
                expected *= (1.0 + grade_map.get(grade_name, 0.0))
            elif isinstance(grade_map, (float, int)):
                expected *= (1.0 + float(grade_map))
            if isinstance(rarity_map, dict):
                expected *= (1.0 + rarity_map.get(rarity_name, 0.0))
            elif isinstance(rarity_map, (float, int)):
                expected *= (1.0 + float(rarity_map))
            result = ScalingManager.compute_stat(actor, 'strength')
            assert abs(result - expected) < 1e-6, f"Scaling failed for grade={grade_name}, rarity={rarity_name}: got {result}, expected {expected}"

def test_flat_fallback_scaling():
    cfg = ConfigManager()
    # Simulate flat float fallback
    actor = DummyActor(grade=0, rarity='COMMON')
    actor.base_stats['strength'] = 10.0
    # Temporarily patch config to flat float
    orig_grade = cfg.get('constants.grade.stat_multiplier')
    orig_rarity = cfg.get('constants.rarity.stat_multiplier')
    cfg.set('constants.grade.stat_multiplier', 0.1)
    cfg.set('constants.rarity.stat_multiplier', 0.2)
    expected = 10.0 * 1.1 * 1.2
    result = ScalingManager.compute_stat(actor, 'strength')
    assert abs(result - expected) < 1e-6, f"Flat fallback scaling failed: got {result}, expected {expected}"
    # Restore config
    cfg.set('constants.grade.stat_multiplier', orig_grade)
    cfg.set('constants.rarity.stat_multiplier', orig_rarity)

def test_level_based_stat_allocation():
    """Test that level progression provides correct number of stat points."""
    cfg = ConfigManager()
    points_per_level = cfg.get('constants.leveling.stat_points_per_level', 3)
    
    # Test various levels
    for level in [1, 2, 5, 10, 20]:
        actor = DummyActor(level=level)
        expected_points = (level - 1) * points_per_level  # Level 1 starts with 0 points
        available_points = actor.leveling_manager.calculate_stat_points_available(actor)
        assert available_points == expected_points, f"At level {level}, expected {expected_points} stat points, got {available_points}"
        
        # Test spending points
        if level > 1:
            # Spend half the points
            spent = expected_points // 2
            actor.spent_stat_points = spent
            actor.base_stats['strength'] += spent  # Simulate spending on strength
            
            # Check updated available points
            available_points = actor.leveling_manager.calculate_stat_points_available(actor)
            assert available_points == expected_points - spent, f"After spending {spent} points, expected {expected_points - spent} points, got {available_points}"
            
            # Check that stat value reflects points spent
            expected_strength = 10 + spent  # Base 10 + spent points
            assert actor.base_stats['strength'] == expected_strength, f"Expected strength to be {expected_strength}, got {actor.base_stats['strength']}"

def test_stat_allocation_and_scaling():
    """Test that allocated stat points are properly scaled by grade and rarity."""
    cfg = ConfigManager()
    grade_map = cfg.get('constants.grade.stat_multiplier')
    rarity_map = cfg.get('constants.rarity.stat_multiplier')
    
    # Use a high grade and rarity for more noticeable scaling
    grade_name = "SEVEN"  # Highest grade
    rarity_name = "LEGENDARY"  # High rarity
    
    # Create actor with level 10 (should have 27 stat points)
    actor = DummyActor(level=10, grade_name=grade_name, rarity_name=rarity_name)
    available_points = actor.leveling_manager.calculate_stat_points_available(actor)
    
    # Spend all points on strength
    actor.base_stats['strength'] = 10 + available_points
    actor.spent_stat_points = available_points
    
    # Calculate expected scaling
    base_strength = 10 + available_points
    expected = base_strength
    if isinstance(grade_map, dict):
        expected *= (1.0 + grade_map.get(grade_name, 0.0))
    elif isinstance(grade_map, (float, int)):
        expected *= (1.0 + float(grade_map))
    if isinstance(rarity_map, dict):
        expected *= (1.0 + rarity_map.get(rarity_name, 0.0))
    elif isinstance(rarity_map, (float, int)):
        expected *= (1.0 + float(rarity_map))
    
    # Check actual scaled stat
    result = ScalingManager.compute_stat(actor, 'strength')
    assert abs(result - expected) < 1e-6, f"Level scaling with grade/rarity failed: got {result}, expected {expected}"

def test_derived_stat_scaling_with_level():
    """Test that derived stats scale properly with level progression."""
    # Create actors at different levels with same grade/rarity
    grade_name = "THREE"
    rarity_name = "RARE"
    
    actors = [
        DummyActor(level=1, grade_name=grade_name, rarity_name=rarity_name),
        DummyActor(level=5, grade_name=grade_name, rarity_name=rarity_name),
        DummyActor(level=10, grade_name=grade_name, rarity_name=rarity_name)
    ]
    
    # Allocate all points to strength for each actor
    for actor in actors:
        points = actor.leveling_manager.calculate_stat_points_available(actor)
        actor.base_stats['strength'] = 10 + points
        actor.spent_stat_points = points
    
    # Derived stats like attack and  should scale with strength
    for i in range(1, len(actors)):
        prev_attack = actors[i-1].get_stat('attack')
        curr_attack = actors[i].get_stat('attack')
        assert curr_attack > prev_attack, f"Attack should increase with level: level {actors[i-1].level}={prev_attack}, level {actors[i].level}={curr_attack}"
        
        prev_dmg = actors[i-1].get_stat('')
        curr_dmg = actors[i].get_stat('')
        assert curr_dmg > prev_dmg, f"Physical damage should increase with level: level {actors[i-1].level}={prev_dmg}, level {actors[i].level}={curr_dmg}"

def test_complex_level_grade_rarity_interaction():
    """Test the combined effects of level, grade, and rarity on stat scaling."""
    cfg = ConfigManager()
    points_per_level = cfg.get('constants.leveling.stat_points_per_level', 3)
    grade_map = cfg.get('constants.grade.stat_multiplier')
    rarity_map = cfg.get('constants.rarity.stat_multiplier')
    
    # Test multiple combinations of level, grade, and rarity
    test_cases = [
        # level, grade, rarity
        (1, "ONE", "COMMON"),
        (5, "THREE", "UNCOMMON"),
        (10, "FIVE", "RARE"),
        (20, "SEVEN", "LEGENDARY")
    ]
    
    for level, grade, rarity in test_cases:
        actor = DummyActor(level=level, grade_name=grade, rarity_name=rarity)
        
        # Allocate all points to strength
        points = (level - 1) * points_per_level
        actor.base_stats['strength'] = 10 + points
        actor.spent_stat_points = points
        
        # Calculate expected strength after scaling
        base_strength = 10 + points
        expected = base_strength
        
        # Apply grade multiplier
        if isinstance(grade_map, dict) and grade in grade_map:
            expected *= (1.0 + grade_map[grade])
        elif isinstance(grade_map, (float, int)):
            expected *= (1.0 + float(grade_map))
            
        # Apply rarity multiplier
        if isinstance(rarity_map, dict) and rarity in rarity_map:
            expected *= (1.0 + rarity_map[rarity])
        elif isinstance(rarity_map, (float, int)):
            expected *= (1.0 + float(rarity_map))
        
        # Check actual scaled stat
        result = ScalingManager.compute_stat(actor, 'strength')
        assert abs(result - expected) < 1e-6, f"Complex scaling (L{level}/G{grade}/R{rarity}) failed: got {result}, expected {expected}"

def test_error_handling_in_level_scaling():
    """Test that scaling manager handles missing or invalid level data gracefully."""
    # Test with missing level attribute
    actor = DummyActor()
    delattr(actor, 'level')  # Remove level attribute
    
    # Should still compute stats without error
    try:
        strength = actor.get_stat('strength')
        assert strength >= 10, "Even with missing level, should return at least base strength"
    except Exception as e:
        assert False, f"Scaling failed with missing level: {e}"
    
    # Test with invalid level value
    actor = DummyActor()
    actor.level = "invalid"  # Non-integer level
    
    # Should handle invalid level gracefully
    try:
        strength = actor.get_stat('strength')
        assert strength >= 10, "Even with invalid level, should return at least base strength"
    except Exception as e:
        assert False, f"Scaling failed with invalid level: {e}"

def test_grade_rarity_stat_point_bonuses():
    """Test that grade and rarity provide proper stat point bonuses per level."""
    cfg = ConfigManager()
    leveling_mgr = LevelingManager()
    
    # Get grade and rarity multipliers from config
    grade_map = cfg.get('constants.grade.stat_multiplier', {})
    rarity_map = cfg.get('constants.rarity.stat_multiplier', {})
    base_points = cfg.get('constants.leveling.stat_points_per_level', 3)
    
    # Test various grade/rarity combinations
    test_cases = [
        # grade, rarity
        ("ONE", "COMMON"),
        ("THREE", "RARE"),
        ("FIVE", "EPIC"),
        ("SEVEN", "LEGENDARY")
    ]
    
    for grade, rarity in test_cases:
        # Create actor with the test grade/rarity
        actor = DummyActor(grade_name=grade, rarity_name=rarity, level=10)
        
        # Get points per level from the LevelingManager
        points_per_level = leveling_mgr.get_stat_points_per_level(actor)
        
        # Calculate expected total points
        expected_total = (actor.level - 1) * points_per_level
        
        # Get actual available points
        actual_points = leveling_mgr.calculate_stat_points_available(actor)
        
        # Verify calculations
        assert actual_points == expected_total, (
            f"Grade {grade}, Rarity {rarity} should give {points_per_level} "
            f"points per level, total {expected_total} at level {actor.level}, "
            f"but got {actual_points}"
        )
        

def test_stat_points_on_levelup():
    """
    Test that leveling up awards the correct number of stat points based on 
    grade/rarity.
    """
    leveling_mgr = LevelingManager()
    
    # Create actor with grade and rarity
    actor = DummyActor(grade_name="FOUR", rarity_name="RARE", level=1)
    initial_points = leveling_mgr.calculate_stat_points_available(actor)
    
    # Level up the actor and check for new points
    leveling_mgr.level_up(actor)
    points_after_levelup = leveling_mgr.calculate_stat_points_available(actor)
    
    # Points gained should match get_stat_points_per_level with grade/rarity bonuses
    points_per_level = leveling_mgr.get_stat_points_per_level(actor)
    expected_points = initial_points + points_per_level
    
    assert points_after_levelup == expected_points, (
        f"Actor should gain {points_per_level} points when leveling up from 1 to 2 "
        f"with grade FOUR and rarity RARE, but got "
        f"{points_after_levelup - initial_points}"
    )
    
    # Level up multiple times and check cumulative points
    for _ in range(3):  # Level from 2 to 5
        leveling_mgr.level_up(actor)
    
    points_after_multiple = leveling_mgr.calculate_stat_points_available(actor)
    expected_total = (actor.level - 1) * points_per_level
    
    assert points_after_multiple == expected_total, (
        f"Actor at level {actor.level} should have {expected_total} total points "
        f"but has {points_after_multiple}"
    )


def test_initial_stat_boost_from_grade_rarity():
    """Test that initial stats are boosted by grade and rarity multipliers."""
    # Create actors with different grade/rarity combinations
    base_actor = DummyActor(grade_name="ONE", rarity_name="COMMON")
    mid_actor = DummyActor(grade_name="THREE", rarity_name="RARE")
    high_actor = DummyActor(grade_name="SEVEN", rarity_name="LEGENDARY")
    
    # All should have the same base stats (10)
    assert base_actor.base_stats['strength'] == 10
    assert mid_actor.base_stats['strength'] == 10
    assert high_actor.base_stats['strength'] == 10
    
    # But computed stats should reflect grade/rarity scaling
    base_str = base_actor.get_stat('strength')
    mid_str = mid_actor.get_stat('strength')
    high_str = high_actor.get_stat('strength')
    
    # Higher grade/rarity should result in higher scaled stats
    assert base_str < mid_str < high_str, (
        f"Stats should scale with grade/rarity: "
        f"base={base_str}, mid={mid_str}, high={high_str}"
    )
    
    # Get the multipliers directly from our test objects
    cfg = ConfigManager()
    grade_map = cfg.get('constants.grade.stat_multiplier', {})
    rarity_map = cfg.get('constants.rarity.stat_multiplier', {})
    
    # Make sure the maps exist
    assert isinstance(grade_map, dict), "Grade multiplier map not found in config"
    assert isinstance(rarity_map, dict), "Rarity multiplier map not found in config"
    
    # Check the grade/rarity combos have different multipliers
    grade_one_mult = grade_map.get("ONE", 0)
    grade_three_mult = grade_map.get("THREE", 0)
    grade_seven_mult = grade_map.get("SEVEN", 0)
    
    rarity_common_mult = rarity_map.get("COMMON", 0)
    rarity_rare_mult = rarity_map.get("RARE", 0)
    rarity_legendary_mult = rarity_map.get("LEGENDARY", 0)
    
    # Verify multipliers are ascending
    assert grade_one_mult < grade_three_mult < grade_seven_mult
    assert rarity_common_mult < rarity_rare_mult < rarity_legendary_mult
