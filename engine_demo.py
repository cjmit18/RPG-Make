"""
RPG Engine Demo - Complete demonstration of the new async-first architecture
Shows the interactive UI, event system, service container, and engine capabilities
"""
import asyncio
import tkinter as tk
from tkinter import ttk
import logging
import threading
import time
import json

from rpg_engine.core.engine import AsyncGameEngine
from rpg_engine.core.event_bus import UIUpdateEvent, CharacterCreatedEvent
from rpg_engine.core.service_container import ServiceContainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('engine_demo.log')
    ]
)
logger = logging.getLogger(__name__)

class RPGEngineDemo:
    """Complete demonstration of the RPG Engine capabilities"""
    
    def __init__(self):
        self.engine = None
        self.root = None
        self.log_text = None
        self.status_labels = {}
        self.running = True
        self.stats_timer = None
        
    def create_ui(self):
        """Create the comprehensive demo UI"""
        self.root = tk.Tk()
        self.root.title("RPG Engine v2.0 - Complete Demo")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Configure styles
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="🎮 RPG Engine v2.0 - Async Architecture Demo", 
                         style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Subtitle
        subtitle = ttk.Label(main_frame, 
                           text="Demonstrating: Async Engine • Event System • Service Container • Interactive UI",
                           font=('Arial', 10))
        subtitle.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Engine Controls
        self.create_control_panel(main_frame)
        
        # Center panel - Output Log
        self.create_log_panel(main_frame)
        
        # Right panel - Status and Stats
        self.create_status_panel(main_frame)
        
        # Bottom panel - Demo Actions
        self.create_demo_panel(main_frame)
        
        # Initial messages
        self.log_message("🚀 RPG Engine Demo Started")
        self.log_message("📋 This demo showcases the new async-first architecture")
        self.log_message("🎯 Click 'Initialize Engine' to begin the demonstration")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_control_panel(self, parent):
        """Create the engine control panel"""
        controls_frame = ttk.LabelFrame(parent, text="🔧 Engine Controls", padding="10")
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        buttons = [
            ("Initialize Engine", self.init_engine, "Initialize the async game engine"),
            ("Start Engine", self.start_engine, "Start the main game loop"),
            ("Pause Engine", self.pause_engine, "Pause engine execution"),
            ("Resume Engine", self.resume_engine, "Resume engine execution"),
            ("Stop Engine", self.stop_engine, "Stop the engine gracefully"),
            ("", None, ""),
            ("Get Engine Stats", self.show_stats, "Show detailed engine statistics"),
            ("Clear Log", self.clear_log, "Clear the output log")
        ]
        
        for i, (text, command, tooltip) in enumerate(buttons):
            if text:
                btn = ttk.Button(controls_frame, text=text, command=command, 
                               style='Action.TButton' if i < 5 else None)
                btn.grid(row=i, column=0, pady=3, sticky=(tk.W, tk.E))
                # Add tooltip (simplified - just show in log when hovered)
            else:
                ttk.Separator(controls_frame, orient='horizontal').grid(
                    row=i, column=0, sticky=(tk.W, tk.E), pady=5)
        
        controls_frame.grid_columnconfigure(0, weight=1)
    
    def create_log_panel(self, parent):
        """Create the main log output panel"""
        log_frame = ttk.LabelFrame(parent, text="📋 Engine Output & Event Log", padding="10")
        log_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(text_frame, wrap=tk.WORD, width=70, height=30,
                               font=('Consolas', 9), bg='#1e1e1e', fg='#d4d4d4',
                               insertbackground='white')
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure colors for different log types
        self.log_text.tag_configure("info", foreground="#4CAF50")
        self.log_text.tag_configure("error", foreground="#F44336")
        self.log_text.tag_configure("warning", foreground="#FF9800")
        self.log_text.tag_configure("system", foreground="#2196F3")
        
        # Configure grid weights
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
    
    def create_status_panel(self, parent):
        """Create the status and statistics panel"""
        status_frame = ttk.LabelFrame(parent, text="📊 Engine Status", padding="10")
        status_frame.grid(row=2, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Status indicators
        status_items = [
            ("Engine State", "stopped", "system"),
            ("Target FPS", "60", "info"),
            ("Actual FPS", "0.0", "info"),
            ("Frame Count", "0", "info"),
            ("Uptime", "0s", "info"),
            ("", "", ""),
            ("Events Published", "0", "system"),
            ("Events Handled", "0", "system"),
            ("Event Errors", "0", "error"),
            ("", "", ""),
            ("Services Registered", "0", "system"),
            ("Memory Usage", "N/A", "warning")
        ]
        
        self.status_labels = {}
        row = 0
        
        for label_text, initial_value, tag in status_items:
            if label_text:
                # Label
                ttk.Label(status_frame, text=f"{label_text}:", 
                         style='Header.TLabel').grid(row=row, column=0, sticky=tk.W, pady=2)
                
                # Value
                value_label = ttk.Label(status_frame, text=initial_value)
                value_label.grid(row=row+1, column=0, sticky=tk.W, padx=(20, 0))
                
                self.status_labels[label_text] = value_label
                row += 2
            else:
                ttk.Separator(status_frame, orient='horizontal').grid(
                    row=row, column=0, sticky=(tk.W, tk.E), pady=5)
                row += 1
    
    def create_demo_panel(self, parent):
        """Create the demo actions panel"""
        demo_frame = ttk.LabelFrame(parent, text="🎮 Demo Actions", padding="10")
        demo_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        demo_buttons = [
            ("Test Event System", self.test_events, "Publish various test events"),
            ("Test Service Container", self.test_services, "Demonstrate service injection"),
            ("Simulate Game Loop", self.simulate_game, "Run a simulated game scenario"),
            ("Performance Test", self.performance_test, "Test engine performance"),
            ("Export Engine Stats", self.export_stats, "Export current statistics"),
        ]
        
        for i, (text, command, tooltip) in enumerate(demo_buttons):
            ttk.Button(demo_frame, text=text, command=command).grid(
                row=0, column=i, padx=5, sticky=(tk.W, tk.E))
        
        # Configure column weights
        for i in range(len(demo_buttons)):
            demo_frame.grid_columnconfigure(i, weight=1)
    
    def log_message(self, message, level="info"):
        """Add a message to the log with color coding"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        if self.log_text:
            self.log_text.insert(tk.END, full_message, (level,))
            self.log_text.see(tk.END)
        
        # Also log to console
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)
    
    def update_status(self, key, value):
        """Update a status label"""
        if key in self.status_labels:
            self.status_labels[key].configure(text=str(value))
    
    def init_engine(self):
        """Initialize the engine"""
        if self.engine:
            self.log_message("⚠️ Engine already initialized", "warning")
            return
        
        self.log_message("🔧 Initializing async game engine...", "system")
        
        def run_init():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                config = {
                    'target_fps': 60,
                    'debug_mode': True,
                    'ui_enabled': True
                }
                
                self.engine = AsyncGameEngine(config)
                loop.run_until_complete(self.engine.initialize_async())
                
                self.root.after(0, lambda: self.on_engine_initialized())
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Engine initialization failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=run_init, daemon=True).start()
    
    def on_engine_initialized(self):
        """Handle successful engine initialization"""
        self.log_message("✅ Engine initialized successfully!", "info")
        self.log_message("📋 Service container and event bus are ready", "system")
        self.update_status("Engine State", "initialized")
        self.update_status("Services Registered", len(self.engine.service_container.list_registered_services()))
        
        # Start status updates
        self.start_status_updates()
    
    def start_engine(self):
        """Start the engine"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        self.log_message("🚀 Starting engine game loop...", "system")
        
        def run_start():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self.engine.start_async())
                self.root.after(0, lambda: self.log_message("✅ Engine started - game loop running!", "info"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Engine start failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=run_start, daemon=True).start()
    
    def pause_engine(self):
        """Pause the engine"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        def run_pause():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.engine.pause_async())
                self.root.after(0, lambda: self.log_message("⏸️ Engine paused", "warning"))
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Pause failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=run_pause, daemon=True).start()
    
    def resume_engine(self):
        """Resume the engine"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        def run_resume():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.engine.resume_async())
                self.root.after(0, lambda: self.log_message("▶️ Engine resumed", "info"))
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Resume failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=run_resume, daemon=True).start()
    
    def stop_engine(self):
        """Stop the engine"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        self.log_message("⏹️ Stopping engine...", "system")
        
        def run_stop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self.engine.stop_async())
                self.root.after(0, lambda: self.log_message("✅ Engine stopped successfully", "info"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Engine stop failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=run_stop, daemon=True).start()
    
    def show_stats(self):
        """Show detailed engine statistics"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        stats = self.engine.get_stats()
        self.log_message("📊 Engine Statistics:", "system")
        self.log_message(f"   State: {stats['state']}")
        self.log_message(f"   Uptime: {stats['uptime']:.2f}s")
        self.log_message(f"   Frame Count: {stats['frame_count']}")
        self.log_message(f"   FPS: {stats['fps']:.2f}")
        self.log_message(f"   Last Frame Time: {stats['last_frame_time']:.4f}s")
        
        event_stats = stats['event_stats']
        self.log_message("📨 Event Bus Statistics:")
        self.log_message(f"   Events Published: {event_stats['events_published']}")
        self.log_message(f"   Events Handled: {event_stats['events_handled']}")
        self.log_message(f"   Errors: {event_stats['errors']}")
        
        self.log_message(f"🔧 Services: {list(stats['services'].keys())}")
    
    def clear_log(self):
        """Clear the output log"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
        self.log_message("🧹 Log cleared", "system")
    
    def test_events(self):
        """Test the event system"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        self.log_message("🧪 Testing event system...", "system")
        
        def run_test():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Test UI update event
                ui_event = UIUpdateEvent(
                    source="demo_ui",
                    component_id="test_panel",
                    update_type="test_interaction",
                    data={"test_time": time.time(), "test_data": "Hello Events!"}
                )
                loop.run_until_complete(self.engine.event_bus.publish(ui_event))
                
                # Test character creation event
                char_event = CharacterCreatedEvent(
                    source="demo_character_system",
                    character_id="test_char_001",
                    character_name="Demo Hero",
                    character_type="Warrior",
                    initial_stats={"strength": 10, "health": 100}
                )
                loop.run_until_complete(self.engine.event_bus.publish(char_event))
                
                self.root.after(0, lambda: self.log_message("✅ Test events published successfully!", "info"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Event test failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def test_services(self):
        """Test the service container"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        self.log_message("🧪 Testing service container...", "system")
        services = self.engine.service_container.list_registered_services()
        
        self.log_message(f"📋 Registered Services ({len(services)}):")
        for service_name, service_type in services.items():
            self.log_message(f"   • {service_name} ({service_type})")
        
        # Test service retrieval
        def test_retrieval():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                event_bus = loop.run_until_complete(
                    self.engine.service_container.get_service(type(self.engine.event_bus))
                )
                
                self.root.after(0, lambda: self.log_message(
                    f"✅ Service retrieval test passed - EventBus: {type(event_bus).__name__}", "info"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Service test failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=test_retrieval, daemon=True).start()
    
    def simulate_game(self):
        """Simulate a simple game scenario"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        self.log_message("🎮 Starting game simulation...", "system")
        
        def run_simulation():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Simulate game events over time
                events = [
                    ("Character created", CharacterCreatedEvent(
                        source="game_sim", character_id="hero_1", character_name="Sim Hero",
                        character_type="Mage", initial_stats={"magic": 15, "health": 80})),
                    ("UI updated", UIUpdateEvent(
                        source="game_sim", component_id="health_bar", update_type="health_changed",
                        data={"old_health": 80, "new_health": 60})),
                    ("Character created", CharacterCreatedEvent(
                        source="game_sim", character_id="enemy_1", character_name="Sim Enemy",
                        character_type="Orc", initial_stats={"strength": 12, "health": 100})),
                ]
                
                for i, (desc, event) in enumerate(events):
                    loop.run_until_complete(self.engine.event_bus.publish(event))
                    self.root.after(0, lambda d=desc, n=i+1: self.log_message(f"   {n}. {d}", "info"))
                    loop.run_until_complete(asyncio.sleep(0.5))
                
                self.root.after(0, lambda: self.log_message("✅ Game simulation completed!", "info"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Simulation failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=run_simulation, daemon=True).start()
    
    def performance_test(self):
        """Test engine performance"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        self.log_message("⚡ Running performance test...", "system")
        
        def run_perf_test():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                start_time = time.time()
                event_count = 100
                
                # Publish many events quickly
                for i in range(event_count):
                    event = UIUpdateEvent(
                        source="perf_test",
                        component_id=f"test_component_{i}",
                        update_type="performance_test",
                        data={"iteration": i, "timestamp": time.time()}
                    )
                    loop.run_until_complete(self.engine.event_bus.publish(event))
                
                end_time = time.time()
                duration = end_time - start_time
                events_per_second = event_count / duration
                
                self.root.after(0, lambda: self.log_message(
                    f"✅ Performance test completed:", "info"))
                self.root.after(0, lambda: self.log_message(
                    f"   Published {event_count} events in {duration:.3f}s", "info"))
                self.root.after(0, lambda: self.log_message(
                    f"   Rate: {events_per_second:.1f} events/second", "info"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Performance test failed: {e}", "error"))
            finally:
                loop.close()
        
        threading.Thread(target=run_perf_test, daemon=True).start()
    
    def export_stats(self):
        """Export engine statistics to file"""
        if not self.engine:
            self.log_message("❌ Engine not initialized", "error")
            return
        
        try:
            stats = self.engine.get_stats()
            filename = f"engine_stats_{int(time.time())}.json"
            
            with open(filename, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            self.log_message(f"📁 Statistics exported to {filename}", "info")
            
        except Exception as e:
            self.log_message(f"❌ Export failed: {e}", "error")
    
    def start_status_updates(self):
        """Start periodic status updates"""
        def update_stats():
            if self.engine and self.running:
                try:
                    stats = self.engine.get_stats()
                    
                    self.update_status("Engine State", stats['state'])
                    self.update_status("Actual FPS", f"{stats['fps']:.1f}")
                    self.update_status("Frame Count", stats['frame_count'])
                    self.update_status("Uptime", f"{stats['uptime']:.1f}s")
                    
                    event_stats = stats['event_stats']
                    self.update_status("Events Published", event_stats['events_published'])
                    self.update_status("Events Handled", event_stats['events_handled'])
                    self.update_status("Event Errors", event_stats['errors'])
                    
                except Exception as e:
                    logger.error(f"Error updating stats: {e}")
                
                # Schedule next update
                if self.running:
                    self.stats_timer = self.root.after(1000, update_stats)
        
        update_stats()
    
    def on_closing(self):
        """Handle window closing"""
        self.log_message("🔄 Shutting down demo...", "system")
        self.running = False
        
        if self.stats_timer:
            self.root.after_cancel(self.stats_timer)
        
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
    """Run the comprehensive RPG Engine demo"""
    logger.info("🚀 Starting RPG Engine Complete Demo")
    
    demo = RPGEngineDemo()
    demo.create_ui()
    demo.root.mainloop()
    
    logger.info("✅ Demo completed")

if __name__ == "__main__":
    main()
