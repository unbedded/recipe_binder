Run complete code quality pipeline: $ARGUMENTS

Options:
- `--fix` - Auto-fix issues where possible
- `--verbose` - Show detailed output
- `--report` - Generate coverage and quality reports

Pipeline steps:
1. `ruff format` - Format code
2. `ruff check --fix` - Lint and auto-fix issues  
3. `mypy .` - Type checking
4. `pytest -q` - Run test suite
5. Optional: Generate coverage report if `--report` specified

If any step fails, display error details and stop pipeline.
Use `--verbose` to see full output from each tool.