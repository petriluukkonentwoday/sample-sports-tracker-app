---
description: Apply to Python files (.py) in this project
applyTo: '\.py$'
---

# Python Coding Standards

## Style & Formatting
- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length of 88 characters (Black formatter compatible)
- Use type hints for function parameters and return types
- Use meaningful variable and function names (no single letters except loop indices)

## Code Organization
- Imports at top: standard library, third-party, local (in groups, alphabetically sorted)
- Keep functions small and focused (ideally under 20 lines)
- Use docstrings for modules, classes, and public functions (Google or NumPy style)
- Group related functionality into classes when appropriate

## Best Practices
- Prefer explicit over implicit (Zen of Python)
- Use context managers (`with` statements) for resource handling
- Avoid mutable default arguments in function definitions
- Use list comprehensions and generator expressions appropriately
- Catch specific exceptions, not bare `except:`
- Use f-strings for string formatting
- Add type hints to improve code clarity and IDE support

## Testing
- Write testable functions (minimal side effects, clear inputs/outputs)
- Include unit tests for new functions and behavior changes
- Use descriptive test names that explain what is being tested
- Aim for high coverage of critical paths

## Error Handling
- Raise appropriate exception types with clear messages
- Validate inputs at function entry points
- Log errors with context when appropriate
