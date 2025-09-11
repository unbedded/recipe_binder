"""Unit tests for InstructionsBuilder extracted from PDFCardGenerator."""

from recipe_fmt.generators.pdf.builders.instructions_builder import InstructionsBuilder
from recipe_fmt.models.recipe import Ingredient, Recipe


class TestInstructionsBuilder:
    """Test suite for InstructionsBuilder component."""

    def setup_method(self):
        """Setup test environment before each test method."""
        # Mock styles dictionary (simplified for testing)
        self.styles = {
            "Instruction": {"fontSize": 10, "fontName": "Helvetica"},
            "Notes": {"fontSize": 9, "fontName": "Helvetica-Oblique"},
        }

        # Create instructions builder
        self.instructions_builder = InstructionsBuilder(
            styles=self.styles, spacing=6.0, default_instruction_font=10, min_font_size=5
        )

        # Create minimal test ingredient (required for Recipe validation)
        test_ingredient = Ingredient(ingredient="test ingredient", amount=1.0, unit="cup")

        # Create test recipe with instructions and notes
        self.test_recipe = Recipe(
            title="Test Recipe",
            category="Baking",
            servings=4,
            ingredients=[test_ingredient],
            instructions=[
                "Preheat oven to 350°F",
                "Mix dry ingredients in large bowl",
                "Combine wet ingredients separately",
                "Fold wet ingredients into dry ingredients",
                "Bake for 25-30 minutes",
            ],
            notes=["Can substitute butter with oil", "Check doneness with toothpick"],
        )

        # Create recipe without notes
        self.recipe_no_notes = Recipe(
            title="Simple Recipe",
            category="Quick",
            servings=2,
            ingredients=[test_ingredient],
            instructions=["Mix ingredients", "Cook until done"],
        )

    def test_build_instructions_text(self):
        """Test numbered instruction text building."""
        instructions = ["First step", "Second step", "Third step"]
        result = self.instructions_builder._build_instructions_text(instructions)

        expected = ["1. First step", "2. Second step", "3. Third step"]
        assert result == expected

    def test_build_instructions_text_empty(self):
        """Test instruction text building with empty list."""
        result = self.instructions_builder._build_instructions_text([])
        assert result == []

    def test_build_notes_text(self):
        """Test bulleted notes text building."""
        notes = ["First note", "Second note", "Third note"]
        result = self.instructions_builder._build_notes_text(notes)

        expected = ["• First note", "• Second note", "• Third note"]
        assert result == expected

    def test_build_notes_text_empty(self):
        """Test notes text building with empty list."""
        result = self.instructions_builder._build_notes_text([])
        assert result == []

    def test_count_instructions_with_notes(self):
        """Test instruction counting with notes."""
        count = self.instructions_builder.count_instructions(self.test_recipe)
        expected = len(self.test_recipe.instructions) + len(self.test_recipe.notes)
        assert count == expected  # 5 instructions + 2 notes = 7

    def test_count_instructions_without_notes(self):
        """Test instruction counting without notes."""
        count = self.instructions_builder.count_instructions(self.recipe_no_notes)
        expected = len(self.recipe_no_notes.instructions)
        assert count == expected  # 2 instructions + 0 notes = 2

    def test_estimate_content_height(self):
        """Test content height estimation."""
        font_size = 10
        height = self.instructions_builder.estimate_content_height(self.test_recipe, font_size)

        # Should be positive and reasonable
        assert height > 0

        # Rough calculation: 7 items * (10 * 1.5 + 1.5) = 7 * 16.5 = 115.5 + spacing
        expected_min = 7 * (font_size * 1.5 + 1.5)
        assert height >= expected_min

    def test_estimate_content_height_with_notes_spacing(self):
        """Test height estimation includes notes separator spacing."""
        font_size = 10
        height_with_notes = self.instructions_builder.estimate_content_height(self.test_recipe, font_size)
        height_without_notes = self.instructions_builder.estimate_content_height(self.recipe_no_notes, font_size)

        # Height with notes should include extra spacing
        assert height_with_notes > height_without_notes

    def test_should_scale_font_no_scaling_needed(self):
        """Test font scaling when content fits."""
        available_height = 200.0  # Large available space
        base_font_size = 10

        should_scale, new_size = self.instructions_builder.should_scale_font(
            self.recipe_no_notes, available_height, base_font_size
        )

        assert should_scale is False
        assert new_size == base_font_size

    def test_should_scale_font_scaling_needed(self):
        """Test font scaling when content doesn't fit."""
        available_height = 50.0  # Limited space
        base_font_size = 10

        should_scale, new_size = self.instructions_builder.should_scale_font(
            self.test_recipe, available_height, base_font_size
        )

        assert should_scale is True
        assert new_size < base_font_size
        assert new_size >= self.instructions_builder.min_font_size

    def test_should_scale_font_minimum_size_limit(self):
        """Test font scaling respects minimum size."""
        available_height = 5.0  # Very limited space
        base_font_size = 10

        should_scale, new_size = self.instructions_builder.should_scale_font(
            self.test_recipe, available_height, base_font_size
        )

        assert should_scale is True
        assert new_size == self.instructions_builder.min_font_size

    def test_builder_initialization(self):
        """Test that builder initializes correctly."""
        assert self.instructions_builder.styles == self.styles
        assert self.instructions_builder.spacing == 6.0
        assert self.instructions_builder.default_instruction_font == 10
        assert self.instructions_builder.min_font_size == 5
        assert self.instructions_builder.logger is not None

    def test_font_size_calculations(self):
        """Test various font size edge cases."""
        # Test with different available heights
        test_cases = [
            (1000.0, 10, False),  # Plenty of space, no scaling
            (100.0, 10, True),  # Some scaling needed
            (10.0, 10, True),  # Heavy scaling needed
        ]

        for available_height, base_font, should_scale_expected in test_cases:
            should_scale, new_size = self.instructions_builder.should_scale_font(
                self.test_recipe, available_height, base_font
            )
            assert should_scale == should_scale_expected
            assert new_size >= self.instructions_builder.min_font_size
            assert new_size <= base_font

    def test_notes_font_size_calculation(self):
        """Test notes font size is properly calculated."""
        # Test the logic used in build_instructions_section
        instruction_font = 10
        notes_font = max(instruction_font - 1, self.instructions_builder.min_font_size)

        assert notes_font == 9  # 10 - 1 = 9

        # Test edge case where instruction font is at minimum
        instruction_font = 5
        notes_font = max(instruction_font - 1, self.instructions_builder.min_font_size)

        assert notes_font == 5  # Can't go below minimum
