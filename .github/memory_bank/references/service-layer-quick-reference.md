# Service Layer Quick Reference for GitHub Copilot

Quick implementation guide for service layer architecture with GitHub Copilot assistance.

## 🚀 Quick Start Template

```python
from game_sys.config.config_manager import ConfigManager
from game_sys.logging import get_logger
from typing import Dict, Any, Optional

class NewFeatureService:
    """Service for [feature description] business logic."""
    
    def __init__(self):
        """Initialize service with dependencies."""
        self.config = ConfigManager()
        self.logger = get_logger(__name__)
        
    def execute_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute main business operation.
        
        Args:
            params: Operation parameters
            
        Returns:
            Result dictionary with success/error information
        """
        try:
            # Validate inputs
            self._validate_params(params)
            
            # Check feature toggle
            if not self.config.get('features.new_feature.enabled', True):
                raise RuntimeError("Feature is disabled")
            
            # Execute business logic
            result = self._perform_operation(params)
            
            self.logger.info("Operation completed successfully")
            return {
                'success': True,
                'result': result,
                'message': 'Operation completed successfully'
            }
            
        except ValueError as e:
            self.logger.error(f"Validation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'type': 'validation',
                'message': 'Invalid input provided'
            }
        except Exception as e:
            self.logger.error(f"Operation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'type': 'runtime',
                'message': 'Operation failed unexpectedly'
            }
    
    def _validate_params(self, params: Dict[str, Any]) -> None:
        """Validate operation parameters."""
        # Add validation logic here
        pass
    
    def _perform_operation(self, params: Dict[str, Any]) -> Any:
        """Perform the actual business operation."""
        # Add business logic here
        return "operation_result"
```

## 📋 Implementation Checklist

### Before Starting
- [ ] Open `memory_bank/patterns/service_layer_pattern.md` for reference
- [ ] Check existing similar services for patterns
- [ ] Review configuration structure in `default_settings.json`
- [ ] Plan UI integration points

### Service Implementation
- [ ] Create service class with descriptive name
- [ ] Initialize ConfigManager and logger
- [ ] Implement main operation method with error handling
- [ ] Add parameter validation
- [ ] Include feature toggle checks
- [ ] Add comprehensive logging
- [ ] Write docstrings for all public methods
- [ ] Add type hints for better Copilot suggestions

### UI Integration
- [ ] Create service instance in UI component
- [ ] Call service methods from UI event handlers
- [ ] Handle success/error responses appropriately
- [ ] Update UI state after operations
- [ ] Display user-friendly error messages

### Testing
- [ ] Write unit tests for service methods
- [ ] Test error conditions and edge cases
- [ ] Validate configuration integration
- [ ] Test UI integration through demo

## 🎯 Common Patterns

### Configuration Integration
```python
def __init__(self):
    self.config = ConfigManager()
    self.timeout = self.config.get('features.example.timeout', 30)
    self.enabled = self.config.get('features.example.enabled', True)
```

### Error Handling
```python
try:
    result = self._perform_operation(params)
    return {'success': True, 'result': result}
except ValueError as e:
    return {'success': False, 'error': str(e), 'type': 'validation'}
except Exception as e:
    return {'success': False, 'error': str(e), 'type': 'runtime'}
```

### Logging
```python
self.logger.debug(f"Processing params: {params}")
self.logger.info("Operation completed successfully")
self.logger.warning(f"Deprecated feature used: {feature}")
self.logger.error(f"Operation failed: {error}")
```

### UI Integration
```python
def on_button_click(self):
    try:
        params = self._get_user_input()
        result = self.service.execute_operation(params)
        
        if result['success']:
            self._show_success(result['message'])
            self._update_display(result['result'])
        else:
            self._show_error(result['message'])
    except Exception as e:
        self._show_error(f"Unexpected error: {e}")
```

## 🧪 Testing Quick Reference

### Basic Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from new_feature_service import NewFeatureService

class TestNewFeatureService:
    def setup_method(self):
        self.service = NewFeatureService()
    
    def test_operation_success(self):
        params = {'param1': 'value1'}
        result = self.service.execute_operation(params)
        
        assert result['success'] is True
        assert 'result' in result
    
    def test_operation_validation_error(self):
        params = {}  # Missing required params
        result = self.service.execute_operation(params)
        
        assert result['success'] is False
        assert result['type'] == 'validation'
```

## ⚙️ Configuration Template

### Add to `default_settings.json`
```json
{
  "features": {
    "new_feature": {
      "enabled": true,
      "timeout": 30,
      "max_retries": 3,
      "debug_mode": false
    }
  }
}
```

## 🎨 UI Integration Template

```python
class FeatureUI:
    def __init__(self, parent):
        self.parent = parent
        self.service = NewFeatureService()
        self._setup_ui()
    
    def _setup_ui(self):
        # UI setup code
        self.button = tk.Button(
            self.parent,
            text="Execute",
            command=self.on_execute_button
        )
    
    def on_execute_button(self):
        try:
            params = self._get_user_input()
            result = self.service.execute_operation(params)
            
            if result['success']:
                self._show_success(result['message'])
                self._update_display(result['result'])
            else:
                self._show_error(result['message'])
        except Exception as e:
            self._show_error(f"Operation failed: {e}")
    
    def _get_user_input(self) -> Dict[str, Any]:
        return {
            'param1': self.entry1.get(),
            'param2': self.entry2.get()
        }
    
    def _show_success(self, message: str):
        # Show success message
        pass
    
    def _show_error(self, message: str):
        # Show error message
        pass
    
    def _update_display(self, data: Any):
        # Update UI with new data
        pass
```

## 🔧 GitHub Copilot Tips

### Context Building
1. Open `service_layer_pattern.md` before implementing
2. Open similar existing service files
3. Open configuration files for structure reference
4. Open test files for testing patterns

### Prompt Engineering
```python
# Use descriptive comments to guide Copilot:
# "Create a character management service with validation"
# "Implement error handling with specific exception types"
# "Add configuration integration for feature toggles"
```

### Type Hints for Better Suggestions
```python
def process_character_data(
    self,
    character_data: Dict[str, Any],
    validation_rules: List[str]
) -> Dict[str, Any]:
    # Copilot will generate better suggestions with clear types
```

## ❌ Common Mistakes to Avoid

### Don't Put Business Logic in UI
```python
# BAD
def on_button_click(self):
    damage = weapon.damage * strength  # Business logic in UI
    target.health -= damage

# GOOD
def on_button_click(self):
    result = self.combat_service.calculate_damage(weapon, attacker, target)
```

### Don't Hardcode Configuration
```python
# BAD
self.timeout = 30  # Hardcoded value

# GOOD
self.timeout = self.config.get('features.example.timeout', 30)
```

### Don't Skip Error Handling
```python
# BAD
def execute_operation(self, params):
    result = self._perform_operation(params)
    return result

# GOOD
def execute_operation(self, params):
    try:
        result = self._perform_operation(params)
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

## 📚 Related References

- `memory_bank/patterns/service_layer_pattern.md` - Detailed pattern documentation
- `memory_bank/lessons/copilot-service-layer-lessons.md` - Implementation lessons
- `COPILOT.md` - Full architecture guidelines
- `docs/UI_SYSTEM_README.md` - UI integration patterns
