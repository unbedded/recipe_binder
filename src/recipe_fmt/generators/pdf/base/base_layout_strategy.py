"""Base class for layout strategies.

Provides common functionality and patterns for layout strategy implementations.
"""

from abc import abstractmethod
from typing import Any

from ..interfaces.layout_strategy import ILayoutStrategy
from ..types import GenerationContext, LayoutConfig
from .component_base import ComponentBase


class BaseLayoutStrategy(ComponentBase, ILayoutStrategy):
    """Base implementation for layout strategies.

    Provides common functionality for layout strategies including
    validation, section management, and content organization patterns.
    """

    def __init__(self, cfg_dict: dict = None) -> None:
        """Initialize layout strategy.

        Args:
            cfg_dict: Strategy-specific configuration
        """
        super().__init__(cfg_dict)
        self._section_builders = {}
        self._required_sections = []

    def get_config_defaults(self) -> dict:
        """Get default configuration for layout strategies."""
        defaults = super().get_config_defaults()
        defaults.update(
            {
                "enable_page_breaks": True,
                "optimize_spacing": True,
                "adaptive_sizing": True,
                "validate_content_fit": True,
            }
        )
        return defaults

    def validate_config(self, config: LayoutConfig) -> list[str]:
        """Validate layout configuration.

        Args:
            config: Layout configuration to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate card dimensions
        if config.card_dimensions.width <= 0 or config.card_dimensions.height <= 0:
            errors.append("Invalid card dimensions")

        # Validate margins
        margins = config.margins
        total_h_margin = margins.left + margins.right
        total_v_margin = margins.top + margins.bottom

        if total_h_margin >= config.card_dimensions.width:
            errors.append("Horizontal margins exceed card width")

        if total_v_margin >= config.card_dimensions.height:
            errors.append("Vertical margins exceed card height")

        # Layout-specific validation
        layout_errors = self._validate_layout_specific(config)
        errors.extend(layout_errors)

        return errors

    def _validate_layout_specific(self, config: LayoutConfig) -> list[str]:
        """Validate layout-specific configuration.

        Subclasses should override this for layout-specific validation.

        Args:
            config: Layout configuration to validate

        Returns:
            List of layout-specific validation errors
        """
        return []

    def get_required_sections(self) -> list[str]:
        """Get required sections for this layout.

        Returns cached list or builds it from layout definition.
        """
        if not self._required_sections:
            self._required_sections = self._build_required_sections()
        return self._required_sections

    @abstractmethod
    def _build_required_sections(self) -> list[str]:
        """Build the list of required sections for this layout.

        Subclasses must implement this to define their section requirements.

        Returns:
            List of required section names
        """
        pass

    def register_section_builder(self, section_name: str, builder: Any) -> None:
        """Register a content builder for a specific section.

        Args:
            section_name: Name of the section
            builder: Content builder instance
        """
        self._section_builders[section_name] = builder
        self.logger.debug("Registered builder for section: %s", section_name)

    def get_section_builder(self, section_name: str) -> Any:
        """Get the content builder for a section.

        Args:
            section_name: Name of the section

        Returns:
            Content builder instance or None if not registered
        """
        return self._section_builders.get(section_name)

    def has_section_builder(self, section_name: str) -> bool:
        """Check if a section builder is registered.

        Args:
            section_name: Name of the section to check

        Returns:
            True if builder is registered
        """
        return section_name in self._section_builders

    def build_section_content(self, section_name: str, context: GenerationContext) -> list[Any]:
        """Build content for a specific section.

        Args:
            section_name: Name of the section to build
            context: Generation context

        Returns:
            List of flowables for the section
        """
        builder = self.get_section_builder(section_name)
        if not builder:
            self.logger.warning("No builder registered for section: %s", section_name)
            return []

        try:
            from ..types import ContentConfig, ContentSection, StyleSpec

            # Create ContentConfig from context with proper style and configuration
            section_enum = (
                ContentSection(section_name.lower())
                if hasattr(ContentSection, section_name.upper())
                else ContentSection.METADATA
            )

            # Use context-aware style configuration
            style = StyleSpec(font_name="Helvetica", font_size=11, alignment="left", color="black")

            config = ContentConfig(
                section=section_enum,
                style=style,
                show_section=True,
                custom_data={"context_width": context.content_width, "context_height": context.content_height},
            )

            result = builder.build_content(context, config)
            if result.success:
                self.logger.debug("Built section %s: %d flowables", section_name, len(result.flowables))
                return result.flowables
            else:
                self.logger.error("Failed to build section %s: %s", section_name, result.error)
                return []

        except Exception as e:
            self.logger.exception("Error building section %s: %s", section_name, e)
            return []

    def calculate_available_space(self, context: GenerationContext, page: int = 1) -> tuple[float, float]:
        """Calculate available space for content on a page.

        Args:
            context: Generation context with layout configuration
            page: Page number (1-based)

        Returns:
            Tuple of (width, height) available for content
        """
        config = context.layout_config

        # Start with card dimensions
        available_width = config.card_dimensions.width
        available_height = config.card_dimensions.height

        # Subtract margins
        margins = config.margins
        available_width -= margins.left + margins.right
        available_height -= margins.top + margins.bottom

        # Subtract space for fixed elements (banners, headers, etc.)
        if config.show_category_banner:
            available_height -= 30.0  # Approximate banner height

        return available_width, available_height

    def supports_feature(self, feature: str) -> bool:
        """Check if this layout supports a specific feature.

        Base implementation checks common features.

        Args:
            feature: Feature name to check

        Returns:
            True if feature is supported
        """
        common_features = {
            "page_breaks": self.cfg_dict.get("enable_page_breaks", True),
            "adaptive_sizing": self.cfg_dict.get("adaptive_sizing", True),
            "spacing_optimization": self.cfg_dict.get("optimize_spacing", True),
        }

        return common_features.get(feature, False)

    def _component_initialize(self) -> bool:
        """Layout strategy specific initialization."""
        # Validate that we have all required sections
        required = self.get_required_sections()
        if not required:
            self.logger.warning("Layout strategy has no required sections")

        self.logger.debug("Layout strategy initialized with %d required sections", len(required))
        return True
