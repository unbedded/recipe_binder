# Installation Guide

Complete setup instructions for Recipe Binder, from system requirements through first recipe generation.

## 📋 System Requirements

### Python Environment
- **Python**: 3.13+ (leverages latest language features)
- **Operating System**: Linux, macOS, Windows
- **Memory**: 512MB minimum, 1GB recommended for large collections
- **Storage**: 100MB for core package + space for recipe collections
- **Network**: Internet connectivity for OpenAI and USDA APIs

### Required API Keys
Recipe Binder requires two API keys for full functionality:

1. **OpenAI API Key** (Required)
   - Used for: AI-powered recipe parsing and structuring
   - Get yours: [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Cost: ~$0.01-0.05 per recipe depending on complexity

2. **USDA API Key** (Optional but Recommended)
   - Used for: Automatic nutrition calculation
   - Get yours: [USDA FoodData Central API](https://fdc.nal.usda.gov/api-key-signup)
   - Cost: Free with rate limits

## 🚀 Quick Installation

### Method 1: Direct from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/recipe-binder.git
cd recipe-binder

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install package and dependencies
pip install -e .

# Verify installation
python -c "import recipe_fmt; print('✅ Installation successful')"
```

### Method 2: Development Installation

```bash
# Clone and setup for development
git clone https://github.com/yourusername/recipe-binder.git
cd recipe-binder

# Install with development dependencies
make install  # Equivalent to: pip install -e ".[dev]"

# Verify development tools
make lint     # Code formatting check
make test     # Run test suite
```

## 🔑 API Key Configuration

### Step 1: Get Your API Keys

#### OpenAI API Key
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Important**: Store securely - you can't view it again

#### USDA API Key (Optional)
1. Visit [USDA API Signup](https://fdc.nal.usda.gov/api-key-signup)
2. Fill out the form (takes 2 minutes)
3. Check your email for the API key
4. Key format: UUID string (e.g., `12345678-1234-1234-1234-123456789abc`)

### Step 2: Set Environment Variables

#### Option A: Command Line (Temporary)
```bash
# Set for current session
export OPENAI_API_KEY="sk-your-openai-key-here"
export USDA_API_KEY="your-usda-key-here"
```

#### Option B: Shell Profile (Persistent)
```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
echo 'export OPENAI_API_KEY="sk-your-openai-key-here"' >> ~/.bashrc
echo 'export USDA_API_KEY="your-usda-key-here"' >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

#### Option C: .env File (Project-Specific)
```bash
# Create .env file in project root
cat > .env << EOF
OPENAI_API_KEY=sk-your-openai-key-here
USDA_API_KEY=your-usda-key-here
EOF

# Add to .gitignore (important!)
echo ".env" >> .gitignore
```

### Step 3: Verify API Configuration

```bash
# Test OpenAI connection
python -c "
from recipe_fmt.models.config import OpenAIConfig
config = OpenAIConfig()
print(f'✅ OpenAI configured: {config.api_key[:10]}...' if config.api_key else '❌ OpenAI key missing')
"

# Test USDA connection
python -c "
import os
usda_key = os.getenv('USDA_API_KEY')
print(f'✅ USDA configured: {usda_key[:10]}...' if usda_key else '❌ USDA key missing (optional)')
"
```

## 🧪 First Recipe Generation

### Step 1: Generate Demo Recipes

```bash
# Generate all sample recipes (includes nutrition calculation)
make demo

# Or generate specific recipe
python -m recipe_fmt.pipeline recipe/markdown/sample-pancakes.md
```

### Step 2: View Generated Files

```bash
# Check generated YAML
cat recipe/yaml/Breakfast-sample-pancakes.yaml

# Open PDF (macOS)
open recipe/pdf/Breakfast-sample-pancakes.pdf

# Open PDF (Linux)
xdg-open recipe/pdf/Breakfast-sample-pancakes.pdf

# Open PDF (Windows)
start recipe/pdf/Breakfast-sample-pancakes.pdf
```

### Step 3: Print Recipe Cards

```bash
# Print all recipes with color/duplex settings
make print

# Or print single recipe
lpr -o ColorModel=CMYK -o sides=two-sided-long-edge recipe/pdf/Breakfast-sample-pancakes.pdf
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Python Version Error
```
ERROR: Python 3.13 or higher is required
```
**Solution**: Update Python or use pyenv
```bash
# Install Python 3.13 with pyenv
pyenv install 3.13.0
pyenv local 3.13.0
```

#### 2. OpenAI API Key Invalid
```
ERROR: OpenAI API key must start with 'sk-'
```
**Solution**: Verify your API key format
```bash
# Check your key format
echo $OPENAI_API_KEY | head -c 10  # Should show "sk-proj-" or "sk-"
```

#### 3. USDA API Rate Limits
```
WARNING: USDA API rate limit exceeded, using sample data
```
**Solution**: This is normal behavior. Recipe generation continues with placeholder nutrition data.

#### 4. Import Errors
```
ModuleNotFoundError: No module named 'recipe_fmt'
```
**Solution**: Ensure virtual environment is activated and package is installed
```bash
# Activate venv
source .venv/bin/activate

# Reinstall package
pip install -e .
```

#### 5. Permission Errors (Linux/macOS)
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Check file permissions and avoid running as root
```bash
# Fix permissions
chmod -R 755 recipe/
chown -R $USER:$USER recipe/
```

### Advanced Troubleshooting

#### Enable Debug Logging
```bash
# Set debug mode
export LOG_LEVEL=DEBUG

# Run with verbose output
python -m recipe_fmt.pipeline --verbose recipe/markdown/your-recipe.md
```

#### Check Dependencies
```bash
# Verify all dependencies installed
pip check

# Show package info
pip show recipe_fmt
```

#### Clean Build
```bash
# Remove all generated files
make clean

# Regenerate everything
make build
```

## 🎯 Performance Optimization

### Faster Processing
```bash
# Cache OpenAI responses to avoid re-parsing
export CACHE_OPENAI_RESPONSES=true

# Parallel processing for multiple recipes
make build -j4  # Use 4 parallel jobs
```

### Memory Management
```bash
# For large recipe collections (100+ recipes)
# Process in batches
find recipe/markdown -name "*.md" | head -20 | xargs -I {} python -m recipe_fmt.pipeline {}
```

## 🔐 Security Best Practices

### API Key Security
1. **Never commit API keys** to version control
2. **Use environment variables** instead of hardcoding
3. **Rotate keys periodically** for production use
4. **Monitor API usage** to detect unauthorized access

### File Permissions
```bash
# Secure API key files
chmod 600 .env

# Restrict recipe directory access
chmod 755 recipe/
```

## 📊 Monitoring and Maintenance

### Check System Health
```bash
# Run test suite
make test

# Check code quality
make lint

# Verify all recipes process correctly
make build && echo "✅ All recipes processed successfully"
```

### Update Dependencies
```bash
# Update to latest compatible versions
pip install --upgrade -e ".[dev]"

# Check for security vulnerabilities
pip audit
```

## 🆘 Getting Help

### Documentation
- **User Manual**: See `USER_MANUAL.md` for detailed usage examples
- **Configuration**: See `CONFIGURATION.md` for advanced settings
- **API Reference**: Generated docs in `docs/` directory

### Support Channels
- **Issues**: [GitHub Issues](https://github.com/yourusername/recipe-binder/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/recipe-binder/discussions)
- **Documentation**: [Project Wiki](https://github.com/yourusername/recipe-binder/wiki)

### Before Reporting Issues
1. **Check this installation guide** for common solutions
2. **Search existing issues** for similar problems
3. **Include debug information**:
   ```bash
   # Generate debug report
   python -c "
   import sys, platform, recipe_fmt
   print(f'Python: {sys.version}')
   print(f'Platform: {platform.platform()}')
   print(f'Recipe Binder: {getattr(recipe_fmt, '__version__', 'unknown')}')
   "
   ```

## ✅ Installation Checklist

- [ ] Python 3.13+ installed and activated
- [ ] Repository cloned and dependencies installed
- [ ] OpenAI API key configured and tested
- [ ] USDA API key configured (optional)
- [ ] Demo recipes generated successfully
- [ ] PDF cards display correctly
- [ ] Printer setup configured (if printing)
- [ ] Debug logging enabled for troubleshooting

**Next Steps**: See `USER_MANUAL.md` for detailed usage examples and advanced features.