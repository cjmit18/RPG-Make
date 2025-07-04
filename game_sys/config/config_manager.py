# game_sys/config/config_manager.py
"""
Module: game_sys.config.config_manager

Thread-safe singleton that loads and validates default & user JSON
from the same package directory, no matter where your game is run from.
Supports sync & async I/O.
"""
import json
import asyncio
import jsonschema
from pathlib import Path
from threading import Lock
from game_sys.logging import config_logger, log_exception


try:
    import aiofiles
except ImportError:
    aiofiles = None
    config_logger.warning("aiofiles not installed, async config loading disabled")

# JSON schema for validating the merged configuration
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "toggles":    {"type": "object", "additionalProperties": {"type": "boolean"}},
        "modules":    {"type": "object"},
        "constants":  {"type": "object"},
        "defaults":   {"type": "object"},
        "randomness": {"type": "object"},
        "logging":    {"type": "object"},
        "paths":      {"type": "object"}
    },
    "required": ["toggles","modules","constants","defaults","randomness","logging","paths"]
}


class ConfigManager:
    """
    Singleton for loading default & user settings from game_sys/config/*.json.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    config_logger.info("Initializing ConfigManager singleton")
                    inst = super().__new__(cls)
                    inst._init_paths()
                    inst._load_all()
                    cls._instance = inst
                    config_logger.info("ConfigManager initialization complete")
        return cls._instance

    def _init_paths(self):
        """
        Determine default & user JSON paths relative to this file.
        """
        base = Path(__file__).parent
        self.default_path = base / 'default_settings.json'
        self.user_path = base / 'settings.json'
        self._data = {}
        self._data_lock = Lock()
        config_logger.debug(
            f"Config paths: default={self.default_path}, user={self.user_path}"
        )

    @log_exception
    def _load_json(self, path: Path, optional: bool = False) -> dict:
        if not path.exists():
            config_logger.warning(f"Config file not found: {path}")
            return {} if optional else {}
        try:
            config_logger.debug(f"Loading config from {path}")
            data = json.loads(path.read_text())
            config_logger.debug(f"Successfully loaded {len(data)} settings from {path}")
            return data
        except json.JSONDecodeError as e:
            config_logger.error(f"Invalid JSON in {path}: {e}")
            raise RuntimeError(f"Invalid JSON in {path}: {e}")

    @log_exception
    async def _load_json_async(self, path: Path, optional: bool = False) -> dict:
        if not path.exists():
            config_logger.warning(f"Config file not found: {path}")
            return {} if optional else {}
        if aiofiles:
            try:
                async with aiofiles.open(path, 'r') as f:
                    text = await f.read()
                return json.loads(text)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON in {path}: {e}")
        else:
            # Fallback to sync in thread
            def _sync_load():
                try:
                    return json.loads(path.read_text())
                except json.JSONDecodeError as e:
                    raise RuntimeError(f"Invalid JSON in {path}: {e}")
            return await asyncio.to_thread(_sync_load)

    def _deep_merge(self, base: dict, override: dict) -> dict:
        config_logger.debug(f"Merging config dictionaries")
        result = base.copy()
        for k, v in override.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self._deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    @log_exception
    def _load_all(self):
        config_logger.info("Loading configuration files")
        defaults = self._load_json(self.default_path)
        overrides = self._load_json(self.user_path, optional=True)
        merged = self._deep_merge(defaults, overrides)

        # Validate
        try:
            config_logger.debug("Validating merged configuration")
            jsonschema.validate(merged, CONFIG_SCHEMA)
            config_logger.info("Configuration validation successful")
        except Exception as e:
            config_logger.error(f"Configuration validation error: {e}")
            raise RuntimeError(f"Config validation error: {e}")

        with self._data_lock:
            self._data = merged
            config_logger.info(
                f"Configuration loaded with {len(merged)} top-level keys"
            )

    @log_exception
    async def _load_all_async(self):
        config_logger.info("Loading configuration files asynchronously")
        defaults = await self._load_json_async(self.default_path)
        overrides = await self._load_json_async(self.user_path, optional=True)
        merged = self._deep_merge(defaults, overrides)

        try:
            config_logger.debug("Validating merged configuration")
            jsonschema.validate(merged, CONFIG_SCHEMA)
            config_logger.info("Configuration validation successful")
        except Exception as e:
            config_logger.error(f"Configuration validation error: {e}")
            raise RuntimeError(f"Config validation error: {e}")

        with self._data_lock:
            self._data = merged
            config_logger.info(
                f"Configuration loaded with {len(merged)} top-level keys"
            )

    def get(self, path: str, default=None):
        """
        Get a config value by dot-separated path.
        
        Args:
            path: Dot-separated path to config value
            default: Value to return if path not found
            
        Returns:
            Config value or default
        """
        keys = path.split('.')
        node = self._data
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                config_logger.debug(
                    f"Config path '{path}' not found, returning default: {default}"
                )
                return default
            node = node[key]
        config_logger.debug(f"Retrieved config value for '{path}'")
        return node

    @log_exception
    def set(self, path: str, value):
        """
        Set a config value by dot-separated path.
        
        Args:
            path: Dot-separated path to config value
            value: New value to set
        """
        keys = path.split('.')
        config_logger.debug(f"Setting config value for '{path}'")
        with self._data_lock:
            node = self._data
            for k in keys[:-1]:
                node = node.setdefault(k, {})
            node[keys[-1]] = value

    def save(self):
        with self._data_lock:
            self.user_path.parent.mkdir(exist_ok=True)
            self.user_path.write_text(json.dumps(self._data, indent=4))

    async def save_async(self):
        with self._data_lock:
            data = json.dumps(self._data, indent=4)
        if aiofiles:
            async with aiofiles.open(self.user_path, 'w') as f:
                await f.write(data)
        else:
            await asyncio.to_thread(self.save)

    def reload(self):
        self._load_all()

    async def reload_async(self):
        await self._load_all_async()