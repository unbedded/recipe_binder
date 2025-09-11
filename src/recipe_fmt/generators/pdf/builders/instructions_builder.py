"""Simple instructions builder extracted from PDFCardGenerator.

This class contains the logic previously in _build_instructions_section() method,
including instructions formatting and notes integration.
"""

from typing import Any

try:
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Spacer

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ....models.recipe import Recipe
from ....utils.logging_setup import get_logger


class InstructionsBuilder:
    """Builds instructions sections for PDF recipe cards.

    Extracted from PDFCardGenerator._build_instructions_section().
    Simple class with no interfaces - just organized code.
    """

    def __init__(
        self, styles: dict[str, Any], spacing: float, default_instruction_font: int = 10, min_font_size: int = 5
    ):
        """Initialize instructions builder with required dependencies.

        Args:
            styles: ReportLab styles dictionary
            spacing: Default spacing value
            default_instruction_font: Default font size for instructions
            min_font_size: Minimum font size allowed
        """
        self.styles = styles
        self.spacing = spacing
        self.default_instruction_font = default_instruction_font
        self.min_font_size = min_font_size
        self.logger = get_logger(__name__)

    def build_instructions_section(self, recipe: Recipe, max_width: float | None = None) -> list[Any]:
        """Build compact instructions section without heading, with integrated notes.

        This is the exact logic from _build_instructions_section().

        Args:
            recipe: Recipe to generate instructions for
            max_width: Optional maximum width constraint

        Returns:
            List of ReportLab flowables
        """
        story = []

        # No section header for compact format

        # Build all instruction text
        all_instructions_text = self._build_instructions_text(recipe.instructions)

        # Add notes text if present
        notes_text = self._build_notes_text(recipe.notes) if recipe.notes else []

        # Calculate font sizes
        final_font_size = self.default_instruction_font
        notes_font_size = max(final_font_size - 1, self.min_font_size)

        self.logger.debug("Building instructions with font size %dpt", final_font_size)

        # Create adaptive styles
        adaptive_instruction_style = self._create_instruction_style(final_font_size)
        adaptive_notes_style = self._create_notes_style(notes_font_size)

        # Log style creation
        self.logger.info(
            "🔧 Creating adaptive styles: instruction=%dpt, notes=%dpt",
            final_font_size,
            notes_font_size,
        )

        # Add instructions with adaptive font
        for instruction_text in all_instructions_text:
            story.append(Paragraph(instruction_text, adaptive_instruction_style))

        # Add notes as italic text at end of instructions
        if recipe.notes:
            story.append(Spacer(1, self.spacing / 4))  # Minimal spacer
            for note_text in notes_text:
                story.append(Paragraph(note_text, adaptive_notes_style))

        # Log font adjustment if changed
        if final_font_size != self.default_instruction_font:
            self.logger.info(
                "Instructions font adjusted from %d to %d to fit page",
                self.default_instruction_font,
                final_font_size,
            )

        return story

    def _build_instructions_text(self, instructions: list[str]) -> list[str]:
        """Build numbered instruction text list.

        Args:
            instructions: List of instruction strings

        Returns:
            List of numbered instruction strings
        """
        all_instructions_text = []
        for i, instruction in enumerate(instructions, 1):
            instruction_text = f"{i}. {instruction}"
            all_instructions_text.append(instruction_text)
        return all_instructions_text

    def _build_notes_text(self, notes: list[str]) -> list[str]:
        """Build bulleted notes text list.

        Args:
            notes: List of note strings

        Returns:
            List of bulleted note strings
        """
        notes_text = []
        for note in notes:
            notes_text.append(f"• {note}")
        return notes_text

    def _create_instruction_style(self, font_size: int) -> ParagraphStyle:
        """Create adaptive instruction style.

        Args:
            font_size: Font size to use

        Returns:
            ParagraphStyle for instructions
        """
        return ParagraphStyle(
            "AdaptiveInstruction",
            parent=self.styles["Instruction"],
            fontSize=font_size,
            spaceAfter=1.5,  # Reduced spacing
        )

    def _create_notes_style(self, font_size: int) -> ParagraphStyle:
        """Create adaptive notes style.

        Args:
            font_size: Font size to use

        Returns:
            ParagraphStyle for notes
        """
        return ParagraphStyle(
            "AdaptiveNotes",
            parent=self.styles["Notes"],
            fontSize=font_size,
            spaceAfter=max(0.5, font_size * 0.1),  # Even smaller spacing for notes
        )

    def count_instructions(self, recipe: Recipe) -> int:
        """Count total number of instructions and notes.

        Args:
            recipe: Recipe to count

        Returns:
            Total count of instructions plus notes
        """
        instruction_count = len(recipe.instructions)
        notes_count = len(recipe.notes) if recipe.notes else 0
        return instruction_count + notes_count

    def estimate_content_height(self, recipe: Recipe, font_size: int) -> float:
        """Estimate the height required for instructions content.

        Args:
            recipe: Recipe to estimate for
            font_size: Font size to use for estimation

        Returns:
            Estimated height in points
        """
        total_items = self.count_instructions(recipe)

        # Rough estimation: font_size * 1.5 (line height) * number of items + spacing
        line_height = font_size * 1.5
        spacing_between = 1.5  # spaceAfter value

        estimated_height = total_items * (line_height + spacing_between)

        # Add extra space for notes separator if notes exist
        if recipe.notes:
            estimated_height += self.spacing / 4

        return estimated_height

    def should_scale_font(self, recipe: Recipe, available_height: float, base_font_size: int) -> tuple[bool, int]:
        """Determine if font should be scaled and calculate new size.

        Args:
            recipe: Recipe to check
            available_height: Available space in points
            base_font_size: Base font size to start with

        Returns:
            Tuple of (should_scale, new_font_size)
        """
        estimated_height = self.estimate_content_height(recipe, base_font_size)

        if estimated_height <= available_height:
            return False, base_font_size

        # Calculate scale factor needed
        scale_factor = available_height / estimated_height
        new_font_size = max(int(base_font_size * scale_factor), self.min_font_size)

        return True, new_font_size
