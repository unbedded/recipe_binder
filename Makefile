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

build-pdfs: recipe/pdf/Dessert-chocolate-chip-cookies.pdf \
           recipe/pdf/Dessert-chocolate-avocado-mousse.pdf \
           recipe/pdf/Main-thai-basil-chicken.pdf \
           recipe/pdf/Baking-homemade-pizza-dough.pdf \
           recipe/pdf/Baking-garlic-herb-bread.pdf \
           recipe/pdf/Salad-green-goddess-salad.pdf \
           recipe/pdf/Breakfast-perfect-pancakes.pdf

# Incremental dependencies - like code compilation!
# Each category gets its own rule for proper dependency tracking

recipe/pdf/Dessert-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Dessert recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Main-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Main recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Baking-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Baking recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Breakfast-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Breakfast recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Salad-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Salad recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Soup-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Soup recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Side-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Side recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Sauce-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Sauce recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Meat-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Meat recipe: $*"
	python -m recipe_fmt.pipeline --yaml-to-pdf $< --log-level INFO

recipe/pdf/Other-%.pdf: recipe/yaml/%.yaml recipe/templates/default-card.yaml | recipe/pdf
	@echo "🚀 Building Other recipe: $*"
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
