"""Unit tests for YAML validator with business rules and weight validation.

This test module provides comprehensive testing of the YAMLValidator class
following CLAUDE.md testing standards with various validation scenarios.

The tests cover:
- YAML schema validation
- Business rule validation
- Weight consistency checking
- Category validation
- Nutrition validation
- Error handling and edge cases

Example usage:
    pytest tests/unit/test_yaml_validator.py -v
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from recipe_fmt.validators.yaml_validator import (
    ValidationError,
    ValidationResult,
    ValidationSeverity,
    YAMLValidator,
    create_validator,
)


class TestYAMLValidatorInitialization:
    """Test suite for YAMLValidator initialization and configuration."""

    def test_initialization_with_defaults(self):
        """Test validator initializes with default configuration."""
        validator = YAMLValidator()

        config = validator.get_cfg()
        assert config["strict_validation"] is True
        assert config["check_weights"] is True
        assert config["check_nutrition"] is False
        assert config["allow_unknown_categories"] is True
        assert config["min_ingredients"] == 1
        assert config["max_ingredients"] == 50

    def test_initialization_with_custom_config(self):
        """Test validator initialization with custom configuration."""
        custom_config = {
            "strict_validation": False,
            "check_weights": False,
            "check_nutrition": True,
            "min_ingredients": 2,
            "max_ingredients": 20,
            "weight_tolerance": 0.2,
        }

        validator = YAMLValidator(custom_config)
        config = validator.get_cfg()

        assert config["strict_validation"] is False
        assert config["check_weights"] is False
        assert config["check_nutrition"] is True
        assert config["min_ingredients"] == 2
        assert config["max_ingredients"] == 20
        assert config["weight_tolerance"] == 0.2

    def test_validation_rules_initialization(self):
        """Test that validation rules and lookup tables are initialized."""
        validator = YAMLValidator()

        # Check unit weights lookup table
        assert "cups" in validator.unit_weights
        assert "TBL" in validator.unit_weights
        assert "tsp" in validator.unit_weights

        # Check valid categories
        assert "Breakfast" in validator.valid_categories
        assert "Dessert" in validator.valid_categories
        assert "Other" in validator.valid_categories

        # Check common purposes
        assert "base" in validator.common_purposes
        assert "seasoning" in validator.common_purposes

    def test_create_validator_factory(self):
        """Test validator factory function."""
        validator = create_validator(strict=False, check_weights=True)

        config = validator.get_cfg()
        assert config["strict_validation"] is False
        assert config["check_weights"] is True


class TestYAMLValidatorFileOperations:
    """Test suite for YAML file validation operations."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = YAMLValidator()

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_validate_valid_yaml_file(self):
        """Test validation of a valid YAML file."""
        # Create valid YAML file
        yaml_file = Path(self.temp_dir) / "valid_recipe.yaml"
        valid_yaml = {
            "title": "Test Recipe",
            "category": "Breakfast",
            "description": "A test recipe",
            "servings": 4,
            "prep_time": "10 minutes",
            "cook_time": "15 minutes",
            "ingredients": [
                {
                    "ingredient": "flour",
                    "amount": 2,
                    "unit": "cups",
                    "weight_grams": 240,
                    "purpose": "base",
                }
            ],
            "instructions": ["Mix ingredients", "Cook until done"],
        }

        with open(yaml_file, "w") as f:
            yaml.dump(valid_yaml, f)

        result = self.validator.validate_yaml_file(yaml_file)

        assert result.valid is True
        assert result.recipe is not None
        assert result.recipe.title == "Test Recipe"
        assert len(result.errors) == 0

    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file."""
        nonexistent_file = Path(self.temp_dir) / "missing.yaml"

        result = self.validator.validate_yaml_file(nonexistent_file)

        assert result.valid is False
        assert len(result.errors) == 1
        assert "not found" in result.errors[0].message

    def test_validate_invalid_file_extension(self):
        """Test validation of file with invalid extension."""
        invalid_file = Path(self.temp_dir) / "recipe.txt"
        invalid_file.write_text("title: Test Recipe")

        result = self.validator.validate_yaml_file(invalid_file)

        assert result.valid is False
        assert "Invalid file type" in result.errors[0].message

    def test_validate_empty_file(self):
        """Test validation of empty file."""
        empty_file = Path(self.temp_dir) / "empty.yaml"
        empty_file.write_text("")

        result = self.validator.validate_yaml_file(empty_file)

        assert result.valid is False
        assert "empty" in result.errors[0].message.lower()

    def test_validate_malformed_yaml(self):
        """Test validation of malformed YAML."""
        yaml_file = Path(self.temp_dir) / "malformed.yaml"
        malformed_yaml = """title: "Test Recipe"
