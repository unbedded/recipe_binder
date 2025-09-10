# Recipe Binder - AI-Powered Recipe Cards
# Makefile for build automation

.PHONY: help install clean build demo lint typecheck test

# Default target
help: ## Show this help message
	@echo "Recipe Binder - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and setup development environment
	@echo "🔧 Installing Recipe Binder..."
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	@echo "✅ Installation complete!"

clean: ## Remove all generated PDF files and cache
	@echo "🧹 Cleaning generated files..."
	rm -rf recipe/pdf/*.pdf recipe/pdf/.timestamp
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete!"

build: build-pdfs ## Process all recipes with incremental dependencies
	@echo "✅ Build complete! Check recipe/pdf/ for generated cards."

# Auto-discover all markdown and YAML files for dynamic building
MD_FILES := $(wildcard recipe/markdown/*.md)
YAML_FILES := $(wildcard recipe/yaml/*.yaml)

# Convert markdown files to their expected YAML targets
YAML_FROM_MD := $(MD_FILES:recipe/markdown/%.md=recipe/yaml/%.yaml)

# All YAML files (existing + converted from markdown)
ALL_YAML := $(sort $(YAML_FILES) $(YAML_FROM_MD))

# Build all recipes by processing YAML files directly
build-pdfs: $(ALL_YAML) | recipe/pdf
	@echo "🚀 Processing $(words $(ALL_YAML)) recipe files..."
	@for yaml in $(ALL_YAML); do \
		if [ -f "$$yaml" ]; then \
			echo "🚀 Building recipe: $$(basename $$yaml .yaml)"; \
			python -m recipe_fmt.pipeline --yaml-to-pdf "$$yaml" --log-level INFO || exit 1; \
		fi; \
	done
	@echo "📊 Built recipe cards from $(words $(MD_FILES)) markdown and $(words $(YAML_FILES)) YAML files"


# Dynamic PDF generation rule
# The pipeline determines the category from YAML content and generates Category-recipe.pdf
recipe/pdf/%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

# Markdown to YAML conversion rules
recipe/yaml/%.yaml: recipe/markdown/%.md | recipe/yaml
	@echo "🔄 Converting markdown to YAML: $*"
	python -m recipe_fmt.pipeline --md-to-yaml $< --log-level INFO

# Ensure directories exist
recipe/pdf:
	@mkdir -p recipe/pdf

recipe/yaml:
	@mkdir -p recipe/yaml

demo: ## Generate demo recipe cards
	@echo "🍳 Creating demo recipes..."
	python -m recipe_fmt.pipeline --demo --log-level INFO
	@echo "✅ Demo complete! Open recipe/pdf/ to view sample cards."

lint: ## Run code formatting and linting
	@echo "🔍 Running ruff formatting and linting..."
	ruff format .
	ruff check --fix .
	@echo "✅ Linting complete!"

typecheck: ## Run static type checking
	@echo "🔍 Running mypy type checking..."
	mypy .
	@echo "✅ Type checking complete!"

test: ## Run comprehensive test suite
	@echo "🧪 Running test suite..."
	pytest -q --tb=short
	@echo "✅ Tests complete!"

# Development workflow
dev-setup: install ## Setup complete development environment
	@echo "🎯 Development environment ready!"
	@echo "Try: make demo"

# CI/CD targets
ci-test: lint typecheck test ## Run all CI checks
	@echo "✅ All CI checks passed!"
