import asyncio
from game_sys.character.character_factory import create_character
from game_sys.skills.passive_manager import PassiveManager
from game_sys.hooks.hooks_setup import ON_CHARACTER_CREATED, emit


async def test_final_verification():
    print("=== Final System Verification ===")
    
    # Test 1: Single resource drains work
    print("\n--- Single Resource Drains ---")
    
    # Mana drain
    hero_mana = create_character('hero')
    hero_mana.passive_ids = ['battle_meditation']
    PassiveManager.register_actor(hero_mana)
    emit(ON_CHARACTER_CREATED, actor=hero_mana)
    
    print(f"Mana hero - Max MP: {hero_mana.max_mana:.0f}")
    hero_mana.current_mana = hero_mana.max_mana * 0.5  # Set to 50%
    hero_mana.current_health = hero_mana.max_health * 0.5  # Set to 50%
    hero_mana.restore_all()
    mana_restored = hero_mana.current_mana == (hero_mana.max_mana * 0.5)
    health_restored = hero_mana.current_health == hero_mana.max_health
    print(f"✓ Mana stays drained: {mana_restored}")
    print(f"✓ Health gets restored: {health_restored}")
    
    # Health drain  
    hero_health = create_character('hero')
    hero_health.passive_ids = ['berserker_rage']
    PassiveManager.register_actor(hero_health)
    emit(ON_CHARACTER_CREATED, actor=hero_health)
    
    hero_health.current_health = hero_health.max_health * 0.3  # Set to 30%
    hero_health.current_mana = hero_health.max_mana * 0.3  # Set to 30%
    hero_health.restore_all()
    health_stays = hero_health.current_health == (hero_health.max_health * 0.3)
    mana_restored2 = hero_health.current_mana == hero_health.max_mana
    print(f"✓ Health stays drained: {health_stays}")
    print(f"✓ Mana gets restored: {mana_restored2}")
    
    # Stamina drain
    hero_stamina = create_character('hero')
    hero_stamina.passive_ids = ['endless_sprint']
    PassiveManager.register_actor(hero_stamina)
    emit(ON_CHARACTER_CREATED, actor=hero_stamina)
    
    hero_stamina.current_stamina = hero_stamina.max_stamina * 0.2  # Set to 20%
    hero_stamina.current_health = hero_stamina.max_health * 0.2  # Set to 20%
    hero_stamina.restore_all()
    stamina_stays = hero_stamina.current_stamina == (hero_stamina.max_stamina * 0.2)
    health_restored2 = hero_stamina.current_health == hero_stamina.max_health
    print(f"✓ Stamina stays drained: {stamina_stays}")
    print(f"✓ Health gets restored: {health_restored2}")
    
    # Test 2: Level up bonuses persist drain
    print("\n--- Level Up Persistence ---")
    initial_mana = hero_mana.current_mana
    initial_defense = hero_mana.get_stat('defense')
    
    hero_mana.gain_xp(hero_mana._xp_for_next())
    await asyncio.sleep(0.1)
    
    final_mana = hero_mana.current_mana
    final_defense = hero_mana.get_stat('defense')
    
    mana_unchanged = abs(initial_mana - final_mana) < 1  # Allow small drift
    defense_increased = final_defense > initial_defense
    
    print(f"✓ Mana drain persists through level up: {mana_unchanged}")
    print(f"✓ Defense bonus applied: {defense_increased}")
    print(f"  Defense: {initial_defense:.1f} → {final_defense:.1f}")
    
    # Test 3: Multiple drains work
    print("\n--- Multiple Drains ---")
    hero_multi = create_character('hero')
    hero_multi.passive_ids = ['battle_meditation', 'berserker_rage']
    PassiveManager.register_actor(hero_multi)
    emit(ON_CHARACTER_CREATED, actor=hero_multi)
    
    # Set all resources to 50%
    hero_multi.current_mana = hero_multi.max_mana * 0.5
    hero_multi.current_health = hero_multi.max_health * 0.5
    hero_multi.current_stamina = hero_multi.max_stamina * 0.5
    hero_multi.restore_all()
    
    mana_stays2 = hero_multi.current_mana == (hero_multi.max_mana * 0.5)
    health_stays2 = hero_multi.current_health == (hero_multi.max_health * 0.5)
    stamina_restored2 = hero_multi.current_stamina == hero_multi.max_stamina
    
    print(f"✓ Mana stays drained: {mana_stays2}")
    print(f"✓ Health stays drained: {health_stays2}")
    print(f"✓ Stamina gets restored: {stamina_restored2}")
    
    print("\n=== System Verification Complete ===")
    all_tests_pass = all([
        mana_restored, health_restored,
        health_stays, mana_restored2,
        stamina_stays, health_restored2,
        mana_unchanged, defense_increased,
        mana_stays2, health_stays2, stamina_restored2
    ])
    print(f"🎯 All tests passed: {all_tests_pass}")


if __name__ == "__main__":
    asyncio.run(test_final_verification())
