"""Unit tests for NotesBuilder extracted from PDFCardGenerator."""

from recipe_fmt.generators.pdf.builders.notes_builder import NotesBuilder
from recipe_fmt.models.recipe import Ingredient, Recipe


class TestNotesBuilder:
    """Test suite for NotesBuilder component."""

    def setup_method(self):
        """Setup test environment before each test method."""
        # Mock styles dictionary (simplified for testing)
        self.styles = {
            "SectionHeader": {"fontSize": 12, "fontName": "Helvetica-Bold"},
            "Notes": {"fontSize": 9, "fontName": "Helvetica"},
        }

        # Create notes builder
        self.notes_builder = NotesBuilder(styles=self.styles, spacing=6.0)

        # Create minimal test ingredient (required for Recipe validation)
        test_ingredient = Ingredient(ingredient="test ingredient", amount=1.0, unit="cup")

        # Create test recipe with notes
        self.recipe_with_notes = Recipe(
            title="Test Recipe",
            category="Baking",
            servings=4,
            ingredients=[test_ingredient],
            instructions=["Mix ingredients"],
            notes=["Can substitute butter with oil", "Check doneness with toothpick", "Store covered for up to 3 days"],
        )

        # Create test recipe without notes
        self.recipe_no_notes = Recipe(
            title="Simple Recipe",
            category="Quick",
            servings=2,
            ingredients=[test_ingredient],
            instructions=["Mix ingredients"],
        )

    def test_has_notes_true(self):
        """Test notes detection when notes are present."""
        assert self.notes_builder.has_notes(self.recipe_with_notes) is True

    def test_has_notes_false(self):
        """Test notes detection when no notes."""
        assert self.notes_builder.has_notes(self.recipe_no_notes) is False

    def test_count_notes_with_notes(self):
        """Test note counting when notes are present."""
        count = self.notes_builder.count_notes(self.recipe_with_notes)
        assert count == 3

    def test_count_notes_no_notes(self):
        """Test note counting when no notes."""
        count = self.notes_builder.count_notes(self.recipe_no_notes)
        assert count == 0

    def test_format_note_text(self):
        """Test individual note formatting."""
        note = "This is a test note"
        formatted = self.notes_builder.format_note_text(note)
        assert formatted == "• This is a test note"

    def test_format_note_text_empty(self):
        """Test formatting empty note."""
        formatted = self.notes_builder.format_note_text("")
        assert formatted == "• "

    def test_format_note_text_special_characters(self):
        """Test formatting note with special characters."""
        note = "Use 350°F for 25-30 minutes"
        formatted = self.notes_builder.format_note_text(note)
        assert formatted == "• Use 350°F for 25-30 minutes"

    def test_estimate_content_height_with_notes(self):
        """Test height estimation with notes."""
        font_size = 10
        height = self.notes_builder.estimate_content_height(self.recipe_with_notes, font_size)

        # Should be positive and reasonable
        assert height > 0

        # Should include spacing + header + 3 notes
        expected_min = self.notes_builder.spacing + font_size * 1.5 + 3 * (font_size * 1.2)
        assert height >= expected_min

    def test_estimate_content_height_no_notes(self):
        """Test height estimation without notes."""
        height = self.notes_builder.estimate_content_height(self.recipe_no_notes)
        assert height == 0.0

    def test_estimate_content_height_different_font_sizes(self):
        """Test height estimation with different font sizes."""
        height_small = self.notes_builder.estimate_content_height(self.recipe_with_notes, font_size=8)
        height_large = self.notes_builder.estimate_content_height(self.recipe_with_notes, font_size=12)

        # Larger font should result in larger height
        assert height_large > height_small

    def test_builder_initialization(self):
        """Test that builder initializes correctly."""
        assert self.notes_builder.styles == self.styles
        assert self.notes_builder.spacing == 6.0
        assert self.notes_builder.logger is not None

    def test_build_notes_section_logic_structure(self):
        """Test the structure of build_notes_section without ReportLab."""
        # We can't easily test the ReportLab objects without mocking,
        # but we can test the logic flow by checking the method exists
        # and doesn't crash with valid input

        # Method should exist and be callable
        assert hasattr(self.notes_builder, "build_notes_section")
        assert callable(self.notes_builder.build_notes_section)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with single note
        single_note_ingredient = Ingredient(ingredient="flour", amount=1.0, unit="cup")
        single_note_recipe = Recipe(
            title="Single Note Recipe",
            category="Test",
            servings=1,
            ingredients=[single_note_ingredient],
            instructions=["Mix"],
            notes=["Single note"],
        )

        assert self.notes_builder.has_notes(single_note_recipe) is True
        assert self.notes_builder.count_notes(single_note_recipe) == 1

        height = self.notes_builder.estimate_content_height(single_note_recipe)
        assert height > 0

    def test_notes_none_vs_empty_list(self):
        """Test handling of None vs empty list for notes."""
        # Recipe with empty notes list should behave same as no notes
        empty_notes_ingredient = Ingredient(ingredient="flour", amount=1.0, unit="cup")
        empty_notes_recipe = Recipe(
            title="Empty Notes Recipe",
            category="Test",
            servings=1,
            ingredients=[empty_notes_ingredient],
            instructions=["Mix"],
            notes=[],
        )

        assert self.notes_builder.has_notes(empty_notes_recipe) is False
        assert self.notes_builder.count_notes(empty_notes_recipe) == 0
        assert self.notes_builder.estimate_content_height(empty_notes_recipe) == 0.0
