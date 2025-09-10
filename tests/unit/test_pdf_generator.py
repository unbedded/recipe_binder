"""Unit tests for PDF generator with ReportLab integration.

This test module provides comprehensive testing of the PDFCardGenerator class
following CLAUDE.md testing standards with mocked ReportLab components.

The tests cover:
- PDF card generation with various layouts
- Category color system
- Typography and styling
- Template integration
- Error handling and edge cases
- Configuration management

Example usage:
    pytest tests/unit/test_pdf_generator.py -v

Note: These tests mock ReportLab components to avoid dependency on the actual library.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from recipe_fmt.generators.pdf_generator import (
    CardLayout,
    CategoryColors,
    PDFCardGenerator,
    create_generator,
)
from recipe_fmt.models.config import DisplayConfig
from recipe_fmt.models.recipe import Ingredient, Recipe


class TestCategoryColors:
    """Test suite for category color system."""

    def test_all_categories_have_colors(self):
        """Test that all expected categories have color definitions."""
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

        assert set(CategoryColors.COLORS.keys()) == expected_categories

    def test_get_valid_category_color(self):
        """Test getting color for valid categories."""
        breakfast_color = CategoryColors.get_color("Breakfast")
        assert breakfast_color is not None
        # Amber/Gold: (0.85, 0.55, 0.0)
        assert breakfast_color.red == 0.85
        assert breakfast_color.green == 0.55
        assert breakfast_color.blue == 0.0

        meat_color = CategoryColors.get_color("Meat")
        assert meat_color is not None
        # Deep Red: (0.8, 0.2, 0.2)
        assert meat_color.red == 0.8
        assert meat_color.green == 0.2
        assert meat_color.blue == 0.2

    def test_get_unknown_category_color(self):
        """Test getting color for unknown category defaults to Other."""
        unknown_color = CategoryColors.get_color("UnknownCategory")
        other_color = CategoryColors.get_color("Other")

        assert unknown_color.red == other_color.red
        assert unknown_color.green == other_color.green
        assert unknown_color.blue == other_color.blue

    def test_get_accent_color(self):
        """Test getting lighter accent colors."""
        base_color = CategoryColors.get_color("Breakfast")
        accent_color = CategoryColors.get_accent_color("Breakfast")

        # Accent should be lighter than base
        assert accent_color.red >= base_color.red
        assert accent_color.green >= base_color.green
        assert accent_color.blue >= base_color.blue

        # Should not exceed 1.0
        assert accent_color.red <= 1.0
        assert accent_color.green <= 1.0
        assert accent_color.blue <= 1.0


class TestPDFCardGeneratorInitialization:
    """Test suite for PDF generator initialization."""

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_initialization_with_reportlab(self):
        """Test generator initializes correctly when ReportLab is available."""
        config = DisplayConfig(show_weights=True)
        generator = PDFCardGenerator(config)

        assert generator.config == config
        assert generator.cfg_dict["card_layout"] == CardLayout.TWO_SIDED
        assert generator.cfg_dict["print_margins"] == 0.25
        assert generator.cfg_dict["show_category_banner"] is True

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", False)
    def test_initialization_without_reportlab(self):
        """Test generator raises error when ReportLab is not available."""
        config = DisplayConfig()

        with pytest.raises(ImportError) as exc_info:
            PDFCardGenerator(config)

        assert "ReportLab is required" in str(exc_info.value)

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_initialization_with_custom_config(self):
        """Test generator initialization with custom configuration."""
        config = DisplayConfig(show_weights=False, show_purpose=True)
        cfg_dict = {
            "card_layout": CardLayout.SINGLE_SIDED,
            "print_margins": 0.5,
            "ingredient_columns": 2,
            "quality": "medium",
        }

        generator = PDFCardGenerator(config, cfg_dict)

        assert generator.config.show_weights is False
        assert generator.config.show_purpose is True
        assert generator.cfg_dict["card_layout"] == CardLayout.SINGLE_SIDED
        assert generator.cfg_dict["print_margins"] == 0.5
        assert generator.cfg_dict["ingredient_columns"] == 2
        assert generator.cfg_dict["quality"] == "medium"

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_card_specifications_initialization(self):
        """Test card specifications are correctly initialized."""
        config = DisplayConfig()
        generator = PDFCardGenerator(config)

        # Check card dimensions (8.5" × 4")
        expected_width = 8.5 * 72  # 72 points per inch
        expected_height = 4.0 * 72

        assert generator.card_width == expected_width
        assert generator.card_height == expected_height

        # Check margins
        expected_margin = 0.25 * 72  # Default margin
        assert generator.margin == expected_margin

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_typography_initialization(self):
        """Test typography styles are properly initialized."""
        config = DisplayConfig()
        generator = PDFCardGenerator(config)

        # Check that custom styles are created
        assert "RecipeTitle" in generator.styles.byName
        assert "CategoryBanner" in generator.styles.byName
        assert "SectionHeader" in generator.styles.byName
        assert "Ingredient" in generator.styles.byName
        assert "Instruction" in generator.styles.byName


class TestPDFCardGeneratorGeneration:
    """Test suite for PDF generation functionality."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = DisplayConfig(show_weights=True)

        # Create test recipe
        self.test_recipe = Recipe(
            title="Test Pancakes",
            category="Breakfast",
            description="Delicious test pancakes",
            servings=4,
            prep_time="10 minutes",
            cook_time="15 minutes",
            ingredients=[
                Ingredient(
                    ingredient="all-purpose flour",
                    amount=2.0,
                    unit="cups",
                    weight_grams=240,
                    purpose="base",
                ),
                Ingredient(ingredient="sugar", amount=2.0, unit="TBL", weight_grams=25, purpose="sweetener"),
            ],
            instructions=[
                "Mix dry ingredients in large bowl",
                "Add wet ingredients and stir until just combined",
                "Cook on griddle until bubbles form",
                "Flip and cook until golden brown",
            ],
            notes=["Don't overmix the batter", "Serve immediately"],
        )

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    @patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate")
    def test_successful_pdf_generation(self, mock_doc_class):
        """Test successful PDF generation with mocked ReportLab."""
        # Setup mock document
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc

        output_path = Path(self.temp_dir) / "test_recipe.pdf"

        generator = PDFCardGenerator(self.config)

        # Mock filesystem operations for testing
        with patch.object(Path, "mkdir"), \
             patch.object(Path, "stat") as mock_stat, \
             patch.object(Path, "is_dir", return_value=True):
            from types import SimpleNamespace

            mock_stat.return_value = SimpleNamespace(st_size=15000)  # 15KB file

            result = generator.generate_card(self.test_recipe, output_path)

        assert result.success is True
        assert result.output_path == output_path
        assert result.pages_generated == 2  # Two-sided card
        assert result.file_size_bytes == 15000

        # Verify document was built
        mock_doc.build.assert_called_once()

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    @patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate")
    def test_pdf_generation_failure(self, mock_doc_class):
        """Test PDF generation failure handling."""
        # Setup mock to raise exception
        mock_doc = Mock()
        mock_doc.build.side_effect = Exception("ReportLab error")
        mock_doc_class.return_value = mock_doc

        output_path = Path(self.temp_dir) / "failed_recipe.pdf"

        generator = PDFCardGenerator(self.config)
        result = generator.generate_card(self.test_recipe, output_path)

        assert result.success is False
        assert "ReportLab error" in result.error

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    @patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate")
    def test_different_card_layouts(self, mock_doc_class):
        """Test generation with different card layouts."""
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc
        output_path = Path(self.temp_dir) / "layout_test.pdf"

        layouts_to_test = [
            (CardLayout.TWO_SIDED, 2),
            (CardLayout.SINGLE_SIDED, 1),
            (CardLayout.INGREDIENTS_ONLY, 1),
            (CardLayout.INSTRUCTIONS_ONLY, 1),
        ]

        for layout, expected_pages in layouts_to_test:
            cfg_dict = {"card_layout": layout}
            generator = PDFCardGenerator(self.config, cfg_dict)

            with patch.object(Path, "mkdir"), \
                 patch.object(Path, "stat") as mock_stat, \
                 patch.object(Path, "is_dir", return_value=True):
                from types import SimpleNamespace

                mock_stat.return_value = SimpleNamespace(st_size=10000)
                result = generator.generate_card(self.test_recipe, output_path)

            assert result.success is True
            assert result.pages_generated == expected_pages

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_output_directory_creation(self):
        """Test that output directories are created if they don't exist."""
        nested_path = Path(self.temp_dir) / "deep" / "nested" / "path" / "recipe.pdf"

        with patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc

            generator = PDFCardGenerator(self.config)

            with patch.object(Path, "stat") as mock_stat:
                from types import SimpleNamespace

                mock_stat.return_value = SimpleNamespace(st_size=5000)
                result = generator.generate_card(self.test_recipe, nested_path)

        assert result.success is True
        # Directory should have been created
        assert nested_path.parent.exists()


