# Contributing to RPG Engine v2.0

Thank you for your interest in contributing to the **async-first RPG engine**! This guide will help you get started with contributing to this modern, event-driven game development framework.

## 🎯 **Project Vision**

We're building a **modern async-first RPG engine** that demonstrates:
- Clean async/await patterns throughout
- Interactive UI as a first-class priority
- Event-driven architecture with strong typing
- Professional software engineering practices
- Comprehensive testing and documentation

## 🚀 **Getting Started**

### Prerequisites
- Python 3.11 or higher
- Git for version control
- Basic understanding of async/await patterns
- Familiarity with type hints and modern Python

### Setup Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/RPG-Make.git
   cd RPG-Make
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   # Test the engine
   python test_engine.py
   
   # Try the interactive demo
   python engine_demo.py
   ```

4. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

## 🏗️ **Architecture Overview**

### Core Components

```
rpg_engine/
├── core/
│   ├── engine.py           # AsyncGameEngine - Main orchestrator
│   ├── service_container.py # Dependency injection system
│   ├── event_bus.py        # Event system with strong typing
│   └── __init__.py
├── ui/
│   ├── ui_system.py        # Async UI management
│   └── __init__.py
└── __init__.py
```

### Key Principles
1. **Async-First**: All core operations use `async/await`
2. **Event-Driven**: Components communicate via strongly-typed events
3. **Service-Oriented**: Clean dependency injection patterns
4. **Type-Safe**: Comprehensive type hints and protocols
5. **Thread-Safe**: Proper cross-thread communication

## 🔧 **Development Guidelines**

### Code Style

1. **Async Patterns**
   ```python
   # ✅ Good - Proper async function
   async def initialize_system(self) -> None:
       await self.service_container.initialize_all_async()
   
   # ❌ Bad - Mixing sync in async context
   def initialize_system(self):
       return asyncio.run(self.setup())
   ```

2. **Type Safety**
   ```python
   # ✅ Good - Full type annotations
   async def handle_event(self, event: GameEvent) -> None:
       if isinstance(event, CharacterCreatedEvent):
           await self._process_character_event(event)
   
   # ❌ Bad - Missing types
   async def handle_event(self, event):
       # Process event...
   ```

3. **Event Design**
   ```python
   # ✅ Good - Strongly typed event
   @dataclass(frozen=True)
   class InventoryUpdatedEvent(GameEvent):
       character_id: str
       item_added: Optional[str] = None
       item_removed: Optional[str] = None
       timestamp: datetime = field(default_factory=datetime.now)
   ```

4. **Service Registration**
   ```python
   # ✅ Good - Proper service registration
   container = ServiceContainer()
   await container.register_singleton(EventBus, EventBus())
   await container.register_transient(CharacterService, CharacterService)
   ```

### Testing Requirements

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test component interactions
3. **Async Tests** - Use `pytest-asyncio` for async code
4. **UI Tests** - Verify UI functionality (where possible)

### Documentation Standards

1. **Docstrings** - All public methods need docstrings
2. **Type Hints** - Complete type annotations
3. **Examples** - Include usage examples
4. **Architecture Notes** - Document design decisions

## 🧪 **Testing Your Changes**

### Required Tests
```bash
# 1. Run unit tests
python test_engine.py

# 2. Test simple UI
python simple_ui_test.py

# 3. Run comprehensive demo
python engine_demo.py

# 4. Verify imports work
python -c "from rpg_engine import AsyncGameEngine, ServiceContainer, EventBus"
```

### Test Categories

1. **Core Engine Tests**
   - Service container functionality
   - Event bus operations
   - Engine lifecycle management
   - Async initialization/shutdown

2. **UI System Tests**
   - Cross-thread communication
   - Event handling
   - Component updates
   - Threading safety

3. **Integration Tests**
   - End-to-end workflows
   - Service interaction
   - Event propagation
   - Performance metrics

## 📝 **Contribution Types**

### 🐛 **Bug Fixes**
- Fix issues with existing functionality
- Improve error handling
- Resolve performance problems
- Address threading issues

### ✨ **New Features**
- Game systems (character, combat, inventory)
- UI components and improvements
- Developer tools and debugging
- Performance optimizations

### 📚 **Documentation**
- API documentation
- Architecture guides
- Tutorial improvements
- Code examples

### 🧪 **Testing**
- Increase test coverage
- Add integration tests
- Improve test reliability
- Performance benchmarks

## 🔄 **Pull Request Process**

### Before Submitting
1. **Test Thoroughly** - Run all test applications
2. **Check Code Style** - Follow async-first patterns
3. **Update Documentation** - Keep docs current
4. **Write Tests** - Add tests for new functionality

### PR Requirements
1. **Clear Description** - Explain what and why
2. **Test Evidence** - Show your changes work
3. **Breaking Changes** - Document any breaking changes
4. **Related Issues** - Link to relevant issues

### Review Process
1. **Automated Checks** - CI tests must pass
2. **Code Review** - Maintainer review
3. **Testing** - Manual testing if needed
4. **Merge** - Squash and merge when approved

## 🎯 **Areas Looking for Contributions**

### High Priority
- [ ] Character creation and management system
- [ ] Combat mechanics with async support
- [ ] Inventory and item management
- [ ] Save/Load functionality
- [ ] Performance optimization

### Medium Priority
- [ ] Advanced UI components
- [ ] Animation system
- [ ] Resource management
- [ ] Plugin architecture
- [ ] Audio integration

### Documentation
- [ ] Architecture documentation
- [ ] API reference
- [ ] Tutorial improvements
- [ ] Example projects

## 🤝 **Community Guidelines**

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### Getting Help
- **GitHub Discussions** - Ask questions and share ideas
- **Issues** - Report bugs or request features
- **Code Review** - Learn from feedback
- **Documentation** - Check existing guides first

## 🏆 **Recognition**

Contributors will be:
- Listed in the project's contributors section
- Credited in release notes for significant contributions
- Given feedback and mentorship opportunities
- Invited to participate in architectural decisions

## 📋 **Quick Checklist**

Before submitting your contribution:

- [ ] Code follows async-first patterns
- [ ] All tests pass (`python test_engine.py`)
- [ ] Interactive demo works (`python engine_demo.py`)
- [ ] Type hints are complete
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description explains the change
- [ ] Related issues are linked

## 🚀 **Next Steps**

1. **Start Small** - Begin with documentation or small bug fixes
2. **Learn the Architecture** - Study the existing async patterns
3. **Ask Questions** - Use GitHub Discussions for help
4. **Join the Community** - Participate in discussions and reviews

Thank you for contributing to the future of async-first game development! 🎮

---

**Questions?** Open a [GitHub Discussion](https://github.com/cjmit18/RPG-Make/discussions) or create an [issue](https://github.com/cjmit18/RPG-Make/issues/new/choose).
