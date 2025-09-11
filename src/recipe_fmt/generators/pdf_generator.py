"""Professional PDF recipe card generator using ReportLab.

This module generates high-quality recipe cards with category-based colors,
two-sided layouts, and optional weight display for precision cooking.

Card specifications:
- Size: 8.5" × 4" landscape
- Front: Recipe title, ingredients with weights
- Back: Instructions, notes, category color coding
- Fonts: Clean, readable typography
- Layout: Professional kitchen-ready design

Example usage:
    from recipe_fmt.generators.pdf_generator import PDFCardGenerator
    from recipe_fmt.models.config import DisplayConfig

    config = DisplayConfig(show_weights=True)
    generator = PDFCardGenerator(config)

    result = generator.generate_card(recipe, "Breakfast-pancakes.pdf")
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from reportlab.lib.colors import Color, black, white
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..models.config import DisplayConfig
from ..models.recipe import Recipe
from ..utils.logging_setup import get_logger
from .pdf.builders import (
    HeaderBuilder,
    IngredientsBuilder,
    InstructionsBuilder,
    NotesBuilder,
    NutritionBuilder,
)


class CardLayout(Enum):
    """Card layout options."""

    TWO_SIDED = "two_sided"  # Front: ingredients, Back: instructions
    SINGLE_SIDED = "single_sided"  # All content on one side
    INGREDIENTS_ONLY = "ingredients_only"  # Just ingredients
    INSTRUCTIONS_ONLY = "instructions_only"  # Just instructions


@dataclass
class GenerationResult:
    """Result of PDF generation operation."""

    success: bool
    output_path: Path | None = None
    error: str | None = None
    pages_generated: int = 0
    file_size_bytes: int | None = None


class CategoryColors:
    """Category-based color scheme for recipe cards."""

    # Color definitions matching README.md specifications
    COLORS = {
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

    # Category icons matching README.md specifications
    ICONS = {
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

    @classmethod
    def get_color(cls, category: str) -> Color:
        """Get color for recipe category.

        Args:
            category: Recipe category name

        Returns:
            ReportLab Color object
        """
        return cls.COLORS.get(category, cls.COLORS["Other"])

    @classmethod
    def get_icon(cls, category: str) -> str:
        """Get icon for recipe category.

        Args:
            category: Recipe category name

        Returns:
            Unicode emoji icon
        """
        return cls.ICONS.get(category, cls.ICONS["Other"])

    @classmethod
    def get_accent_color(cls, category: str) -> Color:
        """Get lighter accent color for category.

        Args:
            category: Recipe category name

        Returns:
            Lighter version of category color
        """
        base_color = cls.get_color(category)
        # Lighten by blending with white
        return Color(
            min(1.0, base_color.red + 0.2),
            min(1.0, base_color.green + 0.2),
            min(1.0, base_color.blue + 0.2),
        )


class PDFCardGenerator:
    """Professional recipe card PDF generator."""

    # Layout constants for three-column layout (Ing Col 1 | Ing Col 2 | Nutrition)
    FRONT_PAGE_SAFETY_MARGIN = 1.2  # inches - prevents overflow on ingredient-heavy recipes
    MAX_COMFORTABLE_INGREDIENTS = 16  # ingredients - much higher with 2 columns (was 8)
    EXTREME_RECIPE_THRESHOLD = 24  # ingredients - extreme measures (was 15)

    def __init__(self, config: DisplayConfig, cfg_dict: dict[str, Any] | None = None) -> None:
        """Initialize PDF generator with display configuration.

        Args:
            config: Display configuration settings
            cfg_dict: Additional configuration dictionary
        """
        # STEP_1: Initialize logging first
        self.logger = get_logger(__name__, cfg_dict)

        # STEP_2: Check ReportLab availability
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")

        # STEP_3: Configuration management
        self.config = config
        self.cfg_dict = self._apply_config_defaults(cfg_dict or {})

        # STEP_4: Initialize card specifications
        self._init_card_specs()
        self._init_typography()

        # STEP_5: Font sizing thresholds for adaptive sizing
        self.min_font_size = 5  # Minimum readable font size (lowered to handle dense content)
        # Get default font sizes from template (will be loaded in _load_template_defaults)
        self.default_table_font = 9  # fallback
        self.default_instruction_font = 10  # fallback
        self._load_template_defaults()

        # STEP_6: Initialize content builders
        self._init_builders()

        self.logger.info(
            "PDFCardGenerator initialized - size: %.1f×%.1f, weights: %s",
            self.card_width,
            self.card_height,
            config.show_weights,
        )

    def _load_template_defaults(self) -> None:
        """Load default font sizes and settings from template configuration."""
        try:
            from pathlib import Path

            import yaml

            template_path = Path("recipe/templates/default-card.yaml")
            if template_path.exists():
                with open(template_path) as f:
                    template_config = yaml.safe_load(f)

                # Extract font sizes from template
                typography = template_config.get("typography", {})

                ingredient_font = typography.get("ingredient", {}).get("font_size", 9)
                instruction_font = typography.get("instruction", {}).get("font_size", 10)

                self.default_table_font = ingredient_font
                self.default_instruction_font = instruction_font

                self.logger.debug(
                    "Loaded template settings: ingredient=%d, instruction=%d",
                    ingredient_font,
                    instruction_font,
                )
            else:
                self.logger.debug("Template file not found, using fallback font sizes")

        except Exception as e:
            self.logger.warning("Failed to load template defaults: %s", e)

    def _init_builders(self) -> None:
        """Initialize content builders with required dependencies."""
        self.header_builder = HeaderBuilder(styles=self.styles, spacing=self.spacing, cfg_dict=self.cfg_dict)

        self.ingredients_builder = IngredientsBuilder(
            cfg_dict=self.cfg_dict,
            default_table_font=self.default_table_font,
            min_font_size=self.min_font_size,
            max_comfortable_ingredients=self.MAX_COMFORTABLE_INGREDIENTS,
            extreme_recipe_threshold=self.EXTREME_RECIPE_THRESHOLD,
        )

        self.instructions_builder = InstructionsBuilder(
            styles=self.styles,
            spacing=self.spacing,
            default_instruction_font=self.default_instruction_font,
            min_font_size=self.min_font_size,
        )

        self.notes_builder = NotesBuilder(styles=self.styles, spacing=self.spacing)

        self.nutrition_builder = NutritionBuilder(styles=self.styles, content_width=self.content_width)

        self.logger.debug("Content builders initialized successfully")

    def _apply_config_defaults(self, cfg_dict: dict[str, Any]) -> dict[str, Any]:
        """Apply configuration defaults and log missing keys.

        Args:
            cfg_dict: Input configuration dictionary

        Returns:
            Configuration with defaults applied
        """
        defaults = {
            "card_layout": CardLayout.TWO_SIDED,
            "ingredient_columns": 3,
            "show_category_banner": True,
            "quality": "high",  # high, medium, low
            "compress_pdf": True,
        }

        for key, default_value in defaults.items():
            if key not in cfg_dict:
                cfg_dict[key] = default_value
                self.logger.debug("Applied default for missing key %s: %s", key, default_value)

        return cfg_dict

    def _init_card_specs(self) -> None:
        """Initialize card size and layout specifications."""
        # STEP_5: Card dimensions (8.5" × 11" portrait - standard letter)
        self.card_width = 8.5 * inch
        self.card_height = 11.0 * inch

        # STEP_6: Fixed margins and spacing
        self.side_margin = 0.375 * inch  # Fixed 3/8 inch side margins
        self.top_margin = 0.15 * inch  # Reduced top margin for more content space
        self.bottom_margin = 0.375 * inch  # Keep bottom margin same as sides
        self.content_width = self.card_width - (2 * self.side_margin)
        self.content_height = self.card_height - (self.top_margin + self.bottom_margin)

        # STEP_7: Layout sections
        self.header_height = 0.6 * inch
        self.banner_height = 0.3 * inch
        self.spacing = 0.05 * inch  # Reduced from 0.1 to 0.05 for tighter spacing

        self.logger.debug(
            "Card specs - Content area: %.1f×%.1f inches",
            self.content_width / inch,
            self.content_height / inch,
        )

    def _init_typography(self) -> None:
        """Initialize fonts and text styles."""
        # STEP_8: Create custom styles
        self.styles = getSampleStyleSheet()

        # Title style
        self.styles.add(
            ParagraphStyle(
                name="RecipeTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                spaceAfter=6,
                alignment=TA_CENTER,
                textColor=black,
            )
        )

        # Category banner style
        self.styles.add(
            ParagraphStyle(
                name="CategoryBanner",
                parent=self.styles["Normal"],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=white,
                spaceAfter=0,
            )
        )

        # Compact banner left style (for title)
        self.styles.add(
            ParagraphStyle(
                name="CompactBannerLeft",
                parent=self.styles["Normal"],
                fontSize=12,
                alignment=TA_LEFT,
                textColor=white,
                spaceAfter=0,
            )
        )

        # Compact banner right style (for category)
        self.styles.add(
            ParagraphStyle(
                name="CompactBannerRight",
                parent=self.styles["Normal"],
                fontSize=12,
                alignment=TA_RIGHT,
                textColor=white,
                spaceAfter=0,
            )
        )

        # Section header style
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceBefore=8,
                spaceAfter=4,
                textColor=black,
            )
        )

        # Ingredient style
        self.styles.add(
            ParagraphStyle(
                name="Ingredient",
                parent=self.styles["Normal"],
                fontSize=10,
                spaceAfter=2,
                alignment=TA_LEFT,
            )
        )

        # Instruction style - reduced spacing for better fit
        self.styles.add(
            ParagraphStyle(
                name="Instruction",
                parent=self.styles["Normal"],
                fontSize=10,
                spaceAfter=1.5,  # Reduced from 3 to 1.5
                alignment=TA_JUSTIFY,
            )
        )

        # Notes style - reduced spacing
        self.styles.add(
            ParagraphStyle(
                name="Notes",
                parent=self.styles["Normal"],
                fontSize=9,
                spaceAfter=1,  # Reduced from 2 to 1
                fontName="Helvetica-Oblique",
                textColor=Color(0.3, 0.3, 0.3),
            )
        )

        self.logger.debug(
            "Typography initialized with %d custom styles",
            len([s for s in self.styles.byName.keys() if "Recipe" in s or "Category" in s]),
        )

    def get_cfg(self) -> dict:
        """Return current configuration dictionary.

        Returns:
            Copy of current configuration
        """
        return self.cfg_dict.copy()

    def generate_card(self, recipe: Recipe, output_path: str | Path) -> GenerationResult:
        """Generate a PDF recipe card.

        Args:
            recipe: Recipe object to generate card for
            output_path: Output PDF file path

        Returns:
            Generation result with success status and details
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self.logger.info("Generating PDF card for: %s → %s", recipe.title, output_path)

            # STEP_9: Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=(self.card_width, self.card_height),
                leftMargin=self.side_margin,
                rightMargin=self.side_margin,
                topMargin=self.top_margin,
                bottomMargin=self.bottom_margin,
            )

            # STEP_10: Build content based on layout
            layout = self.cfg_dict.get("card_layout", CardLayout.TWO_SIDED)

            if layout == CardLayout.TWO_SIDED:
                story = self._build_two_sided_content(recipe)
            elif layout == CardLayout.SINGLE_SIDED:
                story = self._build_single_sided_content(recipe)
            elif layout == CardLayout.INGREDIENTS_ONLY:
                story = self._build_ingredients_content(recipe)
            else:  # INSTRUCTIONS_ONLY
                story = self._build_instructions_content(recipe)

            # STEP_11: Generate PDF
            doc.build(story)

            # STEP_12: Get file statistics
            file_size = output_path.stat().st_size
            pages_count = 2 if layout == CardLayout.TWO_SIDED else 1

            self.logger.info("PDF generated successfully: %d pages, %d bytes", pages_count, file_size)

            return GenerationResult(
                success=True,
                output_path=output_path,
                pages_generated=pages_count,
                file_size_bytes=file_size,
            )

        except Exception as e:
            error_msg = f"PDF generation failed for {recipe.title}: {e}"
            self.logger.exception(error_msg)
            return GenerationResult(success=False, error=error_msg)

    def _build_two_sided_content(self, recipe: Recipe) -> list:
        """Build content for two-sided card layout.

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []

        # STEP_13: Front side - Title and Ingredients
        story.extend(self._build_front_side(recipe))

        # Page break for back side
        story.append(PageBreak())

        # STEP_14: Back side - Instructions and Notes
        story.extend(self._build_back_side(recipe))

        return story

    def _build_single_sided_content(self, recipe: Recipe) -> list:
        """Build content for single-sided card layout.

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []

        # STEP_15: Combined layout on one side
        story.extend(self.header_builder.build_header_section(recipe))

        # Split content into columns
        available_height = self.content_height - self.header_height - self.banner_height

        # Create two-column layout
        col_width = (self.content_width - self.spacing) / 2

        # Left column: Ingredients
        ingredients_content = self.ingredients_builder.build_ingredients_section(recipe, col_width)

        # Right column: Instructions
        instructions_content = self.instructions_builder.build_instructions_section(recipe, col_width)

        # Combine in table
        content_table = Table(
            [[ingredients_content, instructions_content]],
            colWidths=[col_width, col_width],
            rowHeights=[available_height],
        )

        content_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        story.append(content_table)

        return story

    def _build_ingredients_content(self, recipe: Recipe) -> list:
        """Build content for ingredients-only layout.

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []
        story.extend(self.header_builder.build_header_section(recipe))
        story.extend(self.ingredients_builder.build_ingredients_section(recipe))
        return story

    def _build_instructions_content(self, recipe: Recipe) -> list:
        """Build content for instructions-only layout.

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []
        story.extend(self.header_builder.build_header_section(recipe))
        story.extend(self.instructions_builder.build_instructions_section(recipe))
        return story

    def _build_front_side(self, recipe: Recipe) -> list:
        """Build front side content (compact title + ingredients left + nutrition right).

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []

        # STEP_16: Compact banner with title + category
        story.extend(self._build_compact_banner(recipe))

        # STEP_17: Create three-column layout: ingredients col1, ingredients col2, nutrition
        spacing = self.spacing
        ing_col_width = (self.content_width - 2 * spacing) * 0.40  # 40% each for ingredients
        nutrition_width = (self.content_width - 2 * spacing) * 0.20  # 20% for nutrition

        # Build ingredients table with overflow protection (left column)
        if recipe.ingredients:
            # Apply same smart sizing logic as main ingredients section
            num_ingredients = len(recipe.ingredients)
            final_font_size = self.default_table_font

            # Simple dynamic scaling + extreme measures for massive recipes
            rotate_text = False

            if num_ingredients > self.EXTREME_RECIPE_THRESHOLD:
                # Extreme measures: 90° rotation + aggressive scaling (purpose column already dropped)
                rotate_text = True
                scale_factor = self.MAX_COMFORTABLE_INGREDIENTS / num_ingredients
                final_font_size = max(int(self.default_table_font * scale_factor), self.min_font_size)
                self.logger.info(
                    "EXTREME recipe (%d ingredients) - 90° rotation, font: %dpt", num_ingredients, final_font_size
                )

            elif num_ingredients > self.MAX_COMFORTABLE_INGREDIENTS:
                # Regular scaling: smaller font (purpose column already dropped in three-column layout)
                scale_factor = self.MAX_COMFORTABLE_INGREDIENTS / num_ingredients
                final_font_size = max(int(self.default_table_font * scale_factor), self.min_font_size)
                self.logger.info("Scaling recipe (%d ingredients) - font: %dpt", num_ingredients, final_font_size)
            else:
                self.logger.debug(
                    "Recipe (%d ingredients) - using full-size formatting in three-column layout", num_ingredients
                )

            # Fixed margins - no dynamic scaling

            self.logger.debug("Front side ingredients table: %d items, font=%dpt", num_ingredients, final_font_size)

            ingredients_data = []

            # Use original column structure but fit in left column
            for ingredient in recipe.ingredients:
                # Format amount with proper precision
                if ingredient.amount == int(ingredient.amount):
                    amount_str = str(int(ingredient.amount))
                else:
                    amount_str = f"{ingredient.amount:.2f}".rstrip("0").rstrip(".")

                # Abbreviate units
                unit = ingredient.unit
                if unit.lower() in ["cup", "cups"]:
                    unit = "cp"
                elif unit.lower() in ["count"]:
                    unit = "cnt"
                elif unit.lower() in ["tablespoon", "tablespoons", "tbsp"]:
                    unit = "tbsp"
                elif unit.lower() in ["teaspoon", "teaspoons", "tsp"]:
                    unit = "tsp"

                row = [
                    amount_str,
                    "",  # Spacing column between amount and unit
                    unit,
                    f"{ingredient.weight_grams}g" if ingredient.weight_grams else "",
                    ingredient.ingredient,
                ]
                # No purpose column in two-column layout
                ingredients_data.append(row)

            # Split ingredients into two columns
            mid_point = (len(ingredients_data) + 1) // 2  # Round up for odd numbers
            ingredients_col1_data = ingredients_data[:mid_point]
            ingredients_col2_data = ingredients_data[mid_point:]

            # Calculate column widths for each ingredients column (with spacing column)
            #
            # Visual Layout:
            # ┌─────────────────────────────────────────────────────────┐
            # │ Ingredients Col1      │ Ingredients Col2  │ Nutrition     │
            # │ ┌───────────────────┐ │ ┌─────────────────┐ │               │
            # │ │1    cups 240g flour│ │ │2   tsp  12g salt│ │ Calories: 350 │
            # │ │0.5  tsp  3g  vanilla│ │ │1   cnt  50g egg │ │ Protein: 8g   │
            # │ └───────────────────┘ │ └─────────────────┘ │               │
            # └─────────────────────────────────────────────────────────┘
            #    ↑  ↑ ↑    ↑    ↑        Amount [Space] Unit Weight Ingredient
            #
            # Column width variables for easy adjustment:
            amount_col_width = 0.3 * inch  # Amount column (e.g., "1", "0.5", "2.25") - right justified
            space_col_width = 0.1 * inch  # Spacing column between amount and unit
            unit_col_width = 0.3 * inch  # Unit column (e.g., "cups", "tsp", "lbs") - left justified
            weight_col_width = 0.5 * inch  # Weight column (e.g., "240g", "15g")

            # Calculate ingredient name column (gets remainder after fixed columns)
            fixed_widths = amount_col_width + space_col_width + unit_col_width + weight_col_width
            ingredient_name_width = ing_col_width - fixed_widths

            col_widths = [amount_col_width, space_col_width, unit_col_width, weight_col_width, ingredient_name_width]

            # Create two separate ingredient tables (handle empty second column)
            ingredients_table1 = Table(ingredients_col1_data, colWidths=col_widths)

            # Ensure second column has at least one row (empty if needed)
            if not ingredients_col2_data:
                ingredients_col2_data = [["", "", "", "", ""]]  # Empty row with correct column count (5 columns)
            ingredients_table2 = Table(ingredients_col2_data, colWidths=col_widths)

            # Build table style with scaled padding and proper alignment
            padding = 1 if num_ingredients <= self.MAX_COMFORTABLE_INGREDIENTS else 0
            table_style_commands = [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), final_font_size),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # Default left alignment
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),  # Amount column (col 0) right-aligned
                # Space column (col 1) stays empty with default left alignment
                # Unit column (col 2) stays left-aligned (default)
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), padding),
                ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
            ]

            # Add 90-degree rotation for extreme recipes (ingredient names only)
            if rotate_text:
                try:
                    table_style_commands.append(("ROTATION", (4, 0), (4, -1), 90))  # Ingredient name column (col 4)
                    table_style_commands.append(("VALIGN", (4, 0), (4, -1), "BOTTOM"))  # Align rotated text
                    self.logger.info("🔄 Applied 90° rotation to ingredient names (5-column layout)")
                except Exception as e:
                    self.logger.error("❌ Failed to apply 90° rotation: %s", e)
                    rotate_text = False  # Fall back to normal text

            try:
                ingredients_table1.setStyle(TableStyle(table_style_commands))
                ingredients_table2.setStyle(TableStyle(table_style_commands))
                if rotate_text:
                    self.logger.info("✅ TableStyle with rotation applied successfully")
            except Exception as e:
                self.logger.error("❌ Failed to apply TableStyle: %s", e)
                # Try without rotation as fallback
                if rotate_text:
                    self.logger.warning("🔄 Retrying without rotation...")
                    table_style_commands = [cmd for cmd in table_style_commands if cmd[0] != "ROTATION"]
                    ingredients_table1.setStyle(TableStyle(table_style_commands))
                    ingredients_table2.setStyle(TableStyle(table_style_commands))
        else:
            ingredients_table1 = Table([[""]], colWidths=[ing_col_width])
            ingredients_table2 = Table([[""]], colWidths=[ing_col_width])

        # Build simple nutrition text for right column
        nutrition_text = self.nutrition_builder.build_simple_nutrition_text(recipe)

        # Create three-column layout
        layout_data = [[ingredients_table1, ingredients_table2, nutrition_text]]

        main_layout = Table(layout_data, colWidths=[ing_col_width, ing_col_width, nutrition_width])
        main_layout.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),  # Ingredients column 1
                    ("ALIGN", (1, 0), (1, 0), "LEFT"),  # Ingredients column 2
                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),  # Nutrition column
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        story.append(main_layout)

        return story

    def _calculate_available_height(self, has_banner: bool = True, page_num: int = 1) -> float:
        """Calculate available height on a page after margins and fixed elements.

        Args:
            has_banner: Whether page has a banner
            page_num: Page number (1 for front, 2 for back)

        Returns:
            Available height in points
        """
        available_height = self.content_height

        # Subtract banner height if present
        if has_banner:
            available_height -= self.banner_height
            available_height -= self.spacing / 2  # Banner spacing

        # Subtract typical spacers between sections
        if page_num == 1:
            # Front page: banner + ingredients spacing
            available_height -= self.spacing  # Additional spacing
            available_height -= self.FRONT_PAGE_SAFETY_MARGIN * inch  # Safety margin for overflow protection
        else:
            # Back page: banner + instructions + notes spacing
            available_height -= self.spacing / 2

        return max(available_height, 1 * inch)  # Ensure minimum space

    def _build_back_side(self, recipe: Recipe) -> list:
        """Build back side content (compact serves/time + instructions + notes).

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []

        # STEP_18: Compact banner with serves/time + category
        serves_time_text = self._build_serves_time_text(recipe)
        story.extend(self._build_compact_banner(recipe, left_content=serves_time_text))

        # STEP_19: Compact instructions section (no heading, includes notes)
        story.extend(self.instructions_builder.build_instructions_section(recipe))

        return story

    def _build_serves_time_text(self, recipe: Recipe) -> str:
        """Build serves and time text for compact banner.

        Args:
            recipe: Recipe to get metadata from

        Returns:
            Formatted serves/time string
        """
        parts = []

        if recipe.servings:
            parts.append(f"Serves {recipe.servings}")

        if recipe.prep_time:
            parts.append(f"Prep: {recipe.prep_time}")

        if recipe.cook_time:
            parts.append(f"Cook: {recipe.cook_time}")

        return " • ".join(parts) if parts else ""

    def _build_category_banner(self, recipe: Recipe, height: float | None = None) -> list:
        """Build category color banner.

        Args:
            recipe: Recipe to generate banner for
            height: Optional custom height

        Returns:
            List of ReportLab flowables
        """
        story = []

        banner_height = height or self.banner_height
        category_color = CategoryColors.get_color(recipe.category)
        category_icon = CategoryColors.get_icon(recipe.category)

        # STEP_24: Create colored banner with icon
        banner_text = f"{category_icon} {recipe.category.upper()}"
        banner_data = [[Paragraph(banner_text, self.styles["CategoryBanner"])]]

        banner_table = Table(banner_data, colWidths=[self.content_width], rowHeights=[banner_height])

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

    def _build_compact_banner(self, recipe: Recipe, left_content: str = "", height: float | None = None) -> list:
        """Build compact banner with content on left and category on right.

        Args:
            recipe: Recipe to generate banner for
            left_content: Content for left side (e.g., title, serves/time)
            height: Optional custom height

        Returns:
            List of ReportLab flowables
        """
        story = []

        banner_height = height or self.banner_height
        category_color = CategoryColors.get_color(recipe.category)

        # Convert title to Snake_Case format
        title_snake_case = recipe.title.replace(" ", "_").replace("-", "_")
        display_title = left_content or title_snake_case

        # STEP_24a: Create two-column banner: Title (left) + Category (right)
        banner_data = [
            [
                Paragraph(display_title, self.styles["CompactBannerLeft"]),
                Paragraph(recipe.category.upper(), self.styles["CompactBannerRight"]),
            ]
        ]

        # Split banner width: more space for title, fixed space for category
        title_width = self.content_width * 0.7
        category_width = self.content_width * 0.3

        banner_table = Table(banner_data, colWidths=[title_width, category_width], rowHeights=[banner_height])

        banner_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), category_color),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),  # Title left-aligned
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),  # Category right-aligned
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

    def get_generation_stats(self) -> dict:
        """Get PDF generation statistics and configuration.

        Returns:
            Dictionary with generation statistics
        """
        return {
            "generator_config": self.cfg_dict.copy(),
            "card_specs": {
                "size_inches": f"{self.card_width / inch:.1f}×{self.card_height / inch:.1f}",
                "content_area_inches": (f"{self.content_width / inch:.1f}×{self.content_height / inch:.1f}"),
                "margins_inches": {
                    "top": self.top_margin / inch,
                    "bottom": self.bottom_margin / inch,
                    "sides": self.side_margin / inch,
                },
            },
            "supported_layouts": [layout.value for layout in CardLayout],
            "category_colors": {
                cat: f"RGB({c.red:.1f},{c.green:.1f},{c.blue:.1f})" for cat, c in CategoryColors.COLORS.items()
            },
        }


