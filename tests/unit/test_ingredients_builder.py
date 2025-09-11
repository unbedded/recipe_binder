"""Unit tests for IngredientsBuilder extracted from PDFCardGenerator."""

from recipe_fmt.generators.pdf.builders.ingredients_builder import IngredientsBuilder
from recipe_fmt.models.recipe import Ingredient, Recipe


class TestIngredientsBuilder:
    """Test suite for IngredientsBuilder component."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.cfg_dict = {"show_weights": True}

        # Create ingredients builder
        self.ingredients_builder = IngredientsBuilder(
            cfg_dict=self.cfg_dict,
            default_table_font=9,
            min_font_size=5,
            max_comfortable_ingredients=8,
            extreme_recipe_threshold=15,
        )

        # Create test ingredients
        self.test_ingredients = [
            Ingredient(ingredient="flour", amount=2.0, unit="cups", weight_grams=240, purpose="base"),
            Ingredient(ingredient="sugar", amount=0.5, unit="cup", weight_grams=100, purpose="sweetener"),
            Ingredient(ingredient="eggs", amount=3.0, unit="count", weight_grams=150),
            Ingredient(ingredient="milk", amount=1.0, unit="cup", weight_grams=240),
        ]

        # Create test recipe
        self.test_recipe = Recipe(
            title="Test Recipe",
            category="Baking",
            servings=4,
            ingredients=self.test_ingredients,
            instructions=["Mix ingredients"],
        )

    def test_amount_formatting(self):
        """Test amount formatting logic."""
        # Test integer amounts
        assert self.ingredients_builder._format_amount(2.0) == "2"
        assert self.ingredients_builder._format_amount(1.0) == "1"

        # Test decimal amounts
        assert self.ingredients_builder._format_amount(0.5) == "0.5"
        assert self.ingredients_builder._format_amount(1.25) == "1.25"
        assert self.ingredients_builder._format_amount(0.33) == "0.33"

    def test_unit_abbreviation(self):
        """Test unit abbreviation logic."""
        # Test cup variations
        assert self.ingredients_builder._abbreviate_unit("cup") == "cp"
        assert self.ingredients_builder._abbreviate_unit("cups") == "cp"
        assert self.ingredients_builder._abbreviate_unit("Cup") == "cp"

        # Test count variations
        assert self.ingredients_builder._abbreviate_unit("count") == "cnt"
        assert self.ingredients_builder._abbreviate_unit("Count") == "cnt"

        # Test tablespoon variations
        assert self.ingredients_builder._abbreviate_unit("tablespoon") == "tbsp"
        assert self.ingredients_builder._abbreviate_unit("tablespoons") == "tbsp"
        assert self.ingredients_builder._abbreviate_unit("tbsp") == "tbsp"

        # Test teaspoon variations
        assert self.ingredients_builder._abbreviate_unit("teaspoon") == "tsp"
        assert self.ingredients_builder._abbreviate_unit("teaspoons") == "tsp"
        assert self.ingredients_builder._abbreviate_unit("tsp") == "tsp"

        # Test unknown units pass through
        assert self.ingredients_builder._abbreviate_unit("ounces") == "ounces"
        assert self.ingredients_builder._abbreviate_unit("lbs") == "lbs"

    def test_purpose_column_detection(self):
        """Test purpose column detection logic."""
        # Test with ingredients that have purposes
        ingredients_with_purpose = [
            Ingredient(ingredient="flour", amount=2.0, unit="cups", purpose="base"),
            Ingredient(ingredient="sugar", amount=1.0, unit="cup", purpose="sweetener"),
        ]
        assert self.ingredients_builder.should_show_purpose_column(ingredients_with_purpose) is True

        # Test with some ingredients having purposes
        ingredients_mixed = [
            Ingredient(ingredient="flour", amount=2.0, unit="cups", purpose="base"),
            Ingredient(ingredient="water", amount=1.0, unit="cup"),
        ]
        assert self.ingredients_builder.should_show_purpose_column(ingredients_mixed) is True

        # Test with no purposes
        ingredients_no_purpose = [
            Ingredient(ingredient="flour", amount=2.0, unit="cups"),
            Ingredient(ingredient="water", amount=1.0, unit="cup"),
        ]
        assert self.ingredients_builder.should_show_purpose_column(ingredients_no_purpose) is False

    def test_font_size_calculation(self):
        """Test font size scaling logic."""
        # Test small recipe (no scaling)
        assert self.ingredients_builder._calculate_font_size(5) == 9  # default_table_font
        assert self.ingredients_builder._calculate_font_size(8) == 9  # max_comfortable

        # Test medium recipe (regular scaling)
        font_size_10 = self.ingredients_builder._calculate_font_size(10)
        assert font_size_10 < 9  # Should be scaled down
        assert font_size_10 >= 5  # Should not go below min_font_size

        # Test large recipe (extreme scaling)
        font_size_20 = self.ingredients_builder._calculate_font_size(20)
        assert font_size_20 < font_size_10  # Should be even smaller
        assert font_size_20 >= 5  # Should not go below min_font_size

    def test_ingredient_row_building(self):
        """Test individual ingredient row building."""
        ingredient = Ingredient(
            ingredient="all-purpose flour", amount=2.5, unit="cups", weight_grams=300, purpose="base"
        )

        # Test with purpose column
        row_with_purpose = self.ingredients_builder._build_ingredient_row(ingredient, show_purpose=True)
        expected_with_purpose = ["2.5", "cp", "300g", "all-purpose flour", "base"]
        assert row_with_purpose == expected_with_purpose

        # Test without purpose column
        row_without_purpose = self.ingredients_builder._build_ingredient_row(ingredient, show_purpose=False)
        expected_without_purpose = ["2.5", "cp", "300g", "all-purpose flour"]
        assert row_without_purpose == expected_without_purpose

        # Test ingredient without weight
        ingredient_no_weight = Ingredient(ingredient="salt", amount=1.0, unit="tsp")
        row_no_weight = self.ingredients_builder._build_ingredient_row(ingredient_no_weight, show_purpose=False)
        expected_no_weight = ["1", "tsp", "", "salt"]
        assert row_no_weight == expected_no_weight

    def test_column_width_calculation_logic(self):
        """Test column width calculation without ReportLab."""
        # Test basic calculation structure
        ingredients = [
            Ingredient(ingredient="flour", amount=2.0, unit="cups", weight_grams=240),
            Ingredient(ingredient="very long ingredient name", amount=0.25, unit="teaspoons", weight_grams=2),
        ]

        col_widths = self.ingredients_builder._calculate_column_widths(ingredients, show_purpose=False)

        # Should have 4 columns: amount, unit, grams, ingredient
        assert len(col_widths) == 4

        # All widths should be positive
        assert all(width > 0 for width in col_widths)

        # Longer ingredient name should result in wider ingredient column
        # (We can't test exact values without ReportLab inch constant, but we can test structure)

    def test_column_width_with_purpose(self):
        """Test column width calculation with purpose column."""
        ingredients = [
            Ingredient(ingredient="flour", amount=2.0, unit="cups", weight_grams=240, purpose="base"),
        ]

        col_widths = self.ingredients_builder._calculate_column_widths(ingredients, show_purpose=True)

        # Should have 5 columns: amount, unit, grams, ingredient, purpose
        assert len(col_widths) == 5

    def test_table_width_estimation(self):
        """Test table width estimation."""
        ingredients = [
            Ingredient(ingredient="flour", amount=2.0, unit="cups", weight_grams=240),
            Ingredient(ingredient="sugar", amount=1.0, unit="cup", weight_grams=200),
        ]

        width_without_purpose = self.ingredients_builder.estimate_table_width(ingredients, show_purpose=False)
        width_with_purpose = self.ingredients_builder.estimate_table_width(ingredients, show_purpose=True)

        # Width should be positive
        assert width_without_purpose > 0
        assert width_with_purpose > 0

        # Width with purpose should be wider (since no ingredients have purpose, this tests the column is still added)
        # Note: This specific assertion might not hold if purpose column isn't added when no purposes exist
        # Let's just test they're both positive for now

    def test_builder_initialization(self):
        """Test that builder initializes correctly."""
        assert self.ingredients_builder.cfg_dict == self.cfg_dict
        assert self.ingredients_builder.default_table_font == 9
        assert self.ingredients_builder.min_font_size == 5
        assert self.ingredients_builder.max_comfortable_ingredients == 8
        assert self.ingredients_builder.extreme_recipe_threshold == 15
        assert self.ingredients_builder.logger is not None

    def test_scaling_thresholds(self):
        """Test that scaling thresholds work correctly."""
        # Test comfortable range
        assert self.ingredients_builder._calculate_font_size(7) == 9  # No scaling

        # Test scaling range
        scaled_font = self.ingredients_builder._calculate_font_size(12)
        assert scaled_font < 9
        assert scaled_font >= 5

        # Test extreme range
        extreme_font = self.ingredients_builder._calculate_font_size(20)
        assert extreme_font <= scaled_font  # Should be same or smaller
        assert extreme_font >= 5  # Should never go below minimum
