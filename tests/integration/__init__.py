"""
Integration Tests Package
========================

Integration tests for system-wide interactions and service integration.

Test Scenarios:
- Character creation to combat flow
- UI service integration with backend services
- Configuration changes affecting multiple systems
- Data persistence and retrieval workflows

Integration Points:
- Service-to-service communication
- UI-to-service interactions
- Database integration testing
- External API integration
- Configuration system integration
"""

import asyncio
from typing import Dict, Any
from pathlib import Path

# Integration test configuration
INTEGRATION_CONFIG = {
    'test_db_path': Path(__file__).parent / 'test_data.db',
    'mock_external_services': True,
    'cleanup_after_tests': True,
    'timeout_seconds': 30
}

# Integration test helpers
class IntegrationTestHelper:
    """Helper class for integration testing."""
    
    @staticmethod
    def setup_test_environment():
        """Set up test environment for integration tests."""
        pass
    
    @staticmethod
    def cleanup_test_environment():
        """Clean up test environment after integration tests."""
        pass

__all__ = [
    "INTEGRATION_CONFIG",
    "IntegrationTestHelper",
    "asyncio"
]