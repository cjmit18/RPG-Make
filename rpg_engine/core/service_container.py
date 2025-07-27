"""
Service Container - Dependency Injection for RPG Engine
Provides async-first dependency injection with lifecycle management
"""
import asyncio
from typing import Dict, Type, TypeVar, Any, Callable, Optional, Protocol, runtime_checkable
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

@runtime_checkable
class AsyncInitializable(Protocol):
    """Protocol for services that need async initialization"""
    async def initialize_async(self) -> None: ...

@runtime_checkable
class AsyncShutdownable(Protocol):
    """Protocol for services that need async shutdown"""
    async def shutdown_async(self) -> None: ...

class ServiceNotFoundError(Exception):
    """Raised when a requested service is not registered"""
    pass

class ServiceContainer:
    """
    Async-first dependency injection container for managing service lifecycle
    """
    
    def __init__(self):
        self.services: Dict[Type, Any] = {}
        self.singletons: Dict[Type, Type] = {}
        self.factories: Dict[Type, Callable] = {}
        self.instances: Dict[Type, Any] = {}
        self.initialized: bool = False
        self._initialization_lock = asyncio.Lock()
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service"""
        logger.debug(f"Registering singleton: {interface.__name__} -> {implementation.__name__}")
        self.singletons[interface] = implementation
    
    def register_transient(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory-created service"""
        logger.debug(f"Registering transient service: {interface.__name__}")
        self.factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a pre-created instance"""
        logger.debug(f"Registering instance: {interface.__name__}")
        self.services[interface] = instance
    
    async def get_service(self, interface: Type[T]) -> T:
        """Resolve service with async initialization"""
        # Check if already instantiated
        if interface in self.instances:
            return self.instances[interface]
        
        # Check direct service registration
        if interface in self.services:
            return self.services[interface]
        
        # Create singleton instance
        if interface in self.singletons:
            async with self._initialization_lock:
                # Double-check after acquiring lock
                if interface in self.instances:
                    return self.instances[interface]
                
                implementation_class = self.singletons[interface]
                logger.info(f"Creating singleton instance of {interface.__name__}")
                
                # Create instance
                instance = implementation_class(self)
                
                # Initialize if needed
                if isinstance(instance, AsyncInitializable):
                    logger.debug(f"Async initializing {interface.__name__}")
                    await instance.initialize_async()
                
                self.instances[interface] = instance
                return instance
        
        # Create transient instance
        if interface in self.factories:
            logger.debug(f"Creating transient instance of {interface.__name__}")
            return await self.factories[interface]()
        
        raise ServiceNotFoundError(f"Service {interface.__name__} not registered")
    
    def override_service(self, interface: Type[T], instance: T) -> None:
        """Override an existing service with a new instance"""
        logger.info(f"Overriding service: {interface.__name__}")
        self.services[interface] = instance
    
    async def initialize_all_async(self) -> None:
        """Initialize all registered singleton services"""
        if self.initialized:
            return
        
        logger.info("Initializing all services...")
        
        # Initialize all singleton services
        for interface in self.singletons.keys():
            await self.get_service(interface)
        
        self.initialized = True
        logger.info("All services initialized successfully")
    
    async def shutdown_all_async(self) -> None:
        """Shutdown all services gracefully"""
        logger.info("Shutting down all services...")
        
        # Shutdown in reverse order of creation
        for interface, instance in reversed(list(self.instances.items())):
            if isinstance(instance, AsyncShutdownable):
                try:
                    logger.debug(f"Shutting down {interface.__name__}")
                    await instance.shutdown_async()
                except Exception as e:
                    logger.error(f"Error shutting down {interface.__name__}: {e}")
        
        self.instances.clear()
        self.services.clear()
        self.initialized = False
        logger.info("All services shut down")
    
    def list_registered_services(self) -> Dict[str, str]:
        """List all registered services for debugging"""
        services = {}
        
        for interface in self.singletons.keys():
            services[interface.__name__] = "singleton"
        
        for interface in self.factories.keys():
            services[interface.__name__] = "transient"
        
        for interface in self.services.keys():
            services[interface.__name__] = "instance"
        
        return services
