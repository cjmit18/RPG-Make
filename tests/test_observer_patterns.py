"""
Test Event-Driven Architecture - Achievement and Notification Systems

This test demonstrates the complete observer pattern implementation
by creating characters, leveling them up, and verifying that the
achievement and notification systems properly react to events.
"""
import asyncio
import pytest
import logging
from rpg_engine.core.engine import AsyncGameEngine
from rpg_engine.core.event_bus import EventBus
from rpg_engine.core.config import GameConfig
from rpg_engine.systems.character.character_system import CharacterSystem
from rpg_engine.systems.achievements import AchievementSystem
from rpg_engine.systems.notifications import NotificationSystem

# Configure logging for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
async def game_setup():
    """Set up a complete game environment for testing"""
    # Create and initialize the game engine
    engine = AsyncGameEngine()
    await engine.initialize_async()
    
    # Get the services we need
    event_bus = engine.service_container.get(EventBus)
    config = engine.service_container.get(GameConfig)
    achievement_system = engine.service_container.get(AchievementSystem)
    notification_system = engine.service_container.get(NotificationSystem)
    
    # Create character system
    character_system = CharacterSystem(event_bus, config)
    
    yield {
        'engine': engine,
        'event_bus': event_bus,
        'config': config,
        'character_system': character_system,
        'achievement_system': achievement_system,
        'notification_system': notification_system
    }
    
    # Cleanup
    await engine.shutdown_async()


@pytest.mark.asyncio
async def test_complete_observer_pattern_workflow(game_setup):
    """
    Test the complete event-driven workflow:
    1. Create characters (triggers achievements and notifications)
    2. Level up characters (triggers more achievements and notifications)  
    3. Increase stats (triggers stat-based achievements)
    4. Verify all observer patterns worked correctly
    """
    services = game_setup
    character_system = services['character_system']
    achievement_system = services['achievement_system']
    notification_system = services['notification_system']
    
    logger.info("🎮 Starting complete observer pattern workflow test")
    
    # Step 1: Create first character (should trigger first character achievement + notification)
    logger.info("📝 Creating first character...")
    character1 = await character_system.create_character(
        user_id="test_user",
        character_data={
            "name": "Test Hero 1",
            "character_type": "warrior",
            "initial_stats": {
                "strength": 15,
                "dexterity": 12,
                "vitality": 14,
                "intelligence": 10,
                "wisdom": 9,
                "constitution": 13
            }
        }
    )
    
    # Wait for events to propagate
    await asyncio.sleep(0.1)
    
    # Verify first character achievement was unlocked
    unlocked_achievements = achievement_system.get_unlocked_achievements()
    assert len(unlocked_achievements) >= 1, "First character achievement should be unlocked"
    
    first_char_achievement = next(
        (a for a in unlocked_achievements if 'first_character' in a.id), 
        None
    )
    assert first_char_achievement is not None, "First character achievement should exist"
    assert first_char_achievement.unlocked, "First character achievement should be unlocked"
    
    # Verify notification was created
    notifications = notification_system.get_recent_notifications(limit=5)
    character_creation_notifications = [
        n for n in notifications if 'created successfully' in n.message
    ]
    assert len(character_creation_notifications) >= 1, "Character creation notification should exist"
    
    logger.info("✅ First character creation triggered achievements and notifications correctly")
    
    # Step 2: Level up the character multiple times (should trigger level achievements)
    logger.info("📈 Leveling up character to trigger level milestones...")
    
    # Level up to 10 (should trigger level 10 achievement)
    for level in range(2, 11):
        await character_system.level_up_character(character1.id)
        await asyncio.sleep(0.05)  # Brief pause for events
    
    # Verify level 10 achievement
    unlocked_achievements = achievement_system.get_unlocked_achievements()
    level_10_achievement = next(
        (a for a in unlocked_achievements if 'level_10' in a.id),
        None
    )
    assert level_10_achievement is not None, "Level 10 achievement should be unlocked"
    
    # Verify level up notifications
    notifications = notification_system.get_recent_notifications(limit=20)
    level_up_notifications = [
        n for n in notifications if 'Level Up!' in n.message
    ]
    assert len(level_up_notifications) >= 5, "Should have multiple level up notifications"
    
    logger.info("✅ Level up achievements and notifications working correctly")
    
    # Step 3: Increase stats to trigger stat-based achievements
    logger.info("💪 Increasing character stats to trigger stat achievements...")
    
    # Increase strength to 100 (should trigger strength achievement)
    await character_system.increase_stat(character1.id, "strength", 85)  # 15 + 85 = 100
    await asyncio.sleep(0.1)
    
    # Verify strength achievement
    unlocked_achievements = achievement_system.get_unlocked_achievements()
    strength_achievement = next(
        (a for a in unlocked_achievements if 'strength_100' in a.id),
        None
    )
    assert strength_achievement is not None, "Strength 100 achievement should be unlocked"
    
    logger.info("✅ Stat-based achievements working correctly")
    
    # Step 4: Create more characters to test variety achievement
    logger.info("👥 Creating multiple characters to test variety achievement...")
    
    character_names = ["Test Hero 2", "Test Hero 3", "Test Hero 4", "Test Hero 5"]
    for name in character_names:
        await character_system.create_character(
            user_id="test_user",
            character_data={
                "name": name,
                "character_type": "mage",
                "initial_stats": {
                    "strength": 8,
                    "dexterity": 10,
                    "vitality": 9,
                    "intelligence": 18,
                    "wisdom": 16,
                    "constitution": 10
                }
            }
        )
        await asyncio.sleep(0.05)
    
    # Wait for all events to process
    await asyncio.sleep(0.2)
    
    # Verify character variety achievement (5 characters)
    unlocked_achievements = achievement_system.get_unlocked_achievements()
    variety_achievement = next(
        (a for a in unlocked_achievements if 'character_variety' in a.id),
        None
    )
    assert variety_achievement is not None, "Character variety achievement should be unlocked"
    
    logger.info("✅ Character variety achievement working correctly")
    
    # Step 5: Verify achievement system statistics
    progress = achievement_system.get_achievement_progress()
    assert progress['unlocked_count'] >= 3, f"Should have at least 3 achievements unlocked, got {progress['unlocked_count']}"
    assert progress['total_points'] > 0, "Should have earned achievement points"
    
    logger.info(f"🏆 Achievement Progress: {progress['unlocked_count']}/{progress['total_achievements']} unlocked")
    logger.info(f"🎖️ Total Points: {progress['total_points']}")
    
    # Step 6: Verify notification system statistics
    notification_stats = notification_system.get_notification_stats()
    assert notification_stats['total_notifications'] >= 5, "Should have multiple notifications"
    
    logger.info(f"📢 Notification Stats: {notification_stats['total_notifications']} total notifications")
    
    # Step 7: Verify achievement unlocked notifications exist
    achievement_notifications = [
        n for n in notification_system.get_recent_notifications(limit=30)
        if 'Achievement Unlocked' in n.message
    ]
    assert len(achievement_notifications) >= 3, f"Should have achievement unlock notifications, got {len(achievement_notifications)}"
    
    logger.info("✅ Achievement unlock notifications working correctly")
    
    # Final verification: Print all achievements and notifications for manual inspection
    logger.info("\n" + "="*60)
    logger.info("🏆 FINAL ACHIEVEMENT SUMMARY:")
    for achievement in achievement_system.get_unlocked_achievements():
        logger.info(f"  - {achievement.name}: {achievement.description} (+{achievement.points} points)")
    
    logger.info("\n📢 RECENT NOTIFICATIONS:")
    for notification in notification_system.get_recent_notifications(limit=10):
        logger.info(f"  - [{notification.notification_type.value.upper()}] {notification.message}")
    
    logger.info("="*60)
    logger.info("🎉 Complete observer pattern workflow test PASSED!")
    
    return True


