"""Template engine for recipe card customization.

This module provides a comprehensive template system that allows users to
customize recipe card layouts, typography, colors, and display options
through YAML configuration files.

Example usage:
    from recipe_fmt.templates.template_engine import TemplateEngine

    engine = TemplateEngine()
    template = engine.load_template("default-card.yaml")

    # Create customized PDF generator
    generator = engine.create_generator(template, show_weights=True)
    result = generator.generate_card(recipe, "custom-card.pdf")
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from ..models.config import DisplayConfig
from ..utils.logging_setup import get_logger

if TYPE_CHECKING:
    from ..generators.pdf_generator import PDFCardGenerator


class TemplateError(Exception):
    """Template-related errors."""

    pass


class LayoutType(Enum):
    """Supported layout types."""

    TWO_SIDED = "two_sided"
    SINGLE_SIDED = "single_sided"
    INGREDIENTS_ONLY = "ingredients_only"
    INSTRUCTIONS_ONLY = "instructions_only"


@dataclass
class TypographyStyle:
    """Typography style configuration."""

    font_name: str = "Helvetica"
    font_size: int = 10
    alignment: str = "left"
    color: str = "black"
    space_before: int = 0
    space_after: int = 0
    background: str | None = None


@dataclass
class CardDimensions:
    """Card size and margin specifications."""

    width: float = 8.5  # inches
    height: float = 4.0  # inches
    orientation: str = "landscape"
    margin_top: float = 0.25
    margin_bottom: float = 0.25
    margin_left: float = 0.25
    margin_right: float = 0.25


@dataclass
class ColumnConfig:
    """Column configuration for ingredient tables."""

    width: float | str = "auto"
    alignment: str = "left"
    label: str = ""
    format: str | None = None
    show_when: str | None = None


@dataclass
class DisplayOptions:
    """Display options for recipe cards."""

    show_weights: bool = True
    show_purpose: bool = True
    show_category_banner: bool = True
    show_metadata: bool = True
    show_description: bool = True
    show_notes: bool = True
    alternating_rows: bool = True
    row_colors: list[str] = field(default_factory=lambda: ["#FFFFFF", "#F5F5F5"])


@dataclass
class CardTemplate:
    """Complete card template configuration."""

    name: str = "Default Template"
    version: str = "1.0"
    description: str = "Standard recipe card template"

    dimensions: CardDimensions = field(default_factory=CardDimensions)
    layout: LayoutType = LayoutType.TWO_SIDED
    display_options: DisplayOptions = field(default_factory=DisplayOptions)

    # Typography styles
    title_style: TypographyStyle = field(
        default_factory=lambda: TypographyStyle(
            font_name="Helvetica-Bold", font_size=18, alignment="center", space_after=6
        )
    )
    category_banner_style: TypographyStyle = field(
        default_factory=lambda: TypographyStyle(
            font_name="Helvetica-Bold", font_size=12, alignment="center", color="white"
        )
    )
    section_header_style: TypographyStyle = field(
        default_factory=lambda: TypographyStyle(font_name="Helvetica-Bold", font_size=14, space_before=8, space_after=4)
    )
    metadata_style: TypographyStyle = field(
        default_factory=lambda: TypographyStyle(font_size=9, alignment="center", color="#666666", space_after=4)
    )
    description_style: TypographyStyle = field(
        default_factory=lambda: TypographyStyle(
            font_name="Helvetica-Oblique", font_size=10, alignment="center", space_after=6
        )
    )
    ingredient_style: TypographyStyle = field(default_factory=lambda: TypographyStyle(font_size=9, space_after=2))
    instruction_style: TypographyStyle = field(
        default_factory=lambda: TypographyStyle(font_size=10, alignment="justify", space_after=3)
    )
    notes_style: TypographyStyle = field(
        default_factory=lambda: TypographyStyle(
            font_name="Helvetica-Oblique", font_size=9, color="#4D4D4D", space_after=2
        )
    )

    # Column configurations
    columns: dict[str, ColumnConfig] = field(default_factory=dict)

    # Color scheme
    category_colors: dict[str, str] = field(default_factory=dict)
    text_colors: dict[str, str] = field(default_factory=dict)
    background_colors: dict[str, str] = field(default_factory=dict)

    # Layout sections
    layout_sections: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


class TemplateEngine:
    """Template engine for recipe card customization."""

    def __init__(self, cfg_dict: dict = None) -> None:
        """Initialize template engine.

        Args:
            cfg_dict: Configuration dictionary
        """
        # STEP_1: Initialize logging first
        self.logger = get_logger(__name__, cfg_dict)

        # STEP_2: Configuration management
        self.cfg_dict = self._apply_config_defaults(cfg_dict or {})

        # STEP_3: Initialize template cache
        self._template_cache = {}

        # STEP_4: Set default template paths
        self.template_paths = [
            Path("recipe/templates"),
            Path.home() / ".recipe_binder" / "templates",
            Path(__file__).parent.parent.parent.parent / "recipe" / "templates",
        ]

        self.logger.info("TemplateEngine initialized with %d search paths", len(self.template_paths))

    def _apply_config_defaults(self, cfg_dict: dict) -> dict:
        """Apply configuration defaults and log missing keys.

        Args:
            cfg_dict: Input configuration dictionary

        Returns:
            Configuration with defaults applied
        """
        defaults = {
            "cache_templates": True,
            "validate_templates": True,
            "strict_validation": False,
            "default_template": "default-card.yaml",
        }

        for key, default_value in defaults.items():
            if key not in cfg_dict:
                cfg_dict[key] = default_value
                self.logger.debug("Applied default for missing key %s: %s", key, default_value)

        return cfg_dict

    def get_cfg(self) -> dict:
        """Return current configuration dictionary.

        Returns:
            Copy of current configuration
        """
        return self.cfg_dict.copy()

    def add_template_path(self, path: str | Path) -> None:
        """Add a template search path.

        Args:
            path: Template directory path
        """
        path = Path(path)
        if path not in self.template_paths:
            self.template_paths.insert(0, path)
            self.logger.debug("Added template path: %s", path)

    def find_template(self, template_name: str) -> Path | None:
        """Find template file in search paths.

        Args:
            template_name: Template filename

        Returns:
            Path to template file or None if not found
        """
        for search_path in self.template_paths:
            template_path = search_path / template_name
            if template_path.exists():
                self.logger.debug("Found template: %s", template_path)
                return template_path

        self.logger.warning("Template not found: %s", template_name)
        return None

    def load_template(self, template_name: str) -> CardTemplate:
        """Load and parse a template file.

        Args:
            template_name: Template filename or path

        Returns:
            Parsed CardTemplate object

        Raises:
            TemplateError: If template cannot be loaded or parsed
        """
        try:
            # STEP_5: Check cache first
            if self.cfg_dict.get("cache_templates", True) and template_name in self._template_cache:
                self.logger.debug("Template cache hit: %s", template_name)
                return self._template_cache[template_name]

            # STEP_6: Find template file
            if Path(template_name).is_absolute():
                template_path = Path(template_name)
            else:
                template_path = self.find_template(template_name)

            if not template_path or not template_path.exists():
                raise TemplateError(f"Template not found: {template_name}")

            self.logger.info("Loading template: %s", template_path)

            # STEP_7: Load and parse YAML
            try:
                with open(template_path, encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)

                if not isinstance(template_data, dict):
                    raise TemplateError("Invalid template format: expected dictionary at root")

            except yaml.YAMLError as e:
                raise TemplateError(f"YAML parsing error in {template_path}: {e}")
            except Exception as e:
                raise TemplateError(f"Failed to read template {template_path}: {e}")

            # STEP_8: Parse template data
            template = self._parse_template_data(template_data, template_path)

            # STEP_9: Validate template if enabled
            if self.cfg_dict.get("validate_templates", True):
                self._validate_template(template)

            # STEP_10: Cache template
            if self.cfg_dict.get("cache_templates", True):
                self._template_cache[template_name] = template

            self.logger.info("Template loaded successfully: %s (%s)", template.name, template.version)

            return template

        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Unexpected error loading template {template_name}: {e}")

    def _parse_template_data(self, data: dict, source_path: Path) -> CardTemplate:
        """Parse template data into CardTemplate object.

        Args:
            data: Template data dictionary
            source_path: Source template file path

        Returns:
            Parsed CardTemplate object
        """
        try:
            # STEP_11: Extract template info
            template_info = data.get("template_info", {})

            template = CardTemplate(
                name=template_info.get("name", source_path.stem),
                version=template_info.get("version", "1.0"),
                description=template_info.get("description", "Custom template"),
            )

            # STEP_12: Parse card dimensions
            card_data = data.get("card", {})
            size_data = card_data.get("size", {})
            margins_data = card_data.get("margins", {})

            template.dimensions = CardDimensions(
                width=size_data.get("width", 8.5),
                height=size_data.get("height", 4.0),
                orientation=size_data.get("orientation", "landscape"),
                margin_top=margins_data.get("top", 0.25),
                margin_bottom=margins_data.get("bottom", 0.25),
                margin_left=margins_data.get("left", 0.25),
                margin_right=margins_data.get("right", 0.25),
            )

            # STEP_13: Parse layout type
            layout_str = card_data.get("layout", "two_sided")
            try:
                template.layout = LayoutType(layout_str)
            except ValueError:
                self.logger.warning("Unknown layout type: %s, using two_sided", layout_str)
                template.layout = LayoutType.TWO_SIDED

            # STEP_14: Parse typography styles
            typography_data = data.get("typography", {})
            template.title_style = self._parse_typography_style(typography_data.get("title", {}), template.title_style)
            template.category_banner_style = self._parse_typography_style(
                typography_data.get("category_banner", {}), template.category_banner_style
            )
            template.section_header_style = self._parse_typography_style(
                typography_data.get("section_header", {}), template.section_header_style
            )
            template.metadata_style = self._parse_typography_style(
                typography_data.get("metadata", {}), template.metadata_style
            )
            template.description_style = self._parse_typography_style(
                typography_data.get("description", {}), template.description_style
            )
            template.ingredient_style = self._parse_typography_style(
                typography_data.get("ingredient", {}), template.ingredient_style
            )
            template.instruction_style = self._parse_typography_style(
                typography_data.get("instruction", {}), template.instruction_style
            )
            template.notes_style = self._parse_typography_style(typography_data.get("notes", {}), template.notes_style)

            # STEP_15: Parse display options
            display_data = data.get("display", {})
            template.display_options = DisplayOptions(
                show_weights=display_data.get("show_weights", True),
                show_purpose=display_data.get("show_purpose", True),
                show_category_banner=display_data.get("show_category_banner", True),
                show_metadata=display_data.get("show_metadata", True),
                show_description=display_data.get("show_description", True),
                show_notes=display_data.get("show_notes", True),
            )

            # STEP_16: Parse ingredient columns
            ingredients_data = display_data.get("ingredients", {})
            columns_data = ingredients_data.get("columns", {})

            for column_name, column_data in columns_data.items():
                template.columns[column_name] = ColumnConfig(
                    width=column_data.get("width", "auto"),
                    alignment=column_data.get("alignment", "left"),
                    label=column_data.get("label", ""),
                    format=column_data.get("format"),
                    show_when=column_data.get("show_when"),
                )

            # STEP_17: Parse color schemes
            colors_data = data.get("colors", {})
            template.category_colors = colors_data.get("category_colors", {})
            template.text_colors = colors_data.get("text", {})
            template.background_colors = colors_data.get("background", {})

            # STEP_18: Parse layout sections
            template.layout_sections = data.get("layout_sections", {})

            self.logger.debug("Parsed template: %s with %d typography styles", template.name, 8)

            return template

        except Exception as e:
            raise TemplateError(f"Failed to parse template data: {e}")

    def _parse_typography_style(self, style_data: dict, default_style: TypographyStyle) -> TypographyStyle:
        """Parse typography style data.

        Args:
            style_data: Style configuration dictionary
            default_style: Default style to extend

        Returns:
            Parsed TypographyStyle object
        """
        return TypographyStyle(
            font_name=style_data.get("font_name", default_style.font_name),
            font_size=style_data.get("font_size", default_style.font_size),
            alignment=style_data.get("alignment", default_style.alignment),
            color=style_data.get("color", default_style.color),
            space_before=style_data.get("space_before", default_style.space_before),
            space_after=style_data.get("space_after", default_style.space_after),
            background=style_data.get("background", default_style.background),
        )

    def _validate_template(self, template: CardTemplate) -> None:
        """Validate template configuration.

        Args:
            template: Template to validate

        Raises:
            TemplateError: If template validation fails
        """
        # STEP_19: Basic validation
        if template.dimensions.width <= 0 or template.dimensions.height <= 0:
            raise TemplateError("Invalid card dimensions")

        if template.dimensions.margin_top < 0 or template.dimensions.margin_bottom < 0:
            raise TemplateError("Invalid margin values")

        # STEP_20: Typography validation
        styles = [
            template.title_style,
            template.category_banner_style,
            template.section_header_style,
            template.metadata_style,
            template.description_style,
            template.ingredient_style,
            template.instruction_style,
            template.notes_style,
        ]

        for style in styles:
            if style.font_size <= 0:
                raise TemplateError(f"Invalid font size: {style.font_size}")

            if style.alignment not in ["left", "center", "right", "justify"]:
                if self.cfg_dict.get("strict_validation", False):
                    raise TemplateError(f"Invalid text alignment: {style.alignment}")
                else:
                    self.logger.warning("Unknown text alignment: %s", style.alignment)

        self.logger.debug("Template validation passed: %s", template.name)

    def create_generator(self, template: CardTemplate, **overrides) -> "PDFCardGenerator":
        """Create a PDF generator configured with the template.

        Args:
            template: Template to apply
            **overrides: Configuration overrides

        Returns:
            Configured PDFCardGenerator instance
        """
        from ..generators.pdf_generator import CardLayout, PDFCardGenerator

        # STEP_21: Create display config from template
        display_config = DisplayConfig(
            show_weights=overrides.get("show_weights", template.display_options.show_weights),
            show_purpose=overrides.get("show_purpose", template.display_options.show_purpose),
        )

        # STEP_22: Map template layout to generator layout
        layout_map = {
            LayoutType.TWO_SIDED: CardLayout.TWO_SIDED,
            LayoutType.SINGLE_SIDED: CardLayout.SINGLE_SIDED,
            LayoutType.INGREDIENTS_ONLY: CardLayout.INGREDIENTS_ONLY,
            LayoutType.INSTRUCTIONS_ONLY: CardLayout.INSTRUCTIONS_ONLY,
        }

        generator_config = {
            "card_layout": layout_map.get(template.layout, CardLayout.TWO_SIDED),
            "print_margins": template.dimensions.margin_top,
            "show_category_banner": template.display_options.show_category_banner,
            "quality": overrides.get("quality", "high"),
        }

        # STEP_23: Create and configure generator

        generator = PDFCardGenerator(display_config, generator_config)

        # Apply template styles (this would require extending PDFCardGenerator)
        # For now, the generator uses its built-in styles

        self.logger.info("Created PDF generator with template: %s", template.name)

        return generator

    def list_templates(self) -> list[dict[str, str]]:
        """List available templates.

        Returns:
            List of template information dictionaries
        """
        templates = []

        for search_path in self.template_paths:
            if not search_path.exists():
                continue

            for template_file in search_path.glob("*.yaml"):
                try:
                    template = self.load_template(template_file.name)
                    templates.append(
                        {
                            "name": template.name,
                            "filename": template_file.name,
                            "version": template.version,
                            "description": template.description,
                            "path": str(template_file),
                        }
                    )
                except Exception as e:
                    self.logger.warning("Failed to load template %s: %s", template_file, e)

        return templates

    def get_default_template(self) -> CardTemplate:
        """Get the default template.

        Returns:
            Default CardTemplate instance
        """
        default_name = self.cfg_dict.get("default_template", "default-card.yaml")

        try:
            return self.load_template(default_name)
        except TemplateError:
            self.logger.warning("Default template not found, creating basic template")
            return CardTemplate()


def create_engine(template_paths: list[str | Path] = None) -> TemplateEngine:
    """Create a TemplateEngine with custom search paths.

    Args:
        template_paths: List of template search paths

    Returns:
        Configured TemplateEngine instance
    """
    engine = TemplateEngine()

    if template_paths:
        for path in template_paths:
            engine.add_template_path(path)

    return engine


if __name__ == "__main__":
    # Example usage and testing
    import sys
    from pathlib import Path

    # Create engine
    engine = create_engine()

    # List available templates
    print("Available templates:")
    for template_info in engine.list_templates():
        print(f"  {template_info['name']} ({template_info['filename']}) - {template_info['description']}")

    # Load default template
    try:
        template = engine.get_default_template()
        print(f"\nDefault template: {template.name} v{template.version}")
        print(f"Layout: {template.layout.value}")
        print(f"Dimensions: {template.dimensions.width}×{template.dimensions.height} inches")
        print(f"Show weights: {template.display_options.show_weights}")

    except Exception as e:
        print(f"Failed to load default template: {e}")
        sys.exit(1)