ingredients:
  - ingredient: "flour"
    amount: 2
    unit: cups"  # Missing opening quote
"""
        yaml_file.write_text(malformed_yaml)

        result = self.validator.validate_yaml_file(yaml_file)

        assert result.valid is False
        assert "YAML parsing error" in result.errors[0].message


class TestYAMLValidatorContentValidation:
    """Test suite for YAML content validation."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.validator = YAMLValidator()

    def test_validate_valid_yaml_content(self):
        """Test validation of valid YAML content string."""
        valid_yaml = """title: "Chocolate Cookies"
category: "Dessert"
description: "Delicious chocolate cookies"
servings: 12
ingredients:
  - ingredient: "flour"
    amount: 2
    unit: "cups"
    weight_grams: 240
    purpose: "base"
  - ingredient: "sugar"
    amount: 1
    unit: "cup"
    weight_grams: 200
    purpose: "sweetener"
instructions:
  - "Mix dry ingredients"
  - "Add wet ingredients"
  - "Bake at 350F for 12 minutes"
"""

        result = self.validator.validate_yaml_content(valid_yaml, "test_content")

        assert result.valid is True
        assert result.recipe is not None
        assert result.recipe.title == "Chocolate Cookies"
        assert len(result.recipe.ingredients) == 2
        assert len(result.recipe.instructions) == 3

    def test_validate_invalid_yaml_structure(self):
        """Test validation of YAML with invalid structure."""
        invalid_yaml = "not_a_dict"

        result = self.validator.validate_yaml_content(invalid_yaml, "test")

        assert result.valid is False
        assert "Invalid YAML structure" in result.errors[0].message

    def test_validate_yaml_with_schema_errors(self):
        """Test validation of YAML with Pydantic schema errors."""
        invalid_schema_yaml = """title: ""  # Empty title not allowed
category: "Breakfast"
servings: -1  # Negative servings not allowed
ingredients: []  # Empty ingredients not allowed
instructions: []  # Empty instructions not allowed
"""

        result = self.validator.validate_yaml_content(invalid_schema_yaml, "test")

        assert result.valid is False
        assert "Schema validation failed" in result.errors[0].message


