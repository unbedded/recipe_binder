"""Recipe Binder data models.

This module provides Pydantic models for type-safe data handling
throughout the Recipe Binder pipeline.

Example usage:
    from recipe_fmt.models import Recipe, Ingredient, AppConfig

    # Create a recipe
    recipe = Recipe(
        title="Test Recipe",
        category="Main",
        ingredients=[...],
        instructions=[...]
    )

    # Load configuration
    config = AppConfig()
"""

from .config import AppConfig, DisplayConfig, OpenAIConfig
from .recipe import Ingredient, Nutrition, Recipe

__all__ = [
    "Recipe",
    "Ingredient",
    "Nutrition",
    "AppConfig",
    "DisplayConfig",
    "OpenAIConfig",
]
