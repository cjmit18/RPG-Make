"""
UI System - Async-first user interface framework
Provides the foundation for interactive UI components with event-driven updates
"""
import asyncio
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, List, Protocol
import logging
from abc import ABC, abstractmethod
import threading

from ..core.service_container import ServiceContainer, AsyncInitializable, AsyncShutdownable
from ..core.event_bus import EventBus, GameEvent, UIUpdateEvent

logger = logging.getLogger(__name__)

class UIComponent(ABC):
    """Base class for all UI components"""
    
    def __init__(self, component_id: str, parent=None):
        self.component_id = component_id
        self.parent = parent
        self.children: List['UIComponent'] = []
        self.visible = True
        self.enabled = True
        self.data: Dict[str, Any] = {}
    
    @abstractmethod
    def create_widget(self, parent_widget) -> tk.Widget:
        """Create the actual tkinter widget"""
        pass
    
    @abstractmethod
    async def update_async(self, data: Dict[str, Any]) -> None:
        """Update component with new data"""
        pass
    
    def add_child(self, child: 'UIComponent') -> None:
        """Add a child component"""
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child: 'UIComponent') -> None:
        """Remove a child component"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

class AsyncUIManager(AsyncInitializable, AsyncShutdownable):
    """
    Manages the UI system with async support
    Bridges tkinter's synchronous nature with our async engine
    """
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.event_bus: Optional[EventBus] = None
        
        # UI state
        self.root: Optional[tk.Tk] = None
        self.components: Dict[str, UIComponent] = {}
        self.update_queue: asyncio.Queue = asyncio.Queue()
        
        # Threading for tkinter
        self.ui_thread: Optional[threading.Thread] = None
        self.ui_running = False
        self.ui_ready = asyncio.Event()
        
        # Update task
        self.update_task: Optional[asyncio.Task] = None
        
        logger.info("AsyncUIManager initialized")
    
    async def initialize_async(self) -> None:
        """Initialize the UI system"""
        logger.info("Initializing UI system...")
        
        # Get event bus from service container
        self.event_bus = await self.service_container.get_service(EventBus)
        
        # Subscribe to UI update events
        self.event_bus.subscribe(UIUpdateEvent, self)
        
        # Start UI thread
        self.ui_running = True
        self.ui_thread = threading.Thread(target=self._run_ui_thread, daemon=True)
        self.ui_thread.start()
        
        # Wait for UI to be ready
        await self.ui_ready.wait()
        
        # Start update task
        self.update_task = asyncio.create_task(self._process_updates())
        
        logger.info("UI system initialized")
    
    def _run_ui_thread(self) -> None:
        """Run tkinter in a separate thread"""
        try:
            logger.debug("Starting UI thread...")
            
            # Create root window
            self.root = tk.Tk()
            self.root.title("RPG Engine - Interactive UI")
            self.root.geometry("1200x800")
            
            # Configure styling
            self._setup_styling()
            
            # Create main UI
            self._create_main_ui()
            
            # Signal that UI is ready using a simple flag
            self.ui_ready.set()
            
            # Start tkinter main loop
            while self.ui_running:
                try:
                    self.root.update()
                    # Small sleep to prevent excessive CPU usage
                    threading.Event().wait(0.016)  # ~60 FPS
                except tk.TclError:
                    break
            
            logger.debug("UI thread ending...")
            
        except Exception as e:
            logger.error(f"Error in UI thread: {e}")
        finally:
            if self.root:
                self.root.quit()
    
    async def _set_ui_ready(self) -> None:
        """Signal that UI is ready"""
        self.ui_ready.set()
    
    def _setup_styling(self) -> None:
        """Setup UI styling and themes"""
        style = ttk.Style()
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        
        logger.debug("UI styling configured")
    
    def _create_main_ui(self) -> None:
        """Create the main UI layout"""
        if not self.root:
            return
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="RPG Engine - New Architecture", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Controls
        self._create_control_panel(main_frame)
        
        # Center panel - Main content
        self._create_content_panel(main_frame)
        
        # Right panel - Status
        self._create_status_panel(main_frame)
        
        logger.debug("Main UI created")
    
    def _create_control_panel(self, parent) -> None:
        """Create the control panel"""
        control_frame = ttk.LabelFrame(parent, text="Engine Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Engine control buttons
        start_btn = ttk.Button(control_frame, text="Start Engine", 
                              style='Action.TButton',
                              command=self._queue_engine_action('start'))
        start_btn.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        pause_btn = ttk.Button(control_frame, text="Pause Engine",
                              command=self._queue_engine_action('pause'))
        pause_btn.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        stop_btn = ttk.Button(control_frame, text="Stop Engine",
                             command=self._queue_engine_action('stop'))
        stop_btn.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Test actions
        ttk.Separator(control_frame, orient='horizontal').grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        test_event_btn = ttk.Button(control_frame, text="Test Event",
                                   command=self._queue_action('test_event'))
        test_event_btn.grid(row=4, column=0, pady=5, sticky=(tk.W, tk.E))
        
        clear_log_btn = ttk.Button(control_frame, text="Clear Log",
                                  command=self._queue_action('clear_log'))
        clear_log_btn.grid(row=5, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Configure column weight
        control_frame.grid_columnconfigure(0, weight=1)
    
    def _create_content_panel(self, parent) -> None:
        """Create the main content panel"""
        content_frame = ttk.LabelFrame(parent, text="Engine Output", padding="10")
        content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Text area for logs and output
        text_frame = ttk.Frame(content_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create text widget with scrollbar
        self.log_text = tk.Text(text_frame, wrap=tk.WORD, width=60, height=30)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Initial message
        self.log_text.insert(tk.END, "RPG Engine UI System Initialized\n")
        self.log_text.insert(tk.END, "Ready to start the async engine...\n\n")
    
    def _create_status_panel(self, parent) -> None:
        """Create the status panel"""
        status_frame = ttk.LabelFrame(parent, text="Engine Status", padding="10")
        status_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Status labels
        self.status_labels = {}
        
        labels = [
            ("Engine State:", "stopped"),
            ("FPS:", "0"),
            ("Frame Count:", "0"),
            ("Uptime:", "0s"),
            ("Events Published:", "0"),
            ("Events Handled:", "0"),
            ("Services:", "0")
        ]
        
        for i, (label_text, initial_value) in enumerate(labels):
            ttk.Label(status_frame, text=label_text, style='Header.TLabel').grid(
                row=i*2, column=0, sticky=tk.W, pady=(5, 0))
            
            value_label = ttk.Label(status_frame, text=initial_value)
            value_label.grid(row=i*2+1, column=0, sticky=tk.W, padx=(20, 0))
            
            self.status_labels[label_text] = value_label
    
    def _queue_engine_action(self, action: str) -> Callable:
        """Create a callback that queues an engine action"""
        def callback():
            # Use a thread-safe way to add to the queue
            try:
                self.update_queue.put_nowait(('engine_action', action))
            except:
                logger.warning(f"Failed to queue engine action: {action}")
        return callback
    
    def _queue_action(self, action: str) -> Callable:
        """Create a callback that queues a general action"""
        def callback():
            try:
                self.update_queue.put_nowait(('action', action))
            except:
                logger.warning(f"Failed to queue action: {action}")
        return callback
    
    async def _process_updates(self) -> None:
        """Process UI updates from the async queue"""
        logger.debug("Starting UI update processor...")
        
        while self.ui_running:
            try:
                # Wait for update with timeout
                update = await asyncio.wait_for(self.update_queue.get(), timeout=0.1)
                await self._handle_update(update)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing UI update: {e}")
    
    async def _handle_update(self, update) -> None:
        """Handle a UI update"""
        update_type, data = update
        
        if update_type == 'engine_action':
            await self._handle_engine_action(data)
        elif update_type == 'action':
            await self._handle_action(data)
        elif update_type == 'ui_update':
            await self._handle_ui_update_event(data)
    
    async def _handle_engine_action(self, action: str) -> None:
        """Handle engine control actions"""
        try:
            from ..core.engine import AsyncGameEngine
            
            # Get engine instance (this would be injected in a real implementation)
            # For now, we'll create a simple test
            self._add_log_message(f"Engine action requested: {action}")
            
            if action == 'start':
                self._add_log_message("Starting engine... (This would start the actual engine)")
            elif action == 'pause':
                self._add_log_message("Pausing engine...")
            elif action == 'stop':
                self._add_log_message("Stopping engine...")
                
        except Exception as e:
            logger.error(f"Error handling engine action {action}: {e}")
            self._add_log_message(f"Error: {e}")
    
    async def _handle_action(self, action: str) -> None:
        """Handle general UI actions"""
        if action == 'test_event':
            self._add_log_message("Test event triggered!")
            if self.event_bus:
                await self.event_bus.publish(UIUpdateEvent(
                    source="ui",
                    component_id="test",
                    update_type="test_action",
                    data={"message": "Test event from UI"}
                ))
        
        elif action == 'clear_log':
            if self.root:
                self.log_text.delete(1.0, tk.END)
                self._add_log_message("Log cleared.")
    
    async def _handle_ui_update_event(self, event: UIUpdateEvent) -> None:
        """Handle UI update events"""
        self._add_log_message(f"UI Update: {event.update_type} from {event.source}")
    
    def _add_log_message(self, message: str) -> None:
        """Add a message to the log (thread-safe)"""
        def add_message():
            if self.log_text:
                self.log_text.insert(tk.END, f"{message}\n")
                self.log_text.see(tk.END)
        
        if self.root:
            self.root.after(0, add_message)
    
    async def handle(self, event: UIUpdateEvent) -> None:
        """Handle UI update events from the event bus"""
        await self.update_queue.put(('ui_update', event))
    
    async def shutdown_async(self) -> None:
        """Shutdown the UI system"""
        logger.info("Shutting down UI system...")
        
        self.ui_running = False
        
        # Cancel update task
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        
        # Close UI
        if self.root:
            self.root.after(0, self.root.quit)
        
        # Wait for UI thread
        if self.ui_thread and self.ui_thread.is_alive():
            self.ui_thread.join(timeout=2.0)
        
        logger.info("UI system shut down")
