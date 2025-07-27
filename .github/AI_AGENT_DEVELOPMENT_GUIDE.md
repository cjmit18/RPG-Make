# AI Agent Development Guide - RPG Engine Implementation
*A comprehensive guide for AI agents on structuring and developing the RPG engine*

## Overview for AI Agents

This guide provides specific instructions for AI assistants working on the RPG engine codebase. It outlines best practices, code patterns, architectural decisions, and development workflows optimized for AI-assisted development.

## Core Development Principles

### 1. **Code Analysis Before Implementation**
Always perform comprehensive analysis before making changes:

```python
# Analysis Workflow for AI Agents
def analyze_before_implement():
    """AI Agent workflow for code changes"""
    
    # Step 1: Understand the request
    - Parse user requirements carefully
    - Identify affected systems and dependencies
    - Determine scope of changes needed
    
    # Step 2: Gather context
    - Read relevant files completely (not just snippets)
    - Use semantic_search for related functionality  
    - Check existing patterns and conventions
    - Review test files for expected behavior
    
    # Step 3: Plan the implementation
    - Design changes to fit existing architecture
    - Identify all files that need modification
    - Plan backward compatibility preservation
    - Consider error handling and edge cases
    
    # Step 4: Implement incrementally
    - Make small, focused changes
    - Test each change before proceeding
    - Maintain existing APIs during transitions
    - Add comprehensive error handling
```

### 2. **Architectural Pattern Recognition**
The current engine uses these key patterns - preserve and extend them:

#### **Service Layer Pattern**
```python
# Current Pattern - Always Follow This Structure
class SomeService:
    def __init__(self, dependencies...):
        self.dependency = dependency
        self.logger = get_logger(__name__)
    
    def public_method(self, params) -> ServiceResult:
        """Public API methods return ServiceResult objects"""
        try:
            result = self._internal_logic(params)
            return ServiceResult.success_result(data=result)
        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__}: {e}")
            return ServiceResult.error_result(str(e))
    
    def _internal_logic(self, params):
        """Private methods contain actual business logic"""
        # Implementation here
        pass
```

#### **Event-Driven Updates**
```python
# Current Hook System - Use This Pattern
from game_sys.hooks.hooks_setup import emit, on

# Publishing events
emit("CHARACTER_STAT_CHANGED", actor=character, stat="strength", old_value=10, new_value=12)

# Subscribing to events  
def on_stat_changed(actor, stat, old_value, new_value, **kwargs):
    print(f"{actor.name}'s {stat} changed from {old_value} to {new_value}")

on("CHARACTER_STAT_CHANGED", on_stat_changed)
```

#### **Configuration-Driven Design**
```python
# Always use ConfigManager for settings
from game_sys.config.config_manager import ConfigManager

config = ConfigManager()
max_level = config.get('constants.leveling.max_level', 100)
stat_multipliers = config.get_section('derived_stat_multipliers', {})
```

### 3. **File Organization Patterns**
Follow the established directory structure:

```
game_sys/
├── character/           # Character-related functionality
│   ├── services/        # Business logic services
│   ├── data/           # JSON data files (templates, etc.)
│   └── *.py            # Core character modules
├── combat/             # Combat system components
├── config/             # Configuration management
├── core/               # Core engine functionality
├── items/              # Item and equipment system
├── ui/                 # User interface components
└── utils/              # Utility functions

# File Naming Conventions
- Services: character_creation_service.py
- Managers: leveling_manager.py  
- Data Files: character_templates.json
- Tests: test_character_creation.py
- Utilities: stat_calculations.py
```

## Development Workflows for AI Agents

### 1. **Adding New Features**

```python
# AI Agent Workflow for New Features
async def implement_new_feature(feature_request):
    """
    Template workflow for implementing new features
    """
    
    # Phase 1: Analysis and Planning
    existing_patterns = await analyze_codebase(feature_request)
    affected_files = await identify_dependencies(feature_request)
    integration_points = await find_integration_points(existing_patterns)
    
    # Phase 2: Design Validation
    design = create_feature_design(feature_request, existing_patterns)
    validate_backward_compatibility(design, affected_files)
    plan_testing_strategy(design)
    
    # Phase 3: Implementation
    for component in design.components:
        implement_component(component, existing_patterns)
        add_error_handling(component)
        create_tests(component)
        validate_integration(component, integration_points)
    
    # Phase 4: Documentation and Cleanup
    update_documentation(design)
    add_usage_examples(design.components)
    cleanup_temporary_code()
```

