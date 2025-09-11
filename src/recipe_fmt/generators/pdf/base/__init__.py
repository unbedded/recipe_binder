"""Base classes providing common functionality for PDF generation components.

This package contains abstract base classes that provide shared functionality
and patterns used across the PDF generation system.
"""

from .base_content_builder import BaseContentBuilder
from .base_layout_strategy import BaseLayoutStrategy
from .base_style_manager import BaseStyleManager
from .component_base import ComponentBase

__all__ = [
    "ComponentBase",
    "BaseLayoutStrategy",
    "BaseContentBuilder",
    "BaseStyleManager",
]
