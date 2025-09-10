"""Recipe card template system.

This package provides a flexible template engine for customizing recipe card
layouts, styling, and display options through YAML configuration files.

Example usage:
    from recipe_fmt.templates import TemplateEngine, CardTemplate

    engine = TemplateEngine()
    template = engine.load_template("default-card.yaml")

    # Apply template to PDF generator
    generator = engine.create_generator(template)
    result = generator.generate_card(recipe, "output.pdf")
"""

from .template_engine import CardTemplate, TemplateEngine, TemplateError
from .template_loader import DefaultTemplates, TemplateLoader

__all__ = ["TemplateEngine", "CardTemplate", "TemplateError", "TemplateLoader", "DefaultTemplates"]
