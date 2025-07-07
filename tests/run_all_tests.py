# tests/run_all_tests.py
"""
Comprehensive test runner that executes all tests for the game.
This will test the configuration system and demo functionality.
"""

import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the game modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import the test cases
from test_demo_features import TestDemoFeatures
from test_comprehensive_automated import TestComprehensiveAutomated


def run_tests():
    """Run all test cases for the game."""
    print("Running comprehensive tests for game with consolidated "
          "configuration...")
    
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDemoFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestComprehensiveAutomated))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Total tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) 
                        - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