### 2. **Modifying Existing Systems**

```python
# AI Agent Workflow for System Modifications
async def modify_existing_system(modification_request):
    """
    Template workflow for modifying existing systems
    """
    
    # Phase 1: Impact Analysis
    current_implementation = await analyze_current_code(modification_request)
    dependent_systems = await find_all_dependencies(current_implementation)
    breaking_changes = await identify_breaking_changes(modification_request)
    
    # Phase 2: Preservation Strategy
    backward_compatibility_plan = create_compatibility_layer(breaking_changes)
    migration_strategy = plan_gradual_migration(dependent_systems)
    rollback_plan = create_rollback_strategy(current_implementation)
    
    # Phase 3: Safe Implementation
    implement_compatibility_layer(backward_compatibility_plan)
    implement_new_functionality(modification_request)
    migrate_dependent_systems(migration_strategy)
    
    # Phase 4: Validation and Cleanup
    validate_all_existing_functionality()
    update_documentation(modification_request)
    remove_deprecated_code_after_migration()
```

### 3. **Bug Fixing Protocol**

```python
# AI Agent Workflow for Bug Fixes
async def fix_bug(bug_report):
    """
    Template workflow for fixing bugs
    """
    
    # Phase 1: Root Cause Analysis
    reproduction_steps = extract_reproduction_steps(bug_report)
    error_context = gather_error_context(bug_report)
    affected_code = locate_bug_source(error_context, reproduction_steps)
    
    # Phase 2: Impact Assessment
    fix_scope = determine_fix_scope(affected_code)
    regression_risk = assess_regression_risk(fix_scope)
    test_strategy = plan_comprehensive_testing(fix_scope, regression_risk)
    
    # Phase 3: Implementation
    implement_minimal_fix(affected_code, bug_report)
    add_defensive_programming(affected_code)
    enhance_error_handling(affected_code)
    
    # Phase 4: Validation
    verify_bug_fixed(reproduction_steps)
    run_regression_tests(test_strategy)
    update_relevant_documentation()
```

## Code Quality Standards

### 1. **Error Handling Patterns**

```python
# Always use this error handling pattern
class EngineComponent:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def public_method(self, params) -> ServiceResult:
        """All public methods return ServiceResult"""
        try:
            # Validate inputs first
            if not self._validate_params(params):
                return ServiceResult.error_result("Invalid parameters")
            
            # Perform operation
            result = self._perform_operation(params)
            
            # Log success for debugging
            self.logger.debug(f"Operation completed successfully: {result}")
            return ServiceResult.success_result(data=result)
            
        except ValidationError as e:
            self.logger.warning(f"Validation failed: {e}")
            return ServiceResult.error_result(f"Validation error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in {self.__class__.__name__}: {e}", exc_info=True)
            return ServiceResult.error_result(f"Internal error: {e}")
    
    def _validate_params(self, params) -> bool:
        """Always validate inputs"""
        if not params:
            return False
        # Add specific validations
        return True
    
    def _perform_operation(self, params):
        """Internal logic with proper error propagation"""
        # Implementation here
        pass
```

### 2. **Logging Standards**

```python
# Logging Pattern - Use Throughout Engine
from game_sys.logging import get_logger

class ServiceClass:
    def __init__(self):
        # Use class name for logger
        self.logger = get_logger(self.__class__.__name__)
    
    def operation(self):
        # Debug: Detailed development info
        self.logger.debug(f"Starting operation with params: {params}")
        
        # Info: Important state changes
        self.logger.info(f"Character {character.name} leveled up to {new_level}")
        
        # Warning: Recoverable issues
        self.logger.warning(f"Using default value for missing config: {key}")
        
        # Error: Problems that need attention
        self.logger.error(f"Failed to save character: {error}")
        
        # Critical: System-threatening issues
        self.logger.critical(f"Engine initialization failed: {error}")
```

