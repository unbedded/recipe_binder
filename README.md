# 🍳 Recipe Binder

**AI-Powered Recipe Cards for Professional Kitchens**

Transform your markdown recipes into beautiful, print-ready cards using OpenAI and intelligent build automation.

## 🤯 Why AI-Powered Recipes?

**The "WHY" hits you when you realize the power:**

- 📝 **Write Once**: Simple markdown recipe → OpenAI creates structured data with weights & nutrition
- 🔄 **Endless Variations**: Ask any AI to "scale this to 12 servings" or "make it vegan" - instant YAML updates  
- ⚖️ **Professional Precision**: Auto-converts volumes to weights (1 cup flour = 120g) for scale-based cooking
- 🧮 **Smart Calculations**: OpenAI knows ingredient densities, nutritional values, and cooking adjustments
- 🎨 **Perfect Cards**: Structured data → beautiful, consistent PDF cards every time

**From "random recipe blog post" to "professional kitchen-ready card" in seconds, with infinite AI-powered customization.**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![GitHub Actions](https://github.com/yourusername/recipe-binder/workflows/CI/badge.svg)](https://github.com/yourusername/recipe-binder/actions)

---

## ✨ Features

🤖 **AI-Powered Pipeline**: Automatically parse markdown recipes into structured YAML using OpenAI
🎨 **Professional Card Design**: Generate 8.5"×4" landscape, two-sided recipe cards optimized for professional kitchens
🔄 **Smart Build System**: Timestamp-based staleness detection - only rebuild what's changed
📐 **Template-Driven Layout**: Fully customizable card designs via YAML configuration
🎯 **Category Color Coding**: Visual organization with predefined color schemes for different recipe types
🛠️ **Developer-Friendly**: Type hints, comprehensive logging, full test coverage, and makefile automation

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/recipe-binder.git
cd recipe-binder
make install

# Generate demo cards
make demo

# View your first recipe card
open recipe/pdf/Breakfast-sample-pancakes.pdf
```

## 📋 Pipeline Architecture

Recipe Binder uses an intelligent 3-stage pipeline that automatically maintains your recipe collection:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Markdown      │───▶│      YAML        │───▶│       PDF       │
│   Source        │    │   Structured     │    │   Print-Ready   │
│   Recipes       │    │     Data         │    │     Cards       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
      Human               OpenAI Parsing         Template Engine
     Authored                + Schema              + ReportLab
```

### Smart Build Process
- **Staleness Detection**: Only processes files that are newer than their outputs
- **Error Recovery**: Graceful handling of OpenAI API issues with retry logic
- **Incremental Builds**: Process only what's changed, skip what's current
- **Clean Builds**: `make clean` removes all generated PDFs for fresh starts

## 🏗️ Project Structure

```
recipe-binder/
├── recipe/                 # Recipe data pipeline
│   ├── markdown/          # 📝 Source recipe files (.md)
│   ├── yaml/             # 🔄 Parsed structured data (.yaml)
│   ├── pdf/              # 📄 Generated recipe cards (.pdf)
│   ├── templates/        # 🎨 Card layout definitions (.yaml)
│   └── config/           # ⚙️  Global settings (.yaml)
├── src/recipe_fmt/        # Core Python package
│   ├── pipeline.py       # 🚀 Main orchestrator
│   ├── parsers/          # 🤖 Markdown → YAML conversion
│   ├── generators/       # 📄 YAML → PDF card generation
│   └── utils/            # 🔧 File utilities and helpers
├── tests/                # ✅ Comprehensive test suite
├── Makefile              # 🛠️  Build automation
└── pyproject.toml        # 📦 Python package configuration
```

## 🎨 Recipe Card Design

Professional-grade recipe cards designed for commercial kitchen use:

## Recipe Card Template Specifications
- **Size:** 8.5" × 4" landscape, two-sided
- **Margins:** 0.3" left/right, 0.15" top/bottom
- **Fonts:** Helvetica/Arial family
  - Title: 14-16pt bold white text
  - Category: 11-12pt bold white text  
  - Body: 11pt black text
  - Instructions: 12pt title, 11pt list

## Layout Rules
- **Front Page:** Header banner (0.4" tall) + Ingredient table
- **Back Page:** Instructions (forced page break after ingredient table)
- **Header Banner:** Category (right-aligned) + Title (center) with category color background
- **Ingredient Table:** 3 columns (Ingredient | Amount | Purpose) with dynamic column widths
- **Color Coding:** Use category colors from specification

## File Naming and Categories
- **PDF Files:** Automatically prefixed with category (e.g., `Breakfast-perfect-pancakes.pdf`)
- **Category Detection:** Always automatically inferred from recipe content by OpenAI
- **Category Override:** Edit the generated YAML file directly to change categories if needed

### Category Colors
Each category uses a distinct background color with bold white text for the header banner:

| Category    | Icon | Color        | Hex Code  | Sample Header |
|-------------|------|--------------|-----------|---------------|
| Meat        | 🥩   | Dark Brown   | `#5D4037` | <div style="background-color: #5D4037; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🥩 MEAT - Perfect Grilled Steak</div> |
| Side        | 🥗   | Forest Green | `#2E7D32` | <div style="background-color: #2E7D32; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🥗 SIDE - Roasted Vegetables</div> |
| Main        | 🍽️   | Green        | `#388E3C` | <div style="background-color: #388E3C; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🍽️ MAIN - Chicken Parmesan</div> |
| Soup        | 🍲   | Teal         | `#00897B` | <div style="background-color: #00897B; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🍲 SOUP - Tomato Basil Soup</div> |
| Sauce       | 🍯   | Amber        | `#FF8F00` | <div style="background-color: #FF8F00; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🍯 SAUCE - Hollandaise Sauce</div> |
| Breakfast   | 🥞   | Deep Orange  | `#EF6C00` | <div style="background-color: #EF6C00; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🥞 BREAKFAST - Perfect Pancakes</div> |
| Salad       | 🥬   | Dark Green   | `#1B5E20` | <div style="background-color: #1B5E20; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🥬 SALAD - Caesar Salad</div> |
| Baking      | 🍞   | Brown        | `#6D4C41` | <div style="background-color: #6D4C41; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🍞 BAKING - Sourdough Bread</div> |
| Dessert     | 🍰   | Purple       | `#6A1B9A` | <div style="background-color: #6A1B9A; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">🍰 DESSERT - Chocolate Cake</div> |
| Other       | 📝   | Blue Gray    | `#37474F` | <div style="background-color: #37474F; color: white; padding: 4px 8px; font-weight: bold; display: inline-block;">📝 OTHER - Special Recipe</div> |


## 🤖 OpenAI Integration

Intelligent parsing of natural language recipes into structured data:

### Features
- **Schema Validation**: Ensures consistent YAML output format
- **Error Handling**: Robust retry logic with exponential backoff
- **Cost Optimization**: Caches successful parses to avoid reprocessing
- **Fallback Support**: Manual YAML editing when AI parsing needs refinement

## 🚀 AI-Powered Recipe Flexibility

**The separated amount/unit schema unlocks incredible AI-powered recipe modification capabilities:**

### 🔄 Unit Conversion Made Easy
```bash
# Use ChatGPT/Claude to convert any recipe:
"Convert this pancake recipe to metric units"
"Change all measurements to weight-based (grams/ounces)"
"Convert Imperial to metric for European baking"
```

### 📏 Recipe Scaling & Substitution  
```bash
# AI can intelligently modify your YAML:
"Scale this recipe from 4 servings to 8 servings"
"Change 2 lbs carrots to 1.5 lbs and adjust other vegetables proportionally"  
"Convert this recipe for a smaller 6-inch cake pan"
"Substitute honey for sugar and adjust liquid accordingly"
```

### 🧮 Smart Modifications
- **Dietary Adaptations**: "Make this recipe vegan" or "Convert to gluten-free"
- **Precision Scaling**: Perfect ratios maintained when scaling up/down
- **Ingredient Swaps**: "Replace butter with olive oil" with automatic adjustments
- **Nutritional Optimization**: "Reduce sodium by 25%" with balanced replacements

**The Power**: Edit your generated YAML with any AI assistant for instant recipe modifications while maintaining the structured format for perfect PDF generation!

### 📐 Standardized Units & Weight Conversion
- **Tablespoons**: Always use `"TBL"` (not tbsp, tablespoon, etc.)
- **Teaspoons**: Always use `"tsp"` (not teaspoon, t, etc.)
- **Weight Display**: Option to show weights alongside measurements: `"2 cups (240g)"`
- **Professional Weighing**: Enable scale-based cooking without volume measurements
- **Consistency**: Ensures clean, professional PDF formatting

### ⚖️ Weight Conversion Feature
**Default ON** - Automatically converts volume/count measurements to grams:
- OpenAI generates `weight_grams` field during markdown→YAML conversion
- PDF displays: `"2 cups (240g)"` or weight-only mode: `"240g flour"`
- Enables professional kitchen workflows with digital scales
- Supports both volume + weight or weight-only display modes

### Example Transformation

**Markdown Input:**
```markdown
# Perfect Pancakes

A family favorite for weekend mornings.

## Ingredients
- 2 cups flour
- 2 tbsp sugar
- 2 tsp baking powder
- 1 cup milk
- 2 eggs, beaten

## Instructions
1. Mix dry ingredients in large bowl
2. Combine wet ingredients separately
3. Fold wet into dry until just combined
4. Cook on 375°F griddle until golden
```

**Generated YAML (automatically inferred category):**
```yaml
title: "Perfect Pancakes"
category: "Breakfast"  # ← Automatically detected by OpenAI
description: "A family favorite for weekend mornings"
servings: 4
prep_time: "10 minutes"
cook_time: "15 minutes"

ingredients:
  - ingredient: "all-purpose flour"
    amount: 2
    unit: "cups"
    weight_grams: 240  # Automatic conversion for weighing option
    purpose: "base"
  - ingredient: "granulated sugar"
    amount: 2
    unit: "TBL"
    weight_grams: 24
    purpose: "sweetener"
  - ingredient: "baking powder"
    amount: 2
    unit: "tsp"
    weight_grams: 8
    purpose: "leavening"
  - ingredient: "whole milk"
    amount: 1
    unit: "cup"
    weight_grams: 244
    purpose: "liquid"
  - ingredient: "large eggs"
    amount: 2
    unit: "whole"
    weight_grams: 100
    purpose: "binding"

# Future nutrition feature (placeholder)
nutrition:
  per_serving:
    calories: null      # Will be calculated from ingredients
    protein_g: null
    carbs_g: null
    fat_g: null
    fiber_g: null
    sodium_mg: null

instructions:
  - "Mix dry ingredients in large bowl"
  - "Combine wet ingredients separately"  
  - "Fold wet into dry until just combined"
  - "Cook on 375°F griddle until golden"
```

## 🛠️ Development

Built with modern Python best practices and comprehensive tooling:

### Technology Stack
- **Python 3.13+**: Latest language features and performance improvements
- **OpenAI API**: GPT-powered recipe parsing and structuring
- **ReportLab**: Professional PDF generation with precise layout control
- **Pydantic**: Runtime type validation and settings management
- **Click**: Elegant command-line interface construction

### Code Quality Tools
- **Ruff**: Lightning-fast linting and formatting
- **MyPy**: Static type checking for reliability
- **Pytest**: Comprehensive test suite with coverage reporting
- **Pre-commit**: Automated code quality checks on every commit

### Getting Started
```bash
# Development setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run quality checks
make lint        # Code formatting and linting
make typecheck   # Static type analysis
make test        # Full test suite with coverage
make build       # Process all recipes

# Clean rebuild
make clean       # Remove all generated PDFs
make build       # Regenerate everything
```

## 📖 Usage Examples

### Basic Workflow
```bash
# Add a new recipe
echo "# Chocolate Chip Cookies..." > recipe/markdown/cookies.md

# Process the pipeline (automatically detects new/changed files)
make build

# Your PDF card is ready!
open recipe/pdf/Dessert-cookies.pdf
```

### Advanced Usage
```bash
# Process only YAML → PDF (skip OpenAI parsing)
python -m recipe_fmt.pipeline --skip-parsing

# Generate specific recipes
python -m recipe_fmt.pipeline recipe/markdown/cookies.md

# Validate YAML schemas
python -m recipe_fmt.parsers.yaml_validator recipe/yaml/
```

## 🤝 Contributing

This project showcases modern Python development practices:

1. **Branch Strategy**: Feature branches with descriptive names
2. **Code Quality**: All code passes ruff, mypy, and pytest
3. **Documentation**: Comprehensive docstrings and type hints
4. **Testing**: >90% test coverage with edge case handling
5. **CI/CD**: GitHub Actions for automated testing and validation

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for professional kitchens and home cooks alike**

[Report Bug](https://github.com/yourusername/recipe-binder/issues) · [Request Feature](https://github.com/yourusername/recipe-binder/issues) · [Documentation](https://yourusername.github.io/recipe-binder/)

</div>
