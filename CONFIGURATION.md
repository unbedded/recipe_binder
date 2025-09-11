# Configuration Reference

Complete reference for configuring Recipe Binder's behavior, performance, and output formatting.

## 📋 Configuration Overview

Recipe Binder uses a hierarchical configuration system:

1. **Environment Variables** (Highest Priority) - API keys and runtime settings
2. **Pydantic Settings** - Type-safe configuration with validation
3. **Template Files** - Layout and design customization
4. **Hard-coded Defaults** - Fallback values for all settings

## 🔑 Environment Variables

### Required Configuration

#### OpenAI API Configuration
```bash
# Required: Your OpenAI API key
export OPENAI_API_KEY="sk-proj-your-key-here"

# Optional: Override default model (default: gpt-4o-mini)
export OPENAI_MODEL="gpt-4o-mini"

# Optional: Adjust token limits (default: 2000)
export OPENAI_MAX_TOKENS="3000"

# Optional: Control creativity (default: 0.1, range: 0.0-2.0)
export OPENAI_TEMPERATURE="0.2"

# Optional: Request timeout (default: 30 seconds)
export OPENAI_TIMEOUT_SECONDS="45"

# Optional: Retry attempts (default: 3)
export OPENAI_MAX_RETRIES="5"

# Optional: Retry delay (default: 1.0 seconds)
export OPENAI_RETRY_DELAY="2.0"
```

#### USDA Nutrition API Configuration
```bash
# Optional but recommended: USDA API key for nutrition data
export USDA_API_KEY="12345678-1234-1234-1234-123456789abc"
```

### Optional Configuration

#### Display Settings
```bash
# Show ingredient weights alongside measurements (default: true)
export RECIPE_DISPLAY_SHOW_WEIGHTS="true"

# Weight unit for display (default: "grams", options: "grams", "ounces", "g", "oz")
export RECIPE_DISPLAY_WEIGHT_UNIT="grams"

# Show nutrition information on cards (default: false)
export RECIPE_DISPLAY_SHOW_NUTRITION="true"

# Show ingredient purpose in tables (default: true)
export RECIPE_DISPLAY_SHOW_PURPOSE="true"
```

#### Application Settings
```bash
# Enable debug logging (default: false)
export DEBUG="true"

# Set logging level (default: "WARNING")
export LOG_LEVEL="INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Setting Environment Variables

#### Temporary (Current Session)
```bash
export OPENAI_API_KEY="your-key-here"
export USDA_API_KEY="your-usda-key"
```

#### Persistent (Shell Profile)
```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.bashrc
echo 'export USDA_API_KEY="your-usda-key"' >> ~/.bashrc
source ~/.bashrc
```

#### Project-Specific (.env file)
```bash
# Create .env file in project root
cat > .env << 'EOF'
OPENAI_API_KEY=your-key-here
USDA_API_KEY=your-usda-key
RECIPE_DISPLAY_SHOW_NUTRITION=true
LOG_LEVEL=INFO
EOF

# Important: Add to .gitignore
echo ".env" >> .gitignore
```

## ⚙️ Pydantic Configuration Classes

Recipe Binder uses Pydantic for type-safe configuration with validation.

### DisplayConfig

Controls PDF output formatting and display options.

```python
from recipe_fmt.models.config import DisplayConfig

# Default configuration
config = DisplayConfig()

# Custom configuration
config = DisplayConfig(
    show_weights=True,          # Show weights like "2 cups (240g)"
    weight_unit="grams",        # Options: "grams", "ounces", "g", "oz"
    show_nutrition=True,        # Display nutrition facts panel
    show_purpose=True           # Show ingredient purposes ("base", "flavoring", etc.)
)

# Access settings
print(config.show_weights)      # True
print(config.weight_unit)       # "grams"
```

#### DisplayConfig Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `show_weights` | bool | `True` | Display ingredient weights alongside measurements |
| `weight_unit` | str | `"grams"` | Unit for weight display: "grams", "ounces", "g", "oz" |
| `show_nutrition` | bool | `False` | Include nutrition facts panel on recipe cards |
| `show_purpose` | bool | `True` | Show ingredient purposes in ingredient table |

### OpenAIConfig

Controls OpenAI API integration and parsing behavior.

```python
from recipe_fmt.models.config import OpenAIConfig

