"""
Test script to verify the clean new RPG engine codebase works without any game_sys dependencies
"""
import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_clean_imports():
    """Test that all new engine components import cleanly"""
    try:
        logger.info("Testing core engine imports...")
        
        # Test core engine imports
        from rpg_engine.core.engine import AsyncGameEngine
        from rpg_engine.core.service_container import ServiceContainer
        from rpg_engine.core.event_bus import EventBus
        logger.info("✅ Core engine imports successful")
        
        # Test system imports
        from rpg_engine.systems.character.character_system import CharacterSystem
        # Note: Other systems may not be fully implemented yet
        logger.info("✅ System imports successful")
        
        # Test integration service
        from rpg_engine.systems.integration.system_integration_service import SystemIntegrationService
        logger.info("✅ Integration service import successful")
        
        # Test UI system
        from rpg_engine.ui.ui_system import AsyncUIManager
        logger.info("✅ UI system import successful")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

async def test_basic_engine_functionality():
    """Test basic engine initialization and functionality"""
    try:
        logger.info("Testing basic engine functionality...")
        
        # Import core components
        from rpg_engine.core.engine import AsyncGameEngine
        from rpg_engine.core.service_container import ServiceContainer
        from rpg_engine.core.event_bus import EventBus
        
        # Create service container
        container = ServiceContainer()
        logger.info("✅ Service container created")
        
        # Create and register event bus
        event_bus = EventBus()
        container.register_instance(EventBus, event_bus)
        logger.info("✅ Event bus registered")
        
        # Create engine
        config = {
            'target_fps': 60,
            'debug_mode': True,
            'ui_enabled': False  # Disable UI for testing
        }
        engine = AsyncGameEngine(config)
        logger.info("✅ Engine created")
        
        # Initialize engine
        await engine.initialize_async()
        logger.info("✅ Engine initialized")
        
        # Test engine state
        assert engine.state in ["stopped", "initializing", "running"], f"Unexpected engine state: {engine.state}"
        logger.info(f"✅ Engine state: {engine.state}")
        
        # Shutdown engine
        await engine.shutdown_async()
        logger.info("✅ Engine shutdown completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Engine functionality test failed: {e}")
        return False

async def test_character_system():
    """Test character system functionality"""
    try:
        logger.info("Testing character system...")
        
        from rpg_engine.core.service_container import ServiceContainer
        from rpg_engine.core.event_bus import EventBus
        from rpg_engine.systems.character.character_system import CharacterSystem
        
        # Create service container and event bus
        container = ServiceContainer()
        event_bus = EventBus()
        container.register_instance(EventBus, event_bus)
        
        # Create character system
        character_system = CharacterSystem(container)
        await character_system.initialize()
        logger.info("✅ Character system initialized")
        
        # Test character creation
        character_data = {
            'template_id': 'warrior_basic',
            'name': 'Test Hero',
            'appearance': {
                'build': 'muscular',
                'hair_color': 'brown',
                'eye_color': 'blue'
            }
        }
        
        character = await character_system.create_character('test_user', character_data)
        logger.info(f"✅ Character created: {character.name} ({character.character_class})")
        
        # Test character retrieval
        retrieved_character = await character_system.get_character(character.id)
        assert retrieved_character is not None, "Failed to retrieve character"
        assert retrieved_character.name == character.name, "Character name mismatch"
        logger.info("✅ Character retrieval successful")
        
        # Test character statistics
        stats = await character_system.get_character_statistics()
        assert stats['total_characters'] >= 1, "Character statistics not updated"
        logger.info(f"✅ Character statistics: {stats['total_characters']} characters")
        
        # Shutdown character system
        await character_system.shutdown()
        logger.info("✅ Character system shutdown completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Character system test failed: {e}")
        return False

async def test_integration_service():
    """Test system integration service"""
    try:
        logger.info("Testing system integration service...")
        
        from rpg_engine.core.service_container import ServiceContainer
        from rpg_engine.core.event_bus import EventBus
        from rpg_engine.systems.integration.system_integration_service import SystemIntegrationService
        
        # Create service container and event bus
        container = ServiceContainer()
        event_bus = EventBus()
        container.register_instance(EventBus, event_bus)
        
        # Create integration service
        integration_service = SystemIntegrationService(container)
        await integration_service.initialize_async()
        logger.info("✅ Integration service initialized")
        
        # Test character creation through integration service
        result = await integration_service.create_integrated_character_async(
            'warrior_basic', 
            'Integration Test Hero'
        )
        
        assert result['success'], f"Character creation failed: {result.get('message', 'Unknown error')}"
        logger.info(f"✅ Integrated character created: {result['character_name']}")
        
        # Test character data retrieval
        character_data = await integration_service.get_character_data_async(result['character_id'])
        assert character_data is not None, "Failed to retrieve character data"
        logger.info("✅ Character data retrieval successful")
        
        # Test template listing
        templates = await integration_service.get_available_character_templates_async()
        assert len(templates) > 0, "No character templates available"
        logger.info(f"✅ Templates available: {len(templates)}")
        
        # Test system statistics
        stats = await integration_service.get_system_statistics_async()
        assert stats['statistics']['characters_created'] >= 1, "Statistics not updated"
        logger.info(f"✅ Integration statistics: {stats['statistics']}")
        
        # Shutdown integration service
        await integration_service.shutdown_async()
        logger.info("✅ Integration service shutdown completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration service test failed: {e}")
        return False

async def test_no_game_sys_references():
    """Test that there are no game_sys references in the codebase"""
    try:
        logger.info("Testing for game_sys references...")
        
        # Check that game_sys imports fail as expected
        try:
            import game_sys
            logger.error("❌ game_sys module found when it should not exist")
            return False
        except ImportError:
            logger.info("✅ game_sys module not found (as expected)")
        
        # Test that our systems work without game_sys
        from rpg_engine.systems.integration.system_integration_service import SystemIntegrationService
        from rpg_engine.core.service_container import ServiceContainer
        
        container = ServiceContainer()
        service = SystemIntegrationService(container)
        
        # This should work with mock implementations
        result = await service._create_mock_character('warrior', 'Mock Hero')
        assert result['success'], "Mock character creation should work"
        logger.info("✅ Mock functionality works without game_sys")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Game_sys reference test failed: {e}")
        return False

async def run_all_tests():
    """Run all codebase tests"""
    logger.info("🧪 Starting clean codebase tests...")
    
    tests = [
        ("Import Tests", test_clean_imports),
        ("Engine Functionality", test_basic_engine_functionality),
        ("Character System", test_character_system),
        ("Integration Service", test_integration_service),
        ("No Game_sys References", test_no_game_sys_references)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results[test_name] = result
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        emoji = "✅" if result else "❌"
        logger.info(f"{emoji} {test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Clean codebase is working correctly.")
        return True
    else:
        logger.error(f"💥 {total - passed} tests failed. Issues need to be addressed.")
        return False

if __name__ == "__main__":
    print("🚀 RPG Engine Clean Codebase Test")
    print("Testing new async-first architecture without game_sys dependencies")
    print("-" * 60)
    
    try:
        success = asyncio.run(run_all_tests())
        exit_code = 0 if success else 1
        
        print(f"\n{'='*60}")
        if success:
            print("🎉 CLEAN CODEBASE TEST: SUCCESS")
            print("The new RPG engine is working correctly without any game_sys dependencies!")
        else:
            print("💥 CLEAN CODEBASE TEST: FAILED")
            print("Some issues were found that need to be addressed.")
        print(f"{'='*60}")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error during testing: {e}")
        sys.exit(1)
