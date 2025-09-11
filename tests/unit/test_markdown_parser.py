"""Unit tests for MarkdownParser with OpenAI integration.

This test module provides comprehensive testing of the MarkdownParser class
following CLAUDE.md testing standards with mocked OpenAI responses and validation.

The tests cover:
- Recipe file parsing with various formats
- OpenAI integration and response handling
- YAML validation integration
- Error handling and edge cases
- Configuration management
- File I/O operations

Example usage:
    pytest tests/unit/test_markdown_parser.py -v
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from recipe_fmt.models.config import OpenAIConfig
from recipe_fmt.parsers.markdown_parser import MarkdownParser, ParseResult, create_parser_from_env
from recipe_fmt.parsers.openai_client import OpenAIResponse


class TestMarkdownParserInitialization:
    """Test suite for MarkdownParser initialization and configuration."""

    def test_initialization_with_config(self):
        """Test parser initializes correctly with OpenAI config."""
        config = OpenAIConfig(api_key="sk-test-key", model="gpt-4")
        parser = MarkdownParser(config)

        assert parser.config == config
        assert parser.cfg_dict["validate_yaml"] is True
        assert parser.cfg_dict["allow_partial_parsing"] is False
        assert parser.cfg_dict["strict_validation"] is True

    def test_initialization_with_custom_config_dict(self):
        """Test parser initialization with custom configuration dictionary."""
        config = OpenAIConfig(api_key="sk-test-key")
        cfg_dict = {
            "validate_yaml": False,
            "allow_partial_parsing": True,
            "strict_validation": False,
            "preserve_markdown": True,
        }

        parser = MarkdownParser(config, cfg_dict)

        assert parser.cfg_dict["validate_yaml"] is False
        assert parser.cfg_dict["allow_partial_parsing"] is True
        assert parser.cfg_dict["strict_validation"] is False
        assert parser.cfg_dict["preserve_markdown"] is True

    def test_config_defaults_application(self):
        """Test that configuration defaults are applied correctly."""
        config = OpenAIConfig(api_key="sk-test-key")
        parser = MarkdownParser(config, {})

        # Check all defaults are applied
        assert parser.cfg_dict["validate_yaml"] is True
        assert parser.cfg_dict["allow_partial_parsing"] is False
        assert parser.cfg_dict["strict_validation"] is True
        assert parser.cfg_dict["preserve_markdown"] is False

    def test_openai_client_initialization(self):
        """Test that OpenAI client is properly initialized."""
        config = OpenAIConfig(api_key="sk-test-key")
        parser = MarkdownParser(config)

        assert parser.openai_client is not None
        assert parser.openai_client.config == config

    def test_create_parser_from_env(self):
        """Test factory function for creating parser from environment."""
        parser = create_parser_from_env({"validate_yaml": False})

        assert isinstance(parser, MarkdownParser)
        assert parser.cfg_dict["validate_yaml"] is False


class TestMarkdownParserFileOperations:
    """Test suite for file parsing operations."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(api_key="sk-test-key")
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_parse_valid_markdown_file(self):
        """Test parsing a valid markdown recipe file."""
        # Create test markdown file
        test_file = Path(self.temp_dir) / "test_recipe.md"
        markdown_content = """# Chocolate Chip Cookies

A classic cookie recipe that everyone loves.

## Ingredients
- 2 cups all-purpose flour
- 1 tsp baking soda
- 1 cup butter, softened
- 2 large eggs

## Instructions
1. Preheat oven to 375°F
2. Mix dry ingredients in large bowl
3. Cream butter and sugars
4. Add eggs and vanilla
5. Combine wet and dry ingredients
6. Drop spoonfuls on baking sheet
7. Bake 9-11 minutes until golden
"""
        test_file.write_text(markdown_content)

        # Mock successful OpenAI response
        mock_yaml = """title: "Chocolate Chip Cookies"
category: "Dessert"
description: "A classic cookie recipe that everyone loves"
servings: 24
ingredients:
  - ingredient: "all-purpose flour"
    amount: 2
    unit: "cups"
    weight_grams: 240
    purpose: "base"
instructions:
  - "Preheat oven to 375°F"
  - "Mix dry ingredients in large bowl"
"""

        with patch.object(MarkdownParser, "_parse_markdown_content") as mock_parse:
            mock_parse.return_value = ParseResult(
                success=True,
                yaml_content=mock_yaml,
                tokens_used=150,
                cost_estimate=0.001,
                cached=False,
            )

            parser = MarkdownParser(self.config)
            result = parser.parse_recipe_file(test_file)

        assert result.success is True
        assert result.yaml_content == mock_yaml
        assert result.tokens_used == 150
        assert result.cost_estimate == 0.001
        mock_parse.assert_called_once_with(markdown_content, "test_recipe.md")

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        parser = MarkdownParser(self.config)
        nonexistent_file = Path(self.temp_dir) / "missing.md"

        result = parser.parse_recipe_file(nonexistent_file)

        assert result.success is False
        assert "not found" in result.error

    def test_parse_invalid_file_extension(self):
        """Test parsing file with invalid extension."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("# Recipe")

        parser = MarkdownParser(self.config)
        result = parser.parse_recipe_file(test_file)

        assert result.success is False
        assert "Invalid file type" in result.error

    def test_parse_empty_file(self):
        """Test parsing an empty markdown file."""
        test_file = Path(self.temp_dir) / "empty.md"
        test_file.write_text("")

        parser = MarkdownParser(self.config)
        result = parser.parse_recipe_file(test_file)

        assert result.success is False
        assert "empty" in result.error.lower()

    def test_parse_file_with_unicode(self):
        """Test parsing file with unicode characters."""
        test_file = Path(self.temp_dir) / "unicode.md"
        unicode_content = """# Café au Lait

