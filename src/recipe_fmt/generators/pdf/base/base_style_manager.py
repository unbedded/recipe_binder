"""Base class for style managers.

Provides common functionality for style management including template integration,
color management, and ReportLab style creation.
"""

from abc import abstractmethod
from typing import Any

from ..interfaces.style_manager import IStyleManager
from ..types import StyleSpec
from .component_base import ComponentBase


class BaseStyleManager(ComponentBase, IStyleManager):
    """Base implementation for style managers.

    Provides common functionality for style management including
    style caching, validation, and ReportLab integration.
    """

    def __init__(self, cfg_dict: dict = None) -> None:
        """Initialize style manager.

        Args:
            cfg_dict: Style manager configuration
        """
        super().__init__(cfg_dict)
        self._style_registry = {}
        self._reportlab_cache = {}
        self._color_cache = {}

    def get_config_defaults(self) -> dict:
        """Get default configuration for style managers."""
        defaults = super().get_config_defaults()
        defaults.update(
            {
                "cache_reportlab_styles": True,
                "cache_colors": True,
                "default_font_name": "Helvetica",
                "default_font_size": 10,
                "default_color": "black",
            }
        )
        return defaults

    def get_style(self, style_name: str, context: dict = None) -> StyleSpec:
        """Get a style specification by name.

        Args:
            style_name: Name of the style to retrieve
            context: Optional context for dynamic style resolution

        Returns:
            StyleSpec object with typography and color information
        """
        # Check registry first
        if style_name in self._style_registry:
            style = self._style_registry[style_name]

            # Apply context adaptations if provided
            if context:
                style = self._adapt_style_for_context(style, context)

            return style

        # Try to load from template or create default
        style = self._load_or_create_style(style_name, context)
        return style

    @abstractmethod
    def _load_or_create_style(self, style_name: str, context: dict = None) -> StyleSpec:
        """Load style from template or create default.

        Subclasses must implement this to provide style loading logic.

        Args:
            style_name: Name of the style to load/create
            context: Optional context for style creation

        Returns:
            StyleSpec object
        """
        pass

    def _adapt_style_for_context(self, base_style: StyleSpec, context: dict) -> StyleSpec:
        """Adapt a style based on context.

        Args:
            base_style: Base StyleSpec to adapt
            context: Context information for adaptation

        Returns:
            Adapted StyleSpec
        """
        # Simple adaptation - can be extended by subclasses
        adapted = StyleSpec(
            font_name=base_style.font_name,
            font_size=base_style.font_size,
            alignment=base_style.alignment,
            color=base_style.color,
            space_before=base_style.space_before,
            space_after=base_style.space_after,
            background=base_style.background,
        )

        # Apply font scaling if provided
        if "font_scale" in context:
            adapted.font_size = max(1, int(adapted.font_size * context["font_scale"]))

        return adapted

    def get_reportlab_style(self, style_name: str, context: dict = None) -> Any:
        """Get a ReportLab ParagraphStyle object.

        Args:
            style_name: Name of the style to retrieve
            context: Optional context for dynamic style resolution

        Returns:
            ReportLab ParagraphStyle object
        """
        # Check cache if enabled
        cache_key = f"{style_name}_{hash(str(context))}" if context else style_name

        if self.cfg_dict.get("cache_reportlab_styles", True) and cache_key in self._reportlab_cache:
            return self._reportlab_cache[cache_key]

        # Get StyleSpec and convert to ReportLab style
        style_spec = self.get_style(style_name, context)
        reportlab_style = self._create_reportlab_style(style_spec, style_name)

        # Cache if enabled
        if self.cfg_dict.get("cache_reportlab_styles", True):
            self._reportlab_cache[cache_key] = reportlab_style

        return reportlab_style

    def _create_reportlab_style(self, style_spec: StyleSpec, name: str) -> Any:
        """Create ReportLab ParagraphStyle from StyleSpec.

        Args:
            style_spec: StyleSpec to convert
            name: Name for the ReportLab style

        Returns:
            ReportLab ParagraphStyle object
        """
        try:
            from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

            # Map alignment
            alignment_map = {
                "left": TA_LEFT,
                "center": TA_CENTER,
                "right": TA_RIGHT,
                "justify": TA_JUSTIFY,
            }

            # Get base styles
            base_styles = getSampleStyleSheet()

            # Create new style
            return ParagraphStyle(
                name=name,
                parent=base_styles["Normal"],
                fontName=style_spec.font_name,
                fontSize=style_spec.font_size,
                alignment=alignment_map.get(style_spec.alignment, TA_LEFT),
                spaceBefore=style_spec.space_before,
                spaceAfter=style_spec.space_after,
                textColor=self._resolve_color(style_spec.color),
                backColor=self._resolve_color(style_spec.background) if style_spec.background else None,
            )

        except ImportError:
            self.logger.error("ReportLab not available for style creation")
            return None
        except Exception as e:
            self.logger.error("Failed to create ReportLab style: %s", e)
            return None

    def _resolve_color(self, color_spec: str | Any) -> Any:
        """Resolve color specification to ReportLab Color.

        Args:
            color_spec: Color specification (string name or Color object)

        Returns:
            ReportLab Color object
        """
        if color_spec is None:
            return None

        # If already a Color object, return as-is
        if hasattr(color_spec, "red"):  # Duck typing for Color
            return color_spec

        # Check cache
        if self.cfg_dict.get("cache_colors", True) and str(color_spec) in self._color_cache:
            return self._color_cache[str(color_spec)]

        try:
            from reportlab.lib.colors import Color, black, white

            # Handle common color names
            color_map = {
                "black": black,
                "white": white,
                "red": Color(1, 0, 0),
                "green": Color(0, 1, 0),
                "blue": Color(0, 0, 1),
            }

            color = color_map.get(str(color_spec).lower(), black)

            # Cache the result
            if self.cfg_dict.get("cache_colors", True):
                self._color_cache[str(color_spec)] = color

            return color

        except ImportError:
            self.logger.error("ReportLab not available for color resolution")
            return None

    def register_style(self, name: str, style: StyleSpec) -> None:
        """Register a new style specification.

        Args:
            name: Name for the style
            style: StyleSpec object to register
        """
        # Validate style first
        validation_errors = self.validate_style(style)
        if validation_errors:
            self.logger.error("Cannot register invalid style %s: %s", name, validation_errors)
            return

        self._style_registry[name] = style
        self.logger.debug("Registered style: %s", name)

        # Clear any cached ReportLab styles for this name
        if self.cfg_dict.get("cache_reportlab_styles", True):
            keys_to_remove = [k for k in self._reportlab_cache.keys() if k.startswith(name)]
            for key in keys_to_remove:
                del self._reportlab_cache[key]

    def get_available_styles(self) -> list[str]:
        """Get list of available style names.

        Returns:
            List of registered style names
        """
        return list(self._style_registry.keys())

    def cleanup(self) -> None:
        """Clean up style manager resources."""
        super().cleanup()
        self._style_registry.clear()
        self._reportlab_cache.clear()
        self._color_cache.clear()
