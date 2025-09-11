"""Nutrition calculation module for recipe enhancement.

This module provides USDA FoodData Central API integration to automatically
calculate nutrition information for recipes.

Main classes:
    NutritionCalculator: Calculate nutrition data from recipe ingredients

Example usage:
    from recipe_fmt.nutrition import NutritionCalculator

    calculator = NutritionCalculator()
    enhanced_recipe = calculator.enhance_recipe(recipe_dict)
"""

from .calculator import NutritionCalculator

__all__ = ["NutritionCalculator"]
