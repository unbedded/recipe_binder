"""Base class for content builders.

Provides common functionality for building content sections with proper
error handling, validation, and ReportLab integration.
"""

from abc import abstractmethod
from typing import Any

from ..interfaces.content_builder import IContentBuilder
from ..types import ContentBuildResult, ContentConfig, GenerationContext
from .component_base import ComponentBase


class BaseContentBuilder(ComponentBase, IContentBuilder):
    """Base implementation for content builders.

    Provides common functionality for content builders including
    validation, error handling, and ReportLab flowable management.
    """

    def __init__(self, cfg_dict: dict = None) -> None:
        """Initialize content builder.

        Args:
            cfg_dict: Builder-specific configuration
        """
        super().__init__(cfg_dict)
        self._height_cache = {}
        self._style_cache = {}

    def get_config_defaults(self) -> dict:
        """Get default configuration for content builders."""
        defaults = super().get_config_defaults()
        defaults.update(
            {
                "cache_height_estimates": True,
                "cache_styles": True,
                "validate_flowables": False,
                "enable_overflow_protection": True,
            }
        )
        return defaults

    def validate_config(self, config: ContentConfig) -> list[str]:
        """Validate content configuration.

        Args:
            config: Content configuration to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate section type
        section_type = self.get_section_type()
        if config.section.value != section_type:
            errors.append(f"Config section type '{config.section.value}' doesn't match builder type '{section_type}'")

        # Validate style specification
        if config.style:
            style_errors = self._validate_style_spec(config.style)
            errors.extend(style_errors)

        # Builder-specific validation
        builder_errors = self._validate_builder_specific(config)
        errors.extend(builder_errors)

        return errors

    def _validate_style_spec(self, style) -> list[str]:
        """Validate style specification.

        Args:
            style: StyleSpec to validate

        Returns:
            List of validation errors
        """
        errors = []

        if style.font_size <= 0:
            errors.append(f"Invalid font size: {style.font_size}")

        if style.alignment not in ["left", "center", "right", "justify"]:
            errors.append(f"Invalid alignment: {style.alignment}")

        if style.space_before < 0 or style.space_after < 0:
            errors.append("Spacing values cannot be negative")

        return errors

    def _validate_builder_specific(self, config: ContentConfig) -> list[str]:
        """Validate builder-specific configuration.

        Subclasses should override this for builder-specific validation.

        Args:
            config: Content configuration to validate

        Returns:
            List of builder-specific validation errors
        """
        return []

    def build_content(self, context: GenerationContext, config: ContentConfig) -> ContentBuildResult:
        """Build content flowables for this section.

        Template method that handles common concerns and delegates
        to subclass implementation.

        Args:
            context: Generation context
            config: Content configuration

        Returns:
            ContentBuildResult with flowables and metadata
        """
        try:
            # Validate inputs
            validation_errors = self.validate_config(config)
            if validation_errors:
                return ContentBuildResult(
                    success=False, error=f"Configuration validation failed: {'; '.join(validation_errors)}"
                )

            # Check if builder supports this recipe type
            if not self.supports_recipe_type(context.recipe.category):
                return ContentBuildResult(
                    success=False, error=f"Builder does not support recipe category: {context.recipe.category}"
                )

            # Build content using subclass implementation
            result = self._build_content_impl(context, config)

            # Validate flowables if enabled
            if self.cfg_dict.get("validate_flowables", False) and result.success:
                validation_errors = self._validate_flowables(result.flowables)
                if validation_errors:
                    result.success = False
                    result.error = f"Flowable validation failed: {'; '.join(validation_errors)}"

            # Estimate height if not provided and successful
            if result.success and result.estimated_height is None:
                result.estimated_height = self.estimate_height(context, config)

            # Log result
            if result.success:
                self.logger.debug(
                    "Built %s content: %d flowables, %.1fpt estimated height",
                    self.get_section_type(),
                    len(result.flowables),
                    result.estimated_height or 0,
                )
            else:
                self.logger.error("Failed to build %s content: %s", self.get_section_type(), result.error)

            return result

        except Exception as e:
            self.logger.exception("Error building content for section %s", self.get_section_type())
            return ContentBuildResult(success=False, error=f"Unexpected error: {e}")

    @abstractmethod
    def _build_content_impl(self, context: GenerationContext, config: ContentConfig) -> ContentBuildResult:
        """Implementation-specific content building logic.

        Subclasses must implement this to provide their content building logic.

        Args:
            context: Generation context
            config: Content configuration

        Returns:
            ContentBuildResult with generated content
        """
        pass

    def estimate_height(self, context: GenerationContext, config: ContentConfig) -> float:
        """Estimate height required for this section.

        Uses caching if enabled to avoid repeated calculations.

        Args:
            context: Generation context
            config: Content configuration

        Returns:
            Estimated height in points
        """
        # Check cache if enabled
        if self.cfg_dict.get("cache_height_estimates", True):
            cache_key = self._build_cache_key(context, config)
            if cache_key in self._height_cache:
                self.logger.debug("Height estimate cache hit for %s", self.get_section_type())
                return self._height_cache[cache_key]

        # Calculate height
        height = self._estimate_height_impl(context, config)

        # Cache result if enabled
        if self.cfg_dict.get("cache_height_estimates", True):
            self._height_cache[cache_key] = height

        return height

    @abstractmethod
    def _estimate_height_impl(self, context: GenerationContext, config: ContentConfig) -> float:
        """Implementation-specific height estimation.

        Subclasses must implement this to provide height estimates.

        Args:
            context: Generation context
            config: Content configuration

        Returns:
            Estimated height in points
        """
        pass

    def _build_cache_key(self, context: GenerationContext, config: ContentConfig) -> str:
        """Build cache key for this context and config.

        Args:
            context: Generation context
            config: Content configuration

        Returns:
            Cache key string
        """
        # Simple cache key based on recipe and basic config
        return f"{context.recipe.title}_{config.section.value}_{config.style.font_size}"

    def _validate_flowables(self, flowables: list[Any]) -> list[str]:
        """Validate generated flowables.

        Args:
            flowables: List of ReportLab flowables to validate

        Returns:
            List of validation errors
        """
        errors = []

        if not flowables:
            errors.append("No flowables generated")

        for i, flowable in enumerate(flowables):
            if flowable is None:
                errors.append(f"Flowable {i} is None")

        return errors

    def supports_recipe_type(self, recipe_category: str) -> bool:
        """Check if this builder supports recipes of the given category.

        Base implementation supports all categories.

        Args:
            recipe_category: Recipe category to check

        Returns:
            True if category is supported
        """
        return True  # Default: support all categories

    def get_dependencies(self) -> list[str]:
        """Get list of sections this builder depends on.

        Base implementation has no dependencies.

        Returns:
            List of section names this builder depends on
        """
        return []  # Default: no dependencies

    def can_split_across_pages(self) -> bool:
        """Check if this content can be split across pages.

        Base implementation assumes atomic sections.

        Returns:
            True if content can span multiple pages
        """
        return False  # Default: atomic sections

    def cleanup(self) -> None:
        """Clean up builder resources."""
        super().cleanup()
        self._height_cache.clear()
        self._style_cache.clear()
