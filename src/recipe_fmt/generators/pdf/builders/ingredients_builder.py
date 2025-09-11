"""Simple ingredients builder extracted from PDFCardGenerator.

This class contains the logic previously in _build_ingredients_section() method,
including dynamic column width calculation and table generation.
"""

from typing import Any

try:
    from reportlab.lib.colors import white
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ....models.recipe import Recipe
from ....utils.logging_setup import get_logger


class IngredientsBuilder:
    """Builds ingredients sections for PDF recipe cards.

    Extracted from PDFCardGenerator._build_ingredients_section().
    Simple class with no interfaces - just organized code.
    """

    def __init__(
        self,
        cfg_dict: dict[str, Any],
        default_table_font: int = 9,
        min_font_size: int = 5,
        max_comfortable_ingredients: int = 8,
        extreme_recipe_threshold: int = 15,
    ):
        """Initialize ingredients builder with required dependencies.

        Args:
            cfg_dict: Configuration dictionary
            default_table_font: Default font size for tables
            min_font_size: Minimum font size allowed
            max_comfortable_ingredients: Threshold for comfortable ingredient count
            extreme_recipe_threshold: Threshold for extreme scaling measures
        """
        self.cfg_dict = cfg_dict
        self.default_table_font = default_table_font
        self.min_font_size = min_font_size
        self.max_comfortable_ingredients = max_comfortable_ingredients
        self.extreme_recipe_threshold = extreme_recipe_threshold
        self.logger = get_logger(__name__)

    def build_ingredients_section(self, recipe: Recipe, max_width: float | None = None) -> list[Any]:
        """Build ingredients section with optional weight display.

        This is the exact logic from _build_ingredients_section().

        Args:
            recipe: Recipe to generate ingredients for
            max_width: Optional maximum width constraint

        Returns:
            List of ReportLab flowables
        """
        story = []

        # No section header for compact format

        # Build compact ingredients table with dynamic width
        ingredients_data = []

        show_purpose = any(ing.purpose for ing in recipe.ingredients)

        # Calculate optimal column widths
        col_widths = self._calculate_column_widths(recipe.ingredients, show_purpose)
        actual_table_width = sum(col_widths)

        # Build ingredient rows
        for ingredient in recipe.ingredients:
            row = self._build_ingredient_row(ingredient, show_purpose)
            ingredients_data.append(row)

        # Create ingredients table with overflow protection
        if ingredients_data:
            # Calculate font scaling
            num_ingredients = len(ingredients_data)
            final_font_size = self._calculate_font_size(num_ingredients)

            # Create table with adaptive font size
            ingredients_table = Table(ingredients_data, colWidths=col_widths)

            # Apply styling
            table_style = self._build_table_style(final_font_size)
            ingredients_table.setStyle(TableStyle(table_style))

            # Log font adjustment if changed
            if final_font_size != self.default_table_font:
                self.logger.info(
                    "Ingredients table font adjusted from %d to %d to fit page",
                    self.default_table_font,
                    final_font_size,
                )

            # Right-justify the table by wrapping it in a container
            table_container = Table([[ingredients_table]], colWidths=[actual_table_width])
            table_container.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (0, 0), "RIGHT"),
                        ("VALIGN", (0, 0), (0, 0), "TOP"),
                        ("LEFTPADDING", (0, 0), (0, 0), 0),
                        ("RIGHTPADDING", (0, 0), (0, 0), 0),
                        ("TOPPADDING", (0, 0), (0, 0), 0),
                        ("BOTTOMPADDING", (0, 0), (0, 0), 0),
                    ]
                )
            )

            story.append(table_container)

        return story

    def _calculate_column_widths(self, ingredients: list[Any], show_purpose: bool) -> list[float]:
        """Calculate optimal column widths based on ingredient content.

        Args:
            ingredients: List of ingredient objects
            show_purpose: Whether to include purpose column

        Returns:
            List of column widths in points
        """
        # Start with minimum widths (extra unit width for optimal spacing)
        max_amount_width = 0.4 * inch
        max_unit_width = 0.6 * inch
        max_grams_width = 0.5 * inch
        max_purpose_width = 0.8 * inch if show_purpose else 0

        # Analyze content to determine optimal widths
        for ingredient in ingredients:
            # Amount width
            amount_str = self._format_amount(ingredient.amount)
            amount_width = len(amount_str) * 0.08 * inch + 0.2 * inch
            max_amount_width = max(max_amount_width, amount_width)

            # Unit width
            unit = self._abbreviate_unit(ingredient.unit)
            unit_width = len(unit) * 0.08 * inch + 0.3 * inch
            max_unit_width = max(max_unit_width, unit_width)

            # Grams width
            if ingredient.weight_grams:
                grams_str = f"{ingredient.weight_grams}g"
                grams_width = len(grams_str) * 0.08 * inch + 0.15 * inch
                max_grams_width = max(max_grams_width, grams_width)

            # Purpose width
            if show_purpose and ingredient.purpose:
                purpose_width = len(ingredient.purpose) * 0.08 * inch + 0.2 * inch
                max_purpose_width = max(max_purpose_width, min(purpose_width, 1.2 * inch))

        # Calculate ingredient name width based on actual content
        max_ingredient_width = 1.0 * inch  # Minimum width
        for ingredient in ingredients:
            ingredient_width = len(ingredient.ingredient) * 0.08 * inch + 0.3 * inch
            max_ingredient_width = max(max_ingredient_width, ingredient_width)

        # Build column widths: Amount | Unit | Grams | Ingredient | Purpose
        col_widths = [max_amount_width, max_unit_width, max_grams_width, max_ingredient_width]
        if show_purpose:
            col_widths.append(max_purpose_width)

        return col_widths

    def _build_ingredient_row(self, ingredient: Any, show_purpose: bool) -> list[str]:
        """Build a single ingredient row.

        Args:
            ingredient: Ingredient object
            show_purpose: Whether to include purpose column

        Returns:
            List of strings for the table row
        """
        # Format amount and unit
        amount_str = self._format_amount(ingredient.amount)
        unit = self._abbreviate_unit(ingredient.unit)

        row = [
            amount_str,  # Amount
            unit,  # Unit (abbreviated)
            f"{ingredient.weight_grams}g" if ingredient.weight_grams else "",  # Grams
            ingredient.ingredient,  # Ingredient name
        ]

        if show_purpose and ingredient.purpose:
            row.append(ingredient.purpose)
        elif show_purpose:
            row.append("")

        return row

    def _format_amount(self, amount: float) -> str:
        """Format ingredient amount as string with proper precision.

        Args:
            amount: Numeric amount

        Returns:
            Formatted amount string with up to 2 decimal places, trailing zeros removed
        """
        if amount == int(amount):
            return str(int(amount))
        else:
            return f"{amount:.2f}".rstrip("0").rstrip(".")

    def _abbreviate_unit(self, unit: str) -> str:
        """Abbreviate common units.

        Args:
            unit: Unit string

        Returns:
            Abbreviated unit string
        """
        unit_lower = unit.lower()
        if unit_lower in ["cup", "cups"]:
            return "cp"
        elif unit_lower in ["count"]:
            return "cnt"
        elif unit_lower in ["tablespoon", "tablespoons", "tbsp"]:
            return "tbsp"
        elif unit_lower in ["teaspoon", "teaspoons", "tsp"]:
            return "tsp"
        return unit

    def _calculate_font_size(self, num_ingredients: int) -> int:
        """Calculate appropriate font size based on ingredient count.

        Args:
            num_ingredients: Number of ingredients in the recipe

        Returns:
            Font size in points
        """
        final_font_size = self.default_table_font

        if num_ingredients > self.extreme_recipe_threshold:
            # Extreme measures: aggressive scaling
            scale_factor = self.max_comfortable_ingredients / num_ingredients
            final_font_size = max(int(self.default_table_font * scale_factor), self.min_font_size)
            self.logger.info(
                "EXTREME recipe (%d ingredients) - aggressive scaling, font: %dpt", num_ingredients, final_font_size
            )
        elif num_ingredients > self.max_comfortable_ingredients:
            # Regular scaling: smaller font
            scale_factor = self.max_comfortable_ingredients / num_ingredients
            final_font_size = max(int(self.default_table_font * scale_factor), self.min_font_size)
            self.logger.info("Scaling recipe (%d ingredients) - font: %dpt", num_ingredients, final_font_size)
        else:
            self.logger.debug("Small recipe (%d ingredients) - using standard formatting", num_ingredients)

        return final_font_size

    def _build_table_style(self, font_size: int) -> list[Any]:
        """Build ReportLab table style commands.

        Args:
            font_size: Font size to use

        Returns:
            List of ReportLab table style commands
        """
        return [
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), font_size),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # All columns left-aligned
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            # Zero padding for maximum compactness
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            # Remove alternating row colors for cleaner compact look
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [white]),
        ]

    def estimate_table_width(self, ingredients: list[Any], show_purpose: bool) -> float:
        """Estimate the total width the ingredients table will require.

        Args:
            ingredients: List of ingredient objects
            show_purpose: Whether to include purpose column

        Returns:
            Estimated width in points
        """
        col_widths = self._calculate_column_widths(ingredients, show_purpose)
        return sum(col_widths)

    def should_show_purpose_column(self, ingredients: list[Any]) -> bool:
        """Determine if purpose column should be shown.

        Args:
            ingredients: List of ingredient objects

        Returns:
            True if any ingredient has a purpose
        """
        return any(ing.purpose for ing in ingredients)
