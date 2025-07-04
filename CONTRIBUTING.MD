# Contributing to game_sys

Thank you for your interest in contributing! Please follow these steps:

1. Fork the repository and create your feature branch (`git checkout -b feature/myfeature`).  
2. Ensure tests pass locally:  

   ```bash
   pytest --maxfail=1 --disable-warnings -q
   ```

3. Follow PEP8 style and run linters:
    flake8
    mypy .
4. Write or update tests in the tests/ folder for any new functionality
5. Submit a pull request. We’ll review and merge if things look good!

### Coding Guidelines

    Use snake_case for functions and variables, PascalCase for classes.

    Add docstrings (PEP257) for all public methods.

    Do not commit sensitive data (API keys, passwords, etc.).

    Keep commits small and descriptively named.
