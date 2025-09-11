# User Manual

Complete guide to using Recipe Binder for creating professional recipe cards with AI-powered automation.

## 📚 Table of Contents

1. [Quick Start](#-quick-start)
2. [Creating Recipes](#-creating-recipes)
3. [Recipe Processing Pipeline](#-recipe-processing-pipeline)
4. [Customizing Output](#-customizing-output)
5. [Batch Processing](#-batch-processing)
6. [Advanced Features](#-advanced-features)
7. [Troubleshooting](#-troubleshooting)

**Professional recipe cards with precise weights and nutrition facts:**

| Front Side (Ingredients & Nutrition) | Back Side (Instructions) |
|:---:|:---:|
| ![Recipe Front](docs/recipe_front.png) | ![Recipe Back](docs/recipe_back.png) |

*Example: Garlic Herb Bread with auto-calculated weights (grams) and USDA nutrition data*

## 🚀 Quick Start

### Your First Recipe

1. **Create a markdown file** in `recipe/markdown/`:

```markdown
# Chocolate Chip Cookies

Perfect cookies for any occasion!

## Ingredients
- 2 cups all-purpose flour
- 1 tsp baking soda
- 1 tsp salt
- 1 cup butter, softened
- 3/4 cup granulated sugar
- 3/4 cup brown sugar, packed
- 2 large eggs
- 2 tsp vanilla extract
- 2 cups chocolate chips

## Instructions
1. Preheat oven to 375°F
2. Mix flour, baking soda, and salt in bowl
3. Cream butter and sugars until fluffy
4. Beat in eggs and vanilla
5. Gradually blend in flour mixture
6. Stir in chocolate chips
7. Drop onto ungreased cookie sheets
8. Bake 9-11 minutes until golden brown

## Notes
- Makes about 5 dozen cookies
- Store in airtight container
```

2. **Process the recipe**:
```bash
python -m recipe_fmt.pipeline recipe/markdown/chocolate-chip-cookies.md
```

3. **View your recipe card**:
```bash
open recipe/pdf/Dessert-chocolate-chip-cookies.pdf
```

That's it! You now have a professional recipe card with nutrition facts, proper formatting, and print-ready layout.

## 📝 Creating Recipes

### Markdown Format Requirements

Recipe Binder uses a specific markdown structure that OpenAI parses into structured data:

#### Required Sections

```markdown
# Recipe Title

Brief description (optional)

## Ingredients
- ingredient 1
- ingredient 2
- etc.

## Instructions
1. Step one
2. Step two
3. etc.
```

#### Optional Sections

```markdown
## Notes
- Storage instructions
- Serving suggestions
- Variations

## Tips
- Professional cooking tips
- Timing advice
- Equipment recommendations
```

### Writing Tips for Better AI Parsing

#### ✅ Good Examples
```markdown
## Ingredients
- 2 cups all-purpose flour
- 1 tablespoon olive oil
- 1/2 teaspoon salt
- 3 large eggs, beaten
- 1 pound chicken breast, diced
```

#### ❌ Avoid These Patterns
```markdown
## Ingredients
- flour (about 2 cups, maybe more)
- some oil
- salt to taste
- eggs (however many you have)
- chicken (cut up)
```

#### Best Practices
1. **Use specific measurements**: "2 cups" not "some"
2. **Include preparation details**: "diced", "beaten", "softened"
3. **Use standard units**: cups, tablespoons, teaspoons, pounds, ounces
4. **Be consistent with naming**: "all-purpose flour" not "flour" then "AP flour"
5. **Include cooking temperatures and times**: "375°F for 20 minutes"

## 🔄 Recipe Processing Pipeline

### Understanding the 3-Stage Process

```
Markdown → YAML → PDF
   ↓         ↓      ↓
 Human    OpenAI  Template
Content  Parsing  Engine
```

#### Stage 1: Markdown → YAML (AI Processing)
- **Input**: Your markdown recipe
- **Process**: OpenAI GPT-4o-mini parses and structures
- **Output**: Structured YAML with weights, categories, nutrition
- **Time**: ~10-30 seconds per recipe

#### Stage 2: YAML Enhancement (Optional)
- **Input**: Generated YAML file
- **Process**: Manual editing or nutrition calculation
- **Output**: Enhanced YAML with custom modifications
- **Time**: Manual (as needed)

#### Stage 3: YAML → PDF (Template Engine)
- **Input**: Structured YAML data
- **Process**: ReportLab generates professional cards
- **Output**: Print-ready PDF recipe cards
- **Time**: ~2-5 seconds per recipe

### Processing Commands

#### Single Recipe
```bash
# Process one recipe through entire pipeline
python -m recipe_fmt.pipeline recipe/markdown/your-recipe.md

# Process only to YAML (skip PDF generation)
python -m recipe_fmt.pipeline --yaml-only recipe/markdown/your-recipe.md

# Generate PDF from existing YAML
python -m recipe_fmt.pipeline --pdf-only recipe/yaml/your-recipe.yaml
```

#### Multiple Recipes
```bash
# Process all recipes
make build

# Process only changed recipes (incremental)
make build  # Automatically detects staleness

# Force rebuild all
make clean && make build
```

### File Organization

Recipe Binder maintains a clean directory structure:

```
recipe/
├── markdown/           # Your source files
│   ├── breakfast-pancakes.md
│   ├── dinner-pasta.md
│   └── dessert-cookies.md
├── yaml/              # Generated structured data
│   ├── Breakfast-breakfast-pancakes.yaml
│   ├── Main-dinner-pasta.yaml
│   └── Dessert-dessert-cookies.yaml
└── pdf/               # Final recipe cards
    ├── Breakfast-breakfast-pancakes.pdf
    ├── Main-dinner-pasta.pdf
    └── Dessert-dessert-cookies.pdf
```

**File Naming Convention**: `{Category}-{original-filename}.{ext}`

## 🎨 Customizing Output

### Understanding Recipe Categories

OpenAI automatically categorizes recipes into one of 10 predefined categories:

| Category | Color | Use For |
|----------|-------|---------|
| 🥞 Breakfast | Amber | Pancakes, eggs, cereals, morning pastries |
| 🍽️ Main | Royal Blue | Dinner entrees, substantial lunch dishes |
| 🥗 Side | Teal | Vegetables, starches, salads accompanying mains |
| 🥩 Meat | Deep Red | Beef, pork, lamb preparations |
| 🍲 Soup | Burnt Orange | Soups, stews, broths, chilis |
| 🥬 Salad | Leaf Green | Fresh salads, slaws, cold preparations |
| 🍯 Sauce | Indigo | Sauces, dressings, marinades, condiments |
| 🍞 Baking | Chocolate Brown | Breads, rolls, baked goods (non-dessert) |
| 🍰 Dessert | Raspberry | Cakes, cookies, candies, sweet treats |
| 📝 Other | Dark Gray | Beverages, preserves, unusual categories |

### Modifying Generated YAML

After AI processing, you can manually edit YAML files for customization:

#### Example YAML Structure
```yaml
title: "Perfect Chocolate Chip Cookies"
category: "Dessert"  # Change category here
description: "Perfect cookies for any occasion!"
servings: 48
prep_time: "15 minutes"
cook_time: "10 minutes"

ingredients:
  - ingredient: "all-purpose flour"
    amount: 2
    unit: "cups"
    weight_grams: 240
    purpose: "base"

nutrition:  # Add/modify nutrition facts
  per_serving:
    calories: 150
    protein_g: 2
    carbs_g: 20
    fat_g: 7
    fiber_g: 1
    sodium_mg: 95

instructions:
  - "Preheat oven to 375°F (190°C)"
  - "Mix flour, baking soda, and salt in medium bowl"
  # ... more steps
```

#### Common Customizations

1. **Change Category**:
```yaml
category: "Breakfast"  # Will change header color and prefix
```

2. **Adjust Servings**:
```yaml
servings: 24  # Half the recipe, nutrition auto-adjusts per serving
```

3. **Add Custom Notes**:
```yaml
notes:
  - "Best served warm with milk"
  - "Store in airtight container for up to 1 week"
  - "Can freeze dough balls for up to 3 months"
```

4. **Modify Nutrition**:
```yaml
nutrition:
  per_serving:
    calories: 180  # Manual override
    protein_g: 3
    # ... other values
```

### Weight Display Options

Recipe Binder automatically converts volume measurements to weights for professional kitchens:

#### Volume + Weight (Default)
```
2 cups (240g) all-purpose flour
1 TBL (15ml) olive oil
```

#### Weight Only Mode
Edit the YAML to remove unit/amount and use only weight_grams:
```yaml
ingredients:
  - ingredient: "all-purpose flour"
    amount: 240
    unit: "g"
    weight_grams: 240
```

## 📊 Batch Processing

### Processing Large Recipe Collections

#### Parallel Processing
```bash
# Process multiple recipes simultaneously
make build -j4  # Use 4 parallel jobs

# Custom parallel processing
find recipe/markdown -name "*.md" | xargs -P 4 -I {} python -m recipe_fmt.pipeline {}
```

#### Selective Processing
```bash
# Process only breakfast recipes
find recipe/markdown -name "*breakfast*" -o -name "*pancake*" | xargs python -m recipe_fmt.pipeline

# Process recipes modified in last day
find recipe/markdown -mtime -1 -name "*.md" | xargs python -m recipe_fmt.pipeline
```

### Managing Recipe Collections

#### Organization Strategies

1. **By Category**:
```
recipe/markdown/
├── breakfast/
├── mains/
├── sides/
└── desserts/
```

2. **By Source**:
```
recipe/markdown/
├── family-recipes/
├── restaurant-collection/
└── seasonal-specials/
```

3. **By Difficulty**:
```
recipe/markdown/
├── quick-30min/
├── weekend-projects/
└── advanced-techniques/
```

#### Batch Operations

```bash
# Add nutrition to all existing recipes
find recipe/yaml -name "*.yaml" | xargs python -m recipe_fmt.nutrition

# Regenerate all PDFs with updated template
rm recipe/pdf/*.pdf && make build

# Export all recipes to different format
# (Custom script example)
for yaml in recipe/yaml/*.yaml; do
    python custom_exporter.py "$yaml"
done
```

## 🔧 Advanced Features

### Nutrition Calculation

#### Automatic USDA Integration
```bash
# Add nutrition to single recipe
python -m recipe_fmt.nutrition recipe/yaml/cookies.yaml

# Add nutrition to all recipes
python -m recipe_fmt.nutrition recipe/yaml/*.yaml

# Preview nutrition without saving
python -m recipe_fmt.nutrition --dry-run recipe/yaml/cookies.yaml
```

#### Manual Nutrition Override
```yaml
nutrition:
  per_serving:
    calories: 250  # Your custom values
    protein_g: 4
    carbs_g: 35
    fat_g: 10
    fiber_g: 2
    sodium_mg: 180
```

### Template Customization

#### Current Template Features
- **Layout**: 8.5"×11" portrait, two-sided
- **Typography**: Helvetica family with size hierarchy
- **Colors**: Category-specific header backgrounds
- **Sections**: Header, ingredients table, instructions, nutrition facts

#### Template Modifications
Edit `recipe/templates/default-card.yaml` for layout changes:

```yaml
# Example customizations
fonts:
  title_size: 18  # Larger title
  body_size: 12   # Larger body text

colors:
  custom_category:
    background: "#FF6B35"  # Custom orange
    text: "white"

layout:
  margins:
    top: 0.2
    sides: 0.25
```

### AI Prompt Customization

For advanced users, you can modify the OpenAI parsing behavior by editing the system prompts in the source code. See `src/recipe_fmt/parsers/markdown_parser.py` for the current prompt templates.

### Integration with Other Tools

#### Export Formats
```python
# Custom export script example
import yaml
from pathlib import Path

def export_to_json(yaml_file):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    
    json_file = yaml_file.with_suffix('.json')
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

# Usage
for yaml_path in Path('recipe/yaml').glob('*.yaml'):
    export_to_json(yaml_path)
```

#### Recipe Database Integration
```python
# Example: Import into SQLite database
import sqlite3
import yaml

conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY,
        title TEXT,
        category TEXT,
        servings INTEGER,
        prep_time TEXT,
        cook_time TEXT,
        ingredients TEXT,
        instructions TEXT
    )
''')

# Import all recipes
for yaml_file in Path('recipe/yaml').glob('*.yaml'):
    with open(yaml_file) as f:
        recipe = yaml.safe_load(f)
    
    cursor.execute('''
        INSERT INTO recipes (title, category, servings, prep_time, cook_time, ingredients, instructions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        recipe['title'],
        recipe['category'],
        recipe['servings'],
        recipe.get('prep_time', ''),
        recipe.get('cook_time', ''),
        yaml.dump(recipe['ingredients']),
        yaml.dump(recipe['instructions'])
    ))

conn.commit()
```

## 🖨️ Printing and Distribution

### Print Setup

#### Single Recipe
```bash
# Print with optimal settings
lpr -o ColorModel=CMYK -o sides=two-sided-long-edge -o print-quality=4 recipe/pdf/Dessert-cookies.pdf
```

#### Batch Printing
```bash
# Print all recipes
make print

# Print specific category
lpr -o ColorModel=CMYK -o sides=two-sided-long-edge recipe/pdf/Breakfast-*.pdf
```

### Print Quality Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `ColorModel=CMYK` | Color printing | Full color headers and design |
| `sides=two-sided-long-edge` | Duplex printing | Instructions on back |
| `print-quality=4` | High quality | Crisp text and graphics |

### Digital Distribution

#### PDF Optimization
```bash
# Optimize PDFs for web sharing (requires ghostscript)
gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/screen -sOutputFile=web-optimized.pdf original.pdf
```

#### Recipe Card Collections
```bash
# Combine multiple recipes into single PDF
pdftk recipe/pdf/Breakfast-*.pdf cat output breakfast-collection.pdf

# Or create categorized collections
for category in Breakfast Main Side Dessert; do
    pdftk recipe/pdf/${category}-*.pdf cat output ${category}-collection.pdf
done
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Recipe Not Parsing Correctly

**Problem**: OpenAI generates incorrect ingredient amounts or categories

**Solutions**:
```bash
# Try more specific ingredient descriptions
# Instead of: "flour"
# Use: "2 cups all-purpose flour"

# Check for unusual formatting
# Ensure ingredients use standard units
# Use "TBL" for tablespoons, "tsp" for teaspoons

# Manual YAML editing
# Edit the generated YAML file directly
vim recipe/yaml/Your-recipe.yaml
```

#### 2. Missing Nutrition Data

**Problem**: Nutrition section shows placeholder data

**Solutions**:
```bash
# Verify USDA API key is set
echo $USDA_API_KEY

# Add nutrition manually
python -m recipe_fmt.nutrition recipe/yaml/your-recipe.yaml

# Check for ingredient name matching
# USDA database uses specific names
# "all-purpose flour" works better than "flour"
```

#### 3. PDF Formatting Issues

**Problem**: Text cutoff, weird spacing, or layout problems

**Solutions**:
```bash
# Regenerate PDF
rm recipe/pdf/problematic-recipe.pdf
python -m recipe_fmt.pipeline --pdf-only recipe/yaml/problematic-recipe.yaml

# Check ingredient list length
# Very long ingredient lists may cause formatting issues
# Consider breaking into multiple recipes

# Verify YAML structure
python -c "
import yaml
with open('recipe/yaml/your-recipe.yaml') as f:
    data = yaml.safe_load(f)
    print('YAML is valid')
"
```

#### 4. Build System Issues

**Problem**: Make commands fail or rebuild unnecessarily

**Solutions**:
```bash
# Clean and rebuild
make clean
make build

# Check file timestamps
ls -la recipe/markdown/
ls -la recipe/yaml/
ls -la recipe/pdf/

# Force specific recipe rebuild
touch recipe/markdown/problematic-recipe.md
make build
```

### Getting Debug Information

#### Enable Verbose Output
```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python -m recipe_fmt.pipeline --verbose recipe/markdown/your-recipe.md
```

#### Check Pipeline Status
```bash
# Verify each stage
echo "=== Markdown Files ==="
ls -la recipe/markdown/

echo "=== YAML Files ==="
ls -la recipe/yaml/

echo "=== PDF Files ==="
ls -la recipe/pdf/

echo "=== API Configuration ==="
python -c "
from recipe_fmt.models.config import OpenAIConfig
config = OpenAIConfig()
print(f'OpenAI Key: {'✅' if config.api_key else '❌'}')
print(f'Model: {config.model}')
"
```

## 📈 Tips for Success

### Recipe Writing Best Practices

1. **Be Specific**: Use exact measurements and clear descriptions
2. **Use Standard Terms**: Stick to common cooking terminology
3. **Include Context**: Mention serving size, cooking times, temperatures
4. **Test Your Recipes**: Ensure they actually work before processing
5. **Consistent Formatting**: Use the same markdown structure across recipes

### Workflow Optimization

1. **Batch Creation**: Write multiple recipes before processing
2. **Template Reuse**: Copy successful recipe formats for new ones
3. **Regular Backups**: Keep your markdown files in version control
4. **Quality Control**: Review generated YAML before final PDF creation
5. **Iterative Improvement**: Refine recipes based on output quality

### Collection Management

1. **Naming Convention**: Use descriptive, consistent filenames
2. **Category Planning**: Think about your category distribution
3. **Version Control**: Use git to track recipe changes
4. **Documentation**: Keep notes about recipe sources and modifications
5. **Regular Updates**: Periodically regenerate all recipes with improvements

---

## 📚 Next Steps

- **Configuration Guide**: See `CONFIGURATION.md` for advanced settings
- **API Reference**: Generated documentation for developers
- **Contributing**: See `CONTRIBUTING.md` to contribute improvements
- **Examples**: Browse `recipe/markdown/` for more recipe examples

**Happy cooking! 👨‍🍳👩‍🍳**