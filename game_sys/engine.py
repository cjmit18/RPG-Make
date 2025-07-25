# game_sys/engine.py
"""
Module: game_sys.engine

The core Engine class ties together all major subsystems and provides
the main game loop coordination. This module serves as the central
orchestrator for the entire RPG engine.

Key Features:
- Asynchronous game loop with configurable frame rate
- Actor lifecycle management with automatic registration
- Configuration hot-reloading via file watcher
- Event-driven architecture through hooks system
- Integrated save/load functionality
- Modular subsystem management (input, collision, resources, mods)

Example Usage:
    >>> engine = Engine(fps=60)
    >>> engine.run()  # Starts the engine and game loop
    
    # Or use the convenience function:
    >>> start_engine(fps=60)
"""
import asyncio

from game_sys.config.config_manager import ConfigManager
from game_sys.config.watcher import ConfigWatcher
from game_sys.hooks.hooks_setup import emit, on, ON_CHARACTER_CREATED
from game_sys.managers.time_manager import time_manager
from game_sys.managers.factories import (
    get_input_manager,
    get_collision_manager,
    get_resource_manager,
    get_mod_loader
)
from game_sys.effects.status_manager import status_manager
from game_sys.logging import engine_logger


class Engine:
    """
    The main game engine. Manages initialization, the game loop, and shutdown.
    
    This class serves as the central coordinator for all game systems including:
    - Actor management and lifecycle
    - Configuration and hot-reload
    - Core subsystems (input, collision, resources, mods)
    - Asynchronous game loop with frame rate control
    - Event-driven architecture via hooks system
    """
    
    def __init__(self, fps: int = 60):
        engine_logger.info("Initializing Game Engine")
        
        # Load and validate configuration
        self.config: ConfigManager = ConfigManager()
        engine_logger.debug("Configuration loaded")

        # Watch configuration files for changes
        self.config_watcher = ConfigWatcher(path=self.config.get('paths.data_dir', 'config'))
        engine_logger.debug("Configuration watcher initialized")

        # Core subsystems via factories
        self.input      = get_input_manager()
        self.collision  = get_collision_manager()
        self.resource   = get_resource_manager()
        self.mod_loader = get_mod_loader()
        engine_logger.debug("Core subsystems initialized")

        # Actors explicitly managed by the engine (for ready-action processing)
        self.actors: list = []

        # Target frame rate
        self.fps = fps
        self._running = False
        engine_logger.debug(f"Engine initialized with target FPS: {self.fps}")

        # --- Loose‐coupling auto‐registration for character creation ---
        def _auto_register(actor, **_):
            engine_logger.debug(f"Auto-registering actor: {actor.name}")
            # 1) drive regen & action‐queue ticking
            time_manager.register(actor)
            time_manager.register(actor.action_queue)
            # 2) drive DoTs, buffs & debuffs
            status_manager.register_actor(actor)

        # any time a character is created, hook it into time & status systems
        on(ON_CHARACTER_CREATED, _auto_register)
        engine_logger.info("Engine initialization complete")

    async def save_game_async(self, path: str) -> None:
        """Asynchronously save all managed actors to a file."""
        try:
            from game_sys.config.save_load import save_actors_async
            await save_actors_async(self.actors, path)
            engine_logger.info(f"Game saved successfully to {path}")
        except Exception as e:
            engine_logger.error(f"Failed to save game to {path}: {e}")
            raise

    async def load_game_async(self, path: str) -> None:
        """Asynchronously load all actors from a file and replace current actors."""
        try:
            from game_sys.config.save_load import load_actors_async
            loaded_actors = await load_actors_async(path)
            
            # Unregister old actors
            for actor in list(self.actors):
                self.unregister_actor(actor)
            
            # Register loaded actors
            for actor in loaded_actors:
                self.register_actor(actor)
            
            self.actors = loaded_actors
            engine_logger.info(f"Game loaded successfully from {path}")
        except Exception as e:
            engine_logger.error(f"Failed to load game from {path}: {e}")
            raise

    def register_actor(self, actor):
        """Add an Actor for ready‐action dispatch (emit events)."""
        if actor not in self.actors:
            self.actors.append(actor)
            engine_logger.info(f"Registered actor: {actor.name}")
        else:
            engine_logger.debug(f"Actor already registered: {actor.name}")

    def unregister_actor(self, actor):
        """Remove an Actor from engine management."""
        if actor in self.actors:
            self.actors.remove(actor)
            engine_logger.info(f"Unregistered actor: {actor.name}")
        else:
            engine_logger.debug(f"Actor not found for unregistration: {actor.name}")

    def get_actor_count(self) -> int:
        """Get the current number of registered actors."""
        return len(self.actors)

    def get_actors(self) -> list:
        """Get a copy of the current actors list."""
        return self.actors.copy()

    def clear_actors(self):
        """Remove all actors from engine management."""
        actor_count = len(self.actors)
        for actor in list(self.actors):
            self.unregister_actor(actor)
        engine_logger.info(f"Cleared {actor_count} actors from engine")

    def is_running(self) -> bool:
        """Check if the engine is currently running."""
        return self._running

    def start(self):
        """Initialize and start all subsystems."""
        if self._running:
            engine_logger.warning("Engine is already running")
            return
            
        engine_logger.info("Starting game engine")
        
        try:
            # Start hot‐reload for config
            self.config_watcher.start()
            engine_logger.debug("Config watcher started")
            
            # Load user mods
            self.mod_loader.load_mods()
            engine_logger.debug("Mods loaded")
            
            # Start the async time manager (handles ticks)
            time_manager.start(interval=1 / self.fps)
            engine_logger.debug(f"Time manager started with interval: {1/self.fps:.4f}s")
            
            self._running = True
            engine_logger.info("Engine started successfully")
            
        except Exception as e:
            engine_logger.error(f"Failed to start engine: {e}")
            self.stop()  # Clean up any partially started systems
            raise

    async def game_loop(self):
        """
        Main asynchronous game loop. Polls input, processes ready actions,
        and sleeps to maintain frame rate.
        """
        engine_logger.info("Starting game loop")
        interval = 1 / self.fps
        try:
            while self._running:
                # 1) Handle input
                if hasattr(self.input, 'update'):
                    self.input.update()

                # 2) Collision checks (game‐specific)
                # e.g. self.collision.query(...)

                # 3) Process ready actions and emit their events
                for actor in list(self.actors):
                    actions = actor.consume_ready_actions()
                    if actions:  # Only log if there are actions
                        engine_logger.debug(f"Processing {len(actions)} actions for {actor.name}")
                    for action_name, params in actions:
                        engine_logger.debug(f"Emitting action: {action_name}")
                        emit(action_name, actor=actor, **params)

                # 4) Frame pacing
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            engine_logger.info("Game loop cancelled")
            pass
        except Exception as e:
            engine_logger.error(f"Error in game loop: {e}", exc_info=True)
            raise

    def stop(self):
        """Stop the game loop and all subsystems."""
        if not self._running:
            engine_logger.debug("Engine is already stopped")
            return
            
        engine_logger.info("Stopping game engine")
        self._running = False
        
        try:
            # Stop subsystems in reverse order of startup
            time_manager.stop()
            engine_logger.debug("Time manager stopped")
            
            self.config_watcher.stop()
            engine_logger.debug("Config watcher stopped")
            
            engine_logger.info("Engine stopped successfully")
            
        except Exception as e:
            engine_logger.error(f"Error during engine shutdown: {e}")

    def restart(self):
        """Restart the engine by stopping and starting again."""
        engine_logger.info("Restarting engine")
        self.stop()
        self.start()

    def run(self):
        """Entry point: start subsystems, run loop, and clean up."""
        engine_logger.info("Running engine")
        
        try:
            self.start()
            asyncio.run(self.game_loop())
        except KeyboardInterrupt:
            engine_logger.info("Engine interrupted by user")
        except Exception as e:
            engine_logger.error(f"Engine runtime error: {e}", exc_info=True)
            raise
        finally:
            self.stop()
            engine_logger.info("Engine shutdown complete")


def start_engine(fps: int = 60) -> Engine:
    """
    Convenience function to create and start an engine instance.
    
    Args:
        fps: Target frames per second for the game loop
        
    Returns:
        Engine: The created engine instance
    """
    engine = Engine(fps=fps)
    engine.run()
    return engine

