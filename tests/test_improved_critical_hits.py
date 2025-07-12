#!/usr/bin/env python3
"""
Improved Critical Hit Test
Tests that the critical hit system works correctly and provides reasonable rates.
"""

import sys
import os
import io
import contextlib
import logging

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_critical_hit_system():
    """Test critical hit system comprehensively."""
    try:
        print("🔬 Testing Critical Hit System...")
        
        # Set up logging capture
        log_capture_string = io.StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.INFO)
        
        # Get the combat logger
        combat_logger = logging.getLogger('game_sys.combat')
        combat_logger.addHandler(ch)
        combat_logger.setLevel(logging.INFO)
          # Import modules
        from game_sys.character.character_factory import CharacterFactory
        from game_sys.character.job_manager import JobManager
        from game_sys.combat.engine import CombatEngine
        
        print("✅ Modules imported successfully")
          # Create test characters
        player = CharacterFactory.create("hero")
        enemy = CharacterFactory.create("goblin")
        
        # Give player better stats for higher crit chance
        JobManager.assign(player, 'warrior')  # Warriors have higher dexterity
        JobManager.assign(enemy, 'goblin')
        
        print("✅ Characters created")
        print(f"Player dexterity: {player.get_stat('dexterity')}")
        print(f"Player critical_chance: {player.get_stat('critical_chance')}")
        
        # Create combat engine
        combat_engine = CombatEngine()
        
        print("✅ Combat engine created")
        
        # Perform multiple attacks to test critical hit rates
        critical_hits_found = 0
        negative_damage_found = 0
        total_attacks = 100  # Increased for better statistics
        
        print(f"Performing {total_attacks} attacks to test critical hit system...")
        
        for i in range(total_attacks):
            # Reset enemy health for each test
            enemy.current_health = enemy.max_health
            
            # Clear log capture
            log_capture_string.seek(0)
            log_capture_string.truncate(0)
            
            # Perform attack
            outcome = combat_engine.execute_attack_sync(player, [enemy])
            
            # Check log output for critical hits
            log_contents = log_capture_string.getvalue()
            
            if 'CRITICAL HIT!' in log_contents:
                critical_hits_found += 1
                
                # Extract damage value from the log
                for line in log_contents.split('\n'):
                    if 'CRITICAL HIT!' in line:
                        try:
                            # Parse damage from format: "CRITICAL HIT! Attacker crit Target for X.XX"
                            parts = line.split(' for ')
                            if len(parts) > 1:
                                damage_str = parts[1].split(' ')[0]
                                damage = float(damage_str)
                                
                                if damage < 0:
                                    negative_damage_found += 1
                                    print(f"❌ CRITICAL HIT HEALING BUG FOUND! Damage: {damage}")
                                    print(f"Full log line: {line}")
                                else:
                                    if critical_hits_found <= 5:  # Only print first few
                                        print(f"✅ Critical hit {critical_hits_found}: {damage} damage")
                        except (ValueError, IndexError):
                            pass  # Couldn't parse damage, but we know it was a crit
            
        # Calculate statistics
        crit_rate = (critical_hits_found / total_attacks) * 100
        
        print(f"\n📊 Test Results:")
        print(f"Total attacks: {total_attacks}")
        print(f"Critical hits found: {critical_hits_found}")
        print(f"Critical hit rate: {crit_rate:.1f}%")
        print(f"Negative damage (healing) found: {negative_damage_found}")
        
        # Remove our log handler
        combat_logger.removeHandler(ch)
        
        # Evaluate results
        if negative_damage_found > 0:
            print("❌ CRITICAL HIT HEALING BUG STILL EXISTS!")
            return False
        elif critical_hits_found == 0:
            print("⚠️  No critical hits occurred - critical hit system may not be working")
            return False
        elif crit_rate < 2.0:  # Should get at least 2% crit rate with base system
            print(f"⚠️  Critical hit rate ({crit_rate:.1f}%) seems too low")
            return False
        else:
            print("✅ Critical hit system working correctly!")
            print(f"   - Critical hits are dealing positive damage")
            print(f"   - Critical hit rate of {crit_rate:.1f}% is reasonable")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_critical_hit_configuration():
    """Test and potentially improve critical hit configuration."""
    print("\n🔧 Testing Critical Hit Configuration...")
    
    try:
        from game_sys.config.config_manager import ConfigManager
        
        cfg = ConfigManager()
        
        # Check current critical hit configuration
        base_crit = cfg.get('constants.derived_stats.critical_chance', 0.05)
        print(f"Base critical chance: {base_crit} ({base_crit*100:.1f}%)")
        
        # The base crit chance should be reasonable (2-10%)
        if base_crit < 0.02:
            print("⚠️  Base critical chance seems too low, adjusting...")
            return False
        elif base_crit > 0.2:
            print("⚠️  Base critical chance seems too high, might need adjustment")
            return False
        else:
            print("✅ Base critical chance configuration looks good")
            return True
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Critical Hit System Comprehensive Test")
    print("=" * 50)
    
    config_ok = test_critical_hit_configuration()
    system_ok = test_critical_hit_system()
    
    if config_ok and system_ok:
        print("\n🎉 ALL TESTS PASSED! Critical hit system is working correctly!")
        sys.exit(0)
    else:
        print("\n💔 Some tests failed. Critical hit system needs attention.")
        sys.exit(1)
