# game_sys/engine.py
"""
Module: game_sys.engine

The core Engine class ties together all major subsystems.
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

    def register_actor(self, actor):
        """Add an Actor for ready‐action dispatch (emit events)."""
        if actor not in self.actors:
            self.actors.append(actor)
            engine_logger.info(f"Registered actor: {actor.name}")

    def unregister_actor(self, actor):
        """Remove an Actor from engine management."""
        if actor in self.actors:
            self.actors.remove(actor)
            engine_logger.info(f"Unregistered actor: {actor.name}")

    def start(self):
        """Initialize and start all subsystems."""
        engine_logger.info("Starting game engine")
        
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
        self._running = False
        self.config_watcher.stop()
        time_manager.stop()

    def run(self):
        """Entry point: start subsystems, run loop, and clean up."""
        self.start()
        try:
            asyncio.run(self.game_loop())
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def start_engine(fps: int = 60):
    engine = Engine(fps=fps)
    engine.run()
    return engine

