# Copilot Instructions

Use these rules for all code changes in this project.

## General

- Keep solutions simple, readable, and maintainable.
- Follow existing project structure and naming conventions.
- Prefer small, focused changes over broad refactors.
- Do not introduce new dependencies unless clearly justified.

## Code Style

- Write clear code with descriptive names.
- Avoid one-letter variable names.
- Keep functions small and single-purpose.
- Add comments only when intent is not obvious from code.
- Make functions so that they are easy to unit test

## Safety and Quality

- Fix root causes instead of adding temporary workarounds.
- Preserve backward compatibility unless explicitly requested.
- Handle edge cases and error paths.
- Add or update tests when behavior changes.

## PR Hygiene

- Keep changes scoped to the task.
- Update documentation when behavior or setup changes.
- Avoid unrelated formatting or file churn.

## When Requirements Are Unclear

- Choose the simplest valid implementation.
- State assumptions briefly in the response.
- Ask for clarification only when ambiguity blocks safe implementation.