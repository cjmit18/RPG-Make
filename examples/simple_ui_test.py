"""
Simple UI Test - Test the new engine with a basic UI
"""
import asyncio
import tkinter as tk
from tkinter import ttk
import logging
import threading
import time

from rpg_engine.core.engine import AsyncGameEngine
from rpg_engine.core.event_bus import UIUpdateEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleEngineUI:
    """A simple UI to test the engine"""
    
    def __init__(self):
        self.engine = None
        self.root = None
        self.log_text = None
        self.status_labels = {}
        self.running = True
        
    def create_ui(self):
        """Create the basic UI"""
        self.root = tk.Tk()
        self.root.title("RPG Engine Test")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="RPG Engine v2.0 - Test UI", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Control buttons
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        ttk.Button(controls_frame, text="Initialize Engine", 
                  command=self.init_engine).grid(row=0, column=0, pady=5, sticky=tk.W+tk.E)
        ttk.Button(controls_frame, text="Start Engine", 
                  command=self.start_engine).grid(row=1, column=0, pady=5, sticky=tk.W+tk.E)
        ttk.Button(controls_frame, text="Stop Engine", 
                  command=self.stop_engine).grid(row=2, column=0, pady=5, sticky=tk.W+tk.E)
        ttk.Button(controls_frame, text="Test Event", 
                  command=self.test_event).grid(row=3, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Engine Log", padding="10")
        log_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(log_frame, width=50, height=25)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        # Initial message
        self.log_message("RPG Engine UI Test Started")
        self.log_message("Click 'Initialize Engine' to begin")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def log_message(self, message):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        if self.log_text:
            self.log_text.insert(tk.END, full_message)
            self.log_text.see(tk.END)
        
        logger.info(message)
    
    def init_engine(self):
        """Initialize the engine"""
        if self.engine:
            self.log_message("Engine already initialized")
            return
        
        self.log_message("Initializing engine...")
        
        def run_init():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                self.engine = AsyncGameEngine({'target_fps': 60})
                loop.run_until_complete(self.engine.initialize_async())
                
                self.root.after(0, lambda: self.log_message("✓ Engine initialized successfully"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"✗ Engine initialization failed: {e}"))
            finally:
                loop.close()
        
        threading.Thread(target=run_init, daemon=True).start()
    
    def start_engine(self):
        """Start the engine"""
        if not self.engine:
            self.log_message("✗ Engine not initialized")
            return
        
        self.log_message("Starting engine...")
        
        def run_start():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self.engine.start_async())
                self.root.after(0, lambda: self.log_message("✓ Engine started successfully"))
                
                # Run the engine for a few seconds as a test
                asyncio.create_task(self._monitor_engine())
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"✗ Engine start failed: {e}"))
            finally:
                loop.close()
        
        threading.Thread(target=run_start, daemon=True).start()
    
    async def _monitor_engine(self):
        """Monitor engine stats"""
        for i in range(10):  # Monitor for 10 seconds
            if self.engine:
                stats = self.engine.get_stats()
                self.root.after(0, lambda s=stats: self.log_message(
                    f"Engine Stats - State: {s['state']}, FPS: {s['fps']:.1f}, Frames: {s['frame_count']}"
                ))
            await asyncio.sleep(1)
    
    def stop_engine(self):
        """Stop the engine"""
        if not self.engine:
            self.log_message("✗ Engine not initialized")
            return
        
        self.log_message("Stopping engine...")
        
        def run_stop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self.engine.stop_async())
                self.root.after(0, lambda: self.log_message("✓ Engine stopped successfully"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"✗ Engine stop failed: {e}"))
            finally:
                loop.close()
        
        threading.Thread(target=run_stop, daemon=True).start()
    
    def test_event(self):
        """Test event publishing"""
        if not self.engine:
            self.log_message("✗ Engine not initialized")
            return
        
        self.log_message("Publishing test event...")
        
        def run_test():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                test_event = UIUpdateEvent(
                    source="ui_test",
                    component_id="test_button",
                    update_type="test_click",
                    data={"timestamp": time.time()}
                )
                
                loop.run_until_complete(self.engine.event_bus.publish(test_event))
                self.root.after(0, lambda: self.log_message("✓ Test event published successfully"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"✗ Test event failed: {e}"))
            finally:
                loop.close()
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def on_closing(self):
        """Handle window closing"""
        self.log_message("Shutting down...")
        self.running = False
        
        if self.engine:
            def run_shutdown():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.engine.shutdown_async())
                finally:
                    loop.close()
                    self.root.after(0, self.root.destroy)
            
            threading.Thread(target=run_shutdown, daemon=True).start()
        else:
            self.root.destroy()
    
def main():
    """Run the simple UI test"""
    logger.info("Starting Simple Engine UI Test")
    
    ui = SimpleEngineUI()
    ui.create_ui()
    ui.root.mainloop()
    
    logger.info("UI Test completed")

if __name__ == "__main__":
    main()