### 3. **Configuration Integration**

```python
# Configuration Pattern - Always Use ConfigManager
from game_sys.config.config_manager import ConfigManager

class ConfigurableService:
    def __init__(self):
        self.config = ConfigManager()
        self.logger = get_logger(self.__class__.__name__)
        
        # Load configuration with defaults
        self.max_level = self.config.get('constants.leveling.max_level', 100)
        self.stat_points_per_level = self.config.get('constants.leveling.stat_points_per_level', 5)
        
        # Load complex configuration sections
        self.stat_multipliers = self.config.get_section('derived_stat_multipliers', {
            'strength_to_attack': 1.0,
            'dexterity_to_speed': 0.1,
            'vitality_to_defense': 0.8
        })
        
        # Always log configuration loading
        self.logger.info(f"Loaded configuration: max_level={self.max_level}")
    
    def reconfigure(self):
        """Support hot-reload of configuration"""
        old_config = {
            'max_level': self.max_level,
            'stat_points': self.stat_points_per_level
        }
        
        # Reload configuration
        self.config.reload()
        self.max_level = self.config.get('constants.leveling.max_level', 100)
        self.stat_points_per_level = self.config.get('constants.leveling.stat_points_per_level', 5)
        
        # Log changes
        self.logger.info(f"Configuration reloaded: {old_config} -> new values")
```

## Testing Patterns for AI Agents

### 1. **Test Structure**

```python
# Test File Pattern - tests/test_feature_name.py
import pytest
from unittest.mock import Mock, patch
from game_sys.character.character_creation_service import CharacterCreationService
from game_sys.config.config_manager import ConfigManager

class TestCharacterCreationService:
    """Test class follows naming convention: Test + ClassName"""
    
    @pytest.fixture
    def config_manager(self):
        """Create mock configuration"""
        config = Mock(spec=ConfigManager)
        config.get.return_value = 100  # Default return
        config.get_section.return_value = {}
        return config
    
    @pytest.fixture  
    def service(self, config_manager):
        """Create service instance with mocked dependencies"""
        with patch('game_sys.character.character_creation_service.ConfigManager', return_value=config_manager):
            return CharacterCreationService()
    
    def test_create_character_success(self, service):
        """Test successful character creation"""
        # Arrange
        template = {'name': 'Warrior', 'stats': {'strength': 10}}
        
        # Act
        result = service.create_character(template)
        
        # Assert
        assert result.success is True
        assert result.data is not None
        assert 'character' in result.data
    
    def test_create_character_invalid_template(self, service):
        """Test error handling with invalid input"""
        # Arrange
        invalid_template = None
        
        # Act
        result = service.create_character(invalid_template)
        
        # Assert
        assert result.success is False
        assert result.error is not None
        assert "Invalid template" in result.error
    
    @pytest.mark.parametrize(
        "template,expected_stat",
        [
            ({'class': 'warrior'}, 15),  # Warrior gets +5 strength
            ({'class': 'mage'}, 10),     # Mage gets base strength
            ({'class': 'rogue'}, 12),    # Rogue gets +2 strength
        ]
    )
    def test_character_stat_allocation(self, service, template, expected_stat):
        """Test parameterized stat allocation"""
        result = service.create_character(template)
        character = result.data['character']
        assert character.get_stat('strength') == expected_stat
```

### 2. **Integration Testing**

```python
# Integration Test Pattern
class TestCharacterCreationIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_character_creation_workflow(self):
        """Test end-to-end character creation"""
        # Use real services, not mocks
        service = CharacterCreationService()
        
        # Test complete workflow
        template_result = service.get_available_templates()
        assert template_result.success
        
        template = template_result.data['templates'][0]
        create_result = service.create_character(template)
        assert create_result.success
        
        character = create_result.data['character']
        assert character.name is not None
        assert character.level > 0
    
    def test_character_save_and_load(self):
        """Test data persistence"""
        service = CharacterCreationService()
        library_service = CharacterLibraryService()
        
        # Create character
        template = {'name': 'TestChar', 'class': 'warrior'}
        create_result = service.create_character(template)
        character = create_result.data['character']
        
        # Save character
        save_result = library_service.save_character(character)
        assert save_result.success
        character_id = save_result.data['character_id']
        
        # Load character
        load_result = library_service.load_character(character_id)
        assert load_result.success
        loaded_character = load_result.data['character']
        
        # Verify data integrity
        assert loaded_character.name == character.name
        assert loaded_character.get_stat('strength') == character.get_stat('strength')
```

