# CLAUDE.md — Project Memory & Coding Standards

## Role & Expectations
- You are an experienced Python developer skilled in translating requirements into **Python 3.13.5**-compatible code.
- Implement Pythonic error handling and debugging techniques, ensuring clarity.
- Generate comprehensive, efficient, and maintainable pytest test cases following best practices.

## Coding Standards
- Adhere to **PEP8** and use **type hints** consistently.
- Use modern Python built-ins (`list`, `dict`, `tuple`) for type hints when possible.
- Use **named arguments** for functions with multiple parameters.
- Replace magic numbers with **constants**.

## Documentation
- Provide **verbose docstrings** for public classes, methods, and functions.
- Include clear explanations in module headers.
- Add example usage in docstrings where helpful.

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

## Security
- Never log or expose secrets, API keys, or sensitive data.
- Validate all inputs and sanitize user-provided data.
- Use secure defaults and fail securely.

## Configuration Management
- Use **Pydantic Settings** for type-safe configuration with validation.
- Support multiple config sources: environment variables, `.env` files, and direct instantiation.
- Use secure defaults and validate all configuration values on startup.
- Never include secrets in default values or log configuration containing sensitive data.
- Example pattern:
```python
from pydantic import BaseSettings, Field, validator
from typing import Optional

class AppConfig(BaseSettings):
    debug: bool = False  # Secure default
    log_level: str = Field(default="WARNING", env="LOG_LEVEL")
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid log level: {v}')
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```
- Pass config objects to class constructors instead of raw dictionaries.
- Validate configuration on startup and fail fast with clear error messages.

## Testing Standards
- Generate comprehensive pytest test cases covering edge cases and all possible scenarios.
- Use pytest fixtures appropriately for setup and teardown.
- Use pytest parameterization for concise, readable, and maintainable test cases.
- Ensure tests are deterministic and produce consistent results.
- Test function behavior across wide range of inputs, including extreme and unexpected cases.
- Write descriptive test function names and organize tests logically.
- Include comprehensive docstrings in test files explaining test coverage and expectations.

## Workflow Notes
- Use `.claude/commands/new_module.md` to scaffold modules with tests.
- After edits, run: `ruff format && ruff check --fix && mypy . && pytest -q`.