# Default configuration (reads from environment)
config = OpenAIConfig()

# Custom configuration
config = OpenAIConfig(
    model="gpt-4o-mini",        # OpenAI model to use
    max_tokens=2000,            # Maximum tokens per request
    temperature=0.1,            # Sampling temperature (0.0-2.0)
    timeout_seconds=30,         # Request timeout
    max_retries=3,              # Maximum retry attempts
    retry_delay=1.0             # Base delay between retries (exponential backoff)
)

# Validation
if config.api_key:
    print("OpenAI configured successfully")
else:
    print("OpenAI API key required")
```

#### OpenAIConfig Options

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `api_key` | str | `None` | - | OpenAI API key (from `OPENAI_API_KEY` env var) |
| `model` | str | `"gpt-4o-mini"` | - | OpenAI model for recipe parsing |
| `max_tokens` | int | `2000` | 100-8000 | Maximum tokens per API request |
| `temperature` | float | `0.1` | 0.0-2.0 | Sampling temperature (lower = more consistent) |
| `timeout_seconds` | int | `30` | 5-300 | Request timeout in seconds |
| `max_retries` | int | `3` | 1-10 | Maximum retry attempts for failed requests |
| `retry_delay` | float | `1.0` | 0.1-60.0 | Base delay between retries (uses exponential backoff) |

### AppConfig

Main application configuration combining all settings.

```python
from recipe_fmt.models.config import AppConfig

# Initialize with defaults
app_config = AppConfig()

# Access nested configs
print(app_config.display.show_weights)    # True
print(app_config.openai.model)            # "gpt-4o-mini"

# Custom initialization
app_config = AppConfig(
    debug=True,
    log_level="DEBUG",
    display=DisplayConfig(show_nutrition=True),
    openai=OpenAIConfig(temperature=0.2)
)
```

#### AppConfig Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `debug` | bool | `False` | Enable debug logging and verbose output |
| `log_level` | str | `"WARNING"` | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `display` | DisplayConfig | auto | Display configuration object |
| `openai` | OpenAIConfig | auto | OpenAI configuration object |

## 🎨 Template Configuration

### Default Template Structure

Templates are stored in `recipe/templates/` and define the layout and styling of PDF cards.

```yaml
# recipe/templates/default-card.yaml
template_info:
  name: "Default Recipe Card"
  version: "1.0"
  description: "Standard two-sided recipe card template"

# Page settings
page:
  size: "letter"          # Paper size
  orientation: "portrait" # portrait or landscape
  margins:
    top: 0.15             # inches
    bottom: 0.15
    left: 0.25
    right: 0.25

# Typography
fonts:
  title:
    family: "Helvetica-Bold"
    size: 16
    color: "white"
  category:
    family: "Helvetica-Bold"
    size: 12
    color: "white"
  body:
    family: "Helvetica"
    size: 11
    color: "black"
  instructions:
    family: "Helvetica"
    size: 12
    color: "black"

# Layout sections
layout:
  header_height: 0.4      # inches
  column_widths:
    amount: 0.3           # inches
    space: 0.1            # inches
    unit: 0.5             # inches
    weight: 0.7           # inches
    ingredient: "auto"    # remaining space

# Color scheme (category colors defined in code)
colors:
  default_background: "#4D4D4D"
  default_text: "white"
```

### Customizing Templates

#### 1. Create Custom Template
```bash
# Copy default template
cp recipe/templates/default-card.yaml recipe/templates/my-custom.yaml

# Edit customizations
vim recipe/templates/my-custom.yaml
```

#### 2. Template Modifications

**Font Sizes**:
```yaml
fonts:
  title:
    size: 18            # Larger title
  body:
    size: 12            # Larger body text
  instructions:
    size: 13            # Larger instructions
```

**Margins and Spacing**:
```yaml
page:
  margins:
    top: 0.2            # More top margin
    sides: 0.3          # Wider side margins

