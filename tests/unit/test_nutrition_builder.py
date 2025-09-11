"""Unit tests for NutritionBuilder extracted from PDFCardGenerator."""

from recipe_fmt.generators.pdf.builders.nutrition_builder import NutritionBuilder
from recipe_fmt.models.recipe import Ingredient, Recipe


class TestNutritionBuilder:
    """Test suite for NutritionBuilder component."""

    def setup_method(self):
        """Setup test environment before each test method."""
        # Mock styles dictionary (simplified for testing)
        self.styles = {
            "SectionHeader": {"fontSize": 12, "fontName": "Helvetica-Bold"},
            "Normal": {"fontSize": 10, "fontName": "Helvetica"},
        }

        # Create nutrition builder
        self.nutrition_builder = NutritionBuilder(styles=self.styles, content_width=400.0)

        # Create minimal test ingredient (required for Recipe validation)
        test_ingredient = Ingredient(ingredient="test ingredient", amount=1.0, unit="cup")

        # Create test recipe without nutrition data
        self.recipe_no_nutrition = Recipe(
            title="Test Recipe",
            category="Baking",
            servings=4,
            ingredients=[test_ingredient],
            instructions=["Mix ingredients"],
        )

    def test_extract_nutrition_data_no_nutrition(self):
        """Test nutrition data extraction when no nutrition data available."""
        nutrition_data = self.nutrition_builder._extract_nutrition_data(self.recipe_no_nutrition)

        # Should return fallback values
        expected = {
            "calories": 245,
            "protein_g": 8,
            "carbs_g": 35,
            "fat_g": 9,
            "fiber_g": 2,
            "sodium_mg": 387,
        }
        assert nutrition_data == expected

    def test_build_nutrition_table_data(self):
        """Test building nutrition table data."""
        nutrition_data = {
            "calories": 300,
            "protein_g": 12,
            "carbs_g": 40,
            "fat_g": 10,
            "fiber_g": 5,
            "sodium_mg": 400,
        }

        table_data = self.nutrition_builder._build_nutrition_table_data(nutrition_data)

        # Should have header row plus 6 nutrition rows
        assert len(table_data) == 7
        assert table_data[0] == ["Per Serving", ""]

        # Check specific formatted values
        calories_row = table_data[1]
        assert calories_row == ["Calories", "300"]

        protein_row = table_data[2]
        assert protein_row == ["Protein", "12g"]

        sodium_row = table_data[6]
        assert sodium_row == ["Sodium", "400mg"]

    def test_format_note_text_special_cases(self):
        """Test special formatting cases for nutrition values."""
        # Test with zero values
        nutrition_data = {
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0,
            "fiber_g": 0,
            "sodium_mg": 0,
        }

        table_data = self.nutrition_builder._build_nutrition_table_data(nutrition_data)

        # All values should be formatted as "0" or "0g" or "0mg"
        assert table_data[1] == ["Calories", "0"]
        assert table_data[2] == ["Protein", "0g"]
        assert table_data[6] == ["Sodium", "0mg"]

    def test_has_nutrition_data_false(self):
        """Test nutrition data detection when no nutrition available."""
        assert self.nutrition_builder.has_nutrition_data(self.recipe_no_nutrition) is False

    def test_estimate_table_width_default(self):
        """Test table width estimation with default values."""
        width = self.nutrition_builder.estimate_table_width()
        expected = self.nutrition_builder.content_width * 0.4
        assert width == expected

    def test_estimate_table_width_custom(self):
        """Test table width estimation with custom max width."""
        custom_width = 200.0
        width = self.nutrition_builder.estimate_table_width(custom_width)
        assert width == custom_width

    def test_builder_initialization(self):
        """Test that builder initializes correctly."""
        assert self.nutrition_builder.styles == self.styles
        assert self.nutrition_builder.content_width == 400.0
        assert self.nutrition_builder.logger is not None

    def test_nutrition_map_completeness(self):
        """Test that all nutrition data keys are handled in table building."""
        nutrition_data = {
            "calories": 100,
            "protein_g": 5,
            "carbs_g": 20,
            "fat_g": 3,
            "fiber_g": 1,
            "sodium_mg": 200,
        }

        table_data = self.nutrition_builder._build_nutrition_table_data(nutrition_data)

        # Should have all 6 nutrition values plus header
        assert len(table_data) == 7

        # Verify all expected labels are present
        labels = [row[0] for row in table_data[1:]]  # Skip header
        expected_labels = ["Calories", "Protein", "Total Carbs", "Total Fat", "Dietary Fiber", "Sodium"]
        assert labels == expected_labels

    def test_value_type_handling(self):
        """Test handling of different value types in nutrition data."""
        # Test with string values (edge case)
        nutrition_data = {
            "calories": "invalid",
            "protein_g": "5.5",
            "carbs_g": 20,
            "fat_g": 3.7,
            "fiber_g": None,
            "sodium_mg": 200,
        }

        table_data = self.nutrition_builder._build_nutrition_table_data(nutrition_data)

        # Invalid values should be converted to strings
        assert table_data[1][1] == "invalid"  # calories
        assert table_data[2][1] == "5.5"  # protein (string, no formatting)
        assert table_data[3][1] == "20g"  # carbs (int)
        assert table_data[4][1] == "3.7g"  # fat (float)

    def test_nutrition_table_style_structure(self):
        """Test that table style commands are properly structured."""
        style_commands = self.nutrition_builder._build_nutrition_table_style()

        # Should be a list of tuples
        assert isinstance(style_commands, list)
        assert len(style_commands) > 0

        # Each command should be a tuple
        for command in style_commands:
            assert isinstance(command, tuple)
            assert len(command) >= 3  # Should have at least command, position, value