## AI Agent Decision Trees

### 1. **When to Use Each Tool**

```python
# Decision Tree for Tool Selection
def select_appropriate_tool(task_type, context):
    """Guide for AI agents on tool selection"""
    
    if task_type == "analyze_codebase":
        if "specific_function" in context:
            return "grep_search"  # Find specific patterns
        elif "understand_architecture" in context:
            return "semantic_search"  # Broad understanding
        elif "file_exists" in context:
            return "file_search"  # Find files by pattern
        else:
            return "list_dir"  # Explore structure
    
    elif task_type == "read_code":
        if "large_file" in context:
            return "read_file with large ranges"  # Read substantial chunks
        elif "specific_section" in context:
            return "read_file with targeted ranges"  # Focused reading
        else:
            return "read_file"  # Standard reading
    
    elif task_type == "modify_code":
        if "new_file" in context:
            return "create_file"  # Create new implementation
        elif "small_change" in context:
            return "replace_string_in_file"  # Surgical edits
        else:
            return "multiple replace_string_in_file calls"  # Complex changes
    
    elif task_type == "run_operations":
        if "test_code" in context:
            return "run_in_terminal"  # Execute tests
        elif "install_packages" in context:
            return "install_python_packages"  # Package management
        else:
            return "run_in_terminal"  # General execution
```

### 2. **Error Recovery Strategies**

```python
# Error Recovery Decision Tree
def handle_development_error(error_type, context):
    """Guide for recovering from development errors"""
    
    if error_type == "ServiceResult_vs_Dictionary":
        return """
        1. Check if code expects ServiceResult object or plain dictionary
        2. Current system uses backward compatibility layer in demo_v3.py
        3. UI expects dictionary format: {'success': bool, 'data': dict}
        4. Services return ServiceResult objects with .success, .data, .error
        5. Convert using: result_dict = {'success': result.success, 'data': result.data}
        """
    
    elif error_type == "Character_State_Management":
        return """
        1. Never clear existing character state unless explicitly requested
        2. Use character_service.update_character() instead of creating new
        3. Preserve level, grade, rarity when resetting stats
        4. Reset should only affect base_stats, not derived stats
        5. Always validate character exists before operations
        """
    
    elif error_type == "Configuration_Not_Found":
        return """
        1. Always provide default values: config.get('key', default_value)
        2. Check if default_settings.json contains the required key
        3. Use config.get_section() for complex configurations
        4. Log missing configuration with warning level
        5. Ensure backward compatibility with old config files
        """
    
    elif error_type == "Import_Errors":
        return """
        1. Check existing import patterns in similar files
        2. Use relative imports within game_sys package
        3. Verify file exists and has correct class/function names
        4. Check for circular import dependencies
        5. Use absolute imports for external libraries
        """
```

### 3. **Code Review Checklist**

```python
# AI Agent Code Review Checklist
def perform_code_review(changed_files):
    """Comprehensive code review checklist for AI agents"""
    
    checklist = {
        "error_handling": [
            "All public methods return ServiceResult objects",
            "Exceptions are caught and logged appropriately", 
            "Input validation is performed",
            "Graceful degradation for missing resources"
        ],
        
        "backward_compatibility": [
            "Existing APIs are preserved or properly deprecated",
            "Database/save file formats are compatible",
            "Configuration changes have migration paths",
            "UI workflows remain functional"
        ],
        
        "performance": [
            "No unnecessary loops or recursive calls",
            "Database queries are optimized",
            "Large objects are not copied unnecessarily",
            "Async operations are used for I/O"
        ],
        
        "maintainability": [
            "Code follows established patterns",
            "Functions have single responsibilities", 
            "Variable names are descriptive",
            "Magic numbers are replaced with named constants"
        ],
        
        "testing": [
            "Unit tests cover new functionality",
            "Integration tests validate workflows",
            "Error conditions are tested",
            "Performance tests for critical paths"
        ],
        
        "documentation": [
            "Public APIs have docstrings",
            "Complex algorithms are explained",
            "Configuration options are documented",
            "Breaking changes are noted"
        ]
    }
    
    return checklist
```

