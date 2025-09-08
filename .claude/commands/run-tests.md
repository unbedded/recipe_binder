Execute pytest test suite with options: $ARGUMENTS

Options:
- `--coverage` - Include coverage report and generate HTML output
- `--filter <pattern>` - Run only tests matching pattern (pytest -k)
- `--verbose` - Show detailed test output (-v)
- `--parallel` - Run tests in parallel if pytest-xdist available

Examples:
- `/run-tests` - Run all tests quietly
- `/run-tests --coverage` - Run tests with coverage report
- `/run-tests --filter test_user` - Run only tests matching "test_user"
- `/run-tests --verbose --coverage` - Detailed output with coverage

Test execution:
1. Basic: `pytest -q`
2. With coverage: `pytest --cov=src --cov-report=html --cov-report=term`
3. With filter: `pytest -k <pattern>`
4. Verbose: Add `-v` flag

Coverage reports generated in `htmlcov/` directory when `--coverage` used.