@pytest.mark.asyncio
async def test_observer_pattern_isolation():
    """
    Test that observer systems work independently and don't interfere with each other
    """
    # Create minimal setup for isolated testing
    event_bus = EventBus()
    config = GameConfig()
    
    # Create systems independently
    achievement_system = AchievementSystem(event_bus, config)
    notification_system = NotificationSystem(event_bus)
    character_system = CharacterSystem(None)  # Mock service container for isolation test
    
    logger.info("🔬 Testing observer pattern isolation...")
    
    # Create a character
    character = await character_system.create_character(
        user_id="test_user",
        character_data={
            "name": "Isolation Test",
            "character_type": "test",
            "initial_stats": {"strength": 10, "intelligence": 10}
        }
    )
    
    await asyncio.sleep(0.1)
    
    # Both systems should have reacted independently
    achievements = achievement_system.get_unlocked_achievements()
    notifications = notification_system.get_recent_notifications()
    
    assert len(achievements) >= 1, "Achievement system should have reacted"
    assert len(notifications) >= 1, "Notification system should have reacted"
    
    logger.info("✅ Observer systems work independently")
    
    return True


if __name__ == "__main__":
    # Run the test directly for development
    async def run_test():
        logger.info("🚀 Running observer pattern tests...")
        
        # Create game setup manually
        engine = AsyncGameEngine()
        await engine.initialize_async()
        
        # Create character system and initialize it properly
        character_system = CharacterSystem(engine.service_container)
        await character_system.initialize()
        
        services = {
            'engine': engine,
            'event_bus': engine.service_container.get(EventBus),
            'config': engine.service_container.get(GameConfig),
            'character_system': character_system,
            'achievement_system': engine.service_container.get(AchievementSystem),
            'notification_system': engine.service_container.get(NotificationSystem)
        }
        
        try:
            # Run the main test
            await test_complete_observer_pattern_workflow(services)
            
            # Run isolation test
            await test_observer_pattern_isolation()
            
            logger.info("🎉 All observer pattern tests passed!")
            
        finally:
            await engine.shutdown_async()
    
    # Run the test
    asyncio.run(run_test())