## Common Pitfalls and Solutions

### 1. **Service Result vs Dictionary Confusion**

```python
# PROBLEM: Mixing ServiceResult objects with dictionary expectations
# Current UI expects dictionaries, services return ServiceResult objects

# WRONG:
def ui_method(self):
    result = self.character_service.create_character(template)
    if result['success']:  # Error: ServiceResult has .success, not ['success']
        character = result['data']

# RIGHT:
def ui_method(self):
    result = self.character_service.create_character(template)
    if result.success:  # Correct: Access .success attribute
        character = result.data
    
    # OR convert for UI compatibility:
    result_dict = {
        'success': result.success,
        'data': result.data or {},
        'error': result.error
    }
    return result_dict
```

### 2. **Character State Management**

```python
# PROBLEM: Clearing character state when user wants to preserve it

# WRONG:
def reset_character_stats(self):
    self.current_character = None  # Clears everything
    return self.create_new_character()

# RIGHT:
def reset_character_stats(self):
    if not self.current_character:
        return ServiceResult.error_result("No character to reset")
    
    # Preserve important state
    level = self.current_character.level
    grade = self.current_character.grade  
    rarity = self.current_character.rarity
    
    # Reset only base stats to template values
    template = self.get_character_template(self.current_character.template_id)
    self.current_character.base_stats = template['base_stats'].copy()
    
    # Restore preserved state
    self.current_character.level = level
    self.current_character.grade = grade
    self.current_character.rarity = rarity
    
    return ServiceResult.success_result(data={'character': self.current_character})
```

### 3. **Configuration Loading**

```python
# PROBLEM: Not providing defaults or handling missing config

# WRONG:
def load_settings(self):
    max_level = config.get('constants.leveling.max_level')  # Could be None
    if max_level > 100:  # Error if max_level is None
        # logic here

# RIGHT:
def load_settings(self):
    max_level = config.get('constants.leveling.max_level', 100)  # Always has value
    if max_level > 100:
        # logic here
    
    # For complex configs:
    leveling_config = config.get_section('leveling', {
        'max_level': 100,
        'stat_points_per_level': 5,
        'experience_curve': 'linear'
    })
```

## Integration Patterns

### 1. **Adding New Services**

```python
# Pattern for adding new services to the engine
class NewGameService:
    """New service following engine patterns"""
    
    def __init__(self, dependencies...):
        # Always include logger
        self.logger = get_logger(self.__class__.__name__)
        
        # Store dependencies
        self.config = ConfigManager()
        self.other_service = other_service
        
        # Load configuration
        self.settings = self.config.get_section('new_service', {})
        
        self.logger.info(f"{self.__class__.__name__} initialized")
    
    def public_api_method(self, params) -> ServiceResult:
        """Public methods always return ServiceResult"""
        try:
            # Implementation
            result = self._internal_method(params)
            return ServiceResult.success_result(data=result)
        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__}: {e}")
            return ServiceResult.error_result(str(e))
    
    def _internal_method(self, params):
        """Private methods contain business logic"""
        pass

# Integration with demo_v3.py
class DemoAppIntegration:
    def integrate_new_service(self):
        # Add to demo initialization
        self.new_service = NewGameService(dependencies...)
        
        # Create UI wrapper if needed
        def ui_wrapper_method(self, params):
            result = self.new_service.public_api_method(params)
            # Convert to dictionary for UI
            return {
                'success': result.success,
                'data': result.data or {},
                'error': result.error
            }
```

### 2. **Event Integration**

