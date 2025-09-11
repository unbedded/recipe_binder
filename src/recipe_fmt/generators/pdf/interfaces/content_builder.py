"""Interface for content section builders.

Defines the contract for building individual content sections like headers,
ingredients, instructions, etc. Each builder knows how to create ReportLab
flowables for its specific content type.
"""

from abc import ABC, abstractmethod

from ..types import ContentBuildResult, ContentConfig, GenerationContext


class IContentBuilder(ABC):
    """Interface for content section builders.

    Content builders are responsible for creating ReportLab flowables for
    specific sections of a recipe card (header, ingredients, instructions, etc.).
    Each builder focuses on one type of content and can be configured independently.
    """

    @abstractmethod
    def get_section_type(self) -> str:
        """Get the content section type this builder handles.

        Returns:
            String identifier for the section type (e.g., 'header', 'ingredients')
        """

    @abstractmethod
    def build_content(self, context: GenerationContext, config: ContentConfig) -> ContentBuildResult:
        """Build content flowables for this section.

        Args:
            context: Generation context with recipe and layout information
            config: Configuration specific to this content section

        Returns:
            Result containing flowables and build information
        """

    @abstractmethod
    def estimate_height(self, context: GenerationContext, config: ContentConfig) -> float:
        """Estimate the height this section will require.

        Args:
            context: Generation context with recipe and layout information
            config: Configuration specific to this content section

        Returns:
            Estimated height in points
        """

    @abstractmethod
    def validate_config(self, config: ContentConfig) -> list[str]:
        """Validate the content configuration for this builder.

        Args:
            config: Content configuration to validate

        Returns:
            List of validation error messages (empty if valid)
        """

    def supports_recipe_type(self, recipe_category: str) -> bool:
        """Check if this builder supports recipes of the given category.

        Args:
            recipe_category: Recipe category to check

        Returns:
            True if the category is supported (default: all categories)
        """
        return True

    def get_dependencies(self) -> list[str]:
        """Get list of other sections this builder depends on.

        Returns:
            List of section names that must be built before this one
        """
        return []

    def can_split_across_pages(self) -> bool:
        """Check if this content section can be split across multiple pages.

        Returns:
            True if the section supports page breaks within its content
        """
        return False  # Default: sections are atomic
