# RPG Engine - GitHub Configuration

This directory contains GitHub-specific configuration files for the RPG Engine project.

## 🔄 Continuous Integration

### Workflows

- **`rpg-engine-tests.yml`** - Main test suite for the RPG engine
  - Tests core engine imports and functionality
  - Validates data-driven template system 
  - Tests observer pattern implementations (achievements & notifications)
  - Runs character stat calculation tests
  - Includes code quality checks with Black and flake8

- **`demo-tests.yml`** - Template system and observer pattern demonstrations
  - Validates template loading and character creation
  - Tests achievement and notification systems
  - Demonstrates data-driven content loading

- **`rpg-engine-release.yml`** - Release workflow for tagged versions
  - Runs comprehensive tests before release
  - Builds distribution packages
  - Generates automated release notes with system statistics

## 🎯 Current Focus Areas

The CI/CD pipeline focuses on testing our **data-driven template system**:

### ✅ Template System Testing
- **Character Templates**: Validates 6+ character classes with stat calculations  
- **Achievement Templates**: Tests 16+ achievements across multiple categories
- **Configuration System**: Validates derived stat formulas and game mechanics
- **Observer Patterns**: Tests event-driven achievement and notification systems

### ✅ System Architecture Testing  
- **Three-Layer Stat System**: Base stats → Growth rates → Derived stat formulas
- **Event Bus**: Publish/subscribe pattern for game events
- **JSON Validation**: Ensures data integrity across all template files
- **Hot-Reloading**: Tests template system reload capabilities

## 📊 Test Coverage

Current test coverage includes:
- Core engine component imports
- Template loading and validation
- Character stat calculations at multiple levels  
- Observer pattern event handling
- Configuration system validation
- JSON data integrity checks

## 🔧 Development Workflow

1. **Push to branches** triggers automatic testing
2. **Pull requests** run full test suite including demos
3. **Tagged releases** run comprehensive validation and build packages
4. **Code quality** checks ensure consistent formatting and style

## 📁 File Structure

```
.github/
├── workflows/
│   ├── rpg-engine-tests.yml      # Main test suite
│   ├── demo-tests.yml            # Template system demos  
│   └── rpg-engine-release.yml    # Release automation
├── ISSUE_TEMPLATE/               # Issue templates
├── instructions/                 # Development guidelines
└── README.md                     # This file
```

## 🎮 Template System Integration

The CI/CD pipeline is specifically designed around our **data-driven RPG engine**:

- **Character Templates**: Tests warrior, mage, rogue, cleric, paladin, and archmage templates
- **Achievement System**: Validates achievement loading and event-driven unlocking
- **Stat Calculations**: Ensures proper level-based stat progression 
- **Configuration Management**: Tests derived stat formulas (e.g., constitution × 10.0 = health)
- **Observer Patterns**: Validates achievement and notification systems respond to events

## 🚀 Getting Started

To run the same tests locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run template system tests
python test_template_loading.py

# Run character system demo
python examples/demo_character_system.py
```

## 📈 System Statistics

The current system supports:
- **6 Character Templates** (Basic → Legendary tiers)
- **16+ Achievement Templates** (Multiple categories)  
- **Complete Observer Pattern Implementation** (Events, achievements, notifications)
- **Data-Driven Architecture** (JSON-based content management)

All workflows automatically validate these systems and report statistics in the test output.