layout:
  header_height: 0.5    # Taller header
```

**Column Layout**:
```yaml
layout:
  column_widths:
    amount: 0.4         # Wider amount column
    unit: 0.6           # Wider unit column
    weight: 0.8         # Wider weight column
```

#### 3. Using Custom Templates

Currently, templates are applied automatically. Future versions will support template selection:

```bash
# Future feature (not yet implemented)
python -m recipe_fmt.pipeline --template my-custom recipe/markdown/recipe.md
```

## 🔧 Advanced Configuration

### Performance Tuning

#### OpenAI Request Optimization
```bash
# Faster processing with higher temperature (less consistent)
export OPENAI_TEMPERATURE="0.3"

# Smaller token limit for simpler recipes
export OPENAI_MAX_TOKENS="1500"

# Aggressive retry settings for unreliable connections
export OPENAI_MAX_RETRIES="5"
export OPENAI_RETRY_DELAY="0.5"
```

#### Batch Processing Settings
```bash
# Enable parallel processing
make build -j4  # Use 4 parallel jobs

# Large collection optimization
export BATCH_SIZE="10"           # Process 10 recipes at a time
export MEMORY_LIMIT="1GB"        # Limit memory usage
```

### Logging Configuration

#### Detailed Logging Setup
```python
# Custom logging configuration
import logging
from recipe_fmt.utils.logging_setup import setup_logging

# Configure logging
setup_logging(
    level="DEBUG",
    log_file="recipe_binder.log",
    console_output=True,
    file_output=True
)

# Use in scripts
logger = logging.getLogger(__name__)
logger.info("Processing recipe...")
```

#### Log Level Details

| Level | Use Case | Output Includes |
|-------|----------|-----------------|
| `DEBUG` | Development, troubleshooting | All operations, API calls, file I/O |
| `INFO` | Production monitoring | Important events, processing status |
| `WARNING` | Normal operation | Warnings, fallbacks, missing optional data |
| `ERROR` | Issue detection | Errors, failures, but processing continues |
| `CRITICAL` | System failures | Fatal errors that stop processing |

### Development Configuration

#### Development Environment Setup
```bash
# Development-specific settings
export DEBUG="true"
export LOG_LEVEL="DEBUG"
export OPENAI_TEMPERATURE="0.0"    # Most consistent for testing
export RECIPE_DISPLAY_SHOW_NUTRITION="true"

# Enable all optional features
export RECIPE_DISPLAY_SHOW_WEIGHTS="true"
export RECIPE_DISPLAY_SHOW_PURPOSE="true"
```

#### Testing Configuration
```python
# Test configuration example
from recipe_fmt.models.config import AppConfig, OpenAIConfig, DisplayConfig

test_config = AppConfig(
    debug=True,
    log_level="DEBUG",
    display=DisplayConfig(
        show_weights=True,
        show_nutrition=True,
        weight_unit="grams"
    ),
    openai=OpenAIConfig(
        model="gpt-4o-mini",
        temperature=0.0,        # Consistent results
        max_tokens=1000,        # Faster testing
        timeout_seconds=10      # Quick failure
    )
)
```

## 🔍 Configuration Validation

### Checking Current Configuration

#### Environment Variables
```bash
# Check all Recipe Binder environment variables
env | grep -E "(OPENAI|USDA|RECIPE|LOG_LEVEL|DEBUG)"

# Verify API keys
python -c "
import os
from recipe_fmt.models.config import OpenAIConfig

# Check OpenAI
openai_config = OpenAIConfig()
print(f'OpenAI Key: {\"✅ Set\" if openai_config.api_key else \"❌ Missing\"}')
print(f'OpenAI Model: {openai_config.model}')

# Check USDA
usda_key = os.getenv('USDA_API_KEY')
print(f'USDA Key: {\"✅ Set\" if usda_key else \"❌ Missing (optional)\"}')
"
```

#### Configuration Objects
```python
# Validate all configuration
from recipe_fmt.models.config import AppConfig