## Ingrédients
- 1 tasse de café
- 2 cuillères à soupe de lait
"""
        test_file.write_text(unicode_content, encoding="utf-8")

        with patch.object(MarkdownParser, "_parse_markdown_content") as mock_parse:
            mock_parse.return_value = ParseResult(success=True, yaml_content="test: yaml")

            parser = MarkdownParser(self.config)
            result = parser.parse_recipe_file(test_file)

        assert result.success is True
        mock_parse.assert_called_once_with(unicode_content, "unicode.md")


class TestMarkdownParserContentParsing:
    """Test suite for content parsing functionality."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(api_key="sk-test-key")

    def test_parse_recipe_content_direct(self):
        """Test parsing markdown content directly."""
        markdown_content = "# Simple Recipe\n- 1 ingredient\n1. One step"

        with patch.object(MarkdownParser, "_parse_markdown_content") as mock_parse:
            mock_parse.return_value = ParseResult(success=True, yaml_content="simple: yaml")

            parser = MarkdownParser(self.config)
            result = parser.parse_recipe_content(markdown_content, "test_recipe")

        assert result.success is True
        mock_parse.assert_called_once_with(markdown_content, "test_recipe")

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = MarkdownParser(self.config)
        result = parser.parse_recipe_content("", "empty_recipe")

        assert result.success is False
        assert "empty" in result.error.lower()

    def test_parse_content_whitespace_only(self):
        """Test parsing content with only whitespace."""
        parser = MarkdownParser(self.config)
        result = parser.parse_recipe_content("   \n\t  \n  ", "whitespace_recipe")

        assert result.success is False
        assert "empty" in result.error.lower()


