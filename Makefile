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

build: recipe/pdf/.timestamp ## Process all recipes through the pipeline (with dependency tracking)
	@echo "✅ Build complete! Check recipe/pdf/ for generated cards."

# Timestamp-based dependency tracking - only rebuilds when YAML or template files change
recipe/pdf/.timestamp: $(wildcard recipe/yaml/*.yaml) recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building recipe cards..."
	python -m recipe_fmt.pipeline --log-level INFO
	@touch $@

# Ensure PDF directory exists
recipe/pdf:
	@mkdir -p recipe/pdf

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
