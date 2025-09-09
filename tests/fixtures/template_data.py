"""Template configuration data for testing.

This module provides comprehensive template YAML configurations that can be used
across all template-related tests. Includes valid templates, invalid templates,
and edge cases for thorough testing coverage.
"""

from typing import Dict, Any, List
import copy

# Default Card Template - Standard recipe card configuration
DEFAULT_CARD_TEMPLATE = {
    "template_info": {
        "name": "Default Recipe Card",
        "version": "1.0",
        "description": "Standard recipe card template with balanced layout"
    },
    "card": {
        "size": {
            "width": 8.5,
            "height": 4.0,
            "orientation": "landscape"
        },
        "margins": {
            "top": 0.25,
            "bottom": 0.25,
            "left": 0.25,
            "right": 0.25
        },
        "layout": "two_sided"
    },
    "typography": {
        "title": {
            "font_name": "Helvetica-Bold",
            "font_size": 18,
            "alignment": "center",
            "color": "#000000",
            "space_after": 6
        },
        "category_banner": {
            "font_name": "Helvetica-Bold",
            "font_size": 12,
            "alignment": "center",
            "color": "white",
            "background": "category_color"
        },
        "section_header": {
            "font_name": "Helvetica-Bold",
            "font_size": 14,
            "alignment": "left",
            "space_before": 8,
            "space_after": 4
        },
        "metadata": {
            "font_name": "Helvetica",
            "font_size": 9,
            "alignment": "center",
            "color": "#666666",
            "space_after": 4
        },
        "description": {
            "font_name": "Helvetica-Oblique",
            "font_size": 10,
            "alignment": "center",
            "space_after": 6
        },
        "ingredient": {
            "font_name": "Helvetica",
            "font_size": 9,
            "alignment": "left",
            "space_after": 2
        },
        "instruction": {
            "font_name": "Helvetica",
            "font_size": 10,
            "alignment": "justify",
            "space_after": 3
        },
        "notes": {
            "font_name": "Helvetica-Oblique",
            "font_size": 9,
            "color": "#4D4D4D",
            "space_after": 2
        }
    },
    "display": {
        "show_weights": True,
        "show_purpose": True,
        "show_category_banner": True,
        "show_metadata": True,
        "show_description": True,
        "show_notes": True,
        "ingredients": {
            "columns": {
                "ingredient": {
                    "width": "50%",
                    "alignment": "left",
                    "label": "Ingredient"
                },
                "amount": {
                    "width": "15%",
                    "alignment": "right",
                    "label": "Amount"
                },
                "unit": {
                    "width": "10%",
                    "alignment": "left",
                    "label": "Unit"
                },
                "weight": {
                    "width": "15%",
                    "alignment": "right",
                    "label": "Weight",
                    "show_when": "weights_enabled"
                },
                "purpose": {
                    "width": "10%",
                    "alignment": "left",
                    "label": "Purpose",
                    "show_when": "purpose_enabled"
                }
            }
        }
    },
    "colors": {
        "category_colors": {
            "Meat": "#CC3333",
            "Breakfast": "#FFD700",
            "Dessert": "#FF69B4",
            "Vegetarian": "#32CD32",
            "Seafood": "#4682B4",
            "Appetizer": "#FF6347",
            "Soup": "#8B4513",
            "Salad": "#90EE90",
            "Side": "#DDA0DD",
            "Other": "#708090"
        },
        "text": {
            "primary": "#000000",
            "secondary": "#666666",
            "accent": "#333333"
        },
        "background": {
            "card": "#FFFFFF",
            "alternate_row": "#F5F5F5",
            "banner": "category_color"
        }
    },
    "layout_sections": {
        "front": [
            {"type": "category_banner", "height": 0.5},
            {"type": "title", "height": 0.8},
            {"type": "metadata", "height": 0.4},
            {"type": "description", "height": 0.6},
            {"type": "ingredients", "height": "remaining"}
        ],
        "back": [
            {"type": "instructions", "height": "75%"},
            {"type": "notes", "height": "25%"}
        ]
    }
}