class TestPDFCardGeneratorContentBuilding:
    """Test suite for PDF content building methods."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = DisplayConfig(show_weights=True, show_purpose=True)
        self.test_recipe = Recipe(
            title="Content Test Recipe",
            category="Main",
            description="Recipe for testing content building",
            servings=6,
            ingredients=[Ingredient(ingredient="pasta", amount=1.0, unit="lbs", weight_grams=454, purpose="base")],
            instructions=["Boil water", "Cook pasta", "Serve hot"],
            notes=["Use sea salt"],
        )

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_header_section_building(self):
        """Test header section content building."""
        generator = PDFCardGenerator(self.config)

        # Mock the required ReportLab components
        with (
            patch("recipe_fmt.generators.pdf_generator.Paragraph"),
            patch("recipe_fmt.generators.pdf_generator.Spacer"),
        ):
            header_content = generator._build_header_section(self.test_recipe)

        # Should return a list of flowables
        assert isinstance(header_content, list)
        assert len(header_content) > 0

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_ingredients_section_building(self):
        """Test ingredients section content building."""
        generator = PDFCardGenerator(self.config)

        with (
            patch("recipe_fmt.generators.pdf_generator.Paragraph"),
            patch("recipe_fmt.generators.pdf_generator.Table"),
        ):
            ingredients_content = generator._build_ingredients_section(self.test_recipe)

        assert isinstance(ingredients_content, list)
        assert len(ingredients_content) > 0

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_instructions_section_building(self):
        """Test instructions section content building."""
        generator = PDFCardGenerator(self.config)

        with patch("recipe_fmt.generators.pdf_generator.Paragraph"):
            instructions_content = generator._build_instructions_section(self.test_recipe)

        assert isinstance(instructions_content, list)
        assert len(instructions_content) > 0

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_notes_section_building(self):
        """Test notes section content building."""
        generator = PDFCardGenerator(self.config)

        with patch("recipe_fmt.generators.pdf_generator.Paragraph"):
            notes_content = generator._build_notes_section(self.test_recipe)

        assert isinstance(notes_content, list)
        assert len(notes_content) > 0

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_category_banner_building(self):
        """Test category banner content building."""
        generator = PDFCardGenerator(self.config)

        with (
            patch("recipe_fmt.generators.pdf_generator.Table"),
            patch("recipe_fmt.generators.pdf_generator.Paragraph"),
        ):
            banner_content = generator._build_category_banner(self.test_recipe)

        assert isinstance(banner_content, list)
        assert len(banner_content) > 0


class TestPDFCardGeneratorConfiguration:
    """Test suite for configuration management."""

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_config_defaults_application(self):
        """Test that configuration defaults are applied correctly."""
        config = DisplayConfig()
        generator = PDFCardGenerator(config, {})

        cfg = generator.get_cfg()
        assert cfg["card_layout"] == CardLayout.TWO_SIDED
        assert cfg["print_margins"] == 0.25
        assert cfg["ingredient_columns"] == 3
        assert cfg["show_category_banner"] is True
        assert cfg["quality"] == "high"
        assert cfg["compress_pdf"] is True

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_generation_statistics(self):
        """Test generation statistics reporting."""
        config = DisplayConfig()
        generator = PDFCardGenerator(config)

        stats = generator.get_generation_stats()

        assert "generator_config" in stats
        assert "card_specs" in stats
        assert "supported_layouts" in stats
        assert "category_colors" in stats

        # Check card specifications
        card_specs = stats["card_specs"]
        assert "size_inches" in card_specs
        assert "content_area_inches" in card_specs
        assert "margins_inches" in card_specs

        # Check supported layouts
        layouts = stats["supported_layouts"]
        expected_layouts = ["two_sided", "single_sided", "ingredients_only", "instructions_only"]
        assert all(layout in layouts for layout in expected_layouts)

        # Check category colors
        colors = stats["category_colors"]
        assert "Breakfast" in colors
        assert "Dessert" in colors


class TestPDFCardGeneratorEdgeCases:
    """Test suite for edge cases and error conditions."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = DisplayConfig()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_recipe_with_no_ingredients(self):
        """Test generation with recipe containing no ingredients."""
        empty_recipe = Recipe(
            title="Empty Recipe",
            category="Other",
            servings=1,
            ingredients=[Ingredient(ingredient="placeholder", amount=1, unit="item", weight_grams=1)],
            instructions=["Do nothing"],
        )

        with patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc

            generator = PDFCardGenerator(self.config)
            output_path = Path(self.temp_dir) / "empty.pdf"

            with patch.object(Path, "mkdir"), \
                 patch.object(Path, "stat") as mock_stat, \
                 patch.object(Path, "is_dir", return_value=True):
                from types import SimpleNamespace

                mock_stat.return_value = SimpleNamespace(st_size=1000)
                result = generator.generate_card(empty_recipe, output_path)

        # Should handle gracefully
        assert result.success is True

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_recipe_with_very_long_title(self):
        """Test generation with very long recipe title."""
        long_title_recipe = Recipe(
            title="This is a very long recipe title that tests PDF layout gracefully without causing issues",
            category="Other",
            servings=1,
            ingredients=[Ingredient(ingredient="test", amount=1, unit="cup")],
            instructions=["Test instruction"],
        )

        with patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc

            generator = PDFCardGenerator(self.config)
            output_path = Path(self.temp_dir) / "long_title.pdf"

            with patch.object(Path, "mkdir"), \
                 patch.object(Path, "stat") as mock_stat, \
                 patch.object(Path, "is_dir", return_value=True):
                from types import SimpleNamespace

                mock_stat.return_value = SimpleNamespace(st_size=2000)
                result = generator.generate_card(long_title_recipe, output_path)

        assert result.success is True

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_recipe_with_unicode_characters(self):
        """Test generation with unicode characters in recipe."""
        unicode_recipe = Recipe(
            title="Café au Lait ☕",
            category="Breakfast",
            description="Délicieux café français",
            servings=2,
            ingredients=[Ingredient(ingredient="café moulu", amount=2.0, unit="cuillères à soupe", weight_grams=20)],
            instructions=["Chauffer l'eau à 90°C"],
        )

        with patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc

            generator = PDFCardGenerator(self.config)
            output_path = Path(self.temp_dir) / "unicode.pdf"

            with patch.object(Path, "mkdir"), \
                 patch.object(Path, "stat") as mock_stat, \
                 patch.object(Path, "is_dir", return_value=True):
                from types import SimpleNamespace

                mock_stat.return_value = SimpleNamespace(st_size=3000)
                result = generator.generate_card(unicode_recipe, output_path)

        assert result.success is True

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_recipe_with_many_ingredients(self):
        """Test generation with recipe containing many ingredients."""
        many_ingredients = [
            Ingredient(
                ingredient=f"ingredient_{i}",
                amount=1.0,
                unit="cup",
                weight_grams=100,
                purpose="test",
            )
            for i in range(50)
        ]

        large_recipe = Recipe(
            title="Recipe with Many Ingredients",
            category="Other",
            servings=10,
            ingredients=many_ingredients,
            instructions=["Mix all ingredients", "Cook thoroughly"],
        )

        with patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc

            generator = PDFCardGenerator(self.config)
            output_path = Path(self.temp_dir) / "many_ingredients.pdf"

            with patch.object(Path, "mkdir"), \
                 patch.object(Path, "stat") as mock_stat, \
                 patch.object(Path, "is_dir", return_value=True):
                from types import SimpleNamespace

                mock_stat.return_value = SimpleNamespace(st_size=20000)
                result = generator.generate_card(large_recipe, output_path)

        assert result.success is True


