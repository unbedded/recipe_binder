"""Interface for style management.

Defines the contract for managing typography, colors, and style templates
across the PDF generation system.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..types import StyleSpec


class IStyleManager(ABC):
    """Interface for style management.

    Style managers handle typography, colors, and template integration.
    They provide consistent styling across all PDF generation components
    and support template-based customization.
    """

    @abstractmethod
    def get_style(self, style_name: str, context: dict = None) -> StyleSpec:
        """Get a style specification by name.

        Args:
            style_name: Name of the style to retrieve
            context: Optional context for dynamic style resolution

        Returns:
            StyleSpec object with typography and color information
        """

    @abstractmethod
    def get_reportlab_style(self, style_name: str, context: dict = None) -> Any:
        """Get a ReportLab ParagraphStyle object.

        Args:
            style_name: Name of the style to retrieve
            context: Optional context for dynamic style resolution

        Returns:
            ReportLab ParagraphStyle object
        """

    @abstractmethod
    def get_category_color(self, category: str) -> Any:
        """Get the color for a recipe category.

        Args:
            category: Recipe category name

        Returns:
            ReportLab Color object
        """

    @abstractmethod
    def load_template_styles(self, template_path: str) -> bool:
        """Load styles from a template file.

        Args:
            template_path: Path to template file

        Returns:
            True if styles were loaded successfully
        """

    @abstractmethod
    def register_style(self, name: str, style: StyleSpec) -> None:
        """Register a new style specification.

        Args:
            name: Name for the style
            style: StyleSpec object to register
        """

    @abstractmethod
    def create_adaptive_style(self, base_style_name: str, font_scale: float = 1.0, context: dict = None) -> StyleSpec:
        """Create an adaptive style based on a base style.

        Args:
            base_style_name: Name of the base style
            font_scale: Scaling factor for font size
            context: Additional context for adaptation

        Returns:
            Adapted StyleSpec object
        """

    def get_available_styles(self) -> list[str]:
        """Get list of available style names.

        Returns:
            List of registered style names
        """
        return []  # Default: no styles registered

    def validate_style(self, style: StyleSpec) -> list[str]:
        """Validate a style specification.

        Args:
            style: StyleSpec to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        if style.font_size <= 0:
            errors.append(f"Invalid font size: {style.font_size}")
        if style.alignment not in ["left", "center", "right", "justify"]:
            errors.append(f"Invalid alignment: {style.alignment}")
        return errors

    def supports_templates(self) -> bool:
        """Check if this style manager supports template loading.

        Returns:
            True if template loading is supported
        """
        return False  # Default: no template support
