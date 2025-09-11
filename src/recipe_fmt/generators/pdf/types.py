"""Shared types and data structures for PDF generation components.

This module defines the core data types used across the refactored PDF generation
system, providing type safety and clear contracts between components.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

try:
    from reportlab.lib.colors import Color
    from reportlab.platypus import Flowable

    REPORTLAB_AVAILABLE = True
except ImportError:
    # Mock types when ReportLab is not available
    Color = Any
    Flowable = Any
    REPORTLAB_AVAILABLE = False

from ...models.recipe import Recipe


class LayoutType(Enum):
    """Supported PDF layout types."""

    TWO_SIDED = "two_sided"
    SINGLE_SIDED = "single_sided"
    INGREDIENTS_ONLY = "ingredients_only"
    INSTRUCTIONS_ONLY = "instructions_only"


# Removed complex TableType - we're using simple content builders instead


class ContentSection(Enum):
    """Recipe content sections."""

    HEADER = "header"
    BANNER = "banner"
    INGREDIENTS = "ingredients"
    INSTRUCTIONS = "instructions"
    NOTES = "notes"
    METADATA = "metadata"
    NUTRITION = "nutrition"


@dataclass
class Dimensions:
    """Dimensional specifications in points."""

    width: float
    height: float

    def to_inches(self) -> tuple[float, float]:
        """Convert to inches (72 points per inch)."""
        return self.width / 72.0, self.height / 72.0


@dataclass
class Margins:
    """Margin specifications in points."""

    top: float = 18.0  # 0.25 inches
    bottom: float = 18.0
    left: float = 18.0
    right: float = 18.0

    @classmethod
    def from_inches(cls, inches: float) -> "Margins":
        """Create uniform margins from inches."""
        points = inches * 72.0
        return cls(top=points, bottom=points, left=points, right=points)


@dataclass
class ColumnSpec:
    """Column specification for tables."""

    width: float | str = "auto"
    alignment: str = "left"
    label: str = ""
    format_func: str | None = None
    show_condition: str | None = None


@dataclass
class StyleSpec:
    """Typography style specification."""

    font_name: str = "Helvetica"
    font_size: int = 10
    alignment: str = "left"
    color: str | Color = "black"
    space_before: float = 0.0
    space_after: float = 0.0
    background: str | Color | None = None


# Removed complex TableConfig - using simple ContentConfig instead


@dataclass
class LayoutConfig:
    """Configuration for layout generation."""

    layout_type: LayoutType
    card_dimensions: Dimensions = field(default_factory=lambda: Dimensions(612.0, 288.0))  # 8.5"×4"
    margins: Margins = field(default_factory=lambda: Margins.from_inches(0.25))
    show_category_banner: bool = True
    show_metadata: bool = True
    show_nutrition: bool = True


@dataclass
class ContentConfig:
    """Configuration for content building."""

    section: ContentSection
    style: StyleSpec = field(default_factory=StyleSpec)
    show_section: bool = True
    custom_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationContext:
    """Context object passed between generation components."""

    recipe: Recipe
    layout_config: LayoutConfig
    available_width: float
    available_height: float
    current_page: int = 1

    # Calculated dimensions
    content_width: float = field(init=False)
    content_height: float = field(init=False)

    def __post_init__(self) -> None:
        """Calculate content dimensions from layout config."""
        margins = self.layout_config.margins
        self.content_width = self.layout_config.card_dimensions.width - margins.left - margins.right
        self.content_height = self.layout_config.card_dimensions.height - margins.top - margins.bottom


@dataclass
class GenerationResult:
    """Result of PDF generation operation."""

    success: bool
    output_path: Path | None = None
    error: str | None = None
    pages_generated: int = 0
    file_size_bytes: int | None = None
    generation_time_seconds: float | None = None

    # Component-specific metrics
    tables_generated: int = 0
    sections_built: int = 0
    styles_applied: int = 0


# Removed complex TableGenerationResult - using simple ContentBuildResult instead


@dataclass
class ContentBuildResult:
    """Result of content section building."""

    success: bool
    flowables: list[Any] = field(default_factory=list)  # List of ReportLab flowables
    error: str | None = None
    estimated_height: float | None = None
    style_used: StyleSpec | None = None


class ComponentConfig(Protocol):
    """Protocol for component configuration objects."""

    def get_cfg(self) -> dict[str, Any]:
        """Return configuration as dictionary."""
        ...


@dataclass
class ValidationResult:
    """Result of component validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
