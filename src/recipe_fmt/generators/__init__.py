"""Recipe PDF generation modules.

This package provides comprehensive PDF generation for recipe cards using ReportLab
with support for category-based colors, two-sided layouts, and weight display options.

Example usage:
    from recipe_fmt.generators import PDFCardGenerator
    from recipe_fmt.models.config import DisplayConfig
    from recipe_fmt.models.recipe import Recipe

    config = DisplayConfig()
    generator = PDFCardGenerator(config)

    result = generator.generate_card(recipe, "output.pdf")
    if result.success:
        print(f"Generated PDF: {result.output_path}")
"""

from .pdf_generator import CardLayout, GenerationResult, PDFCardGenerator

__all__ = ["PDFCardGenerator", "GenerationResult", "CardLayout"]