# Compact Card Template - Space-efficient layout
COMPACT_CARD_TEMPLATE = {
    "template_info": {
        "name": "Compact Recipe Card", 
        "version": "1.1",
        "description": "Space-efficient template with smaller fonts and tighter spacing"
    },
    "card": {
        "size": {
            "width": 6.0,
            "height": 4.0,
            "orientation": "landscape"
        },
        "margins": {
            "top": 0.125,
            "bottom": 0.125,
            "left": 0.125,
            "right": 0.125
        },
        "layout": "single_sided"
    },
    "typography": {
        "title": {
            "font_name": "Helvetica-Bold",
            "font_size": 14,
            "alignment": "center",
            "space_after": 3
        },
        "category_banner": {
            "font_name": "Helvetica-Bold",
            "font_size": 10,
            "alignment": "center",
            "color": "white"
        },
        "section_header": {
            "font_name": "Helvetica-Bold", 
            "font_size": 11,
            "space_before": 4,
            "space_after": 2
        },
        "ingredient": {
            "font_name": "Helvetica",
            "font_size": 8,
            "space_after": 1
        },
        "instruction": {
            "font_name": "Helvetica",
            "font_size": 8,
            "space_after": 2
        }
    },
    "display": {
        "show_weights": False,
        "show_purpose": False,
        "show_category_banner": True,
        "show_metadata": False,
        "show_description": False,
        "show_notes": False
    }
}

# Minimal Card Template - Bare bones layout
MINIMAL_CARD_TEMPLATE = {
    "template_info": {
        "name": "Minimal Recipe Card",
        "version": "1.0", 
        "description": "Minimal template with only essential elements"
    },
    "card": {
        "size": {
            "width": 5.0,
            "height": 3.0,
            "orientation": "landscape"
        },
        "margins": {
            "top": 0.1,
            "bottom": 0.1,
            "left": 0.1,
            "right": 0.1
        },
        "layout": "ingredients_only"
    },
    "typography": {
        "title": {
            "font_name": "Helvetica",
            "font_size": 12,
            "alignment": "left"
        },
        "ingredient": {
            "font_name": "Helvetica",
            "font_size": 8
        }
    },
    "display": {
        "show_weights": False,
        "show_purpose": False,
        "show_category_banner": False,
        "show_metadata": False,
        "show_description": False,
        "show_notes": False
    }
}

# Large Format Template - For detailed recipes
LARGE_FORMAT_TEMPLATE = {
    "template_info": {
        "name": "Large Format Recipe Card",
        "version": "1.0",
        "description": "Large format template for complex recipes with detailed instructions"
    },
    "card": {
        "size": {
            "width": 11.0,
            "height": 8.5,
            "orientation": "landscape"
        },
        "margins": {
            "top": 0.5,
            "bottom": 0.5,
            "left": 0.5,
            "right": 0.5
        },
        "layout": "two_sided"
    },
    "typography": {
        "title": {
            "font_name": "Times-Bold",
            "font_size": 24,
            "alignment": "center",
            "space_after": 12
        },
        "category_banner": {
            "font_name": "Times-Bold",
            "font_size": 16,
            "alignment": "center",
            "color": "white"
        },
        "section_header": {
            "font_name": "Times-Bold",
            "font_size": 18,
            "space_before": 12,
            "space_after": 6
        },
        "ingredient": {
            "font_name": "Times",
            "font_size": 12,
            "space_after": 3
        },
        "instruction": {
            "font_name": "Times",
            "font_size": 12,
            "alignment": "justify",
            "space_after": 4
        }
    },
    "display": {
        "show_weights": True,
        "show_purpose": True,
        "show_category_banner": True,
        "show_metadata": True,
        "show_description": True,
        "show_notes": True
    }
}

# Invalid Template Data - For error testing
INVALID_TEMPLATE_DATA = {
    "missing_template_info": {
        # Missing template_info section
        "card": {
            "size": {"width": 8.5, "height": 4.0}
        }
    },
    "invalid_dimensions": {
        "template_info": {"name": "Invalid Dimensions"},
        "card": {
            "size": {
                "width": 0,  # Invalid - zero width
                "height": -1  # Invalid - negative height
            }
        }
    },
    "invalid_margins": {
        "template_info": {"name": "Invalid Margins"},
        "card": {
            "margins": {
                "top": -0.5,  # Invalid - negative margin
                "bottom": "invalid"  # Invalid - wrong type
            }
        }
    },
    "invalid_font_sizes": {
        "template_info": {"name": "Invalid Font Sizes"},
        "typography": {
            "title": {
                "font_size": 0  # Invalid - zero font size
            },
            "ingredient": {
                "font_size": -10  # Invalid - negative font size
            }
        }
    },
    "invalid_alignment": {
        "template_info": {"name": "Invalid Alignment"},
        "typography": {
            "title": {
                "alignment": "invalid_alignment"  # Invalid alignment value
            }
        }
    },
    "invalid_layout_type": {
        "template_info": {"name": "Invalid Layout"},
        "card": {
            "layout": "nonexistent_layout"  # Invalid layout type
        }
    },
    "malformed_yaml": "invalid: yaml: content: [unclosed",
    "non_dict_root": ["this", "is", "a", "list", "not", "dict"],
    "empty_template": {},
    "unicode_issues": {
        "template_info": {"name": "Unicode Test \x00\x01\x02"},  # Control characters
        "invalid_unicode": "\udcff\udcfe"  # Invalid surrogate pairs
    }
}

