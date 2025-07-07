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

- Use snake_case for functions and variables, PascalCase for classes.
- Add docstrings (PEP257) for all public methods.
- Do not commit sensitive data (API keys, passwords, etc.).
- Keep commits small and descriptively named.

### Testing UI Guidelines

When working on testing UI components:

1. Ensure all UI elements are clearly visible and properly sized
2. Use tk.Button instead of ttk.Button for colored elements (PASS/FAIL buttons, etc.)
3. Configure buttons with appropriate properties:
   - bg/fg for colors
   - relief=tk.RAISED for 3D effect
   - Appropriate font and sizing
4. Test the UI on different screen sizes and resolutions
5. Use the `run_comprehensive_test_updated.bat` file to verify UI changes