class TestMarkdownParserOpenAIIntegration:
    """Test suite for OpenAI integration."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(api_key="sk-test-key")

    @patch("recipe_fmt.parsers.markdown_parser.OpenAIClient")
    def test_openai_parsing_failure(self, mock_openai_client_class):
        """Test handling of OpenAI parsing failure."""
        # Setup mock OpenAI client to fail
        mock_client = Mock()
        mock_openai_response = OpenAIResponse(
            success=False, error="API rate limit exceeded", tokens_used=0, cost_estimate=0.0
        )
        mock_client.parse_recipe_markdown.return_value = mock_openai_response
        mock_openai_client_class.return_value = mock_client

        parser = MarkdownParser(self.config)
        result = parser._parse_markdown_content("# Test Recipe", "test.md")

        assert result.success is False
        assert "API rate limit exceeded" in result.error

    @patch("recipe_fmt.parsers.markdown_parser.OpenAIClient")
    def test_openai_empty_response(self, mock_openai_client_class):
        """Test handling of empty OpenAI response."""
        # Setup mock OpenAI client to return empty content
        mock_client = Mock()
        mock_openai_response = OpenAIResponse(success=True, data={"content": ""}, tokens_used=50, cost_estimate=0.001)
        mock_client.parse_recipe_markdown.return_value = mock_openai_response
        mock_openai_client_class.return_value = mock_client

        parser = MarkdownParser(self.config)
        result = parser._parse_markdown_content("# Test Recipe", "test.md")

        assert result.success is False
        assert "empty content" in result.error


class TestMarkdownParserYAMLValidation:
    """Test suite for YAML validation integration."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(api_key="sk-test-key")

    def test_yaml_validation_success(self):
        """Test successful YAML validation and Recipe creation."""
        valid_yaml = """title: "Test Recipe"
category: "Breakfast"
description: "A test recipe"
servings: 4
ingredients:
  - ingredient: "flour"
    amount: 2
    unit: "cups"
    weight_grams: 240
    purpose: "base"
instructions:
  - "Mix ingredients"
  - "Cook until done"
"""

        parser = MarkdownParser(self.config, {"validate_yaml": True})
        result = parser._validate_and_parse_yaml(valid_yaml, "test.md", 100, 0.001, False)

        assert result.success is True
        assert result.recipe is not None
        assert result.recipe.title == "Test Recipe"
        assert result.recipe.category == "Breakfast"
        assert len(result.recipe.ingredients) == 1
        assert len(result.recipe.instructions) == 2

    def test_yaml_validation_invalid_yaml(self):
        """Test handling of invalid YAML syntax."""
        invalid_yaml = """title: "Test Recipe"
category: "Breakfast"
ingredients:
  - ingredient: "flour"
    amount: 2
    unit: cups"  # Missing opening quote
"""

        parser = MarkdownParser(self.config, {"validate_yaml": True})
        result = parser._validate_and_parse_yaml(invalid_yaml, "test.md", 100, 0.001, False)

        assert result.success is False
        # Should contain error information about validation/parsing issues
        error_msg = result.error.lower()
        assert any(keyword in error_msg for keyword in ["parsing", "yaml", "validation", "error"])

    def test_yaml_validation_pydantic_error(self):
        """Test handling of Pydantic validation errors."""
        invalid_recipe_yaml = """title: ""  # Empty title not allowed
category: "InvalidCategory"
servings: -1  # Negative servings not allowed
ingredients: []  # Empty ingredients not allowed
instructions: []  # Empty instructions not allowed
"""

        parser = MarkdownParser(self.config, {"validate_yaml": True})
        result = parser._validate_and_parse_yaml(invalid_recipe_yaml, "test.md", 100, 0.001, False)

        assert result.success is False
        assert "Recipe validation error" in result.error

    def test_partial_parsing_allowed(self):
        """Test partial parsing when validation fails but partial parsing is enabled."""
        invalid_yaml = """title: "Test Recipe"
servings: "invalid_number"  # Should be integer
ingredients:
  - ingredient: "flour"
    amount: 2
    unit: "cups"
instructions:
  - "Mix ingredients"
"""

        parser = MarkdownParser(self.config, {"validate_yaml": True, "allow_partial_parsing": True})
        result = parser._validate_and_parse_yaml(invalid_yaml, "test.md", 100, 0.001, False)

        assert result.success is False
        assert result.yaml_content == invalid_yaml  # Raw YAML preserved
        assert "validation error" in result.error


class TestMarkdownParserEdgeCases:
    """Test suite for edge cases and error conditions."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(api_key="sk-test-key")

    def test_very_large_markdown_file(self):
        """Test parsing very large markdown content."""
        # Create large content (100KB)
        large_content = "# Large Recipe\n" + "- ingredient\n" * 10000

        with patch.object(MarkdownParser, "_parse_markdown_content") as mock_parse:
            mock_parse.return_value = ParseResult(success=True, yaml_content="test: yaml")

            parser = MarkdownParser(self.config)
            result = parser.parse_recipe_content(large_content, "large_recipe")

        assert result.success is True
        mock_parse.assert_called_once()

    def test_markdown_with_special_characters(self):
        """Test parsing markdown with special characters."""
        special_content = """# Recipe with Special Chars & Symbols

## Ingredients
- 1/2 cup sugar (½ cup)
- 2 tablespoons butter @ room temperature
- Salt & pepper to taste

