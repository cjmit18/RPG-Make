"""
Simple Observer Pattern Test - Minimal character events to test achievements

This test creates a minimal working example to demonstrate that our
achievement and notification observer systems work correctly.
"""
import asyncio
import logging
import time
from rpg_engine.core.engine import AsyncGameEngine
from rpg_engine.core.event_bus import EventBus
from rpg_engine.core.config import GameConfig
from rpg_engine.systems.achievements import AchievementSystem
from rpg_engine.systems.notifications import NotificationSystem
from rpg_engine.systems.character.character_system import CharacterCreatedEvent
from rpg_engine.systems.character.progression_system import CharacterLevelUpEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_observer_patterns_directly():
    """Test observer patterns by directly firing events"""
    logger.info("🚀 Testing observer patterns with direct events...")
    
    # Create and initialize the game engine
    engine = AsyncGameEngine()
    await engine.initialize_async()
    
    try:
        # Get the services we need
        event_bus = engine.service_container.get(EventBus)
        achievement_system = engine.service_container.get(AchievementSystem)
        notification_system = engine.service_container.get(NotificationSystem)
        
        logger.info("🎮 Testing character creation events...")
        
        # Fire character creation event directly
        character_created_event = CharacterCreatedEvent(
            character_id="test_char_1",
            character_name="Test Hero",
            character_type="warrior",
            initial_stats={"strength": 15, "intelligence": 10},
            timestamp=time.time()
        )
        
        await event_bus.publish(character_created_event)
        await asyncio.sleep(0.2)  # Wait for observers to process
        
        # Check if achievement was unlocked
        unlocked_achievements = achievement_system.get_unlocked_achievements()
        logger.info(f"🏆 Unlocked achievements: {len(unlocked_achievements)}")
        
        for achievement in unlocked_achievements:
            logger.info(f"  - {achievement.name}: {achievement.description} (+{achievement.points} points)")
        
        # Check if notifications were created
        notifications = notification_system.get_recent_notifications()
        logger.info(f"📢 Recent notifications: {len(notifications)}")
        
        for notification in notifications:
            logger.info(f"  - [{notification.notification_type.value.upper()}] {notification.message}")
        
        # Test level up event
        logger.info("📈 Testing level up events...")
        
        level_up_event = CharacterLevelUpEvent(
            character_id="test_char_1",
            old_level=1,
            new_level=10,
            timestamp=time.time()
        )
        
        await event_bus.publish(level_up_event)
        await asyncio.sleep(0.2)  # Wait for observers to process
        
        # Check for level milestone achievements
        unlocked_achievements = achievement_system.get_unlocked_achievements()
        logger.info(f"🏆 Total unlocked achievements after level up: {len(unlocked_achievements)}")
        
        # Check for level up notifications
        notifications = notification_system.get_recent_notifications()
        logger.info(f"📢 Total notifications after level up: {len(notifications)}")
        
        # Test creating multiple characters to trigger variety achievement
        logger.info("👥 Testing multiple character creation...")
        
        character_names = ["Hero 2", "Hero 3", "Hero 4", "Hero 5"]
        for i, name in enumerate(character_names, 2):
            character_event = CharacterCreatedEvent(
                character_id=f"test_char_{i}",
                character_name=name,
                character_type="mage",
                initial_stats={"strength": 8, "intelligence": 18},
                timestamp=time.time()
            )
            await event_bus.publish(character_event)
            await asyncio.sleep(0.1)
        
        # Final check
        unlocked_achievements = achievement_system.get_unlocked_achievements()
        notifications = notification_system.get_recent_notifications()
        progress = achievement_system.get_achievement_progress()
        
        logger.info("\n" + "="*60)
        logger.info("🎉 FINAL OBSERVER PATTERN TEST RESULTS:")
        logger.info(f"🏆 Total Achievements Unlocked: {len(unlocked_achievements)}")
        logger.info(f"🎖️ Total Points Earned: {progress['total_points']}")
        logger.info(f"📢 Total Notifications: {len(notifications)}")
        logger.info(f"📊 Achievement Progress: {progress['unlocked_count']}/{progress['total_achievements']} ({progress['completion_percentage']:.1f}%)")
        
        logger.info("\n🏆 UNLOCKED ACHIEVEMENTS:")
        for achievement in unlocked_achievements:
            logger.info(f"  ✅ {achievement.name}: {achievement.description} (+{achievement.points} points)")
        
        logger.info("\n📢 RECENT NOTIFICATIONS:")
        for notification in notifications[-10:]:  # Show last 10
            logger.info(f"  📌 [{notification.notification_type.value.upper()}] {notification.message}")
        
        logger.info("="*60)
        
        # Verify that observer patterns worked
        assert len(unlocked_achievements) >= 2, f"Expected at least 2 achievements, got {len(unlocked_achievements)}"
        assert len(notifications) >= 5, f"Expected at least 5 notifications, got {len(notifications)}"
        assert progress['total_points'] > 0, "Should have earned achievement points"
        
        logger.info("✅ Observer pattern test PASSED! All systems working correctly.")
        
        return True
        
    finally:
        await engine.shutdown_async()


if __name__ == "__main__":
    asyncio.run(test_observer_patterns_directly())
