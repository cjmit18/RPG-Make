# Contributing to RPG Engine v2.0

Thank you for your interest in contributing to the RPG Engine! This guide will help you get started with contributing to our modern, async-based RPG development framework.

## 🚀 Quick Start

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/RPG-Make.git
   cd RPG-Make
   ```

2. **Set up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Run Tests**
   ```bash
   pytest --maxfail=1 --disable-warnings -q
   ```

4. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

## 🏗️ Development Workflow

### 1. Before You Start
- Check existing [issues](https://github.com/cjmit18/RPG-Make/issues) and [discussions](https://github.com/cjmit18/RPG-Make/discussions)
- For large changes, open an issue first to discuss your approach
- Review our [project documentation](docs/README.md)

### 2. Code Standards
Our CI/CD pipeline automatically checks these, but please follow:

**Style Guidelines**
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes  
- Follow PEP8 with 88-character line limit (Black formatter)
- Add type hints for all function signatures
- Write docstrings (Google style) for all public methods

**Code Quality**
```bash
# Format code
black .

# Sort imports  
isort .

# Lint code
flake8

# Type checking
mypy .

# Security scan
bandit -r rpg_engine/
```

### 3. Testing Requirements

**Test Coverage**
- Write tests for new functionality in `tests/`
- Maintain >90% test coverage
- Include both unit and integration tests
- Test async functionality properly

**Running Tests**
```bash
# Full test suite
pytest

# With coverage
pytest --cov=rpg_engine --cov-report=html

# Specific test file
pytest tests/test_character_system.py -v
```

**UI Testing Guidelines**
- Use `tk.Button` instead of `ttk.Button` for colored elements
- Ensure UI elements are properly sized and visible
- Test keyboard navigation and accessibility
- Verify async UI updates work correctly
- Configure buttons with appropriate properties:
  - `bg/fg` for colors
  - `relief=tk.RAISED` for 3D effect  
  - Appropriate font and sizing
- Test the UI on different screen sizes and resolutions

## 🎯 Contributing Areas

### 🔧 Core Engine
- **AsyncGameEngine**: Main engine improvements
- **ServiceContainer**: Dependency injection enhancements  
- **EventBus**: Event system optimizations

### 🎮 Game Systems
- **Character System**: Stats, creation, templates
- **Achievement System**: New achievements, conditions
- **UI System**: Modular UI components, themes

### 📚 Documentation
- Code documentation improvements
- Tutorial and guide creation
- Example applications

### 🧪 Testing & Quality
- Test coverage improvements
- Performance testing
- Security enhancements

## 🏷️ Commit Guidelines

Use conventional commits format:
```
type(scope): description

feat(character): add stat point validation
fix(ui): resolve button state issues  
docs(readme): update installation guide
test(engine): add async lifecycle tests
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `ci`, `chore`

## 📋 Pull Request Process

1. **Update Documentation**
   - Update relevant docstrings
   - Add/update examples if needed
   - Update CHANGELOG.md for notable changes

2. **Test Your Changes**
   - All tests pass locally
   - New tests written for new features
   - Manual testing with demo applications

3. **Submit PR**
   - Use our PR template
   - Link related issues
   - Describe changes clearly
   - Request review from maintainers

4. **Code Review**
   - Address reviewer feedback promptly
   - Keep PR focused and reasonably sized
   - Update documentation as needed

## 🚨 Security

- Report security vulnerabilities via [GitHub Security](https://github.com/cjmit18/RPG-Make/security)
- Never commit sensitive data (API keys, passwords)
- Follow secure coding practices
- Use our security scanning tools

## 🎨 UI Development Guidelines

### Async UI Patterns
```python
# Good: Proper async UI updates
async def update_character_stats(self):
    await self.engine.update_stats()
    self.root.after(0, self._refresh_ui)

# Bad: Blocking UI operations  
def update_character_stats(self):
    time.sleep(1)  # Blocks UI thread
    self.refresh_ui()
```

### Component Architecture
- Follow modular UI patterns
- Use proper separation of concerns
- Implement proper cleanup in destructors
- Handle window/tab lifecycle correctly

## 🔍 Debugging Tips

**Common Issues**
- Import errors: Check `__init__.py` files
- Async issues: Use proper `await` patterns
- UI freezing: Don't block the main thread
- Test failures: Check async test patterns

**Debugging Tools**
```bash
# Debug mode
python -m rpg_engine --debug

# Verbose logging
python examples/engine_demo.py --verbose

# Profile performance
python -m cProfile examples/engine_demo.py
```

## 📞 Getting Help

- 💬 [GitHub Discussions](https://github.com/cjmit18/RPG-Make/discussions)
- 📖 [Documentation](docs/README.md)  
- 🎮 [Examples](examples/)
- 🐛 [Issues](https://github.com/cjmit18/RPG-Make/issues)

## 🏆 Recognition

Contributors are recognized in:
- CHANGELOG.md for notable contributions
- GitHub contributors page
- Release notes for significant features

---

**Thank you for contributing to the RPG Engine! 🎮✨**