def create_generator(show_weights: bool = True, layout: CardLayout = CardLayout.TWO_SIDED) -> PDFCardGenerator:
    """Create a PDFCardGenerator with common configuration.

    Args:
        show_weights: Enable weight display
        layout: Card layout mode

    Returns:
        Configured PDFCardGenerator instance
    """
    from ..models.config import DisplayConfig

    config = DisplayConfig(show_weights=show_weights)
    cfg_dict = {"card_layout": layout}

    return PDFCardGenerator(config, cfg_dict)


if __name__ == "__main__":
    # Example usage and testing
    import sys
    from pathlib import Path

    if len(sys.argv) != 3:
        print("Usage: python -m recipe_fmt.generators.pdf_generator <recipe_yaml> <output_pdf>")
        sys.exit(1)

    import yaml

    from ..models.recipe import Recipe

    # Load recipe from YAML
    recipe_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    try:
        with open(recipe_file) as f:
            recipe_data = yaml.safe_load(f)

        recipe = Recipe(**recipe_data)

        # Generate PDF
        generator = create_generator(show_weights=True)
        result = generator.generate_card(recipe, output_file)

        if result.success:
            print(f"✅ Generated PDF: {result.output_path}")
            print(f"   Pages: {result.pages_generated}")
            print(f"   Size: {result.file_size_bytes} bytes")
        else:
            print(f"❌ Generation failed: {result.error}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