# Edge Case Template Data - For boundary testing
EDGE_CASE_TEMPLATES = {
    "maximum_values": {
        "template_info": {
            "name": "A" * 100,  # Very long name
            "version": "99.99.99",
            "description": "X" * 500  # Very long description
        },
        "card": {
            "size": {
                "width": 50.0,  # Very large width
                "height": 50.0,  # Very large height
            },
            "margins": {
                "top": 5.0,  # Large margins
                "bottom": 5.0,
                "left": 5.0,
                "right": 5.0
            }
        },
        "typography": {
            "title": {
                "font_size": 72,  # Very large font
                "space_before": 50,
                "space_after": 50
            }
        }
    },
    "minimum_values": {
        "template_info": {
            "name": "A",  # Single character name
            "version": "1",
            "description": "X"  # Single character description
        },
        "card": {
            "size": {
                "width": 1.0,  # Minimum width
                "height": 1.0,  # Minimum height
            },
            "margins": {
                "top": 0.01,  # Tiny margins
                "bottom": 0.01,
                "left": 0.01,
                "right": 0.01
            }
        },
        "typography": {
            "title": {
                "font_size": 1,  # Tiny font
                "space_before": 0,
                "space_after": 0
            }
        }
    },
    "unicode_template": {
        "template_info": {
            "name": "Recette Café ☕",
            "description": "Template with unicode: ½ ¼ ¾ ° ™ ® €"
        },
        "card": {
            "size": {"width": 8.5, "height": 4.0}
        },
        "colors": {
            "category_colors": {
                "Café": "#8B4513",
                "Dessért": "#FF69B4"
            }
        }
    }
}

# Template with All Layout Types - For layout testing
ALL_LAYOUT_TYPES = {
    "two_sided": {
        "template_info": {"name": "Two Sided Layout"},
        "card": {"layout": "two_sided"}
    },
    "single_sided": {
        "template_info": {"name": "Single Sided Layout"},
        "card": {"layout": "single_sided"}
    },
    "ingredients_only": {
        "template_info": {"name": "Ingredients Only Layout"},
        "card": {"layout": "ingredients_only"}
    },
    "instructions_only": {
        "template_info": {"name": "Instructions Only Layout"}, 
        "card": {"layout": "instructions_only"}
    }
}

# Collection of all template data
ALL_TEMPLATE_DATA = {
    "default_card": DEFAULT_CARD_TEMPLATE,
    "compact_card": COMPACT_CARD_TEMPLATE,
    "minimal_card": MINIMAL_CARD_TEMPLATE,
    "large_format": LARGE_FORMAT_TEMPLATE,
    **INVALID_TEMPLATE_DATA,
    **EDGE_CASE_TEMPLATES,
    **ALL_LAYOUT_TYPES
}

def get_template_data(template_name: str) -> Dict[str, Any]:
    """Get template data by name.
    
    Args:
        template_name: Name of the template to retrieve
        
    Returns:
        Template data dictionary
        
    Raises:
        KeyError: If template name not found
    """
    if template_name not in ALL_TEMPLATE_DATA:
        raise KeyError(f"Template '{template_name}' not found. Available: {list(ALL_TEMPLATE_DATA.keys())}")
    
    return copy.deepcopy(ALL_TEMPLATE_DATA[template_name])