class TestYAMLValidatorBusinessRules:
    """Test suite for business rule validation."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.validator = YAMLValidator()

    def test_category_validation_valid(self):
        """Test validation of valid categories."""
        valid_categories = [
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
        ]

        for category in valid_categories:
            yaml_data = {
                "title": "Test Recipe",
                "category": category,
                "servings": 4,
                "ingredients": [{"ingredient": "test", "amount": 1, "unit": "cup"}],
                "instructions": ["Test instruction"],
            }

            errors = []
            warnings = []
            self.validator._validate_business_rules(yaml_data, errors, warnings)

            # Should not generate category errors for valid categories
            category_errors = [e for e in errors if e.field == "category"]
            assert len(category_errors) == 0

    def test_category_validation_unknown(self):
        """Test validation of unknown category."""
        yaml_data = {
            "title": "Test Recipe",
            "category": "UnknownCategory",
            "servings": 4,
            "ingredients": [{"ingredient": "test", "amount": 1, "unit": "cup"}],
            "instructions": ["Test instruction"],
        }

        errors = []
        warnings = []
        self.validator._validate_business_rules(yaml_data, errors, warnings)

        # Should generate warning for unknown category (default behavior)
        category_warnings = [w for w in warnings if w.field == "category"]
        assert len(category_warnings) == 1
        assert "Unknown category" in category_warnings[0].message

    def test_category_validation_strict_mode(self):
        """Test category validation in strict mode."""
        strict_validator = YAMLValidator({"allow_unknown_categories": False})

        yaml_data = {
            "category": "InvalidCategory",
            "ingredients": [{"ingredient": "test", "amount": 1, "unit": "cup"}],
            "instructions": ["Test instruction"],
        }

        errors = []
        warnings = []
        strict_validator._validate_business_rules(yaml_data, errors, warnings)

        # Should generate error for unknown category in strict mode
        category_errors = [e for e in errors if e.field == "category"]
        assert len(category_errors) == 1
        assert "Invalid category" in category_errors[0].message

    def test_ingredient_count_validation(self):
        """Test validation of ingredient count limits."""
        # Test too few ingredients
        yaml_data_few = {"ingredients": [], "instructions": ["Test instruction"]}

        errors = []
        warnings = []
        self.validator._validate_business_rules(yaml_data_few, errors, warnings)

        ingredient_errors = [e for e in errors if e.field == "ingredients"]
        assert len(ingredient_errors) == 1
        assert "Too few ingredients" in ingredient_errors[0].message

        # Test many ingredients (should warn)
        many_ingredients = [{"ingredient": f"ingredient_{i}", "amount": 1, "unit": "cup"} for i in range(60)]
        yaml_data_many = {"ingredients": many_ingredients, "instructions": ["Test instruction"]}

        errors = []
        warnings = []
        self.validator._validate_business_rules(yaml_data_many, errors, warnings)

        ingredient_warnings = [w for w in warnings if w.field == "ingredients"]
        assert len(ingredient_warnings) == 1
        assert "Many ingredients" in ingredient_warnings[0].message

    def test_instructions_count_validation(self):
        """Test validation of instructions count limits."""
        # Test too few instructions
        yaml_data_few = {
            "ingredients": [{"ingredient": "test", "amount": 1, "unit": "cup"}],
            "instructions": [],
        }

        errors = []
        warnings = []
        self.validator._validate_business_rules(yaml_data_few, errors, warnings)

        instruction_errors = [e for e in errors if e.field == "instructions"]
        assert len(instruction_errors) == 1
        assert "Too few instructions" in instruction_errors[0].message

        # Test many instructions (should warn)
        many_instructions = [f"Step {i}" for i in range(25)]
        yaml_data_many = {
            "ingredients": [{"ingredient": "test", "amount": 1, "unit": "cup"}],
            "instructions": many_instructions,
        }

        errors = []
        warnings = []
        self.validator._validate_business_rules(yaml_data_many, errors, warnings)

        instruction_warnings = [w for w in warnings if w.field == "instructions"]
        assert len(instruction_warnings) == 1
        assert "Many instructions" in instruction_warnings[0].message

    def test_servings_validation(self):
        """Test validation of servings field."""
        # Test invalid servings (too low)
        yaml_data_low = {
            "servings": 0,
            "ingredients": [{"ingredient": "test", "amount": 1, "unit": "cup"}],
            "instructions": ["Test instruction"],
        }

        errors = []
        warnings = []
        self.validator._validate_business_rules(yaml_data_low, errors, warnings)

        servings_errors = [e for e in errors if e.field == "servings"]
        assert len(servings_errors) == 1
        assert "at least 1" in servings_errors[0].message

        # Test high servings (should warn)
        yaml_data_high = {
            "servings": 150,
            "ingredients": [{"ingredient": "test", "amount": 1, "unit": "cup"}],
            "instructions": ["Test instruction"],
        }

        errors = []
        warnings = []
        self.validator._validate_business_rules(yaml_data_high, errors, warnings)

        servings_warnings = [w for w in warnings if w.field == "servings"]
        assert len(servings_warnings) == 1
        assert "Large serving count" in servings_warnings[0].message


class TestYAMLValidatorWeightValidation:
    """Test suite for weight consistency validation."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.validator = YAMLValidator({"check_weights": True})

    def test_weight_consistency_validation_accurate(self):
        """Test weight validation with accurate estimates."""
        from recipe_fmt.models.recipe import Ingredient, Recipe

        # Create recipe with accurate weight estimates
        ingredients = [
            Ingredient(
                ingredient="all-purpose flour",
                amount=2.0,
                unit="cups",
                weight_grams=240,  # Accurate: 2 cups * 120g/cup = 240g
                purpose="base",
            ),
            Ingredient(
                ingredient="sugar",
                amount=1.0,
                unit="cup",
                weight_grams=200,  # Accurate: 1 cup * 200g/cup = 200g
                purpose="sweetener",
            ),
        ]

        recipe = Recipe(
            title="Test Recipe",
            category="Dessert",
            servings=4,
            ingredients=ingredients,
            instructions=["Mix ingredients"],
        )

        warnings = []
        self.validator._validate_weight_consistency(recipe, warnings)

        # Should not generate warnings for accurate weights
        weight_warnings = [w for w in warnings if "weight_grams" in w.field]
        assert len(weight_warnings) == 0

    def test_weight_consistency_validation_inaccurate(self):
        """Test weight validation with inaccurate estimates."""
        from recipe_fmt.models.recipe import Ingredient, Recipe

        # Create recipe with inaccurate weight estimates
        ingredients = [
            Ingredient(
                ingredient="all-purpose flour",
                amount=2.0,
                unit="cups",
                weight_grams=500,  # Inaccurate: should be ~240g
                purpose="base",
            )
        ]

        recipe = Recipe(
            title="Test Recipe",
            category="Dessert",
            servings=4,
            ingredients=ingredients,
            instructions=["Mix ingredients"],
        )

        warnings = []
        self.validator._validate_weight_consistency(recipe, warnings)

        # Should generate warning for inaccurate weight
        weight_warnings = [w for w in warnings if "weight_grams" in w.field]
        assert len(weight_warnings) == 1
        assert "inaccurate" in weight_warnings[0].message.lower()

    def test_weight_estimation_algorithm(self):
        """Test weight estimation algorithm for various ingredients."""
        from recipe_fmt.models.recipe import Ingredient

        test_cases = [
            # (ingredient_name, amount, unit, expected_weight_range)
            ("all-purpose flour", 1, "cups", (110, 130)),
            ("flour", 2, "TBL", (14, 16)),
            ("sugar", 1, "tsp", (3, 5)),
            ("butter", 1, "cups", (220, 230)),
            ("unknown ingredient", 1, "cups", None),  # Should return None
        ]

        for ingredient_name, amount, unit, expected_range in test_cases:
            ingredient = Ingredient(
                ingredient=ingredient_name,
                amount=amount,
                unit=unit,
                weight_grams=100,  # Dummy value
            )

            estimated_weight = self.validator._estimate_ingredient_weight(ingredient)

            if expected_range is None:
                assert estimated_weight is None
            else:
                assert estimated_weight is not None
                assert expected_range[0] <= estimated_weight <= expected_range[1]

    def test_weight_validation_disabled(self):
        """Test that weight validation can be disabled."""
        validator = YAMLValidator({"check_weights": False})

        from recipe_fmt.models.recipe import Ingredient, Recipe

        # Create recipe with very inaccurate weights
        ingredients = [
            Ingredient(
                ingredient="flour",
                amount=1.0,
                unit="cups",
                weight_grams=9999,  # Extremely inaccurate
                purpose="base",
            )
        ]

        recipe = Recipe(
            title="Test Recipe",
            category="Other",
            servings=4,
            ingredients=ingredients,
            instructions=["Test"],
        )

        warnings = []
        validator._validate_weight_consistency(recipe, warnings)

        # Should not generate warnings when disabled
        weight_warnings = [w for w in warnings if "weight_grams" in w.field]
        assert len(weight_warnings) == 0


