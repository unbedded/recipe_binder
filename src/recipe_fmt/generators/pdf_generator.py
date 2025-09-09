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

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Tuple
from enum import Enum

try:
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.units import inch
    from reportlab.lib.colors import Color, black, white
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.platypus.flowables import KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.graphics.shapes import Drawing, Rect
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..models.recipe import Recipe
from ..models.config import DisplayConfig
from ..utils.logging_setup import get_logger


class CardLayout(Enum):
    """Card layout options."""
    TWO_SIDED = "two_sided"      # Front: ingredients, Back: instructions
    SINGLE_SIDED = "single_sided" # All content on one side
    INGREDIENTS_ONLY = "ingredients_only"  # Just ingredients
    INSTRUCTIONS_ONLY = "instructions_only"  # Just instructions


@dataclass
class GenerationResult:
    """Result of PDF generation operation."""
    success: bool
    output_path: Optional[Path] = None
    error: Optional[str] = None
    pages_generated: int = 0
    file_size_bytes: Optional[int] = None


class CategoryColors:
    """Category-based color scheme for recipe cards."""
    
    # Color definitions matching README.md specifications
    COLORS = {
        'Meat': Color(0.8, 0.2, 0.2),        # Deep Red
        'Side': Color(0.4, 0.8, 0.4),        # Light Green  
        'Main': Color(0.2, 0.4, 0.8),        # Royal Blue
        'Soup': Color(1.0, 0.6, 0.2),        # Orange
        'Sauce': Color(0.6, 0.4, 0.8),       # Purple
        'Breakfast': Color(1.0, 0.8, 0.2),   # Golden Yellow
        'Salad': Color(0.2, 0.8, 0.2),       # Fresh Green
        'Baking': Color(0.8, 0.6, 0.4),      # Warm Brown
        'Dessert': Color(0.8, 0.4, 0.6),     # Pink
        'Other': Color(0.6, 0.6, 0.6)        # Gray
    }
    
    @classmethod
    def get_color(cls, category: str) -> Color:
        """Get color for recipe category.
        
        Args:
            category: Recipe category name
            
        Returns:
            ReportLab Color object
        """
        return cls.COLORS.get(category, cls.COLORS['Other'])
    
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
            min(1.0, base_color.blue + 0.2)
        )


