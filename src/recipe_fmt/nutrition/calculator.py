"""Nutrition calculator for recipe enhancement using USDA FoodData Central API.

This module provides a standalone class to calculate nutrition information
for recipes by querying the USDA API and enhancing YAML recipe data.
"""

import json
import os
from pathlib import Path
from typing import Any

import requests
import yaml

from ..utils.logging_setup import get_logger


class NutritionCalculator:
    """Calculate nutrition data for recipes using USDA FoodData Central API.

    This class takes recipe data (YAML dict) and enhances it with nutrition
    information by looking up ingredients in the USDA database.

    Example:
        calculator = NutritionCalculator()
        enhanced_recipe = calculator.enhance_recipe(recipe_dict)
    """

    def __init__(self, api_key: str | None = None, cfg_dict: dict[str, Any] | None = None):
        """Initialize nutrition calculator.

        Args:
            api_key: USDA API key (tries env USDA_API_KEY, then DEMO_KEY)
            cfg_dict: Configuration dictionary for logging
        """
        self.logger = get_logger(__name__, cfg_dict)
        self.api_key = api_key or os.getenv("USDA_API_KEY") or "DEMO_KEY"
        self.base_url = "https://api.nal.usda.gov/fdc/v1"

        # Cache for API results to avoid repeated calls
        self._ingredient_cache: dict[str, dict[str, float | str]] = {}

        # Load conversion table from extracted recipe data
        self._conversion_table = self._load_conversion_table()

        self.logger.info(
            "NutritionCalculator initialized with API key type: %s",
            "DEMO_KEY" if self.api_key == "DEMO_KEY" else "custom",
        )

    def _load_conversion_table(self) -> dict[str, dict[str, float]]:
        """Load ingredient conversion table from extracted recipe data.

        Returns:
            Dictionary mapping ingredient names to unit conversions:
            {ingredient_name: {unit: grams_per_unit}}
        """
        conversion_file = Path(__file__).parent / "ingredient_conversions.json"

        if conversion_file.exists():
            try:
                with open(conversion_file, encoding="utf-8") as f:
                    conversions = json.load(f)
                self.logger.info(f"Loaded {len(conversions)} ingredient conversions from {conversion_file}")
                return conversions
            except Exception as e:
                self.logger.warning(f"Failed to load conversion table: {e}")
        else:
            self.logger.warning(f"Conversion table not found: {conversion_file}")

        # Fallback to basic conversions
        return {
            "all-purpose flour": {"cups": 120, "tsp": 2.5, "tbl": 7.5},
            "sugar": {"cups": 200, "tsp": 4, "tbl": 12.5},
            "butter": {"cups": 225, "tsp": 4.5, "tbl": 14},
            "milk": {"cups": 240},
            "salt": {"tsp": 6},
            "eggs": {"cnt": 50},  # Average egg weight
        }

    def enhance_recipe(self, recipe_dict: dict[str, Any]) -> dict[str, Any]:
        """Enhance recipe dictionary with nutrition information.

        Args:
            recipe_dict: Recipe data as dictionary

        Returns:
            Enhanced recipe dictionary with nutrition data
        """
        try:
            self.logger.info("Calculating nutrition for recipe: %s", recipe_dict.get("title", "Unknown"))

            ingredients = recipe_dict.get("ingredients", [])
            servings = recipe_dict.get("servings", 1)

            if not ingredients:
                self.logger.warning("No ingredients found in recipe")
                recipe_dict["nutrition"] = self._create_na_nutrition()
                return recipe_dict

            # Calculate total nutrition
            total_nutrition = self._calculate_total_nutrition(ingredients)

            # Convert to per-serving
            per_serving = self._calculate_per_serving(total_nutrition, servings)

            # Add to recipe
            recipe_dict["nutrition"] = {"per_serving": per_serving}

            self.logger.info("Nutrition calculation completed successfully")
            return recipe_dict

        except Exception as e:
            self.logger.error("Error calculating nutrition: %s", e)
            recipe_dict["nutrition"] = self._create_na_nutrition()
            return recipe_dict

    def _calculate_total_nutrition(self, ingredients: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate total nutrition for all ingredients.

        Args:
            ingredients: List of ingredient dictionaries

        Returns:
            Total nutrition values
        """
        total = {
            "calories": 0.0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
            "fiber_g": 0.0,
            "sodium_mg": 0.0,
        }

        for ingredient in ingredients:
            ingredient_name = ingredient.get("ingredient", "")
            amount = ingredient.get("amount", 0)
            unit = ingredient.get("unit", "")

            if not ingredient_name or not amount:
                continue

            self.logger.debug("Processing ingredient: %s (%s %s)", ingredient_name, amount, unit)

            # Estimate weight in grams
            weight_grams = self._estimate_ingredient_weight(ingredient_name, amount, unit)

            if weight_grams == 0:
                self.logger.warning("Could not estimate weight for %s", ingredient_name)
                continue

            # Get nutrition data from USDA API
            nutrition = self._get_ingredient_nutrition(ingredient_name, weight_grams)

            # Add to totals (skip N/A values)
            for key, value in nutrition.items():
                if value != "N/A" and isinstance(value, (int, float)):
                    total[key] += value

        return total

    def _estimate_ingredient_weight(self, ingredient: str, amount: float, unit: str) -> float:
        """Estimate ingredient weight in grams.

        Args:
            ingredient: Ingredient name
            amount: Amount/quantity
            unit: Unit of measurement

        Returns:
            Estimated weight in grams
        """
        unit = unit.lower().strip()
        ingredient = ingredient.lower().strip()

        # Direct weight units
        if unit in ["g", "grams", "gram"]:
            return float(amount)
        elif unit in ["kg", "kilograms", "kilogram"]:
            return float(amount) * 1000
        elif unit in ["oz", "ounces", "ounce"]:
            return float(amount) * 28.35
        elif unit in ["lb", "lbs", "pounds", "pound"]:
            return float(amount) * 453.59

        # Volume/count units - look up in conversion table
        # Try exact ingredient match first
        if ingredient in self._conversion_table:
            ingredient_conversions = self._conversion_table[ingredient]
            if unit in ingredient_conversions:
                return float(amount) * float(ingredient_conversions[unit])

        # Try partial ingredient matches
        for conv_ingredient, unit_conversions in self._conversion_table.items():
            if conv_ingredient in ingredient or ingredient in conv_ingredient:
                if unit in unit_conversions:
                    return float(amount) * float(unit_conversions[unit])

        # Fallback estimate based on unit type
        fallback_weights = {
            "cups": 120,
            "cup": 120,
            "tablespoons": 15,
            "tbsp": 15,
            "teaspoons": 5,
            "tsp": 5,
            "pieces": 50,
            "piece": 50,
            "slices": 30,
            "slice": 30,
        }

        if unit in fallback_weights:
            estimated = float(amount) * fallback_weights[unit]
            self.logger.warning("Using fallback weight estimate for %s: %sg", ingredient, estimated)
            return estimated

        # Last resort - assume 1 unit = 100g
        self.logger.warning("Unknown unit '%s' for %s, assuming 100g per unit", unit, ingredient)
        return float(amount) * 100

    def _get_ingredient_nutrition(self, ingredient_name: str, weight_grams: float) -> dict[str, float | str]:
        """Get nutrition data for an ingredient from USDA API.

        Args:
            ingredient_name: Name of ingredient
            weight_grams: Weight in grams

        Returns:
            Nutrition data dictionary
        """
        # Check cache first
        cache_key = ingredient_name.lower().strip()
        if cache_key in self._ingredient_cache:
            self.logger.debug("Using cached data for %s", ingredient_name)
            return self._scale_nutrition(self._ingredient_cache[cache_key], weight_grams)

        try:
            # Search USDA API
            food_data = self._search_usda_ingredient(ingredient_name)

            if food_data:
                nutrition = self._extract_nutrition_from_usda(food_data)
                # Cache the per-100g nutrition data
                self._ingredient_cache[cache_key] = nutrition
                self.logger.debug("Cached nutrition data for %s", ingredient_name)
                return self._scale_nutrition(nutrition, weight_grams)
            else:
                self.logger.warning("No USDA data found for %s", ingredient_name)
                return self._create_na_nutrition()["per_serving"]

        except Exception as e:
            self.logger.error("Error fetching nutrition for %s: %s", ingredient_name, e)
            return self._create_na_nutrition()["per_serving"]

    def _search_usda_ingredient(self, ingredient_name: str) -> dict[str, Any] | None:
        """Search USDA API for ingredient.

        Args:
            ingredient_name: Ingredient to search for

        Returns:
            USDA food data or None if not found
        """
        search_url = f"{self.base_url}/foods/search"
        params = {
            "query": ingredient_name,
            "pageSize": 5,
            "dataType": ["Foundation", "SR Legacy"],
            "api_key": self.api_key,
        }

        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        foods = data.get("foods", [])

        if foods:
            return foods[0]  # Return best match
        return None

    def _extract_nutrition_from_usda(self, food_data: dict[str, Any]) -> dict[str, float | str]:
        """Extract nutrition values from USDA food data.

        Args:
            food_data: USDA food data dictionary

        Returns:
            Nutrition values per 100g
        """
        nutrients = food_data.get("foodNutrients", [])

        # USDA nutrient ID mapping
        nutrient_map = {
            "calories": [1008],  # Energy (kcal)
            "protein_g": [1003],  # Protein
            "carbs_g": [1005],  # Carbohydrate, by difference
            "fat_g": [1004],  # Total lipid (fat)
            "fiber_g": [1079],  # Fiber, total dietary
            "sodium_mg": [1093],  # Sodium, Na
        }

        nutrition: dict[str, float | str] = {}

        for nutr_name, nutr_ids in nutrient_map.items():
            value = None

            for nutrient in nutrients:
                nutrient_id = nutrient.get("nutrientId") or nutrient.get("nutrientNumber")
                if nutrient_id in nutr_ids:
                    value = nutrient.get("value", 0)
                    break

            if value is not None and value > 0:
                nutrition[nutr_name] = float(value)
            else:
                nutrition[nutr_name] = "N/A"

        return nutrition

    def _scale_nutrition(
        self, nutrition_per_100g: dict[str, float | str], weight_grams: float
    ) -> dict[str, float | str]:
        """Scale nutrition values from per-100g to actual weight.

        Args:
            nutrition_per_100g: Nutrition values per 100g
            weight_grams: Actual weight in grams

        Returns:
            Scaled nutrition values
        """
        scale_factor = weight_grams / 100.0
        scaled: dict[str, float | str] = {}

        for key, value in nutrition_per_100g.items():
            if value == "N/A":
                scaled[key] = "N/A"
            else:
                scaled[key] = round(float(value) * scale_factor, 2)

        return scaled

    def _calculate_per_serving(self, total_nutrition: dict[str, float], servings: int) -> dict[str, int | str]:
        """Calculate per-serving nutrition from totals.

        Args:
            total_nutrition: Total nutrition values
            servings: Number of servings

        Returns:
            Per-serving nutrition values as integers (following nutrition label standards)
        """
        per_serving: dict[str, int | str] = {}

        for key, value in total_nutrition.items():
            # Round to nearest integer following nutrition label standards
            per_serving[key] = round(float(value) / max(servings, 1))

        return per_serving

    def _create_na_nutrition(self) -> dict[str, dict[str, str]]:
        """Create nutrition dict with N/A values.

        Returns:
            Nutrition dict with N/A values
        """
        return {
            "per_serving": {
                "calories": "N/A",
                "protein_g": "N/A",
                "carbs_g": "N/A",
                "fat_g": "N/A",
                "fiber_g": "N/A",
                "sodium_mg": "N/A",
            }
        }

    def enhance_yaml_file(self, yaml_file: Path) -> None:
        """Enhance a YAML recipe file with nutrition information.

        Args:
            yaml_file: Path to YAML recipe file
        """
        try:
            # Load YAML file
            with open(yaml_file, encoding="utf-8") as f:
                recipe_data = yaml.safe_load(f)

            # Enhance with nutrition
            enhanced_data = self.enhance_recipe(recipe_data)

            # Save back to file
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(enhanced_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

            self.logger.info("Enhanced YAML file: %s", yaml_file)

        except Exception as e:
            self.logger.error("Error enhancing YAML file %s: %s", yaml_file, e)
            raise

    def get_cache_stats(self) -> dict[str, int | str]:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        return {
            "cached_ingredients": len(self._ingredient_cache),
            "api_key_type": "DEMO_KEY" if self.api_key == "DEMO_KEY" else "custom",
        }