class TestYAMLValidatorNutritionValidation:
    """Test suite for nutrition validation."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.validator = YAMLValidator({"check_nutrition": True})

    def test_nutrition_validation_basic_checks(self):
        """Test basic nutrition validation checks."""
        from recipe_fmt.models.recipe import Ingredient, Nutrition, Recipe

        # Test very high calories that should trigger warning
        nutrition_high = Nutrition(calories=3000)  # Very high calorie count
        recipe = Recipe(
            title="Test Recipe",
            category="Other",
            servings=4,
            ingredients=[Ingredient(ingredient="test", amount=1, unit="cup")],
            instructions=["Test"],
            nutrition=nutrition_high,
        )

        warnings = []
        self.validator._validate_nutrition_data(recipe, warnings)

        nutrition_warnings = [w for w in warnings if w.field.startswith("nutrition")]
        assert len(nutrition_warnings) == 1
        assert "High calorie count" in nutrition_warnings[0].message

    def test_nutrition_macronutrient_balance(self):
        """Test macronutrient balance validation."""
        from recipe_fmt.models.recipe import Ingredient, Nutrition, Recipe

        # Create nutrition with balanced macros
        # 20g protein * 4 + 30g carbs * 4 + 10g fat * 9 = 290 calories
        nutrition = Nutrition(calories=290, protein_g=20, carbs_g=30, fat_g=10)

        recipe = Recipe(
            title="Test Recipe",
            category="Other",
            servings=4,
            ingredients=[Ingredient(ingredient="test", amount=1, unit="cup")],
            instructions=["Test"],
            nutrition=nutrition,
        )

        warnings = []
        self.validator._validate_nutrition_data(recipe, warnings)

        # Should not generate warnings for balanced macros
        balance_warnings = [w for w in warnings if "doesn't match macronutrients" in w.message]
        assert len(balance_warnings) == 0

        # Test unbalanced macros
        nutrition.calories = 500  # Way off from calculated 290
        recipe.nutrition = nutrition

        warnings = []
        self.validator._validate_nutrition_data(recipe, warnings)

        balance_warnings = [w for w in warnings if "doesn't match macronutrients" in w.message]
        assert len(balance_warnings) == 1

    def test_nutrition_validation_disabled(self):
        """Test that nutrition validation can be disabled."""
        validator = YAMLValidator({"check_nutrition": False})

        from recipe_fmt.models.recipe import Ingredient, Nutrition, Recipe

        # Create recipe with high nutrition data (since negative is blocked by Pydantic)
        nutrition = Nutrition(calories=5000)  # Very high calories
        recipe = Recipe(
            title="Test Recipe",
            category="Other",
            servings=4,
            ingredients=[Ingredient(ingredient="test", amount=1, unit="cup")],
            instructions=["Test"],
            nutrition=nutrition,
        )

        warnings = []
        validator._validate_nutrition_data(recipe, warnings)

        # Should not generate warnings when disabled
        assert len(warnings) == 0


class TestYAMLValidatorStrictMode:
    """Test suite for strict validation mode."""

    def test_strict_mode_enabled(self):
        """Test behavior in strict validation mode."""
        strict_validator = YAMLValidator({"strict_validation": True})

        # YAML with schema errors should fail in strict mode
        invalid_yaml = """title: ""  # Empty title
