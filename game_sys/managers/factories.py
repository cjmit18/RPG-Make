# game_sys/managers/factories.py
"""
Module: game_sys.managers.factories

Provides factory functions to instantiate real or null implementations
of core engine subsystems based on feature flags.
NullActionQueue now implements tick(dt) for registration with AsyncTimeManager.
"""
from game_sys.config.feature_flags import FeatureFlags

# Real implementations
from game_sys.managers.input_manager import InputManager
from game_sys.managers.collision_manager import CollisionManager
from game_sys.managers.action_queue import ActionQueue
from game_sys.managers.resource_manager import ResourceManager
from game_sys.managers.mod_loader import ModLoader
from game_sys.inventory.inventory_manager import InventoryManager

# Null implementations with no-op tick where appropriate
class NullInputManager:
    def just_pressed(self, key): return False
    def mouse_pos(self): return (0, 0)

class NullCollisionManager:
    def query(self, shape, layer=None): return []
    def raycast(self, origin, direction, distance): return None

class NullActionQueue:
    def register_actor(self, actor): pass
    def schedule(self, actor, action_name, cooldown, **params): return False
    def consume(self, actor): return []
    def tick(self, dt: float):
        """No-op tick for disabled action queue."""
        pass

class NullResourceManager:
    def load(self, path): return None
    def preload(self, paths): pass

class NullModLoader:
    def load_mods(self, directory): return []
    def get_override(self, key): return None

class NullInventoryManager:
    def __init__(self, actor): pass
    def add_item(self, item): return False
    def remove_item(self, item): return False
    def find(self, item_id): return None
    def list_items(self): return []

# Factory functions
flags = FeatureFlags()

def get_input_manager():
    return InputManager() if flags.is_enabled('input_manager') else NullInputManager()

def get_collision_manager():
    return CollisionManager() if flags.is_enabled('collision_manager') else NullCollisionManager()

def get_action_queue():
    return ActionQueue() if flags.is_enabled('action_queue') else NullActionQueue()

def get_resource_manager():
    return ResourceManager() if flags.is_enabled('resource_manager') else NullResourceManager()

def get_mod_loader():
    return ModLoader() if flags.is_enabled('mod_loader') else NullModLoader()

def get_inventory_manager(actor):
    return InventoryManager(actor) if flags.is_enabled('inventory') else NullInventoryManager(actor)
