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
        "Meat": Color(0.8, 0.2, 0.2),       # Deep Red
        "Side": Color(0.0, 0.6, 0.6),       # Teal
        "Main": Color(0.2, 0.4, 0.8),       # Royal Blue
        "Soup": Color(0.9, 0.4, 0.0),       # Burnt Orange
        "Sauce": Color(0.4, 0.2, 0.6),      # Indigo Purple
        "Breakfast": Color(0.85, 0.55, 0.0),# Amber/Gold
        "Salad": Color(0.0, 0.6, 0.2),      # Leaf Green
        "Baking": Color(0.45, 0.25, 0.1),   # Chocolate Brown
        "Dessert": Color(0.7, 0.2, 0.4),    # Raspberry
        "Other": Color(0.3, 0.3, 0.3),      # Dark Gray
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

    # Layout constants
    FRONT_PAGE_SAFETY_MARGIN = 1.2  # inches - prevents overflow on ingredient-heavy recipes
    MAX_COMFORTABLE_INGREDIENTS = 8   # ingredients - above this, start scaling down font/spacing
    EXTREME_RECIPE_THRESHOLD = 15      # ingredients - drop purpose column + 90° rotation

    def __init__(self, config: DisplayConfig, cfg_dict: dict = None) -> None:
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

    def _apply_config_defaults(self, cfg_dict: dict) -> dict:
        """Apply configuration defaults and log missing keys.

        Args:
            cfg_dict: Input configuration dictionary

        Returns:
            Configuration with defaults applied
        """
        defaults = {
            "card_layout": CardLayout.TWO_SIDED,
            "print_margins": 0.25,  # inches
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
        # STEP_5: Card dimensions (8.5" × 4" landscape)
        self.card_width = 8.5 * inch
        self.card_height = 4.0 * inch

        # STEP_6: Margins and spacing (will be adjusted later for large recipes)
        self.base_margin = self.cfg_dict.get("print_margins", 0.25)
        self.margin = self.base_margin * inch
        self.content_width = self.card_width - (2 * self.margin)
        self.content_height = self.card_height - (2 * self.margin)

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
                leftMargin=self.margin,
                rightMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin,
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
        story.extend(self._build_header_section(recipe))

        # Split content into columns
        available_height = self.content_height - self.header_height - self.banner_height

        # Create two-column layout
        col_width = (self.content_width - self.spacing) / 2

        # Left column: Ingredients
        ingredients_content = self._build_ingredients_section(recipe, col_width)

        # Right column: Instructions
        instructions_content = self._build_instructions_section(recipe, col_width)

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
        story.extend(self._build_header_section(recipe))
        story.extend(self._build_ingredients_section(recipe))
        return story

    def _build_instructions_content(self, recipe: Recipe) -> list:
        """Build content for instructions-only layout.

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []
        story.extend(self._build_header_section(recipe))
        story.extend(self._build_instructions_section(recipe))
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

        # STEP_17: Create side-by-side layout: ingredients left, nutrition right
        col_width = (self.content_width - self.spacing) / 2

        # Build ingredients table with overflow protection (left column)
        if recipe.ingredients:
            # Apply same smart sizing logic as main ingredients section
            num_ingredients = len(recipe.ingredients)
            final_font_size = self.default_table_font
            
            # Simple dynamic scaling + extreme measures for massive recipes
            rotate_text = False
            drop_purpose_column = False
            
            if num_ingredients > self.EXTREME_RECIPE_THRESHOLD:
                # Extreme measures: drop purpose column + 90° rotation + aggressive scaling
                drop_purpose_column = True
                rotate_text = True
                scale_factor = self.MAX_COMFORTABLE_INGREDIENTS / num_ingredients
                final_font_size = max(int(self.default_table_font * scale_factor), self.min_font_size)
                self.logger.info("EXTREME recipe (%d ingredients) - dropping purpose column + 90° rotation, font: %dpt", 
                               num_ingredients, final_font_size)
                
            elif num_ingredients > self.MAX_COMFORTABLE_INGREDIENTS:
                # Regular scaling: smaller font
                scale_factor = self.MAX_COMFORTABLE_INGREDIENTS / num_ingredients
                final_font_size = max(int(self.default_table_font * scale_factor), self.min_font_size)
                self.logger.info("Scaling recipe (%d ingredients) - font: %dpt", num_ingredients, final_font_size)
            else:
                self.logger.debug("Small recipe (%d ingredients) - using standard formatting", num_ingredients)
            
            # Scale margins and spacing for large recipes
            if num_ingredients > self.MAX_COMFORTABLE_INGREDIENTS:
                scale_factor = self.MAX_COMFORTABLE_INGREDIENTS / num_ingredients
                scaled_margin = max(0.05, self.base_margin * scale_factor)  # Don't go below 0.05"
                old_margin = self.margin
                self.margin = scaled_margin * inch
                self.content_width = self.card_width - (2 * self.margin)  
                self.content_height = self.card_height - (2 * self.margin)
                self.logger.info("Scaled margins from %.2fin to %.2fin (scale: %.2f)", old_margin/inch, self.margin/inch, scale_factor)
            
            self.logger.debug("Front side ingredients table: %d items, font=%dpt", 
                            num_ingredients, final_font_size)

            ingredients_data = []
            show_purpose = any(ing.purpose for ing in recipe.ingredients) and not drop_purpose_column

            # Use original column structure but fit in left column
            for ingredient in recipe.ingredients:
                amount_str = (
                    str(ingredient.amount)
                    if ingredient.amount != int(ingredient.amount)
                    else str(int(ingredient.amount))
                )

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
                    unit,
                    f"{ingredient.weight_grams}g" if ingredient.weight_grams else "",
                    ingredient.ingredient,
                ]
                if show_purpose and ingredient.purpose:
                    row.append(ingredient.purpose)
                elif show_purpose:
                    row.append("")

                ingredients_data.append(row)

            # Calculate column widths for left side
            col_widths = [0.4 * inch, 0.4 * inch, 0.5 * inch, col_width - 1.3 * inch]
            if show_purpose:
                col_widths.append(0.6 * inch)
                col_widths[-2] = col_width - 1.9 * inch  # Adjust ingredient name width

            ingredients_table = Table(ingredients_data, colWidths=col_widths)
            
            # Build table style with scaled padding
            padding = 1 if num_ingredients <= self.MAX_COMFORTABLE_INGREDIENTS else 0
            table_style_commands = [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), final_font_size),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), padding),
                ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
            ]
            
            # Add 90-degree rotation for extreme recipes (ingredient names only)
            if rotate_text:
                try:
                    table_style_commands.append(("ROTATION", (0, 0), (0, -1), 90))  # Only ingredient name column
                    table_style_commands.append(("VALIGN", (0, 0), (0, -1), "BOTTOM"))  # Align rotated text
                    self.logger.info("🔄 Applied 90° rotation to ingredient names (no purpose column)")
                except Exception as e:
                    self.logger.error("❌ Failed to apply 90° rotation: %s", e)
                    rotate_text = False  # Fall back to normal text
                
            try:
                ingredients_table.setStyle(TableStyle(table_style_commands))
                if rotate_text:
                    self.logger.info("✅ TableStyle with rotation applied successfully")
            except Exception as e:
                self.logger.error("❌ Failed to apply TableStyle: %s", e)
                # Try without rotation as fallback
                if rotate_text:
                    self.logger.warning("🔄 Retrying without rotation...")
                    table_style_commands = [cmd for cmd in table_style_commands if cmd[0] != "ROTATION"]
                    ingredients_table.setStyle(TableStyle(table_style_commands))
        else:
            ingredients_table = Table([[""]], colWidths=[col_width])

        # Build simple nutrition text for right column
        nutrition_text = self._build_simple_nutrition_text(recipe)

        # Create side-by-side layout
        layout_data = [[ingredients_table, nutrition_text]]

        main_layout = Table(layout_data, colWidths=[col_width, col_width])
        main_layout.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),  # Left column
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),  # Right column
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
        story.extend(self._build_instructions_section(recipe))

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

    def _build_header_section(self, recipe: Recipe) -> list:
        """Build header section with title and category banner.

        Args:
            recipe: Recipe to generate content for

        Returns:
            List of ReportLab flowables
        """
        story = []

        # STEP_21: Category banner
        if self.cfg_dict.get("show_category_banner", True):
            story.extend(self._build_category_banner(recipe))

        # STEP_22: Recipe title
        title = Paragraph(recipe.title, self.styles["RecipeTitle"])
        story.append(title)

        # STEP_23: Recipe metadata
        if recipe.servings or recipe.prep_time or recipe.cook_time:
            story.extend(self._build_metadata_section(recipe))

        story.append(Spacer(1, self.spacing))

        return story

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

    def _build_metadata_section(self, recipe: Recipe) -> list:
        """Build recipe metadata section.

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

    def _build_ingredients_section(self, recipe: Recipe, max_width: float | None = None) -> list:
        """Build ingredients section with optional weight display.

        Args:
            recipe: Recipe to generate ingredients for
            max_width: Optional maximum width constraint

        Returns:
            List of ReportLab flowables
        """
        story = []

        # STEP_25: No section header for compact format

        # STEP_26: Build compact ingredients table with dynamic width
        ingredients_data = []

        show_purpose = any(ing.purpose for ing in recipe.ingredients)

        # Dynamic column widths based on content
        # Calculate optimal widths by analyzing content
        max_amount_width = 0.4 * inch  # Start with minimum
        max_unit_width = 0.3 * inch
        max_grams_width = 0.5 * inch
        max_purpose_width = 0.8 * inch if show_purpose else 0

        # Analyze content to determine optimal widths
        for ingredient in recipe.ingredients:
            # Amount width
            amount_str = (
                str(ingredient.amount) if ingredient.amount != int(ingredient.amount) else str(int(ingredient.amount))
            )
            amount_width = len(amount_str) * 0.08 * inch + 0.2 * inch
            max_amount_width = max(max_amount_width, amount_width)

            # Unit width
            unit = ingredient.unit
            if unit.lower() in ["cup", "cups"]:
                unit = "cp"
            elif unit.lower() in ["count"]:
                unit = "cnt"
            unit_width = len(unit) * 0.08 * inch + 0.15 * inch
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
        for ingredient in recipe.ingredients:
            ingredient_width = len(ingredient.ingredient) * 0.08 * inch + 0.3 * inch
            max_ingredient_width = max(max_ingredient_width, ingredient_width)

        # Build column widths: Amount | Unit | Grams | Ingredient | Purpose (all minimum needed)
        col_widths = [max_amount_width, max_unit_width, max_grams_width, max_ingredient_width]
        if show_purpose:
            col_widths.append(max_purpose_width)

        # Calculate actual table width needed
        actual_table_width = sum(col_widths)

        # STEP_27: Add ingredient rows with updated formatting
        for ingredient in recipe.ingredients:
            # Convert unit abbreviations: cups → cp, count → cnt
            unit = ingredient.unit
            if unit.lower() in ["cup", "cups"]:
                unit = "cp"
            elif unit.lower() in ["count"]:
                unit = "cnt"

            # Format amount and separate unit and grams
            amount_str = (
                str(ingredient.amount) if ingredient.amount != int(ingredient.amount) else str(int(ingredient.amount))
            )

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

            ingredients_data.append(row)

        # STEP_28: Create ingredients table with overflow protection
        if ingredients_data:
            # Smart fallback: large ingredient lists need more space
            num_ingredients = len(ingredients_data)
            final_font_size = self.default_table_font
            
            # Simple dynamic scaling + extreme measures for massive recipes
            rotate_text = False
            drop_purpose_column = False
            
            if num_ingredients > self.EXTREME_RECIPE_THRESHOLD:
                # Extreme measures: drop purpose column + 90° rotation + aggressive scaling
                drop_purpose_column = True
                rotate_text = True
                scale_factor = self.MAX_COMFORTABLE_INGREDIENTS / num_ingredients
                final_font_size = max(int(self.default_table_font * scale_factor), self.min_font_size)
                self.logger.info("EXTREME recipe (%d ingredients) - dropping purpose column + 90° rotation, font: %dpt", 
                               num_ingredients, final_font_size)
                
            elif num_ingredients > self.MAX_COMFORTABLE_INGREDIENTS:
                # Regular scaling: smaller font
                scale_factor = self.MAX_COMFORTABLE_INGREDIENTS / num_ingredients
                final_font_size = max(int(self.default_table_font * scale_factor), self.min_font_size)
                self.logger.info("Scaling recipe (%d ingredients) - font: %dpt", num_ingredients, final_font_size)
            else:
                self.logger.debug("Small recipe (%d ingredients) - using standard formatting", num_ingredients)
            
            self.logger.debug("Creating ingredients table: %d items, font=%dpt", num_ingredients, final_font_size)

            # Create table with adaptive font size
            ingredients_table = Table(ingredients_data, colWidths=col_widths)

            table_style = [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), final_font_size),
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

            ingredients_table.setStyle(TableStyle(table_style))

            # Log font adjustment if changed
            if final_font_size != self.default_table_font:
                self.logger.info(
                    "Ingredients table font adjusted from %d to %d to fit page",
                    self.default_table_font,
                    final_font_size,
                )

            # Right-justify the table by wrapping it in a container

            # Create a table that's only as wide as needed, then right-align it
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

    def _build_nutrition_section(self, recipe: Recipe, max_width: float | None = None) -> list:
        """Build nutrition facts section for display.

        Args:
            recipe: Recipe to generate nutrition for
            max_width: Optional maximum width constraint

        Returns:
            List of ReportLab flowables
        """
        story = []

        # Get nutrition data from properly parsed Recipe model
        nutrition = getattr(recipe, "nutrition", None)
        if nutrition and hasattr(nutrition, "calories") and nutrition.calories:
            # Use real nutrition data from YAML
            nutrition_data = {
                "calories": nutrition.calories or 0,
                "protein_g": nutrition.protein_g or 0,
                "carbs_g": nutrition.carbs_g or 0,
                "fat_g": nutrition.fat_g or 0,
                "fiber_g": nutrition.fiber_g or 0,
                "sodium_mg": nutrition.sodium_mg or 0,
            }
        else:
            # Fallback sample data when no nutrition data available
            nutrition_data = {
                "calories": 245,
                "protein_g": 8,
                "carbs_g": 35,
                "fat_g": 9,
                "fiber_g": 2,
                "sodium_mg": 387,
            }

        # Nutrition Facts title
        nutrition_style = ParagraphStyle(
            "NutritionTitle",
            parent=self.styles["SectionHeader"],
            fontSize=12,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=4,
        )
        nutrition_title = Paragraph("NUTRITION FACTS", nutrition_style)
        story.append(nutrition_title)

        # Build nutrition table
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
                display_value = f"{value}mg" if isinstance(value, (int, float)) else str(value)
            elif "_g" in key:
                display_value = f"{value}g" if isinstance(value, (int, float)) else str(value)
            else:
                display_value = f"{value}" if isinstance(value, (int, float)) else str(value)

            nutrition_rows.append([label, display_value])

        # Calculate column widths
        width = max_width or (self.content_width * 0.4)
        col_widths = [width * 0.7, width * 0.3]

        nutrition_table = Table(nutrition_rows, colWidths=col_widths)
        nutrition_table.setStyle(
            TableStyle(
                [
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
            )
        )

        story.append(nutrition_table)
        return story

    def _build_simple_nutrition_text(self, recipe: Recipe) -> Paragraph:
        """Build simple nutrition facts as right-justified text column.

        Args:
            recipe: Recipe to generate nutrition for

        Returns:
            Paragraph with nutrition facts
        """
        # Get nutrition data from properly parsed Recipe model
        nutrition = getattr(recipe, "nutrition", None)
        if nutrition and hasattr(nutrition, "calories") and nutrition.calories:
            # Use real nutrition data from YAML
            nutrition_data = {
                "calories": nutrition.calories or 0,
                "protein_g": nutrition.protein_g or 0,
                "carbs_g": nutrition.carbs_g or 0,
                "fat_g": nutrition.fat_g or 0,
                "fiber_g": nutrition.fiber_g or 0,
                "sodium_mg": nutrition.sodium_mg or 0,
            }
        else:
            # Fallback sample data when no nutrition data available
            nutrition_data = {
                "calories": 245,
                "protein_g": 8,
                "carbs_g": 35,
                "fat_g": 9,
                "fiber_g": 2,
                "sodium_mg": 387,
            }

        # Build simple text format
        lines = [
            "<b>NUTRITION FACTS</b>",
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
        nutrition_style = ParagraphStyle(
            "SimpleNutrition",
            parent=self.styles["Normal"],
            fontSize=9,
            alignment=TA_RIGHT,
            spaceAfter=2,
        )

        return Paragraph(nutrition_text, nutrition_style)

    def _build_instructions_section(self, recipe: Recipe, max_width: float | None = None) -> list:
        """Build compact instructions section without heading, with integrated notes.

        Args:
            recipe: Recipe to generate instructions for
            max_width: Optional maximum width constraint

        Returns:
            List of ReportLab flowables
        """
        story = []

        # STEP_29: No section header for compact format

        # STEP_30: Add numbered instructions with adaptive font sizing
        # Calculate available height for instructions on back page
        available_height = self._calculate_available_height(has_banner=True, page_num=2)
        self.logger.info(
            "📏 Back page available height: %.1fpt (content=%.1fpt, banner=%.1fpt, margins=%.1fpt)",
            available_height,
            self.content_height,
            self.banner_height,
            (self.card_height - self.content_height),
        )

        # Build all instruction text to measure total height needed
        all_instructions_text = []
        for i, instruction in enumerate(recipe.instructions, 1):
            instruction_text = f"{i}. {instruction}"
            all_instructions_text.append(instruction_text)

        # Add notes text if present
        notes_text = []
        if recipe.notes:
            for note in recipe.notes:
                notes_text.append(f"• {note}")

        # Simple approach: use default fonts and let ReportLab handle layout
        final_font_size = self.default_instruction_font
        notes_font_size = max(final_font_size - 1, self.min_font_size)
        
        self.logger.debug("Building instructions with font size %dpt", final_font_size)

        # Create instruction style with standard font size
        adaptive_instruction_style = ParagraphStyle(
            "AdaptiveInstruction",
            parent=self.styles["Instruction"],
            fontSize=final_font_size,
            spaceAfter=1.5,  # Reduced spacing as you suggested
        )
        adaptive_notes_style = ParagraphStyle(
            "AdaptiveNotes",
            parent=self.styles["Notes"],
            fontSize=notes_font_size,
            spaceAfter=max(0.5, notes_font_size * 0.1),  # Even smaller spacing for notes
        )

        # Debug: Log the actual font sizes being applied
        self.logger.info(
            "🔧 Creating adaptive styles: instruction=%dpt, notes=%dpt",
            final_font_size,
            notes_font_size,
        )
        self.logger.info(
            "🔧 Instruction style fontSize: %s",
            getattr(adaptive_instruction_style, "fontSize", "MISSING"),
        )
        self.logger.info("🔧 Notes style fontSize: %s", getattr(adaptive_notes_style, "fontSize", "MISSING"))

        # Add instructions with adaptive font
        for instruction_text in all_instructions_text:
            story.append(Paragraph(instruction_text, adaptive_instruction_style))

        # STEP_31: Add notes as italic text at end of instructions (if room)
        if recipe.notes:
            story.append(Spacer(1, self.spacing / 4))  # Minimal spacer - reduced from /2 to /4
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

    def _build_notes_section(self, recipe: Recipe) -> list:
        """Build notes section.

        Args:
            recipe: Recipe to generate notes for

        Returns:
            List of ReportLab flowables
        """
        story = []

        if recipe.notes:
            # STEP_31: Section header
            story.append(Spacer(1, self.spacing))
            story.append(Paragraph("NOTES", self.styles["SectionHeader"]))

            # STEP_32: Add notes
            for note in recipe.notes:
                story.append(Paragraph(f"• {note}", self.styles["Notes"]))

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
                "margins_inches": self.margin / inch,
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
