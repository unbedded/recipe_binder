"""Interface for PDF layout strategies.

Defines the contract for different layout implementations (two-sided, single-sided, etc.).
Each strategy knows how to organize content sections for its specific layout type.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..types import GenerationContext, LayoutConfig


class ILayoutStrategy(ABC):
    """Interface for PDF layout strategies.

    A layout strategy determines how content sections are organized and positioned
    on the PDF card. Different strategies handle different layout types like
    two-sided cards, single-sided cards, ingredient-only cards, etc.
    """

    @abstractmethod
    def get_layout_type(self) -> str:
        """Get the layout type this strategy handles.

        Returns:
            String identifier for the layout type
        """

    @abstractmethod
    def build_content(self, context: GenerationContext) -> list[Any]:
        """Build the complete content structure for this layout.

        Args:
            context: Generation context with recipe and configuration

        Returns:
            List of ReportLab flowables representing the complete layout
        """

    @abstractmethod
    def validate_config(self, config: LayoutConfig) -> list[str]:
        """Validate that the layout configuration is compatible with this strategy.

        Args:
            config: Layout configuration to validate

        Returns:
            List of validation error messages (empty if valid)
        """

    @abstractmethod
    def estimate_pages(self, context: GenerationContext) -> int:
        """Estimate the number of pages this layout will generate.

        Args:
            context: Generation context with recipe and configuration

        Returns:
            Estimated number of pages
        """

    @abstractmethod
    def get_required_sections(self) -> list[str]:
        """Get the list of content sections required by this layout.

        Returns:
            List of section names that this layout needs to generate
        """

    def supports_feature(self, feature: str) -> bool:
        """Check if this layout supports a specific feature.

        Args:
            feature: Feature name to check

        Returns:
            True if the feature is supported
        """
        return False  # Default: no optional features

    def get_section_order(self, page: int = 1) -> list[str]:
        """Get the order of sections for a specific page.

        Args:
            page: Page number (1-based)

        Returns:
            Ordered list of section names for the given page
        """
        return self.get_required_sections()  # Default: same order for all pages
