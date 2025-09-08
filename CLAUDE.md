# CLAUDE.md — Project Memory & Coding Standards

## Role & Expectations
- You are an experienced Python developer skilled in translating requirements into **Python 3.13.5**-compatible code.
- Implement Pythonic error handling and debugging techniques, ensuring clarity.

## Coding Standards
- Adhere to **PEP8** and use **type hints** consistently.
- Import and use generics from `typing` (e.g., `List`, `Dict`, `Tuple`).
- Use **named arguments** for functions with multiple parameters.
- Replace magic numbers with **constants**.

## Documentation
- Each file includes a header with:
  - Today’s date as `<DATE>`.
  - Explanations inside comments.
  - An `Example usage:` comment in the header (not at the end of the file).
- For each significant step, add `STEP_ACTION_TABLE` entries in comments: `STEP_%d`.
- Provide **verbose docstrings** for public classes, methods, and functions.

## Error Handling
- Use Pythonic `try-except` blocks.
- Raise appropriate built-in or custom exceptions.
- Provide clear and informative error messages.
- Use `logging.exception()` to capture stack traces when errors occur.

## Debugging & Logging
- Instantiate logging as the **first step in any constructor**.
- Use the `logging` module with lazy `%` formatting.
- Configure logging with file output and timestamps.
- Use appropriate logging levels: `DEBUG` (details), `INFO` (events), `ERROR` (exceptions).
- Default logger level: `WARNING`.
- Ensure logging is **thread-safe**.
- Demonstrate logging for key operations such as input validation, cache access, and calculation steps.
- Avoid logging sensitive or redundant information.

## Configuration Management (Every Class)
- Constructor signature uses `Optional[Dict[str, Any]] = None` for `cfg_dict`.
- Initialize parameters from `cfg_dict` via a helper that applies defaults and logs missing keys.
- Implement:
  - `get_cfg()` → returns `cfg_dict` updated with current parameter values.
  - `set_cfg(cfg_dict)` → update matching keys; log updates and key/parameter mismatches.

## Workflow Notes
- Use `.claude/commands/new_module.md` to scaffold modules with tests.
- After edits, run: `ruff format && ruff check --fix && mypy . && pytest -q`.