class TestPDFCardGeneratorFactoryFunction:
    """Test suite for factory function."""

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_create_generator_with_defaults(self):
        """Test factory function with default parameters."""
        generator = create_generator()

        assert isinstance(generator, PDFCardGenerator)
        assert generator.config.show_weights is True
        assert generator.cfg_dict["card_layout"] == CardLayout.TWO_SIDED

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_create_generator_with_custom_params(self):
        """Test factory function with custom parameters."""
        generator = create_generator(show_weights=False, layout=CardLayout.SINGLE_SIDED)

        assert isinstance(generator, PDFCardGenerator)
        assert generator.config.show_weights is False
        assert generator.cfg_dict["card_layout"] == CardLayout.SINGLE_SIDED


class TestPDFCardGeneratorIntegration:
    """Test suite for integration scenarios."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = DisplayConfig(show_weights=True, show_purpose=True)

        # Create comprehensive test recipe
        self.comprehensive_recipe = Recipe(
            title="Comprehensive Test Recipe",
            category="Main",
            description="A recipe with all possible fields for testing",
            servings=8,
            prep_time="20 minutes",
            cook_time="45 minutes",
            ingredients=[
                Ingredient(
                    ingredient="chicken breast",
                    amount=2.0,
                    unit="lbs",
                    weight_grams=908,
                    purpose="protein",
                ),
                Ingredient(ingredient="olive oil", amount=3.0, unit="TBL", weight_grams=40, purpose="fat"),
                Ingredient(ingredient="salt", amount=1.0, unit="tsp", weight_grams=6, purpose="seasoning"),
            ],
            instructions=[
                "Preheat oven to 375°F",
                "Season chicken with salt and pepper",
                "Heat olive oil in oven-safe skillet",
                "Sear chicken breast until golden brown on both sides",
                "Transfer skillet to oven and bake for 25-30 minutes",
                "Let rest for 5 minutes before serving",
            ],
            notes=[
                "Internal temperature should reach 165°F",
                "Can be served with various side dishes",
                "Leftovers keep in refrigerator for 3 days",
            ],
        )

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    @patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate")
    def test_comprehensive_recipe_generation(self, mock_doc_class):
        """Test generation with a comprehensive recipe containing all fields."""
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc

        generator = PDFCardGenerator(self.config)
        output_path = Path(self.temp_dir) / "comprehensive.pdf"

        with patch.object(Path, "mkdir"), \
             patch.object(Path, "stat") as mock_stat, \
             patch.object(Path, "is_dir", return_value=True):
            from types import SimpleNamespace

            mock_stat.return_value = SimpleNamespace(st_size=25000)
            result = generator.generate_card(self.comprehensive_recipe, output_path)

        assert result.success is True
        assert result.output_path == output_path
        assert result.pages_generated == 2
        assert result.file_size_bytes == 25000

        # Verify document building was called
        mock_doc.build.assert_called_once()

        # The story passed to build should be a list
        build_args = mock_doc.build.call_args[0]
        story = build_args[0]
        assert isinstance(story, list)
        assert len(story) > 0

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    def test_all_layout_combinations(self):
        """Test all layout combinations work correctly."""
        layouts = [
            CardLayout.TWO_SIDED,
            CardLayout.SINGLE_SIDED,
            CardLayout.INGREDIENTS_ONLY,
            CardLayout.INSTRUCTIONS_ONLY,
        ]

        for layout in layouts:
            with patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate") as mock_doc_class:
                mock_doc = Mock()
                mock_doc_class.return_value = mock_doc

                cfg_dict = {"card_layout": layout}
                generator = PDFCardGenerator(self.config, cfg_dict)
                output_path = Path(self.temp_dir) / f"{layout.value}.pdf"

                with patch.object(Path, "mkdir"), \
                     patch.object(Path, "stat") as mock_stat, \
                     patch.object(Path, "is_dir", return_value=True):
                    from types import SimpleNamespace

                    mock_stat.return_value = SimpleNamespace(st_size=10000)
                    result = generator.generate_card(self.comprehensive_recipe, output_path)

                assert result.success is True, f"Failed for layout: {layout.value}"
                mock_doc.build.assert_called_once()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
