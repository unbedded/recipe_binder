"""Simple content builders extracted from PDFCardGenerator.

These classes contain the logic previously embedded in the monolithic
PDFCardGenerator class. They're simple extractions with no fancy patterns -
just better organization.
"""

from .header_builder import HeaderBuilder
from .ingredients_builder import IngredientsBuilder
from .instructions_builder import InstructionsBuilder
from .notes_builder import NotesBuilder
from .nutrition_builder import NutritionBuilder

__all__ = [
    "HeaderBuilder",
    "IngredientsBuilder",
    "InstructionsBuilder",
    "NotesBuilder",
    "NutritionBuilder",
]
