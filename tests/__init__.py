"""
Test Suite Package
==================

Comprehensive test suite for the RPG engine covering all major components.

Test Categories:
- Unit tests for individual components
- Integration tests for system interactions
- UI tests for interface functionality
- Performance tests for optimization
- Regression tests for stability

Testing Utilities:
- Mock objects and test fixtures
- Test data generators
- Performance benchmarking tools
- UI testing helpers

Test Structure:
- tests/unit/: Unit tests for individual modules
- tests/integration/: Integration tests for system interactions
- tests/ui/: UI component and interaction tests
- tests/performance/: Performance and load tests
"""

import sys
import os
from pathlib import Path

# Add project root to path for test imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_CONFIG = {
    'data_dir': project_root / 'tests' / 'data',
    'fixtures_dir': project_root / 'tests' / 'fixtures',
    'temp_dir': project_root / 'tests' / 'temp',
    'verbose': True,
    'parallel': False
}

# Common test utilities
try:
    from .test_helpers import TestDataGenerator, MockServiceFactory
    from .fixtures import character_fixtures, combat_fixtures
except ImportError:
    TestDataGenerator = None
    MockServiceFactory = None
    character_fixtures = None
    combat_fixtures = None

__all__ = [
    "TEST_CONFIG",
    "TestDataGenerator",
    "MockServiceFactory",
    "character_fixtures",
    "combat_fixtures"
]