```python
# Pattern for integrating with event system
from game_sys.hooks.hooks_setup import emit, on

class EventIntegratedService:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        
        # Subscribe to relevant events
        on("CHARACTER_CREATED", self.on_character_created)
        on("CHARACTER_LEVEL_UP", self.on_character_level_up)
    
    def perform_action(self, character, action_data):
        """Action that triggers events"""
        try:
            # Perform action
            result = self._execute_action(character, action_data)
            
            # Emit event for other systems
            emit("ACTION_PERFORMED", 
                 actor=character, 
                 action=action_data, 
                 result=result)
            
            return ServiceResult.success_result(data=result)
        except Exception as e:
            # Emit error event
            emit("ACTION_FAILED", 
                 actor=character, 
                 action=action_data, 
                 error=str(e))
            return ServiceResult.error_result(str(e))
    
    def on_character_created(self, actor, **kwargs):
        """Event handler for character creation"""
        self.logger.info(f"New character created: {actor.name}")
        # Initialize service-specific data for character
    
    def on_character_level_up(self, actor, old_level, new_level, **kwargs):
        """Event handler for level up"""
        self.logger.info(f"{actor.name} leveled up: {old_level} -> {new_level}")
        # Handle level up consequences
```

## File Modification Guidelines

### 1. **Reading Files Effectively**

```python
# AI Agent file reading strategy
def read_file_strategically(file_path, purpose):
    """Strategic file reading for AI agents"""
    
    if purpose == "understand_structure":
        # Read key sections: imports, class definitions, main functions
        key_ranges = [
            (1, 50),      # Imports and module docstring
            (100, 200),   # Main class definitions
            (-50, -1)     # End of file (main execution)
        ]
        return [read_file(file_path, start, end) for start, end in key_ranges]
    
    elif purpose == "find_specific_function":
        # Use grep_search first, then read surrounding context
        search_result = grep_search(f"def {function_name}", file_path)
        if search_result:
            line_num = search_result[0].line_number
            return read_file(file_path, line_num - 10, line_num + 50)
    
    elif purpose == "understand_error":
        # Read error-prone sections with extra context
        error_line = extract_line_number_from_error(error_msg)
        return read_file(file_path, max(1, error_line - 20), error_line + 20)
```

### 2. **Making Surgical Changes**

```python
# Pattern for precise code modifications
def make_surgical_edit(file_path, change_description):
    """Make precise changes without affecting surrounding code"""
    
    # Step 1: Read enough context to uniquely identify the change location
    context_lines = 10  # Read 10 lines before and after target
    
    # Step 2: Identify the exact old_string to replace
    old_string = extract_old_code_with_context(file_path, change_description, context_lines)
    
    # Step 3: Create new_string preserving whitespace and indentation
    new_string = create_new_code_preserving_formatting(old_string, change_description)
    
    # Step 4: Validate the change won't break syntax
    validate_syntax_after_change(file_path, old_string, new_string)
    
    # Step 5: Make the change
    return replace_string_in_file(file_path, old_string, new_string)

# Example of surgical edit
def fix_service_result_access():
    """Fix ServiceResult vs dictionary access"""
    
    old_string = """        # UI expects dictionary format
        if result['success']:  # This will fail
            character = result['data']
            return {'success': True, 'character': character}"""
    
    new_string = """        # UI expects dictionary format
        if result.success:  # Correct ServiceResult access
            character = result.data
            return {'success': True, 'character': character}"""
    
    return replace_string_in_file(file_path, old_string, new_string)
```

## Debugging Strategies

### 1. **Error Investigation Process**

