# Review Code - Analyze Modified Files for Quality

**Description:** Reviews modified files for code quality, patterns, potential issues, and suggests improvements following project standards.

**Usage:** `/review-code [--files <pattern>]`

## Options

- `--files <pattern>`: Focus review on specific files using glob pattern (e.g., "src/auth*", "*.py")

## How it works

1. **Identify Changes**: Detects modified files in working directory or staging area
2. **Code Analysis**: Reviews code for:
   - CLAUDE.md compliance (PEP8, type hints, docstrings)
   - Security best practices
   - Error handling patterns
   - Logging implementation
   - Configuration management
3. **Pattern Matching**: Checks consistency with existing codebase patterns
4. **Improvement Suggestions**: Provides specific, actionable recommendations

## Implementation

This command will:
- Run `git status` and `git diff` to identify changed files
- Read and analyze modified Python files
- Check compliance with CLAUDE.md coding standards
- Verify proper error handling and logging patterns
- Review security practices (no exposed secrets, input validation)
- Suggest improvements aligned with project conventions

## Review Criteria

### ✅ Code Quality Checks
- **PEP8 Compliance**: Formatting, naming conventions
- **Type Hints**: Proper type annotations
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Pythonic exception handling
- **Logging**: Proper logging implementation

### 🔒 Security Review  
- **Secret Management**: No hardcoded credentials
- **Input Validation**: Proper data sanitization
- **Configuration**: Secure defaults and validation

### 🏗️ Architecture Patterns
- **Configuration Management**: Pydantic Settings usage
- **Logging Setup**: Thread-safe logging in constructors
- **Testing**: Comprehensive pytest coverage

## Example Output

```
📊 Code Review Report

Files Analyzed: 3 files
- src/auth/service.py
- src/auth/models.py  
- tests/test_auth.py

## ✅ Good Practices Found
- Proper type hints throughout codebase
- Comprehensive docstrings with examples
- Thread-safe logging configuration
- Pydantic models for configuration

## ⚠️ Issues Identified

### src/auth/service.py:42
```python
# Current
def authenticate_user(username, password):
    return user

# Suggested
def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    return user
```

### src/auth/models.py:15
**Missing**: Input validation for email field
**Suggestion**: Add email validator using Pydantic

## 💡 Recommendations
1. Add missing type hints in authenticate_user function
2. Implement email validation in User model  
3. Consider adding rate limiting for authentication attempts
4. Add integration tests for authentication flow

## 🎯 Overall Score: 8.5/10
Code follows most project conventions with minor improvements needed.
```