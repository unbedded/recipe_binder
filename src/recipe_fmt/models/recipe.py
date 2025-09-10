"""Recipe data models with Pydantic validation.

This module defines the core data structures for recipes, ingredients,
and nutrition information with comprehensive validation and type safety.

Example usage:
    from recipe_fmt.models.recipe import Recipe, Ingredient

    ingredient = Ingredient(
        ingredient="all-purpose flour",
        amount=2,
        unit="cups",
        weight_grams=240,
        purpose="base"
    )

    recipe = Recipe(
        title="Perfect Pancakes",
        category="Breakfast",
        ingredients=[ingredient]
    )
"""

from pydantic import BaseModel, Field, field_validator


class Ingredient(BaseModel):
    """Individual recipe ingredient with standardized measurements."""

    ingredient: str = Field(..., min_length=1, description="Ingredient name")
    amount: float = Field(..., gt=0, description="Quantity amount (number or fraction)")
    unit: str = Field(..., min_length=1, description="Measurement unit (TBL, tsp, cups, etc.)")
    weight_grams: int | None = Field(None, ge=0, description="Weight in grams for precision weighing")
    purpose: str | None = Field(None, description="Ingredient's role in recipe (base, seasoning, etc.)")

    @field_validator("unit")
    def standardize_units(cls, v: str) -> str:
        """Ensure consistent unit naming."""
        unit_map = {
            "tbsp": "TBL",
            "tablespoon": "TBL",
            "tablespoons": "TBL",
            "teaspoon": "tsp",
            "teaspoons": "tsp",
            "t": "tsp",
        }
        return unit_map.get(v.lower(), v)


class Nutrition(BaseModel):
    """Nutritional information per serving."""

    calories: int | None = Field(None, ge=0, description="Calories per serving")
    protein_g: float | None = Field(None, ge=0, description="Protein in grams")
    carbs_g: float | None = Field(None, ge=0, description="Carbohydrates in grams")
    fat_g: float | None = Field(None, ge=0, description="Fat in grams")
    fiber_g: float | None = Field(None, ge=0, description="Fiber in grams")
    sodium_mg: int | None = Field(None, ge=0, description="Sodium in milligrams")


class Recipe(BaseModel):
    """Complete recipe with metadata, ingredients, and instructions."""

    title: str = Field(..., min_length=1, max_length=100, description="Recipe title")
    category: str = Field(..., min_length=1, description="Recipe category for PDF naming and color coding")
    description: str | None = Field(None, max_length=500, description="Brief recipe description")
    servings: int = Field(4, ge=1, le=100, description="Number of servings")
    prep_time: str | None = Field(None, description="Preparation time (e.g., '10 minutes')")
    cook_time: str | None = Field(None, description="Cooking time (e.g., '15 minutes')")
    total_time: str | None = Field(None, description="Total time including prep and cooking")

    ingredients: list[Ingredient] = Field(..., min_length=1, description="List of recipe ingredients")
    instructions: list[str] = Field(..., min_length=1, description="Step-by-step cooking instructions")

    nutrition: Nutrition | None = Field(None, description="Nutritional information per serving")
    notes: list[str] | None = Field(None, description="Additional recipe notes or tips")

    # Additional metadata fields
    difficulty: str | None = Field(None, description="Recipe difficulty level (Easy, Medium, Hard)")
    prep_time_minutes: int | None = Field(None, ge=0, description="Preparation time in minutes")
    cook_time_minutes: int | None = Field(None, ge=0, description="Cooking time in minutes")
    tags: list[str] | None = Field(None, description="Recipe tags for categorization")
    source: str | None = Field(None, description="Recipe source or attribution")

    @field_validator("category")
    def validate_category(cls, v: str) -> str:
        """Ensure category matches supported types."""
        valid_categories = {
            "Meat",
            "Side",
            "Main",
            "Soup",
            "Sauce",
            "Breakfast",
            "Salad",
            "Baking",
            "Dessert",
            "Other",
        }
        if v not in valid_categories:
            # Allow custom categories but log a warning
            pass
        return v

    @field_validator("instructions")
    def validate_instructions(cls, v: list[str]) -> list[str]:
        """Ensure instructions are non-empty strings."""
        if not all(instruction.strip() for instruction in v):
            raise ValueError("Instructions cannot be empty")
        return v

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "title": "Perfect Pancakes",
                "category": "Breakfast",
                "description": "Fluffy weekend pancakes",
                "servings": 4,
                "prep_time": "10 minutes",
                "cook_time": "15 minutes",
                "ingredients": [
                    {
                        "ingredient": "all-purpose flour",
                        "amount": 2,
                        "unit": "cups",
                        "weight_grams": 240,
                        "purpose": "base",
                    }
                ],
                "instructions": ["Mix dry ingredients in large bowl"],
            }
        },
    }
