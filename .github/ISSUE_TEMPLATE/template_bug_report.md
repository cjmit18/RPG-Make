---
name: Template System Bug Report
about: Report a bug in the character template system or achievement system
title: '[TEMPLATE BUG] '
labels: 'bug, template-system'
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is in the template system.

**Template System Component**
- [ ] Character Templates
- [ ] Achievement Templates  
- [ ] Template Loader
- [ ] Template Validation
- [ ] Stat Calculations
- [ ] Configuration System

**Template Information**
- Template ID: (e.g., `warrior_basic`, `character_creation.first_character`)
- Template Type: (Character/Achievement)
- Rarity/Grade: (if applicable)

**To Reproduce**
Steps to reproduce the behavior:
1. Load template '...'
2. Calculate stat at level '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Actual behavior**
What actually happened.

**Template Data**
If applicable, include relevant template JSON:
```json
{
  "template_data": "here"
}
```

**Error Output**
If applicable, include error messages or logs:
```
Error output here
```

**Environment:**
- Python version: [e.g., 3.11]
- RPG Engine version: [e.g., 2.0]
- OS: [e.g., Windows 11]

**Test Results**
- [ ] Template loading test passes: `python test_template_loading.py`
- [ ] Character demo passes: `python examples/demo_character_system.py`

**Additional context**
Add any other context about the problem here.