def get_valid_template_names() -> List[str]:
    """Get list of valid template names (excluding invalid/error test cases).
    
    Returns:
        List of valid template names
    """
    valid_names = [
        "default_card",
        "compact_card", 
        "minimal_card",
        "large_format",
        "two_sided",
        "single_sided",
        "ingredients_only",
        "instructions_only",
        "unicode_template"
    ]
    return valid_names

def get_invalid_template_names() -> List[str]:
    """Get list of invalid template names for error testing.
    
    Returns:
        List of invalid template names
    """
    return [
        "missing_template_info",
        "invalid_dimensions",
        "invalid_margins", 
        "invalid_font_sizes",
        "invalid_alignment",
        "invalid_layout_type",
        "malformed_yaml",
        "non_dict_root",
        "empty_template",
        "unicode_issues"
    ]

def get_edge_case_template_names() -> List[str]:
    """Get list of edge case template names for boundary testing.
    
    Returns:
        List of edge case template names
    """
    return [
        "maximum_values",
        "minimum_values",
        "unicode_template"
    ]

def create_template_variations() -> Dict[str, Dict[str, Any]]:
    """Create template variations for parameterized testing.
    
    Returns:
        Dictionary of template variations
    """
    variations = {}
    
    # Different card sizes
    sizes = [
        (3.5, 2.5),  # Business card
        (4.0, 6.0),  # Index card portrait
        (6.0, 4.0),  # Index card landscape
        (8.5, 11.0), # Letter portrait
        (11.0, 8.5), # Letter landscape
        (8.5, 4.0),  # Half letter landscape
    ]
    
    for i, (width, height) in enumerate(sizes):
        template = copy.deepcopy(DEFAULT_CARD_TEMPLATE)
        template["template_info"]["name"] = f"Size Variation {width}x{height}"
        template["card"]["size"]["width"] = width
        template["card"]["size"]["height"] = height
        variations[f"size_{i}"] = template
    
    # Different font sizes
    font_sizes = [6, 8, 10, 12, 14, 16, 18, 20, 24]
    for size in font_sizes:
        template = copy.deepcopy(DEFAULT_CARD_TEMPLATE)
        template["template_info"]["name"] = f"Font Size {size}"
        template["typography"]["title"]["font_size"] = size
        variations[f"font_{size}"] = template
    
    # Different margin sizes
    margins = [0.0, 0.125, 0.25, 0.5, 0.75, 1.0]
    for margin in margins:
        template = copy.deepcopy(DEFAULT_CARD_TEMPLATE)
        template["template_info"]["name"] = f"Margin {margin}"
        template["card"]["margins"]["top"] = margin
        template["card"]["margins"]["bottom"] = margin
        template["card"]["margins"]["left"] = margin
        template["card"]["margins"]["right"] = margin
        variations[f"margin_{margin}"] = template
    
    return variations

def create_color_scheme_variations() -> Dict[str, Dict[str, Any]]:
    """Create template variations with different color schemes.
    
    Returns:
        Dictionary of color scheme variations
    """
    color_schemes = {
        "grayscale": {
            "Meat": "#333333",
            "Breakfast": "#666666",
            "Dessert": "#999999",
            "Vegetarian": "#CCCCCC",
            "Other": "#555555"
        },
        "bright": {
            "Meat": "#FF0000",
            "Breakfast": "#FFFF00",
            "Dessert": "#FF00FF",
            "Vegetarian": "#00FF00",
            "Other": "#0000FF"
        },
        "pastel": {
            "Meat": "#FFB3BA",
            "Breakfast": "#FFFFBA",
            "Dessert": "#FFDFBA",
            "Vegetarian": "#BAFFC9",
            "Other": "#BAE1FF"
        }
    }
    
    variations = {}
    for scheme_name, colors in color_schemes.items():
        template = copy.deepcopy(DEFAULT_CARD_TEMPLATE)
        template["template_info"]["name"] = f"Color Scheme {scheme_name.title()}"
        template["colors"]["category_colors"].update(colors)
        variations[scheme_name] = template
    
    return variations

# Template file content for file I/O testing
TEMPLATE_FILE_CONTENT = {
    name: f"# Template: {name}\n" + 
          f"# Auto-generated YAML content for {template.get('template_info', {}).get('name', 'Unknown Template')}\n" +
          f"template_info:\n  name: {template.get('template_info', {}).get('name', 'Test Template')}\n"
    for name, template in ALL_TEMPLATE_DATA.items() 
    if isinstance(template, dict) and 'template_info' in template
}