try:
    config = AppConfig()
    print("✅ Configuration valid")
    print(f"Debug mode: {config.debug}")
    print(f"Log level: {config.log_level}")
    print(f"Show weights: {config.display.show_weights}")
    print(f"OpenAI model: {config.openai.model}")
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

### Configuration Troubleshooting

#### Common Issues

1. **Invalid Log Level**
```
ValueError: Invalid log level: debug. Must be one of: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
```
**Solution**: Use uppercase log levels
```bash
export LOG_LEVEL="DEBUG"  # Not "debug"
```

2. **Invalid OpenAI API Key**
```
ValueError: OpenAI API key must start with 'sk-'
```
**Solution**: Verify your API key format
```bash
echo $OPENAI_API_KEY | head -c 10  # Should show "sk-proj-" or "sk-"
```

3. **Invalid Weight Unit**
```
ValueError: Weight unit must be one of: {'grams', 'ounces', 'g', 'oz'}
```
**Solution**: Use supported units
```bash
export RECIPE_DISPLAY_WEIGHT_UNIT="grams"  # Not "pounds"
```

## 📊 Configuration Examples

### Common Configuration Scenarios

#### 1. Home Cook Setup
```bash
# Basic setup for personal use
export OPENAI_API_KEY="sk-your-key-here"
export USDA_API_KEY="your-usda-key"
export RECIPE_DISPLAY_SHOW_NUTRITION="true"
export LOG_LEVEL="WARNING"
```

#### 2. Professional Kitchen
```bash
# Commercial kitchen with weight focus
export OPENAI_API_KEY="sk-your-key-here"
export USDA_API_KEY="your-usda-key"
export RECIPE_DISPLAY_SHOW_WEIGHTS="true"
export RECIPE_DISPLAY_WEIGHT_UNIT="grams"
export RECIPE_DISPLAY_SHOW_NUTRITION="true"
export RECIPE_DISPLAY_SHOW_PURPOSE="true"
export LOG_LEVEL="INFO"
```

#### 3. Development Environment
```bash
# Development with verbose logging
export OPENAI_API_KEY="sk-your-key-here"
export USDA_API_KEY="your-usda-key"
export DEBUG="true"
export LOG_LEVEL="DEBUG"
export OPENAI_TEMPERATURE="0.0"        # Consistent results
export RECIPE_DISPLAY_SHOW_NUTRITION="true"
export RECIPE_DISPLAY_SHOW_WEIGHTS="true"
```

#### 4. Batch Processing Server
```bash
# Optimized for large collections
export OPENAI_API_KEY="sk-your-key-here"
export USDA_API_KEY="your-usda-key"
export OPENAI_MAX_TOKENS="1500"        # Faster processing
export OPENAI_TIMEOUT_SECONDS="60"     # Longer timeout
export OPENAI_MAX_RETRIES="5"          # More retries
export LOG_LEVEL="INFO"
export RECIPE_DISPLAY_SHOW_NUTRITION="false"  # Skip nutrition for speed
```

## 🚀 Configuration Best Practices

### Security
1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys regularly** in production
4. **Monitor API usage** for unauthorized access

### Performance
1. **Use appropriate token limits** for your recipes
2. **Adjust retry settings** based on network reliability
3. **Enable parallel processing** for large collections
4. **Cache results** when possible

### Maintainability
1. **Document custom configurations** in your project
2. **Use consistent naming** for environment variables
3. **Validate configuration** before processing
4. **Test configuration changes** with sample recipes

### Monitoring
1. **Set appropriate log levels** for your environment
2. **Monitor API usage** and costs
3. **Track processing performance** metrics
4. **Alert on configuration errors**

---

## 📚 Related Documentation

- **Installation Guide**: `INSTALLATION.md` - Complete setup instructions
- **User Manual**: `USER_MANUAL.md` - Usage examples and workflows
- **API Reference**: Generated documentation for developers
- **Release Notes**: `CHANGELOG.md` - Configuration changes across versions

For questions about configuration, see the [GitHub Issues](https://github.com/yourusername/recipe-binder/issues) or [Discussions](https://github.com/yourusername/recipe-binder/discussions) page.