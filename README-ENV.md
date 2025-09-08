# Python Claude Code Development Template

This repository serves as a comprehensive template for Python 3.13.5 development projects using Claude Code, with built-in GitFlow workflow support, version management, and best practices.

## Features

### Core Development Setup
- **CLAUDE.md**: Project-specific coding standards and configuration management patterns
- **.claude/**: Claude Code settings, slash commands, and development utilities
  - `commands/`: Custom Claude Code slash commands
  - `tools/`: Development utilities (version_bump.py, yaml_to_py.py, etc.)
- **pyproject.toml**: Complete pytest/ruff/mypy configuration with placeholders
- **requirements.txt**: Development tooling, stubs, and pre-commit hooks
- **.pre-commit-config.yaml**: Automated code quality checks
- **.vscode/settings.json**: VS Code configuration for consistent development
- **.github/workflows/ci.yml**: Continuous integration pipeline

### GitFlow & Version Management
- **VERSION**: PEP 440 compliant version tracking
- **CHANGELOG.md**: Keep a Changelog format for release notes  
- **.gitflow**: Branch naming conventions and GitFlow configuration
- **.claude/tools/version_bump.py**: Automated version management with pre-release tags
- Support for semantic versioning with alpha, beta, rc pre-release identifiers

### Code Quality & Standards
- **PEP 8** compliance with type hints
- **Python 3.13.5** compatibility
- Consistent logging patterns with thread-safe configuration
- Configuration management pattern for all classes
- Comprehensive error handling and debugging support

## Template Structure

```
├── .claude/                 # Claude Code configuration & tools
│   ├── commands/           # Custom slash commands
│   └── tools/              # Development utilities
├── .github/workflows/       # CI/CD pipelines
├── .vscode/                # VS Code settings
├── src/__PKG__/            # Main package (replace __PKG__)
├── tests/                  # Test suite
├── CLAUDE.md               # Project coding standards
├── CHANGELOG.md            # Release history
├── VERSION                 # Current version (PEP 440)
├── pyproject.toml          # Build and tool configuration
├── requirements.txt        # Dependencies
└── .pre-commit-config.yaml # Git hooks
```

## Claude Commands Structure

```
.claude/
├── commands/                              # Claude Code slash commands
│   │
│   ├─── 🤖 INTELLIGENT COMMANDS (Claude Analysis + Decision Making)
│   │
│   ├── review-commits.md                  # /review-commits [--count <n>] [--since <date>]
│   │   ├── ACTIONS: Analyze recent commits, suggest message improvements
│   │   ├── OPTIONS:
│   │   │   ├── --count <n>               # Number of recent commits (default: 5)
│   │   │   └── --since <date>            # Commits since date (e.g., "1 week ago")
│   │   └── OUTPUT: Commit quality analysis, suggested improvements
│   │
│   ├── suggest-version.md                 # /suggest-version [--analyze]
│   │   ├── ANALYSIS: Examine changes since last version, recommend bump level
│   │   ├── CONSIDERS: Breaking changes, new features, bug fixes
│   │   └── OPTIONS:
│   │       └── --analyze                 # Show detailed change analysis
│   │
│   ├── analyze-changes.md                 # /analyze-changes [--branch <name>]
│   │   ├── EXAMINES: Current branch vs base, modified files
│   │   ├── GENERATES: Release notes, change summary
│   │   └── OPTIONS:
│   │       └── --branch <name>           # Compare against specific branch
│   │
│   ├── review-code.md                     # /review-code [--files <pattern>]
│   │   ├── REVIEWS: Modified files, suggests improvements
│   │   ├── CHECKS: Code quality, patterns, potential issues
│   │   └── OPTIONS:
│   │       └── --files <pattern>         # Focus on specific files (glob pattern)
│   │
│   ├── smart-commit.md                    # /smart-commit [--stage-all]
│   │   ├── ANALYZES: Staged changes, generates meaningful commit message
│   │   ├── FOLLOWS: Conventional commits, project patterns
│   │   └── OPTIONS:
│   │       └── --stage-all               # Stage all changes first
│   │
│   ├── plan-release.md                    # /plan-release [--target <version>]
│   │   ├── ANALYZES: Unreleased changes, suggests release plan
│   │   ├── CREATES: Release checklist, version recommendation  
│   │   └── OPTIONS:
│   │       └── --target <version>         # Plan for specific version
│   │
│   │
│   ├─── ⚙️ AUTOMATED TOOLS (Direct Python Execution)
│   │
│   ├── check-code.md                      # /check-code [OPTIONS]
│   │   ├── OPTIONS:
│   │   │   ├── --fix                      # Auto-fix issues where possible
│   │   │   ├── --verbose                  # Show detailed output  
│   │   │   └── --report                   # Generate coverage/quality reports
│   │   └── PIPELINE: ruff format → ruff check → mypy → pytest
│   │
│   ├── bump-version.md                    # /bump-version <LEVEL> [OPTIONS]
│   │   ├── LEVEL (required):
│   │   │   ├── patch                      # 1.0.0 → 1.0.1
│   │   │   ├── minor                      # 1.0.0 → 1.1.0
│   │   │   └── major                      # 1.0.0 → 2.0.0
│   │   └── OPTIONS:
│   │       └── --pre-release <TYPE>       # Add pre-release identifier
│   │           ├── alpha (or a)           # 1.0.0 → 1.0.1a1
│   │           ├── beta (or b)            # 1.0.0 → 1.0.1b1
│   │           └── rc                     # 1.0.0 → 1.0.1rc1
│   │
│   ├── new-module.md                      # /new-module <MODULE_NAME> [OPTIONS]
│   │   ├── MODULE_NAME (required):        # snake_case module name
│   │   └── OPTIONS:
│   │       └── --with-tests               # Include test file (default: true)
│   │
│   ├── run-tests.md                       # /run-tests [OPTIONS]
│   │   └── OPTIONS:
│   │       ├── --coverage                 # Include coverage report + HTML output
│   │       ├── --filter <PATTERN>         # Run tests matching pattern (pytest -k)
│   │       ├── --verbose                  # Show detailed test output (-v)
│   │       └── --parallel                 # Run tests in parallel (if pytest-xdist available)
│   │
│   │
│   └─── 🤖⚙️ HYBRID COMMANDS (Claude Analysis + Python Execution)
│   │
│   ├── gitflow-start.md                   # /gitflow-start <TYPE> [NAME]
│   │   ├── TYPE (required):
│   │   │   ├── feature                    # Branches from develop
│   │   │   ├── release                    # Branches from develop  
│   │   │   ├── hotfix                     # Branches from main
│   │   │   └── bugfix                     # Branches from develop
│   │   ├── NAME (optional):               # Branch name - Claude suggests if omitted
│   │   └── INTELLIGENCE: Suggests branch names based on recent work/commits
│   │
│   └── gitflow-finish.md                  # /gitflow-finish <TYPE> <NAME> [OPTIONS]
│       ├── TYPE & NAME:                   # Same as gitflow-start
│       ├── ANALYSIS: Checks branch status, conflicts, readiness
│       └── OPTIONS:
│           ├── --keep-branch              # Keep branch after merging
│           └── --no-ff                    # Force no fast-forward merge
│
└── tools/                                 # Direct Python execution
    │
    ├─── 🏗️ ENVIRONMENT MANAGEMENT
    │
    ├── bootstrap_common.py                # Shared utilities for project bootstrapping
    │   └── PROVIDES: Directory creation, git setup, common file operations
    │
    ├── bootstrap_python.py                # python .claude/tools/bootstrap_python.py [OPTIONS]
    │   ├── ACTIONS: Setup Python project with complete dev environment
    │   └── OPTIONS:
    │       ├── --package <NAME>           # Package name (replaces __PKG__)
    │       ├── --python <VERSION>         # Python version (default: 3.13)
    │       ├── --author <NAME>            # Author name for project metadata
    │       ├── --email <EMAIL>            # Author email
    │       ├── --create-venv              # Create virtual environment
    │       ├── --install                  # Install dependencies after setup
    │       ├── --include-fastapi          # Add FastAPI dependencies
    │       └── --include-cli              # Add CLI dependencies (click, rich)
    │
    ├── bootstrap_cpp.py                   # python .claude/tools/bootstrap_cpp.py [OPTIONS] (TODO)
    │   ├── STATUS: ⚠️ Placeholder implementation with TODO comments
    │   ├── ACTIONS: Setup C++ project structure (future implementation)
    │   └── OPTIONS:
    │       ├── --package <NAME>           # C++ project name  
    │       ├── --cmake <VERSION>          # Minimum CMake version (default: 3.20)
    │       ├── --std <VERSION>            # C++ standard (default: 20)
    │       ├── --conan                    # Use Conan package manager
    │       ├── --vcpkg                    # Use vcpkg package manager
    │       ├── --test-framework <TYPE>    # gtest|catch2|doctest (default: gtest)
    │       └── --header-only              # Create header-only library
    │
    ├── update_config.py                   # python .claude/tools/update_config.py [OPTIONS]
    │   ├── ACTIONS: Update tool configurations across project
    │   └── OPTIONS:
    │       ├── --ruff-target <VERSION>    # Update ruff target (e.g., py313)
    │       ├── --mypy-version <VERSION>   # Update mypy Python version
    │       ├── --python <VERSION>         # Update all Python version references
    │       └── --validate                 # Validate configs after update
    │
    ├── validate_setup.py                  # python .claude/tools/validate_setup.py [OPTIONS]
    │   ├── CHECKS: Project structure, configs, dependencies
    │   └── OPTIONS:
    │       ├── --check-all                # Full validation suite
    │       ├── --fix-issues               # Auto-fix common issues
    │       └── --report                   # Generate validation report
    │
    │
    ├─── 🔧 DEVELOPMENT TOOLS
    │
    ├── version_bump.py                    # python .claude/tools/version_bump.py [OPTIONS]
    │   ├── REQUIRED:
    │   │   └── --bump <LEVEL>             # patch|minor|major
    │   ├── OPTIONS:
    │   │   ├── --pre-release <TYPE>       # alpha|beta|rc|a|b
    │   │   └── --verbose                  # Enable debug logging
    │   └── ACTIONS: Read VERSION → Calculate new → Write VERSION → Update CHANGELOG
    │
    ├── code_quality.py                    # python .claude/tools/code_quality.py [OPTIONS]
    │   └── OPTIONS:
    │       ├── --fix                      # Auto-fix issues where possible
    │       ├── --coverage                 # Include coverage reporting
    │       ├── --verbose                  # Show detailed output
    │       └── --report                   # Generate additional reports
    │
    ├── module_scaffold.py                 # python .claude/tools/module_scaffold.py <NAME> [OPTIONS]
    │   ├── NAME (required):               # Module name in snake_case
    │   └── OPTIONS:
    │       ├── --tests                    # Create test file (default)
    │       ├── --no-tests                 # Skip test file creation
    │       └── --verbose                  # Enable debug logging
    │
    └── yaml_to_py.py                      # python .claude/tools/yaml_to_py.py <INPUT> [OPTIONS]
        ├── INPUT (required):              # YAML file path
        └── OPTIONS:
            └── --output <FILE>            # Output Python file path
```

### Usage Patterns

**Via Claude Code (Interactive):**
```bash
# In Claude Code interface
/check-code --fix --verbose
/bump-version minor --pre-release alpha
/new-module user_manager --with-tests
/gitflow-start feature authentication
```

**Direct Command Line:**
```bash
# Direct Python execution
python .claude/tools/version_bump.py --bump patch
python .claude/tools/code_quality.py --fix --report
python .claude/tools/module_scaffold.py auth_service --tests

# Via Claude Code CLI (if installed)
claude run @.claude/commands/check-code --fix
claude run @.claude/commands/bump-version minor
claude run @.claude/commands/new-module user_auth --with-tests
```

**Environment Management:**
```bash
# Setup new environment from template
python .claude/tools/bootstrap_env.py --package myproject --python 3.13

# Update all tool configurations
python .claude/tools/update_config.py --ruff-target py313 --mypy-version 3.13

# Validate environment setup
python .claude/tools/validate_setup.py --check-all
```

## Quick Start

### 🚀 **Using This as a GitHub Template (Recommended)**

1. **Make This a Template Repository**:
   - Go to your repo settings on GitHub
   - Check **"Template repository"** under "General"
   - Save changes

2. **Create New Project from Template**:
   ```bash
   # On GitHub.com: Click "Use this template" → Create new repository
   # Clone your new repository
   git clone https://github.com/yourusername/your_new_project.git
   cd your_new_project
   
   # Bootstrap the project (replaces placeholders)
   python .claude/tools/bootstrap_python.py --package your_new_project --python 3.13 --author "Your Name" --install --create-venv
   
   # Commit bootstrapped changes
   git add .
   git commit -m "Bootstrap project from Claude Code template"
   git push
   ```

### 📋 **Manual Template Setup**

1. **Clone and Setup**:
   ```bash
   # Clone template
   git clone https://github.com/unbedded/claud_code_bootstrap_python.git my_new_project
   cd my_new_project
   
   # Remove template git history
   rm -rf .git
   git init
   git branch -M main
   
   # Bootstrap project
   python .claude/tools/bootstrap_python.py --package my_new_project --python 3.13 --author "Your Name" --install --create-venv
   
   # Connect to your GitHub repo (create on GitHub first)
   git remote add origin https://github.com/yourusername/my_new_project.git
   git add .
   git commit -m "Initial commit: Python project from Claude Code template"  
   git push -u origin main
   ```

2. **What Bootstrap Does**:
   - Replaces `__RUFF_TARGET__` → Python version target (e.g., `py313`)
   - Replaces `__MYPY_PY_VERSION__` → MyPy Python version (e.g., `3.13`)
   - Replaces `__PKG__` → Your package name
   - Creates `src/your_package/` directory structure
   - Updates all configuration files with your project details
   - Sets up virtual environment and installs dependencies

3. **GitFlow Initialization**:
   ```bash
   git flow init
   # Uses predefined branch conventions from .gitflow
   ```

4. **Development Workflow**:
   ```bash
   # Start new feature (via Claude or command line)
   /gitflow-start feature user-auth
   # OR: git flow feature start user-auth
   
   # Development cycle
   /check-code --fix
   # OR: python .claude/tools/code_quality.py --fix
   
   # Version bump
   /bump-version patch --pre-release alpha
   # OR: python .claude/tools/version_bump.py --bump patch --pre-release alpha
   
   # Finish feature
   /gitflow-finish feature user-auth
   # OR: git flow feature finish user-auth
   ```

5. **Version Management**:
   - Use `.claude/tools/version_bump.py` for PEP 440 compliant version updates
   - Supports pre-release tags: `1.2.3a1`, `1.2.3b2`, `1.2.3rc1`
   - Automatically updates VERSION file and CHANGELOG.md

## Configuration Placeholders

The template uses the following placeholders that should be replaced during setup:

| Placeholder | Example Value | Description |
|-------------|---------------|-------------|
| `__RUFF_TARGET__` | `py313` | Ruff Python target version |
| `__MYPY_PY_VERSION__` | `3.13` | MyPy Python version |
| `__PKG__` | `mypackage` | Primary package name |

## Claude Code Integration

This template is optimized for Claude Code development with:

- **Custom slash commands** in `.claude/commands/` for common tasks
- **Development utilities** in `.claude/tools/` accessible to Claude
- **Consistent coding patterns** defined in CLAUDE.md
- **Automated workflows** that Claude can execute
- **Dual execution modes**: Interactive via Claude or direct command line

## Three-Method Development Workflow Comparison

| Task | Manual Git Commands | Git Flow Commands | Claude Code Integration |
|------|-------------------|------------------|------------------------|
| **🚀 Start New Feature** | `git checkout develop`<br>`git checkout -b feature/user-auth`<br>`git push -u origin feature/user-auth` | `git flow feature start user-auth` | `/gitflow-start feature user-auth` |
| **📝 Code Quality Check** | `ruff format .`<br>`ruff check --fix .`<br>`mypy .`<br>`pytest -q` | *(same as manual)* | `/check-code --fix --verbose` |
| **🧪 Run Tests** | `pytest -v`<br>`pytest --cov=src --cov-report=html` | *(same as manual)* | `/run-tests --coverage --verbose` |
| **📦 Create New Module** | `touch src/pkg/module.py`<br>`touch tests/test_module.py`<br>*(manual coding...)* | *(same as manual)* | `/new-module user_manager --with-tests` |
| **🔢 Version Bump** | `echo "1.2.0" > VERSION`<br>`vim CHANGELOG.md`<br>`git add VERSION CHANGELOG.md`<br>`git commit -m "Bump to 1.2.0"` | *(manual + git flow release)* | `/bump-version minor` |
| **🔄 Finish Feature** | `git checkout develop`<br>`git merge feature/user-auth`<br>`git branch -d feature/user-auth`<br>`git push origin develop` | `git flow feature finish user-auth` | `/gitflow-finish feature user-auth` |
| **📋 Start Release** | `git checkout develop`<br>`git checkout -b release/1.2.0`<br>`echo "1.2.0" > VERSION`<br>`git add VERSION && git commit -m "Release 1.2.0"` | `git flow release start 1.2.0` | `/bump-version minor --pre-release rc`<br>`/gitflow-start release 1.2.0` |
| **✅ Finish Release** | `git checkout main`<br>`git merge release/1.2.0`<br>`git tag v1.2.0`<br>`git checkout develop`<br>`git merge release/1.2.0`<br>`git branch -d release/1.2.0` | `git flow release finish 1.2.0` | `/gitflow-finish release 1.2.0` |
| **🚨 Emergency Hotfix** | `git checkout main`<br>`git checkout -b hotfix/critical-fix`<br>`# fix code`<br>`echo "1.1.1" > VERSION` | `git flow hotfix start critical-fix` | `/gitflow-start hotfix critical-fix`<br>`/bump-version patch` |
| **🔧 Complete Hotfix** | `git checkout main`<br>`git merge hotfix/critical-fix`<br>`git tag v1.1.1`<br>`git checkout develop`<br>`git merge hotfix/critical-fix` | `git flow hotfix finish critical-fix` | `/gitflow-finish hotfix critical-fix` |
| **📊 Full Quality Pipeline** | `ruff format .`<br>`ruff check --fix .`<br>`mypy .`<br>`pytest --cov=src --cov-report=html`<br>`# Check htmlcov/index.html` | *(same as manual)* | `/check-code --fix --report` |

## Method Comparison Summary

### 🔧 Manual Git Commands
**Pros:** Complete control, works everywhere, no dependencies  
**Cons:** Verbose, error-prone, no automation, manual changelog management

### 🌊 Git Flow Commands  
**Pros:** Standardized branching, enforces workflow, automatic merging  
**Cons:** Still requires manual version/changelog updates, separate quality tools

### 🤖 Claude Code Integration
**Pros:** Fully automated, PEP 440 compliance, integrated quality pipeline, one-command workflows  
**Cons:** Requires Claude Code environment, template-specific

## Recommended Workflow Combinations

### 🏗️ Environment Setup & Management:

#### **🚀 From GitHub Template (Recommended)**
```bash
# Step 1: Use GitHub template (one-time setup)
# Go to repo settings → Check "Template repository"

# Step 2: Create new project from template
# On GitHub: Click "Use this template" → Create repository

# Step 3: Clone and bootstrap
git clone https://github.com/yourusername/your_new_project.git
cd your_new_project
python .claude/tools/bootstrap_python.py --package your_new_project --python 3.13 --author "Your Name" --install --create-venv
git add . && git commit -m "Bootstrap project from template" && git push
```

#### **📋 Manual Template Setup**
```bash
# 🐍 PYTHON PROJECT SETUP (Manual)
git clone https://github.com/unbedded/claud_code_bootstrap_python.git my_new_project
cd my_new_project && rm -rf .git && git init && git branch -M main
python .claude/tools/bootstrap_python.py --package my_new_project --python 3.13 --author "Your Name" --install --create-venv
git remote add origin https://github.com/yourusername/my_new_project.git
git add . && git commit -m "Initial commit from Claude Code template" && git push -u origin main

# ⚡ C++ PROJECT SETUP (Future - Currently TODO)
python .claude/tools/bootstrap_cpp.py --package myproject --cmake 3.20 --std 20 --conan
# Will create C++ project when fully implemented
```

#### **🔧 Ongoing Management**
```bash
# CONFIGURATION UPDATES  
python .claude/tools/update_config.py --python 3.13 --validate
# Updates all tool configs when Python version changes

# ✅ ENVIRONMENT VALIDATION
python .claude/tools/validate_setup.py --check-all --fix-issues --report
# Ensures project structure and configs are correct

# 🔄 MAINTENANCE
python .claude/tools/validate_setup.py --check-all          # Regular health checks
python .claude/tools/update_config.py --ruff-target py314   # Tool updates
```

### Complete Development Workflow:
```bash
# 🚀 FEATURE DEVELOPMENT
/gitflow-start feature                        # Claude suggests branch name from recent work
/new-module user_profile --with-tests
# ... coding ...
/review-code --files "src/user_profile*"      # (skip for solo dev - optional review)
/check-code --fix --verbose
/smart-commit --stage-all                     # Claude generates meaningful commit message
/gitflow-finish feature user-profile

# 📊 PRE-RELEASE ANALYSIS  
/review-commits --count 10                    # (skip for solo dev - analyze recent work)
/analyze-changes --branch develop             # Generate release notes
/suggest-version --analyze                    # Claude recommends version bump level

# 📦 RELEASE PREPARATION
/bump-version $(suggested_level) --pre-release rc   # Use Claude's suggestion
/plan-release --target $(cat VERSION)              # (skip for solo dev - create release plan)
git flow release start $(cat VERSION)              # (skip for solo dev - use /gitflow-start)
/check-code --fix --report                         # Full quality pipeline
/review-commits --since "last release"             # (skip for solo dev - final commit review)
git flow release finish $(cat VERSION)             # (skip for solo dev - use /gitflow-finish)

# 🚨 EMERGENCY HOTFIX
/gitflow-start hotfix                         # Claude suggests name from critical issues
# ... fix code ...
/review-code                                  # (skip for solo dev - quick review)
/check-code --fix
/smart-commit                                 # Generate descriptive hotfix message
/suggest-version                              # Usually patch, but Claude confirms
/bump-version patch
/gitflow-finish hotfix critical-fix
```

### Streamlined Solo Development:
```bash
# Most solo developers can skip the commented steps above and use:
/gitflow-start feature
/new-module module_name --with-tests
# ... coding ...
/check-code --fix
/smart-commit --stage-all
/gitflow-finish feature branch-name

# When ready for release:
/suggest-version --analyze
/bump-version $(suggested_level)
/check-code --fix --report
```

### Team Collaboration Workflow:
```bash
# Teams should use the complete workflow above, especially:
# - /review-commits for code quality oversight
# - /analyze-changes for comprehensive release notes  
# - /plan-release for coordinated releases
# - /review-code before merging features

# Additional team-specific steps:
/review-commits --count 20 --since "1 week ago"  # Weekly team review
/analyze-changes --branch main                   # Compare against production
```

## GitFlow Workflow

This template follows GitFlow branching strategy:

- `main`: Production-ready code
- `develop`: Integration branch for features  
- `feature/*`: New feature development
- `release/*`: Release preparation
- `hotfix/*`: Emergency fixes for production

Version tags follow PEP 440 semantic versioning with optional pre-release identifiers.

## Language-Specific Adaptations

### 🐍 Python (Current Template)
- **Quality Tools**: ruff, mypy, pytest, coverage
- **Package Management**: pip, requirements.txt, pyproject.toml  
- **Versioning**: PEP 440 compliant (1.2.3a1, 1.2.3b2, 1.2.3rc1)
- **Module Creation**: Python classes with CLAUDE.md patterns
- **Testing**: pytest with fixtures and parametrized tests

### ⚡ C++ Workflow Adaptations
```bash
# 🛠️ C++ QUALITY PIPELINE (instead of /check-code)
/check-cpp --format --lint --build --test
# → clang-format → cppcheck/clang-tidy → cmake build → ctest

# 📦 C++ MODULE CREATION (instead of /new-module)  
/new-class MyClass --namespace myproject --header-only
# → Creates .hpp/.cpp files with proper includes, namespaces, documentation

# 🔧 C++ ENVIRONMENT TOOLS
python .claude/tools/bootstrap_env.py --language cpp --cmake 3.20 --standard 20
# → Updates CMakeLists.txt, .clang-format, conanfile.txt templates

# 📊 C++ SPECIFIC COMMANDS
/analyze-includes --unused --circular          # Header dependency analysis  
/review-performance --profile --benchmarks     # Performance code review
/check-memory --valgrind --sanitizers          # Memory leak detection
```

### 🔄 Cross-Language Workflow Differences

| Aspect | Python Template | C++ Adaptation |
|--------|----------------|---------------|
| **Build System** | `pip install -e .` | `cmake --build build/` |
| **Quality Check** | `ruff + mypy + pytest` | `clang-format + cppcheck + ctest` |
| **Dependencies** | `requirements.txt` | `conanfile.txt` or `vcpkg.json` |
| **Module Template** | Class with config pattern | Header/source with namespaces |
| **Version Format** | PEP 440 (1.2.3a1) | SemVer (1.2.3-alpha.1) |
| **Testing** | pytest fixtures | Google Test or Catch2 |
| **Documentation** | Docstrings + Sphinx | Doxygen comments |

### 🚀 Multi-Language Project Support
```bash
# 🔧 LANGUAGE DETECTION & ADAPTATION
python .claude/tools/detect_language.py --adapt-workflow
# → Automatically configures tools based on project files found

# 🌍 POLYGLOT PROJECT MANAGEMENT  
/check-code --lang python cpp                 # Multi-language quality pipeline
/new-module auth_service --python --cpp       # Generate modules in both languages
python .claude/tools/sync_versions.py         # Keep version files synchronized
```

## Best Practices

- Use `/check-code` before commits to ensure code quality
- Leverage `/bump-version` for consistent semantic versioning
- Follow GitFlow patterns with `/gitflow-start` and `/gitflow-finish`
- Generate modules with `/new-module` to maintain coding standards
- All tools support both Claude Code slash commands and direct CLI execution
- **For C++**: Adapt quality pipeline and module templates to language-specific tools
- **Multi-language**: Use detection tools to auto-configure workflows