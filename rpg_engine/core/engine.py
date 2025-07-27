"""
Async Game Engine - Core orchestrator for the RPG Engine
Manages the main game loop, services, and system coordination
"""
import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

from .service_container import ServiceContainer, AsyncInitializable, AsyncShutdownable
from .event_bus import EventBus, GameEvent, UIUpdateEvent

logger = logging.getLogger(__name__)

class EngineState:
    """Represents the current state of the game engine"""
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"

class AsyncGameEngine(AsyncInitializable, AsyncShutdownable):
    """
    Main async game engine that orchestrates all game systems
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.service_container = ServiceContainer()
        self.event_bus = EventBus()
        
        # Engine state
        self.state = EngineState.STOPPED
        self.running = False
        self.target_fps = self.config.get('target_fps', 60)
        self.target_frame_time = 1.0 / self.target_fps
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = 0.0
        self.last_frame_time = 0.0
        
        # Tasks
        self.game_loop_task: Optional[asyncio.Task] = None
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info(f"AsyncGameEngine initialized with target FPS: {self.target_fps}")
    
    async def initialize_async(self) -> None:
        """Initialize the game engine and all systems"""
        if self.state != EngineState.STOPPED:
            logger.warning("Engine already initialized")
            return
        
        logger.info("Initializing game engine...")
        self.state = EngineState.INITIALIZING
        
        try:
            # Initialize event bus middleware
            from .event_bus import LoggingMiddleware, ValidationMiddleware
            self.event_bus.add_middleware(ValidationMiddleware())
            self.event_bus.add_middleware(LoggingMiddleware())
            
            # Register core services
            await self._register_core_services()
            
            # Initialize all services
            await self.service_container.initialize_all_async()
            
            # Publish initialization event
            await self.event_bus.publish(UIUpdateEvent(
                source="engine",
                component_id="engine",
                update_type="initialized",
                data={"state": self.state}
            ))
            
            logger.info("Game engine initialized successfully")
            
        except Exception as e:
            self.state = EngineState.STOPPED
            logger.error(f"Failed to initialize game engine: {e}")
            raise
    
    async def _register_core_services(self) -> None:
        """Register core engine services"""
        # Register the event bus and service container as services
        self.service_container.register_instance(EventBus, self.event_bus)
        self.service_container.register_instance(ServiceContainer, self.service_container)
        
        # UI services will be registered when UI system is created
        logger.debug("Core services registered")
    
    async def start_async(self) -> None:
        """Start the main game loop"""
        if self.state == EngineState.RUNNING:
            logger.warning("Engine already running")
            return
        
        if self.state != EngineState.INITIALIZING:
            await self.initialize_async()
        
        logger.info("Starting game engine...")
        self.state = EngineState.RUNNING
        self.running = True
        self.start_time = time.time()
        
        # Start the main game loop
        self.game_loop_task = asyncio.create_task(self._game_loop())
        
        # Publish start event
        await self.event_bus.publish(UIUpdateEvent(
            source="engine",
            component_id="engine", 
            update_type="started",
            data={"state": self.state}
        ))
        
        logger.info("Game engine started")
    
    async def _game_loop(self) -> None:
        """Main async game loop"""
        logger.info("Game loop started")
        
        while self.running and self.state == EngineState.RUNNING:
            frame_start = time.time()
            
            try:
                # Update all systems in parallel
                await self._update_systems()
                
                # Update frame statistics
                self.frame_count += 1
                self.last_frame_time = time.time() - frame_start
                
            except Exception as e:
                logger.error(f"Error in game loop: {e}")
                await self.stop_async()
                break
            
            # Frame timing control
            frame_time = time.time() - frame_start
            sleep_time = max(0, self.target_frame_time - frame_time)
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        logger.info("Game loop ended")
    
    async def _update_systems(self) -> None:
        """Update all game systems"""
        # This will be expanded as we add more systems
        update_tasks = []
        
        # UI system updates will go here
        # Physics system updates will go here
        # AI system updates will go here
        # etc.
        
        if update_tasks:
            await asyncio.gather(*update_tasks, return_exceptions=True)
    
    async def pause_async(self) -> None:
        """Pause the game engine"""
        if self.state == EngineState.RUNNING:
            logger.info("Pausing game engine...")
            self.state = EngineState.PAUSED
            
            await self.event_bus.publish(UIUpdateEvent(
                source="engine",
                component_id="engine",
                update_type="paused", 
                data={"state": self.state}
            ))
    
    async def resume_async(self) -> None:
        """Resume the game engine"""
        if self.state == EngineState.PAUSED:
            logger.info("Resuming game engine...")
            self.state = EngineState.RUNNING
            
            await self.event_bus.publish(UIUpdateEvent(
                source="engine",
                component_id="engine",
                update_type="resumed",
                data={"state": self.state}
            ))
    
    async def stop_async(self) -> None:
        """Stop the game engine"""
        if self.state == EngineState.STOPPED:
            return
        
        logger.info("Stopping game engine...")
        self.running = False
        self.state = EngineState.SHUTTING_DOWN
        
        # Cancel game loop
        if self.game_loop_task:
            self.game_loop_task.cancel()
            try:
                await self.game_loop_task
            except asyncio.CancelledError:
                pass
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        self.state = EngineState.STOPPED
        
        await self.event_bus.publish(UIUpdateEvent(
            source="engine",
            component_id="engine",
            update_type="stopped",
            data={"state": self.state}
        ))
        
        logger.info("Game engine stopped")
    
    async def shutdown_async(self) -> None:
        """Shutdown the game engine and cleanup resources"""
        await self.stop_async()
        
        logger.info("Shutting down game engine...")
        
        # Shutdown all services
        await self.service_container.shutdown_all_async()
        
        # Shutdown event bus
        await self.event_bus.shutdown()
        
        logger.info("Game engine shutdown complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine performance statistics"""
        current_time = time.time()
        uptime = current_time - self.start_time if self.start_time > 0 else 0
        fps = self.frame_count / uptime if uptime > 0 else 0
        
        return {
            'state': self.state,
            'uptime': uptime,
            'frame_count': self.frame_count,
            'fps': fps,
            'target_fps': self.target_fps,
            'last_frame_time': self.last_frame_time,
            'event_stats': self.event_bus.get_stats(),
            'services': self.service_container.list_registered_services()
        }
    
    def add_background_task(self, coro) -> asyncio.Task:
        """Add a background task to the engine"""
        task = asyncio.create_task(coro)
        self.background_tasks.append(task)
        return task
