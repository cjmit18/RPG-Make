"""
Main Application - Entry point for the new RPG Engine
Demonstrates the async-first architecture with interactive UI
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from rpg_engine.core.engine import AsyncGameEngine
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus
from rpg_engine.ui.ui_system import AsyncUIManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rpg_engine.log')
    ]
)

logger = logging.getLogger(__name__)

class RPGApplication:
    """
    Main application class that orchestrates the new RPG Engine
    """
    
    def __init__(self):
        self.engine: Optional[AsyncGameEngine] = None
        self.ui_manager: Optional[AsyncUIManager] = None
        self.running = False
    
    async def initialize(self) -> None:
        """Initialize the application"""
        logger.info("Initializing RPG Application...")
        
        # Create engine with configuration
        config = {
            'target_fps': 60,
            'debug_mode': True,
            'ui_enabled': True
        }
        
        self.engine = AsyncGameEngine(config)
        
        # Initialize engine
        await self.engine.initialize_async()
        
        # Register UI system
        ui_manager = AsyncUIManager(self.engine.service_container)
        self.engine.service_container.register_instance(AsyncUIManager, ui_manager)
        
        # Initialize UI
        await ui_manager.initialize_async()
        self.ui_manager = ui_manager
        
        logger.info("RPG Application initialized successfully")
    
    async def run(self) -> None:
        """Run the application"""
        if not self.engine:
            await self.initialize()
        
        logger.info("Starting RPG Application...")
        self.running = True
        
        try:
            # Start the engine
            await self.engine.start_async()
            
            # Keep the application running
            while self.running and self.engine.state != "stopped":
                await asyncio.sleep(0.1)
                
                # Check if UI is still running
                if self.ui_manager and not self.ui_manager.ui_running:
                    logger.info("UI closed, shutting down...")
                    break
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Shutdown the application"""
        logger.info("Shutting down RPG Application...")
        self.running = False
        
        if self.engine:
            await self.engine.shutdown_async()
        
        logger.info("RPG Application shut down complete")

async def main():
    """Main entry point"""
    logger.info("Starting New RPG Engine with Interactive UI")
    
    app = RPGApplication()
    
    try:
        await app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Handle imports properly
    try:
        from typing import Optional
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
