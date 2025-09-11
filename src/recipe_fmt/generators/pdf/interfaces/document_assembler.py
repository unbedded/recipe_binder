"""Interface for document assembly.

Defines the contract for assembling final PDF documents from content sections
and handling document-level concerns like page breaks, margins, and output.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..types import GenerationContext, GenerationResult


class IDocumentAssembler(ABC):
    """Interface for PDF document assembly.

    Document assemblers handle the final stage of PDF generation: taking
    content flowables from various builders and assembling them into a
    complete PDF document with proper page layout and output handling.
    """

    @abstractmethod
    def create_document(self, output_path: Path, context: GenerationContext) -> Any:
        """Create a new PDF document.

        Args:
            output_path: Path where the PDF will be saved
            context: Generation context with layout configuration

        Returns:
            ReportLab SimpleDocTemplate or similar document object
        """

    @abstractmethod
    def add_content(self, document: Any, flowables: list[Any]) -> None:
        """Add content flowables to the document.

        Args:
            document: Document object from create_document
            flowables: List of ReportLab flowables to add
        """

    @abstractmethod
    def finalize_document(self, document: Any, output_path: Path) -> GenerationResult:
        """Finalize and save the PDF document.

        Args:
            document: Document object with added content
            output_path: Path where the PDF should be saved

        Returns:
            GenerationResult with success status and metadata
        """

    @abstractmethod
    def estimate_file_size(self, flowables: list[Any]) -> int:
        """Estimate the file size of the final PDF.

        Args:
            flowables: Content that will be added to the document

        Returns:
            Estimated file size in bytes
        """

    def supports_compression(self) -> bool:
        """Check if this assembler supports PDF compression.

        Returns:
            True if compression is supported
        """
        return False  # Default: no compression

    def supports_metadata(self) -> bool:
        """Check if this assembler supports PDF metadata.

        Returns:
            True if metadata can be added to documents
        """
        return False  # Default: no metadata support

    @abstractmethod
    def set_metadata(self, document: Any, metadata: dict) -> None:
        """Set metadata for the PDF document.

        Args:
            document: Document object to add metadata to
            metadata: Dictionary of metadata key-value pairs
        """

    def validate_output_path(self, output_path: Path) -> list[str]:
        """Validate the output path for PDF generation.

        Args:
            output_path: Path to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        if not output_path.suffix.lower() == ".pdf":
            errors.append("Output path must have .pdf extension")
        if not output_path.parent.exists():
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")
        return errors
