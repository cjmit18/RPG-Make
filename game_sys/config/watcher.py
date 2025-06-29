# game_sys/config/watcher.py
"""
Module: game_sys.config.watcher

Watches config files for changes on disk, reloads configuration, and emits
ON_CONFIG_CHANGED events via ChangeCallbacks.
Requires 'watchdog' to monitor filesystem events.
"""
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from game_sys.config.config_manager import ConfigManager
from game_sys.config.change_callbacks import ChangeCallbacks

class ConfigChangeHandler(FileSystemEventHandler):
    """
    Handles file modification events, reloads config, and triggers change callbacks.
    """
    def __init__(self, change_cb: ChangeCallbacks):
        self.cfg = ConfigManager()
        self.change_cb = change_cb

    def on_modified(self, event):
        # Respond only to JSON config changes
        if event.src_path.endswith('.json'):
            # Reload config data
            self.cfg.reload()
            # Invoke change detection and event emission
            self.change_cb.check_changes()

class ConfigWatcher:
    """
    Monitors the directory containing config files and triggers callbacks on change.
    """
    def __init__(self, path: str = 'config'):
        self.observer = Observer()
        # Instantiate ChangeCallbacks to track config diffs
        self.change_cb = ChangeCallbacks()
        self.watch_path = path

    def start(self):
        """
        Start watching the config directory for JSON changes.
        """
        handler = ConfigChangeHandler(self.change_cb)
        self.observer.schedule(handler, self.watch_path, recursive=False)
        thread = threading.Thread(target=self.observer.start, daemon=True)
        thread.start()

    def stop(self):
        """
        Stop watching and clean up.
        """
        self.observer.stop()
        self.observer.join()
