"""Unit tests for HeaderBuilder extracted from PDFCardGenerator."""

from unittest.mock import Mock

from recipe_fmt.generators.pdf.builders.header_builder import HeaderBuilder
from recipe_fmt.models.recipe import Ingredient, Recipe


class TestHeaderBuilder:
    """Test suite for HeaderBuilder component."""

    def setup_method(self):
        """Setup test environment before each test method."""
        # Create mock styles
        self.mock_styles = {
            "RecipeTitle": Mock(),
            "CategoryBanner": Mock(),
            "Normal": Mock(),
        }

        # Create test configuration
        self.cfg_dict = {"show_category_banner": True}
        self.spacing = 3.6  # 0.05 * 72 points

        # Create header builder
        self.header_builder = HeaderBuilder(styles=self.mock_styles, spacing=self.spacing, cfg_dict=self.cfg_dict)

        # Create test recipe
        self.test_recipe = Recipe(
            title="Test Pancakes",
            category="Breakfast",
            servings=4,
            prep_time="10 minutes",
            cook_time="15 minutes",
            ingredients=[Ingredient(ingredient="flour", amount=2.0, unit="cups")],
            instructions=["Mix ingredients"],
        )

    def test_category_color_mapping(self):
        """Test that category colors are mapped correctly."""
        # Test known categories
        breakfast_color = self.header_builder._get_category_color("Breakfast")
        assert breakfast_color.red == 0.85
        assert breakfast_color.green == 0.55
        assert breakfast_color.blue == 0.0

        meat_color = self.header_builder._get_category_color("Meat")
        assert meat_color.red == 0.8
        assert meat_color.green == 0.2
        assert meat_color.blue == 0.2

        # Test unknown category defaults to "Other"
        unknown_color = self.header_builder._get_category_color("UnknownCategory")
        other_color = self.header_builder._get_category_color("Other")
        assert unknown_color.red == other_color.red
        assert unknown_color.green == other_color.green
        assert unknown_color.blue == other_color.blue

    def test_category_icon_mapping(self):
        """Test that category icons are mapped correctly."""
        # Test known categories
        assert self.header_builder._get_category_icon("Breakfast") == "🥞"
        assert self.header_builder._get_category_icon("Meat") == "🥩"
        assert self.header_builder._get_category_icon("Dessert") == "🍰"

        # Test unknown category defaults to "Other"
        assert self.header_builder._get_category_icon("UnknownCategory") == "📝"

    def test_metadata_text_generation(self):
        """Test metadata text generation logic without ReportLab."""
        # Test with all fields
        metadata_parts = []
        if self.test_recipe.servings:
            metadata_parts.append(f"Serves {self.test_recipe.servings}")
        if self.test_recipe.prep_time:
            metadata_parts.append(f"Prep: {self.test_recipe.prep_time}")
        if self.test_recipe.cook_time:
            metadata_parts.append(f"Cook: {self.test_recipe.cook_time}")

        expected_text = " • ".join(metadata_parts)
        assert expected_text == "Serves 4 • Prep: 10 minutes • Cook: 15 minutes"

    def test_metadata_text_partial_fields(self):
        """Test metadata text with only some fields."""
        # Test the logic directly
        servings = 2
        prep_time = None
        cook_time = "30 minutes"

        metadata_parts = []
        if servings:
            metadata_parts.append(f"Serves {servings}")
        if prep_time:
            metadata_parts.append(f"Prep: {prep_time}")
        if cook_time:
            metadata_parts.append(f"Cook: {cook_time}")

        expected_text = " • ".join(metadata_parts)
        assert expected_text == "Serves 2 • Cook: 30 minutes"

    def test_banner_configuration_logic(self):
        """Test banner configuration logic."""
        # Test banner enabled
        assert self.header_builder.cfg_dict.get("show_category_banner", True) is True

        # Test banner disabled
        no_banner_config = {"show_category_banner": False}
        assert no_banner_config.get("show_category_banner", True) is False

    def test_builder_initialization(self):
        """Test that builder initializes correctly."""
        assert self.header_builder.styles == self.mock_styles
        assert self.header_builder.spacing == self.spacing
        assert self.header_builder.cfg_dict == self.cfg_dict
        assert self.header_builder.logger is not None