class PDFCardGenerator:
    """Professional recipe card PDF generator."""
    
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
            raise ImportError(
                "ReportLab is required for PDF generation. "
                "Install with: pip install reportlab"
            )
        
        # STEP_3: Configuration management
        self.config = config
        self.cfg_dict = self._apply_config_defaults(cfg_dict or {})
        
        # STEP_4: Initialize card specifications
        self._init_card_specs()
        self._init_typography()
        
        self.logger.info("PDFCardGenerator initialized - size: %.1f×%.1f, weights: %s", 
                        self.card_width, self.card_height, config.show_weights)
    
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
            "compress_pdf": True
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
        
        # STEP_6: Margins and spacing
        self.margin = self.cfg_dict.get("print_margins", 0.25) * inch
        self.content_width = self.card_width - (2 * self.margin)
        self.content_height = self.card_height - (2 * self.margin)
        
        # STEP_7: Layout sections
        self.header_height = 0.6 * inch
        self.banner_height = 0.3 * inch
        self.spacing = 0.1 * inch
        
        self.logger.debug("Card specs - Content area: %.1f×%.1f inches", 
                         self.content_width/inch, self.content_height/inch)
    
    def _init_typography(self) -> None:
        """Initialize fonts and text styles."""
        # STEP_8: Create custom styles
        self.styles = getSampleStyleSheet()
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='RecipeTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=black
        ))
        
        # Category banner style
        self.styles.add(ParagraphStyle(
            name='CategoryBanner',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=white,
            spaceAfter=0
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=8,
            spaceAfter=4,
            textColor=black
        ))
        
        # Ingredient style
        self.styles.add(ParagraphStyle(
            name='Ingredient',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=2,
            alignment=TA_LEFT
        ))
        
        # Instruction style
        self.styles.add(ParagraphStyle(
            name='Instruction',
            parent=self.styles['Normal'], 
            fontSize=10,
            spaceAfter=3,
            alignment=TA_JUSTIFY
        ))
        
        # Notes style
        self.styles.add(ParagraphStyle(
            name='Notes',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=2,
            fontName='Helvetica-Oblique',
            textColor=Color(0.3, 0.3, 0.3)
        ))
        
        self.logger.debug("Typography initialized with %d custom styles", 
                         len([s for s in self.styles.byName.keys() if 'Recipe' in s or 'Category' in s]))
    
    def get_cfg(self) -> dict:
        """Return current configuration dictionary.
        
        Returns:
            Copy of current configuration
        """
        return self.cfg_dict.copy()
    
    def generate_card(self, recipe: Recipe, output_path: Union[str, Path]) -> GenerationResult:
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
                bottomMargin=self.margin
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
            
            self.logger.info("PDF generated successfully: %d pages, %d bytes", 
                           pages_count, file_size)
            
            return GenerationResult(
                success=True,
                output_path=output_path,
                pages_generated=pages_count,
                file_size_bytes=file_size
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
            rowHeights=[available_height]
        )
        
        content_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
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
        """Build front side content (title + ingredients).
        
        Args:
            recipe: Recipe to generate content for
            
        Returns:
            List of ReportLab flowables
        """
        story = []
        
        # STEP_16: Header section
        story.extend(self._build_header_section(recipe))
        
        # STEP_17: Ingredients section
        story.extend(self._build_ingredients_section(recipe))
        
        return story
    
    def _build_back_side(self, recipe: Recipe) -> list:
        """Build back side content (instructions + notes).
        
        Args:
            recipe: Recipe to generate content for
            
        Returns:
            List of ReportLab flowables
        """
        story = []
        
        # STEP_18: Category banner (smaller on back)
        if self.cfg_dict.get("show_category_banner", True):
            story.extend(self._build_category_banner(recipe, height=0.2*inch))
        
        # STEP_19: Instructions section
        story.extend(self._build_instructions_section(recipe))
        
        # STEP_20: Notes section
        if recipe.notes:
            story.extend(self._build_notes_section(recipe))
        
        return story
    
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
        title = Paragraph(recipe.title, self.styles['RecipeTitle'])
        story.append(title)
        
        # STEP_23: Recipe metadata
        if recipe.description or recipe.servings or recipe.prep_time or recipe.cook_time:
            story.extend(self._build_metadata_section(recipe))
        
        story.append(Spacer(1, self.spacing))
        
        return story
    
    def _build_category_banner(self, recipe: Recipe, height: Optional[float] = None) -> list:
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
        
        # STEP_24: Create colored banner
        banner_data = [[Paragraph(recipe.category.upper(), self.styles['CategoryBanner'])]]
        
        banner_table = Table(
            banner_data,
            colWidths=[self.content_width],
            rowHeights=[banner_height]
        )
        
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), category_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(banner_table)
        story.append(Spacer(1, self.spacing/2))
        
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
                name='Metadata',
                parent=self.styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=Color(0.4, 0.4, 0.4),
                spaceAfter=4
            )
            
            story.append(Paragraph(metadata_text, metadata_style))
        
        if recipe.description:
            desc_style = ParagraphStyle(
                name='Description',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique',
                spaceAfter=6
            )
            story.append(Paragraph(recipe.description, desc_style))
        
        return story
    
    def _build_ingredients_section(self, recipe: Recipe, max_width: Optional[float] = None) -> list:
        """Build ingredients section with optional weight display.
        
        Args:
            recipe: Recipe to generate ingredients for
            max_width: Optional maximum width constraint
            
        Returns:
            List of ReportLab flowables
        """
        story = []
        
        # STEP_25: Section header
        story.append(Paragraph("INGREDIENTS", self.styles['SectionHeader']))
        
        # STEP_26: Build ingredients table
        table_width = max_width or self.content_width
        ingredients_data = []
        
        show_weights = self.config.show_weights
        show_purpose = any(ing.purpose for ing in recipe.ingredients)
        
        # Determine column structure
        if show_weights and show_purpose:
            # Amount | Unit | Ingredient | Weight | Purpose
            col_widths = [0.8*inch, 0.8*inch, table_width-3.2*inch, 0.8*inch, 0.8*inch]
        elif show_weights:
            # Amount | Unit | Ingredient | Weight
            col_widths = [0.8*inch, 0.8*inch, table_width-2.4*inch, 0.8*inch]
        elif show_purpose:
            # Amount | Unit | Ingredient | Purpose
            col_widths = [0.8*inch, 0.8*inch, table_width-2.4*inch, 0.8*inch]
        else:
            # Amount | Unit | Ingredient
            col_widths = [0.8*inch, 0.8*inch, table_width-1.6*inch]
        
        # STEP_27: Add ingredient rows
        for ingredient in recipe.ingredients:
            row = [
                str(ingredient.amount) if ingredient.amount != int(ingredient.amount) else str(int(ingredient.amount)),
                ingredient.unit,
                ingredient.ingredient
            ]
            
            if show_weights and ingredient.weight_grams:
                row.append(f"({ingredient.weight_grams}g)")
            elif show_weights:
                row.append("")
            
            if show_purpose and ingredient.purpose:
                row.append(ingredient.purpose)
            elif show_purpose:
                row.append("")
                
            ingredients_data.append(row)
        
        # STEP_28: Create ingredients table
        if ingredients_data:
            ingredients_table = Table(ingredients_data, colWidths=col_widths)
            
            table_style = [
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (1, -1), 'RIGHT'),  # Amount and unit right-aligned
                ('ALIGN', (2, 0), (-1, -1), 'LEFT'),   # Rest left-aligned
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, Color(0.95, 0.95, 0.95)])
            ]
            
            ingredients_table.setStyle(TableStyle(table_style))
            story.append(ingredients_table)
        
        return story
    
    def _build_instructions_section(self, recipe: Recipe, max_width: Optional[float] = None) -> list:
        """Build instructions section.
        
        Args:
            recipe: Recipe to generate instructions for
            max_width: Optional maximum width constraint
            
        Returns:
            List of ReportLab flowables
        """
        story = []
        
        # STEP_29: Section header
        story.append(Paragraph("INSTRUCTIONS", self.styles['SectionHeader']))
        
        # STEP_30: Add numbered instructions
        for i, instruction in enumerate(recipe.instructions, 1):
            instruction_text = f"{i}. {instruction}"
            story.append(Paragraph(instruction_text, self.styles['Instruction']))
        
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
            story.append(Paragraph("NOTES", self.styles['SectionHeader']))
            
            # STEP_32: Add notes
            for note in recipe.notes:
                story.append(Paragraph(f"• {note}", self.styles['Notes']))
        
        return story
    
    def get_generation_stats(self) -> dict:
        """Get PDF generation statistics and configuration.
        
        Returns:
            Dictionary with generation statistics
        """
        return {
            "generator_config": self.cfg_dict.copy(),
            "card_specs": {
                "size_inches": f"{self.card_width/inch:.1f}×{self.card_height/inch:.1f}",
                "content_area_inches": f"{self.content_width/inch:.1f}×{self.content_height/inch:.1f}",
                "margins_inches": self.margin/inch
            },
            "supported_layouts": [layout.value for layout in CardLayout],
            "category_colors": {cat: f"RGB({c.red:.1f},{c.green:.1f},{c.blue:.1f})" 
                             for cat, c in CategoryColors.COLORS.items()}
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
    
    from ..models.recipe import Recipe
    import yaml
    
    # Load recipe from YAML
    recipe_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    try:
        with open(recipe_file, 'r') as f:
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