"""
Unit Tests Package
=================

Unit tests for individual components and modules of the RPG engine.

Test Modules:
- test_character_creation: Character creation service tests
- test_combat_system: Combat mechanics tests
- test_config_manager: Configuration management tests
- test_equipment_system: Equipment and inventory tests
- test_ui_components: UI component tests

Testing Approach:
- Isolated component testing
- Mock dependencies for true unit testing
- Comprehensive edge case coverage
- Performance validation
"""

# Unit test utilities
from unittest.mock import Mock, MagicMock, patch
import pytest

# Common test fixtures for unit tests
@pytest.fixture
def mock_config_manager():
    """Mock ConfigManager for unit tests."""
    mock = Mock()
    mock.get.return_value = "test_value"
    mock.set.return_value = True
    return mock

@pytest.fixture
def mock_logger():
    """Mock logger for unit tests."""
    mock = Mock()
    mock.info = Mock()
    mock.error = Mock()
    mock.warning = Mock()
    mock.debug = Mock()
    return mock

__all__ = [
    "Mock",
    "MagicMock", 
    "patch",
    "pytest",
    "mock_config_manager",
    "mock_logger"
]