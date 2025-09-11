"""Simple header builder extracted from PDFCardGenerator.

This class contains the logic previously in _build_header_section(),
_build_category_banner(), and _build_metadata_section() methods.
"""

from typing import Any

try:
    from reportlab.lib.colors import Color
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ....models.recipe import Recipe
from ....utils.logging_setup import get_logger


class HeaderBuilder:
    """Builds header sections for PDF recipe cards.

    Extracted from PDFCardGenerator._build_header_section() and related methods.
    Simple class with no interfaces - just organized code.
    """

    def __init__(self, styles: dict[str, Any], spacing: float, cfg_dict: dict[str, Any]):
        """Initialize header builder with required dependencies.

        Args:
            styles: ReportLab styles dictionary
            spacing: Default spacing value
            cfg_dict: Configuration dictionary
        """
        self.styles = styles
        self.spacing = spacing
        self.cfg_dict = cfg_dict
        self.logger = get_logger(__name__)

    def build_header_section(self, recipe: Recipe) -> list[Any]:
        """Build header section with title and category banner.

        This is the exact logic from _build_header_section().

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []

        # Category banner
        if self.cfg_dict.get("show_category_banner", True):
            story.extend(self.build_category_banner(recipe))

        # Recipe title
        title = Paragraph(recipe.title, self.styles["RecipeTitle"])
        story.append(title)

        # Recipe metadata
        if recipe.servings or recipe.prep_time or recipe.cook_time:
            story.extend(self.build_metadata_section(recipe))

        story.append(Spacer(1, self.spacing))

        return story

    def build_category_banner(self, recipe: Recipe, height: float | None = None) -> list[Any]:
        """Build category color banner.

        This is the exact logic from _build_category_banner().

        Args:
            recipe: Recipe to generate banner for
            height: Optional custom height

        Returns:
            List of ReportLab flowables
        """
        story = []

        banner_height = height or (0.3 * inch)  # Default banner height
        category_color = self._get_category_color(recipe.category)
        category_icon = self._get_category_icon(recipe.category)

        # Create colored banner with icon
        banner_text = f"{category_icon} {recipe.category.upper()}"
        banner_data = [[Paragraph(banner_text, self.styles["CategoryBanner"])]]

        # Calculate content width (approximation - in real usage passed from generator)
        content_width = 7.0 * inch  # Approximate content width

        banner_table = Table(banner_data, colWidths=[content_width], rowHeights=[banner_height])

        banner_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), category_color),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(banner_table)
        story.append(Spacer(1, self.spacing / 2))

        return story

    def build_metadata_section(self, recipe: Recipe) -> list[Any]:
        """Build recipe metadata section.

        This is the exact logic from _build_metadata_section().

        Args:
            recipe: Recipe to generate metadata for

        Returns:
            List of ReportLab flowables
        """
        story = []

        metadata_parts = []

        if recipe.servings:
            metadata_parts.append(f"Serves {recipe.servings}")

        if recipe.prep_time:
            metadata_parts.append(f"Prep: {recipe.prep_time}")

        if recipe.cook_time:
            metadata_parts.append(f"Cook: {recipe.cook_time}")

        if metadata_parts:
            metadata_text = " • ".join(metadata_parts)
            metadata_style = ParagraphStyle(
                name="Metadata",
                parent=self.styles["Normal"],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=Color(0.4, 0.4, 0.4),
                spaceAfter=4,
            )

            story.append(Paragraph(metadata_text, metadata_style))

        return story

    def _get_category_color(self, category: str) -> Color:
        """Get color for recipe category.

        Simplified version of CategoryColors.get_color().
        """
        # Color definitions matching the original
        colors = {
            "Meat": Color(0.8, 0.2, 0.2),  # Deep Red
            "Side": Color(0.0, 0.6, 0.6),  # Teal
            "Main": Color(0.2, 0.4, 0.8),  # Royal Blue
            "Soup": Color(0.9, 0.4, 0.0),  # Burnt Orange
            "Sauce": Color(0.4, 0.2, 0.6),  # Indigo Purple
            "Breakfast": Color(0.85, 0.55, 0.0),  # Amber/Gold
            "Salad": Color(0.0, 0.6, 0.2),  # Leaf Green
            "Baking": Color(0.45, 0.25, 0.1),  # Chocolate Brown
            "Dessert": Color(0.7, 0.2, 0.4),  # Raspberry
            "Other": Color(0.3, 0.3, 0.3),  # Dark Gray
        }
        return colors.get(category, colors["Other"])

    def _get_category_icon(self, category: str) -> str:
        """Get icon for recipe category.

        Simplified version of CategoryColors.get_icon().
        """
        icons = {
            "Meat": "🥩",
            "Side": "🥗",
            "Main": "🍽️",
            "Soup": "🍲",
            "Sauce": "🍯",
            "Breakfast": "🥞",
            "Salad": "🥬",
            "Baking": "🍞",
            "Dessert": "🍰",
            "Other": "📝",
        }
        return icons.get(category, icons["Other"])
