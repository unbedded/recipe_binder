"""Core interfaces for PDF generation components.

This package defines the contracts that all PDF generation components must follow,
enabling clean separation of concerns and easy testing through dependency injection.
"""

from .content_builder import IContentBuilder
from .document_assembler import IDocumentAssembler
from .layout_strategy import ILayoutStrategy
from .style_manager import IStyleManager

__all__ = [
    "ILayoutStrategy",
    "IContentBuilder",
    "IStyleManager",
    "IDocumentAssembler",
]
