# game_sys/engine.py
"""
Module: game_sys.engine

The core Engine class ties together all major subsystems.
"""
import asyncio
from game_sys.config.config_manager import ConfigManager
from game_sys.config.watcher import ConfigWatcher
from game_sys.hooks.hooks_setup import emit
from game_sys.managers.time_manager import time_manager
from game_sys.managers.factories import (
    get_input_manager,
    get_collision_manager,
    get_resource_manager,
    get_mod_loader
)

class Engine:
    """
    The main game engine. Manages initialization, the game loop, and shutdown.
    """
    def __init__(self, fps: int = 60):
        # Load and validate configuration
        self.config: ConfigManager = ConfigManager()

        # Watch configuration files for changes
        self.config_watcher = ConfigWatcher(path=self.config.get('paths.data_dir', 'config'))

        # Core subsystems via factories
        self.input = get_input_manager()
        self.collision = get_collision_manager()
        self.resource = get_resource_manager()
        self.mod_loader = get_mod_loader()

        # Actors managed by this engine
        self.actors = []

        # Target frame rate
        self.fps = fps
        self._running = False

    def register_actor(self, actor):
        """Add an Actor instance to be managed by the engine."""
        if actor not in self.actors:
            self.actors.append(actor)

    def unregister_actor(self, actor):
        """Remove an Actor from engine management."""
        if actor in self.actors:
            self.actors.remove(actor)

    def start(self):
        """Initialize and start all subsystems."""
        # Start watching config for hot-reload
        self.config_watcher.start()

        # Load user-defined mods
        self.mod_loader.load_mods()

        # Start the async time manager (status ticks, action queue ticks)
        time_manager.start(interval=1/self.fps)

        self._running = True

    async def game_loop(self):
        """
        Main asynchronous game loop. Polls input, processes actions, and ticks subsystems.
        """
        interval = 1 / self.fps
        try:
            while self._running:
                # 1) Handle input
                if hasattr(self.input, 'update'):
                    self.input.update()

                # 2) Collision checks (custom per game)
                # e.g., self.collision.query(...)

                # 3) Process ready actions for actors
                for actor in list(self.actors):
                    ready = actor.consume_ready_actions()
                    for action_name, params in ready:
                        emit(action_name, actor=actor, **params)

                # 4) Wait until next frame
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass

    def stop(self):
        """Stop the game loop and all subsystems."""
        self._running = False
        self.config_watcher.stop()
        time_manager.stop()

    def run(self):
        """Synchronous entry point: starts subsystems and runs the async loop."""
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
