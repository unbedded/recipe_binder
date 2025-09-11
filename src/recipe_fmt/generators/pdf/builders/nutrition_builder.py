"""Simple nutrition builder extracted from PDFCardGenerator.

This class contains the logic previously in _build_nutrition_section() method,
including nutrition data formatting and table generation.
"""

from typing import Any

try:
    from reportlab.lib.colors import Color, black
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ....models.recipe import Recipe
from ....utils.logging_setup import get_logger


class NutritionBuilder:
    """Builds nutrition sections for PDF recipe cards.

    Extracted from PDFCardGenerator._build_nutrition_section().
    Simple class with no interfaces - just organized code.
    """

    def __init__(self, styles: dict[str, Any], content_width: float):
        """Initialize nutrition builder with required dependencies.

        Args:
            styles: ReportLab styles dictionary
            content_width: Available content width for calculations
        """
        self.styles = styles
        self.content_width = content_width
        self.logger = get_logger(__name__)

    def build_nutrition_section(self, recipe: Recipe, max_width: float | None = None) -> list[Any]:
        """Build nutrition facts section for display.

        This is the exact logic from _build_nutrition_section().

        Args:
            recipe: Recipe to generate nutrition for
            max_width: Optional maximum width constraint

        Returns:
            List of ReportLab flowables
        """
        story = []

        # Get nutrition data from properly parsed Recipe model
        nutrition_data = self._extract_nutrition_data(recipe)

        # Nutrition Facts title
        nutrition_style = self._create_nutrition_title_style()
        nutrition_title = Paragraph("NUTRITION", nutrition_style)
        story.append(nutrition_title)

        # Build nutrition table
        nutrition_rows = self._build_nutrition_table_data(nutrition_data)

        # Calculate column widths
        width = max_width or (self.content_width * 0.4)
        col_widths = [width * 0.7, width * 0.3]

        nutrition_table = Table(nutrition_rows, colWidths=col_widths)
        nutrition_table.setStyle(TableStyle(self._build_nutrition_table_style()))

        story.append(nutrition_table)
        return story

    def build_simple_nutrition_text(self, recipe: Recipe) -> Any:
        """Build simple nutrition facts as right-justified text column.

        Args:
            recipe: Recipe to generate nutrition for

        Returns:
            Paragraph with nutrition facts
        """
        # Get nutrition data from properly parsed Recipe model
        nutrition_data = self._extract_nutrition_data(recipe)

        # Build simple text format
        lines = [
            "<b>NUTRITION</b>",
            "<i>Per Serving</i>",
            "",
            f"Calories: {nutrition_data['calories']}",
            f"Protein: {nutrition_data['protein_g']}g",
            f"Carbs: {nutrition_data['carbs_g']}g",
            f"Fat: {nutrition_data['fat_g']}g",
            f"Fiber: {nutrition_data['fiber_g']}g",
            f"Sodium: {nutrition_data['sodium_mg']}mg",
        ]

        nutrition_text = "<br/>".join(lines)

        # Create right-aligned paragraph
        nutrition_style = self._create_simple_nutrition_style()
        nutrition_paragraph = Paragraph(nutrition_text, nutrition_style)

        # Add logo at bottom and combine into single table cell
        return self._build_nutrition_with_logo(nutrition_paragraph)

    def _extract_nutrition_data(self, recipe: Recipe) -> dict[str, int]:
        """Extract nutrition data from recipe or provide fallback.

        Args:
            recipe: Recipe to extract nutrition from

        Returns:
            Dictionary with nutrition values
        """
        nutrition = getattr(recipe, "nutrition", None)
        if nutrition and hasattr(nutrition, "calories") and nutrition.calories:
            # Use real nutrition data from YAML
            return {
                "calories": nutrition.calories or 0,
                "protein_g": nutrition.protein_g or 0,
                "carbs_g": nutrition.carbs_g or 0,
                "fat_g": nutrition.fat_g or 0,
                "fiber_g": nutrition.fiber_g or 0,
                "sodium_mg": nutrition.sodium_mg or 0,
            }
        else:
            # Fallback sample data when no nutrition data available
            return {
                "calories": 245,
                "protein_g": 8,
                "carbs_g": 35,
                "fat_g": 9,
                "fiber_g": 2,
                "sodium_mg": 387,
            }

    def _build_nutrition_table_data(self, nutrition_data: dict[str, int]) -> list[list[str]]:
        """Build table data rows for nutrition table.

        Args:
            nutrition_data: Dictionary with nutrition values

        Returns:
            List of table rows
        """
        nutrition_rows = [["Per Serving", ""]]

        nutrition_map = {
            "calories": "Calories",
            "protein_g": "Protein",
            "carbs_g": "Total Carbs",
            "fat_g": "Total Fat",
            "fiber_g": "Dietary Fiber",
            "sodium_mg": "Sodium",
        }

        for key, label in nutrition_map.items():
            value = nutrition_data.get(key, 0)
            # All nutrition values are now integers - much simpler display logic
            if key == "sodium_mg":
                display_value = f"{value}mg" if isinstance(value, int | float) else str(value)
            elif "_g" in key:
                display_value = f"{value}g" if isinstance(value, int | float) else str(value)
            else:
                display_value = f"{value}" if isinstance(value, int | float) else str(value)

            nutrition_rows.append([label, display_value])

        return nutrition_rows

    def _create_nutrition_title_style(self) -> ParagraphStyle:
        """Create style for nutrition title.

        Returns:
            ParagraphStyle for nutrition title
        """
        return ParagraphStyle(
            "NutritionTitle",
            parent=self.styles["SectionHeader"],
            fontSize=12,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=4,
        )

    def _create_simple_nutrition_style(self) -> ParagraphStyle:
        """Create style for simple nutrition text.

        Returns:
            ParagraphStyle for simple nutrition text
        """
        return ParagraphStyle(
            "SimpleNutrition",
            parent=self.styles["Normal"],
            fontSize=9,
            alignment=TA_RIGHT,
            spaceAfter=2,
        )

    def _build_nutrition_table_style(self) -> list[Any]:
        """Build ReportLab table style commands for nutrition table.

        Returns:
            List of ReportLab table style commands
        """
        return [
            # Header row styling
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 0), (-1, 0), Color(0.9, 0.9, 0.9)),
            # Data rows styling
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),  # Labels left aligned
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),  # Values right aligned
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            # Borders and padding
            ("BOX", (0, 0), (-1, -1), 1, black),
            ("LINEBELOW", (0, 0), (-1, 0), 1, black),  # Line under header
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]

    def has_nutrition_data(self, recipe: Recipe) -> bool:
        """Check if recipe has real nutrition data.

        Args:
            recipe: Recipe to check

        Returns:
            True if recipe has nutrition data
        """
        nutrition = getattr(recipe, "nutrition", None)
        return bool(nutrition and hasattr(nutrition, "calories") and nutrition.calories)

    def estimate_table_width(self, max_width: float | None = None) -> float:
        """Estimate the width the nutrition table will require.

        Args:
            max_width: Optional maximum width constraint

        Returns:
            Estimated width in points
        """
        return max_width or (self.content_width * 0.4)

    def _build_logo_section(self) -> list[Any]:
        """Build logo section for bottom of nutrition column.

        Returns:
            List of ReportLab elements (Spacer and Image)
        """
        elements = []

        try:
            # Add small spacer before logo
            elements.append(Spacer(1, 0.1 * inch))

            # Create logo image - full width of nutrition column with proper aspect ratio
            logo_path = "docs/kinetic_labs_logo_tight_spacing.jpg"
            logo_width = self.content_width * 0.2  # Full width of nutrition column (20% of content)

            # Calculate height to maintain aspect ratio (original logo is ~3.2:1 width:height)
            original_aspect_ratio = 0.8 / 0.25  # 3.2:1 from original dimensions
            logo_height = logo_width / original_aspect_ratio

            logo_image = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo_image)

        except Exception:
            # If logo fails to load, continue without it (graceful fallback)
            pass

        return elements

    def _build_nutrition_with_logo(self, nutrition_paragraph: Paragraph) -> Table:
        """Build nutrition column with logo at bottom as single table.

        Args:
            nutrition_paragraph: The nutrition text paragraph

        Returns:
            Single Table containing nutrition and logo
        """
        # Create table data with nutrition at top and logo at bottom
        table_data = [[nutrition_paragraph]]

        # Add logo if available
        logo_elements = self._build_logo_section()
        if logo_elements:
            for element in logo_elements:
                table_data.append([element])

        # Create single-column table - full nutrition column width
        nutrition_column_width = self.content_width * 0.2  # 20% of content width
        nutrition_table = Table(table_data, colWidths=[nutrition_column_width])

        # Style the table with different alignment for nutrition vs logo
        style_commands = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, 0), "RIGHT"),  # Right-align nutrition text (first row)
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]

        # Center-align logo rows (if they exist)
        if len(table_data) > 1:
            logo_start_row = 1
            logo_end_row = len(table_data) - 1
            style_commands.append(("ALIGN", (0, logo_start_row), (0, logo_end_row), "CENTER"))

        nutrition_table.setStyle(TableStyle(style_commands))

        return nutrition_table
