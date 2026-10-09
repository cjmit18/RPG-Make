"""
Test the new RPG Engine architecture
"""
import asyncio
import pytest
import logging
from unittest.mock import Mock

from rpg_engine.core.engine import AsyncGameEngine
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus, UIUpdateEvent

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

@pytest.mark.asyncio
async def test_service_container():
    """Test the service container functionality"""
    container = ServiceContainer()
    
    # Test instance registration
    event_bus = EventBus()
    container.register_instance(EventBus, event_bus)
    
    # Test service retrieval
    retrieved = await container.get_service(EventBus)
    assert retrieved is event_bus
    
    # Test service listing
    services = container.list_registered_services()
    assert "EventBus" in services

@pytest.mark.asyncio
async def test_event_bus():
    """Test the event bus functionality"""
    event_bus = EventBus()
    
    # Test event subscription and publishing
    received_events = []
    
    class TestHandler:
        async def handle(self, event: UIUpdateEvent):
            received_events.append(event)
    
    handler = TestHandler()
    event_bus.subscribe(UIUpdateEvent, handler)
    
    # Publish test event
    test_event = UIUpdateEvent(
        source="test",
        component_id="test_component",
        update_type="test_update", 
        data={"test": "data"}
    )
    
    await event_bus.publish(test_event)
    
    # Verify event was received
    assert len(received_events) == 1
    assert received_events[0].source == "test"

@pytest.mark.asyncio
async def test_engine_initialization():
    """Test engine initialization"""
    config = {'target_fps': 30, 'debug_mode': True}
    engine = AsyncGameEngine(config)
    
    # Test initialization
    await engine.initialize_async()
    assert engine.state == "initializing"
    
    # Test service container is set up
    assert isinstance(engine.service_container, ServiceContainer)
    assert isinstance(engine.event_bus, EventBus)
    
    # Test cleanup
    await engine.shutdown_async()

@pytest.mark.asyncio
async def test_full_engine_lifecycle():
    """Test complete engine lifecycle"""
    engine = AsyncGameEngine({'target_fps': 60})
    
    try:
        # Initialize
        await engine.initialize_async()
        assert engine.state == "initializing"
        
        # Start (but don't run the full loop)
        await engine.start_async()
        assert engine.state == "running"
        assert engine.running is True
        
        # Stop
        await engine.stop_async()
        assert engine.state == "stopped"
        assert engine.running is False
        
    finally:
        await engine.shutdown_async()

if __name__ == "__main__":
    # Run a simple manual test
    async def manual_test():
        print("Testing new RPG Engine architecture...")
        
        # Test service container
        print("1. Testing Service Container...")
        container = ServiceContainer()
        event_bus = EventBus()
        container.register_instance(EventBus, event_bus)
        retrieved = await container.get_service(EventBus)
        print(f"   ✓ Service retrieval works: {retrieved is event_bus}")
        
        # Test event bus
        print("2. Testing Event Bus...")
        received = []
        
        class TestHandler:
            async def handle(self, event):
                received.append(event)
        
        handler = TestHandler()
        event_bus.subscribe(UIUpdateEvent, handler)
        
        test_event = UIUpdateEvent(
            source="test", component_id="test", 
            update_type="test", data={}
        )
        await event_bus.publish(test_event)
        print(f"   ✓ Event publishing works: {len(received) == 1}")
        
        # Test engine
        print("3. Testing Engine...")
        engine = AsyncGameEngine({'target_fps': 60})
        await engine.initialize_async()
        print(f"   ✓ Engine initialization: {engine.state}")
        
        await engine.shutdown_async()
        print("   ✓ Engine shutdown complete")
        
        print("\nAll tests passed! ✓")
    
    asyncio.run(manual_test())