## Instructions
1. Mix ingredients "thoroughly"
2. Bake at 350°F for 30' (30 minutes)
"""

        with patch.object(MarkdownParser, "_parse_markdown_content") as mock_parse:
            mock_parse.return_value = ParseResult(success=True, yaml_content="test: yaml")

            parser = MarkdownParser(self.config)
            result = parser.parse_recipe_content(special_content, "special_recipe")

        assert result.success is True

    def test_parsing_statistics(self):
        """Test parsing statistics collection."""
        parser = MarkdownParser(self.config)
        stats = parser.get_parsing_stats()

        assert "openai_stats" in stats
        assert "parser_config" in stats
        assert "validate_yaml" in stats["parser_config"]
        assert "allow_partial_parsing" in stats["parser_config"]
        assert "strict_validation" in stats["parser_config"]

    def test_concurrent_parsing_simulation(self):
        """Test parser behavior under simulated concurrent access."""
        import threading

        parser = MarkdownParser(self.config)
        results = []
        errors = []

        def worker(worker_id):
            try:
                content = f"# Recipe {worker_id}\n- ingredient {worker_id}\n1. Step {worker_id}"
                with patch.object(parser, "_parse_markdown_content") as mock_parse:
                    mock_parse.return_value = ParseResult(success=True, yaml_content=f"title: Recipe {worker_id}")
                    result = parser.parse_recipe_content(content, f"recipe_{worker_id}")
                    results.append((worker_id, result.success))
            except Exception as e:
                errors.append((worker_id, str(e)))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All should succeed without errors
        assert len(errors) == 0
        assert len(results) == 5
        assert all(success for _, success in results)


class TestMarkdownParserIntegration:
    """Test suite for integration scenarios."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(api_key="sk-test-key")
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("recipe_fmt.parsers.markdown_parser.OpenAIClient")
    def test_end_to_end_parsing_flow(self, mock_openai_client_class):
        """Test complete end-to-end parsing flow."""
        # Create test file
        test_file = Path(self.temp_dir) / "pancakes.md"
        markdown_content = """# Perfect Pancakes

Fluffy weekend pancakes for the family.

## Ingredients
- 2 cups all-purpose flour
- 2 TBL granulated sugar
- 2 tsp baking powder
- 1 tsp salt
- 1 cup whole milk

## Instructions
1. Mix dry ingredients in large bowl
2. Combine wet ingredients separately
3. Fold wet into dry until just combined
4. Cook on hot griddle until bubbles form
5. Flip and cook until golden brown
"""
        test_file.write_text(markdown_content)

        # Setup mock OpenAI response
        mock_yaml = """title: "Perfect Pancakes"
category: "Breakfast"
description: "Fluffy weekend pancakes for the family"
servings: 4
prep_time: "10 minutes"
cook_time: "15 minutes"
ingredients:
  - ingredient: "all-purpose flour"
    amount: 2
    unit: "cups"
    weight_grams: 240
    purpose: "base"
  - ingredient: "granulated sugar"
    amount: 2
    unit: "TBL"
    weight_grams: 25
    purpose: "sweetener"
instructions:
  - "Mix dry ingredients in large bowl"
  - "Combine wet ingredients separately"
  - "Fold wet into dry until just combined"
  - "Cook on hot griddle until bubbles form"
  - "Flip and cook until golden brown"
"""

        mock_client = Mock()
        mock_openai_response = OpenAIResponse(
            success=True,
            data={"content": mock_yaml},
            tokens_used=200,
            cost_estimate=0.003,
            cached=False,
        )
        mock_client.parse_recipe_markdown.return_value = mock_openai_response
        mock_openai_client_class.return_value = mock_client

        # Parse the file
        parser = MarkdownParser(self.config, {"validate_yaml": True})
        result = parser.parse_recipe_file(test_file)

        # Verify results
        assert result.success is True
        assert result.recipe is not None
        assert result.recipe.title == "Perfect Pancakes"
        assert result.recipe.category == "Breakfast"
        assert len(result.recipe.ingredients) == 2
        assert len(result.recipe.instructions) == 5
        assert result.tokens_used == 200
        assert result.cost_estimate == 0.003

        # Verify OpenAI was called correctly
        mock_client.parse_recipe_markdown.assert_called_once_with(markdown_content)

    def test_configuration_combinations(self):
        """Test various configuration combinations."""
        test_configs = [
            {"validate_yaml": True, "strict_validation": True},
            {"validate_yaml": False, "allow_partial_parsing": True},
            {"validate_yaml": True, "allow_partial_parsing": False},
            {"preserve_markdown": True, "strict_validation": False},
        ]

        for cfg in test_configs:
            parser = MarkdownParser(self.config, cfg)

            # Verify configuration was applied
            for key, value in cfg.items():
                assert parser.cfg_dict[key] == value

            # Verify parser is functional
            assert parser.openai_client is not None
            assert parser.get_cfg() == parser.cfg_dict


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
