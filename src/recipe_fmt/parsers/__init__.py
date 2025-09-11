"""Recipe parsing modules.

This package provides intelligent parsing of markdown recipes using OpenAI
with comprehensive error handling, caching, and validation.

Example usage:
    from recipe_fmt.parsers import MarkdownParser, OpenAIClient
    from recipe_fmt.models.config import OpenAIConfig

    config = OpenAIConfig()
    parser = MarkdownParser(config)

    result = parser.parse_recipe_file("recipe.md")
    if result.success:
        recipe = result.recipe
"""

from .markdown_parser import MarkdownParser, ParseResult, create_parser_from_env
from .openai_client import OpenAIClient, OpenAIResponse

__all__ = [
    "MarkdownParser",
    "ParseResult",
    "create_parser_from_env",
    "OpenAIClient",
    "OpenAIResponse",
]
