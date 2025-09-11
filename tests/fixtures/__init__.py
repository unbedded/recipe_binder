"""Test fixtures and sample data for Recipe Binder testing.

This package provides reusable test fixtures, sample data, and test utilities
that can be imported and used across all test modules to ensure consistency
and reduce duplication in test setup.

Available fixtures:
- Sample Recipe models with various categories
- Mock OpenAI API responses
- Template YAML configurations
- Test markdown files
- PDF generation test data
- File system test utilities

Example usage:
    from tests.fixtures.sample_recipes import SAMPLE_PANCAKES
    from tests.fixtures.template_data import DEFAULT_CARD_TEMPLATE
    from tests.fixtures.openai_responses import SUCCESSFUL_PARSE_RESPONSE
"""

# Make key fixtures available at package level
from .file_utils import (
    MockFileSystem,
    cleanup_temp_files,
    create_temp_recipe_files,
    create_temp_template_files,
)
from .openai_responses import (
    ALL_MOCK_RESPONSES,
    ERROR_RATE_LIMIT_RESPONSE,
    PARTIAL_PARSE_RESPONSE,
    SUCCESSFUL_PARSE_RESPONSE,
)
from .sample_recipes import (
    ALL_SAMPLE_RECIPES,
    SAMPLE_BEEF_STEW,
    SAMPLE_CHOCOLATE_CAKE,
    SAMPLE_INVALID_RECIPE,
    SAMPLE_PANCAKES,
)
from .template_data import (
    ALL_TEMPLATE_DATA,
    COMPACT_CARD_TEMPLATE,
    DEFAULT_CARD_TEMPLATE,
    INVALID_TEMPLATE_DATA,
    MINIMAL_CARD_TEMPLATE,
)

__all__ = [
    # Sample recipes
    "SAMPLE_PANCAKES",
    "SAMPLE_BEEF_STEW",
    "SAMPLE_CHOCOLATE_CAKE",
    "SAMPLE_INVALID_RECIPE",
    "ALL_SAMPLE_RECIPES",
    # Template data
    "DEFAULT_CARD_TEMPLATE",
    "COMPACT_CARD_TEMPLATE",
    "MINIMAL_CARD_TEMPLATE",
    "INVALID_TEMPLATE_DATA",
    "ALL_TEMPLATE_DATA",
    # OpenAI responses
    "SUCCESSFUL_PARSE_RESPONSE",
    "ERROR_RATE_LIMIT_RESPONSE",
    "PARTIAL_PARSE_RESPONSE",
    "ALL_MOCK_RESPONSES",
    # File utilities
    "create_temp_recipe_files",
    "create_temp_template_files",
    "cleanup_temp_files",
    "MockFileSystem",
]