category: "Breakfast"
servings: 4
ingredients:
  - ingredient: "test"
    amount: 1
    unit: "cup"
instructions:
  - "Test instruction"
"""

        result = strict_validator.validate_yaml_content(invalid_yaml, "test")

        assert result.valid is False
        assert "Schema validation failed" in result.errors[0].message

    def test_strict_mode_disabled(self):
        """Test behavior with strict validation disabled."""
        lenient_validator = YAMLValidator({"strict_validation": False})

        # Same invalid YAML should continue validation in lenient mode
        invalid_yaml = """title: ""  # Empty title
category: "Breakfast"
servings: 4
ingredients:
  - ingredient: "test"
    amount: 1
    unit: "cup"
instructions:
  - "Test instruction"
"""

        result = lenient_validator.validate_yaml_content(invalid_yaml, "test")

        # Should still fail but with different handling
        assert result.valid is False


class TestYAMLValidatorStatistics:
    """Test suite for validation statistics and reporting."""

    def test_validation_stats(self):
        """Test validation statistics reporting."""
        validator = YAMLValidator()
        stats = validator.get_validation_stats()

        assert "validator_config" in stats
        assert "supported_categories" in stats
        assert "supported_units" in stats
        assert "validation_rules" in stats

        # Check that all expected categories are listed
        expected_categories = {
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
        assert set(stats["supported_categories"]) == expected_categories

        # Check that validation rules are documented
        rules = stats["validation_rules"]
        assert "min_ingredients" in rules
        assert "max_ingredients" in rules
        assert "weight_tolerance" in rules

    def test_validation_result_summary(self):
        """Test validation result summary methods."""
        # Create result with errors and warnings
        result = ValidationResult(valid=False)
        result.errors = [
            ValidationError(ValidationSeverity.ERROR, "field1", "Error message 1"),
            ValidationError(ValidationSeverity.ERROR, "field2", "Error message 2"),
        ]
        result.warnings = [ValidationError(ValidationSeverity.WARNING, "field3", "Warning message 1")]

        assert result.has_errors is True
        assert result.has_warnings is True
        assert result.get_error_summary() == "2 errors, 1 warnings"

        # Test result with only warnings
        result_warnings_only = ValidationResult(valid=True)
        result_warnings_only.warnings = [ValidationError(ValidationSeverity.WARNING, "field", "Warning")]

        assert result_warnings_only.has_errors is False
        assert result_warnings_only.has_warnings is True
        assert result_warnings_only.get_error_summary() == "1 warnings"

        # Test result with no issues
        result_clean = ValidationResult(valid=True)

        assert result_clean.has_errors is False
        assert result_clean.has_warnings is False
        assert result_clean.get_error_summary() == "No issues"


class TestYAMLValidatorEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_very_large_recipe(self):
        """Test validation of very large recipe."""
        # Create recipe with many ingredients and instructions
        ingredients = []
        for i in range(100):
            ingredients.append({"ingredient": f"ingredient_{i}", "amount": 1, "unit": "cup", "weight_grams": 100})

        instructions = [f"Step {i}" for i in range(50)]

        large_yaml = {
            "title": "Large Recipe",
            "category": "Other",
            "servings": 20,
            "ingredients": ingredients,
            "instructions": instructions,
        }

        validator = YAMLValidator()
        yaml_content = yaml.dump(large_yaml)
        result = validator.validate_yaml_content(yaml_content, "large_recipe")

        # Should handle large recipes but may have warnings
        assert result.recipe is not None
        assert len(result.recipe.ingredients) == 100
        assert len(result.recipe.instructions) == 50

    def test_unicode_handling(self):
        """Test validation with unicode characters."""
        unicode_yaml = """title: "Café au Lait ☕"
category: "Breakfast"
description: "Délicieux café français"
servings: 2
ingredients:
  - ingredient: "café moulu"
    amount: 2
    unit: "cuillères à soupe"
    weight_grams: 20
    purpose: "base"
instructions:
  - "Chauffer l'eau à 90°C"
  - "Verser sur le café et mélanger"
"""

        validator = YAMLValidator()
        result = validator.validate_yaml_content(unicode_yaml, "unicode_test")

        assert result.recipe is not None
        assert "☕" in result.recipe.title
        assert "Délicieux" in result.recipe.description

    def test_validation_error_suggestions(self):
        """Test that validation errors include helpful suggestions."""
        yaml_data = {
            "category": "InvalidCategory",
            "ingredients": [{"ingredient": "test", "amount": 1, "unit": "cup"}],
            "instructions": ["Test"],
        }

        validator = YAMLValidator({"allow_unknown_categories": False})
        errors = []
        warnings = []
        validator._validate_business_rules(yaml_data, errors, warnings)

        category_errors = [e for e in errors if e.field == "category"]
        assert len(category_errors) == 1
        assert category_errors[0].suggestion is not None
        assert "Must be one of:" in category_errors[0].suggestion


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
