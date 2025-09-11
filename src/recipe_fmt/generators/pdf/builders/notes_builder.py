"""Simple notes builder extracted from PDFCardGenerator.

This class contains the logic previously in _build_notes_section() method,
including notes formatting and section generation.
"""

from typing import Any

try:
    from reportlab.platypus import Paragraph, Spacer

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ....models.recipe import Recipe
from ....utils.logging_setup import get_logger


class NotesBuilder:
    """Builds notes sections for PDF recipe cards.

    Extracted from PDFCardGenerator._build_notes_section().
    Simple class with no interfaces - just organized code.
    """

    def __init__(self, styles: dict[str, Any], spacing: float):
        """Initialize notes builder with required dependencies.

        Args:
            styles: ReportLab styles dictionary
            spacing: Default spacing value
        """
        self.styles = styles
        self.spacing = spacing
        self.logger = get_logger(__name__)

    def build_notes_section(self, recipe: Recipe) -> list[Any]:
        """Build notes section.

        This is the exact logic from _build_notes_section().

        Args:
            recipe: Recipe to generate notes for

        Returns:
            List of ReportLab flowables
        """
        story = []

        if recipe.notes:
            # Section header
            story.append(Spacer(1, self.spacing))
            story.append(Paragraph("NOTES", self.styles["SectionHeader"]))

            # Add notes
            for note in recipe.notes:
                story.append(Paragraph(f"• {note}", self.styles["Notes"]))

        return story

    def has_notes(self, recipe: Recipe) -> bool:
        """Check if recipe has notes.

        Args:
            recipe: Recipe to check

        Returns:
            True if recipe has notes
        """
        return bool(recipe.notes)

    def count_notes(self, recipe: Recipe) -> int:
        """Count number of notes in recipe.

        Args:
            recipe: Recipe to count notes for

        Returns:
            Number of notes
        """
        return len(recipe.notes) if recipe.notes else 0

    def format_note_text(self, note: str) -> str:
        """Format a single note with bullet.

        Args:
            note: Note text to format

        Returns:
            Formatted note text with bullet
        """
        return f"• {note}"

    def estimate_content_height(self, recipe: Recipe, font_size: int = 10) -> float:
        """Estimate the height required for notes content.

        Args:
            recipe: Recipe to estimate for
            font_size: Font size to use for estimation

        Returns:
            Estimated height in points
        """
        if not recipe.notes:
            return 0.0

        # Rough estimation: spacing + header + notes
        header_height = font_size * 1.5  # Section header height
        note_count = len(recipe.notes)
        note_height = note_count * (font_size * 1.2)  # Line height per note

        return self.spacing + header_height + note_height