```python
# AI Agent debugging workflow
def investigate_error(error_message, stack_trace):
    """Systematic error investigation"""
    
    # Step 1: Parse the error
    error_type = extract_error_type(error_message)
    file_path = extract_file_from_stack_trace(stack_trace)
    line_number = extract_line_number(stack_trace)
    
    # Step 2: Gather context
    error_context = read_file(file_path, line_number - 10, line_number + 10)
    related_code = semantic_search(f"similar functionality to {error_type}")
    
    # Step 3: Identify root cause
    if error_type == "AttributeError":
        # Check if accessing wrong attribute type (ServiceResult vs dict)
        return investigate_attribute_error(error_context)
    elif error_type == "KeyError":
        # Check if expected dictionary key is missing
        return investigate_key_error(error_context)
    elif error_type == "TypeError":
        # Check type mismatches in function calls
        return investigate_type_error(error_context)
    
    # Step 4: Plan fix
    root_cause = identify_root_cause(error_context, related_code)
    fix_strategy = plan_fix_strategy(root_cause, error_type)
    
    return fix_strategy

def investigate_attribute_error(error_context):
    """Specific investigation for AttributeError"""
    
    # Common pattern: ServiceResult vs dictionary confusion
    if "has no attribute 'success'" in error_context:
        return "Convert ServiceResult to dictionary for UI compatibility"
    elif "'dict' object has no attribute 'success'" in error_context:
        return "Use dictionary access ['success'] instead of .success attribute"
    
    return "Unknown attribute error - investigate further"
```

### 2. **Testing Strategy**

```python
# AI Agent testing approach
def create_comprehensive_tests(new_feature):
    """Create test suite for new functionality"""
    
    test_categories = [
        "unit_tests",      # Test individual functions
        "integration_tests",  # Test component interactions  
        "error_tests",     # Test error handling
        "edge_case_tests", # Test boundary conditions
        "regression_tests" # Ensure existing functionality works
    ]
    
    for category in test_categories:
        create_test_category(new_feature, category)

def create_test_category(feature, category):
    """Create specific test category"""
    
    if category == "unit_tests":
        return create_unit_tests(feature)
    elif category == "integration_tests":
        return create_integration_tests(feature)
    elif category == "error_tests":
        return create_error_handling_tests(feature)
    elif category == "edge_case_tests":
        return create_edge_case_tests(feature)
    elif category == "regression_tests":
        return create_regression_tests(feature)

# Example test creation
def create_unit_tests(feature):
    """Create unit tests following engine patterns"""
    
    test_template = f"""
import pytest
from unittest.mock import Mock, patch
from game_sys.{feature.module}.{feature.service_name} import {feature.class_name}

class Test{feature.class_name}:
    @pytest.fixture
    def service(self):
        return {feature.class_name}()
    
    def test_{feature.main_method}_success(self, service):
        # Arrange
        test_data = {feature.test_data}
        
        # Act
        result = service.{feature.main_method}(test_data)
        
        # Assert
        assert result.success is True
        assert result.data is not None
    
    def test_{feature.main_method}_error_handling(self, service):
        # Arrange
        invalid_data = None
        
        # Act
        result = service.{feature.main_method}(invalid_data)
        
        # Assert
        assert result.success is False
        assert result.error is not None
    """
    
    return test_template
```

## Summary for AI Agents

### **Key Success Principles**

1. **Always Analyze First**: Understand existing patterns before implementing
2. **Preserve Backward Compatibility**: Never break existing functionality
3. **Follow Established Patterns**: Use ServiceResult, logging, configuration patterns
4. **Test Comprehensively**: Unit tests, integration tests, error handling tests
5. **Document Changes**: Update documentation and add usage examples

### **Critical Don'ts**

1. **Don't Clear User State**: Unless explicitly requested, preserve character data
2. **Don't Mix Result Types**: Be consistent with ServiceResult vs dictionary patterns
3. **Don't Skip Error Handling**: Always handle exceptions and validate inputs
4. **Don't Ignore Configuration**: Use ConfigManager with defaults
5. **Don't Break Event Integration**: Maintain event publishing and subscription patterns

### **Essential Tools Usage**

- **semantic_search**: Understanding architecture and finding related code
- **grep_search**: Finding specific patterns and functions  
- **read_file**: Reading substantial context, not just snippets
- **replace_string_in_file**: Making precise, surgical code changes
- **run_in_terminal**: Testing changes and validating functionality

### **Quality Assurance**

Every change should:
- Follow existing architectural patterns
- Include comprehensive error handling
- Preserve backward compatibility
- Include appropriate logging
- Have corresponding tests
- Update relevant documentation

This guide ensures AI agents can effectively contribute to the RPG engine while maintaining code quality and architectural consistency.

---

*This guide should be referenced for every development task to ensure consistency and quality in AI-assisted development.*
