"""Integration tests for the complete recipe processing pipeline.

This test module provides comprehensive integration testing of the full pipeline
following CLAUDE.md testing standards with end-to-end processing scenarios.

The tests cover:
- Complete markdown → YAML → PDF pipeline
- Component integration
- Error handling across components
- Configuration management
- Performance and scalability
- Real-world usage scenarios

Example usage:
    pytest tests/integration/test_pipeline_integration.py -v
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from recipe_fmt.models.config import AppConfig
from recipe_fmt.parsers.openai_client import OpenAIResponse
from recipe_fmt.pipeline import RecipePipeline


class TestPipelineIntegrationBasic:
    """Test suite for basic pipeline integration."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig(debug=True)

        # Create test directory structure
        self.recipe_dir = Path(self.temp_dir) / "recipe"
        self.markdown_dir = self.recipe_dir / "markdown"
        self.yaml_dir = self.recipe_dir / "yaml"
        self.pdf_dir = self.recipe_dir / "pdf"

        for dir_path in [self.markdown_dir, self.yaml_dir, self.pdf_dir]:
            dir_path.mkdir(parents=True)

        # Create test markdown file
        self.test_md_file = self.markdown_dir / "test-recipe.md"
        self.test_markdown_content = """# Test Recipe

A simple test recipe for integration testing.

## Ingredients
- 2 cups all-purpose flour
- 1 TBL sugar
- 1 tsp salt
- 1 cup milk

## Instructions
1. Mix dry ingredients in bowl
2. Add milk and stir until combined
3. Cook on griddle until golden
"""
        self.test_md_file.write_text(self.test_markdown_content)

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("recipe_fmt.parsers.openai_client.OpenAIClient")
    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    @patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate")
    def test_complete_pipeline_success(self, mock_doc_class, mock_openai_client_class):
        """Test successful end-to-end pipeline execution."""
        # Setup mock OpenAI response
        mock_yaml_content = """title: "Test Recipe"
category: "Other"
description: "A simple test recipe for integration testing"
servings: 4
prep_time: "5 minutes"
cook_time: "10 minutes"
ingredients:
  - ingredient: "all-purpose flour"
    amount: 2
    unit: "cups"
    weight_grams: 240
    purpose: "base"
  - ingredient: "sugar"
    amount: 1
    unit: "TBL"
    weight_grams: 12
    purpose: "sweetener"
  - ingredient: "salt"
    amount: 1
    unit: "tsp"
    weight_grams: 6
    purpose: "seasoning"
  - ingredient: "milk"
    amount: 1
    unit: "cup"
    weight_grams: 240
    purpose: "liquid"
instructions:
  - "Mix dry ingredients in bowl"
  - "Add milk and stir until combined"
  - "Cook on griddle until golden"
"""

        mock_client = Mock()
        mock_openai_response = OpenAIResponse(
            success=True,
            data={"content": mock_yaml_content},
            tokens_used=150,
            cost_estimate=0.003,
            cached=False,
        )
        mock_client.parse_recipe_markdown.return_value = mock_openai_response
        mock_openai_client_class.return_value = mock_client

        # Setup mock PDF generation
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc

        # Configure file manager to use test directory
        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()

            # Mock file manager methods
            mock_file_manager.ensure_directories_exist.return_value = True
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": [self.test_md_file],
                "yaml_to_pdf": [],  # Will be populated after YAML creation
            }
            mock_file_manager.get_corresponding_yaml_path.return_value = self.yaml_dir / "test-recipe.yaml"
            mock_file_manager.get_corresponding_pdf_path.return_value = self.pdf_dir / "Other-test-recipe.pdf"

            mock_file_manager_class.return_value = mock_file_manager

            # Run pipeline
            pipeline = RecipePipeline(self.config)

            with patch.object(Path, "stat") as mock_stat:
                mock_stat.return_value.st_size = 25000
                results = pipeline.run()

        # Verify results
        assert results["success"] is True
        assert results["total_processed"] >= 1
        assert len(results["errors"]) == 0

        # Verify metrics
        metrics = results["metrics"]
        assert metrics["total_tokens_used"] == 150
        assert metrics["total_cost_estimate"] == 0.003
        assert metrics["cached_responses"] == 0

    @patch("recipe_fmt.parsers.openai_client.OpenAIClient")
    def test_pipeline_openai_failure(self, mock_openai_client_class):
        """Test pipeline behavior when OpenAI parsing fails."""
        # Setup mock OpenAI to fail
        mock_client = Mock()
        mock_openai_response = OpenAIResponse(
            success=False, error="API rate limit exceeded", tokens_used=0, cost_estimate=0.0
        )
        mock_client.parse_recipe_markdown.return_value = mock_openai_response
        mock_openai_client_class.return_value = mock_client

        # Configure file manager
        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = True
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": [self.test_md_file],
                "yaml_to_pdf": [],
            }
            mock_file_manager.get_corresponding_yaml_path.return_value = self.yaml_dir / "test-recipe.yaml"
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(self.config)
            results = pipeline.run()

        # Should handle OpenAI failure gracefully
        assert results["success"] is False
        assert len(results["errors"]) > 0
        assert "API rate limit exceeded" in str(results["errors"])

    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", False)
    def test_pipeline_pdf_generation_failure(self):
        """Test pipeline behavior when PDF generation fails."""
        # Create valid YAML file first
        yaml_file = self.yaml_dir / "test-recipe.yaml"
        yaml_content = {
            "title": "Test Recipe",
            "category": "Other",
            "servings": 4,
            "ingredients": [{"ingredient": "flour", "amount": 1, "unit": "cup"}],
            "instructions": ["Mix ingredients"],
        }
        with open(yaml_file, "w") as f:
            yaml.dump(yaml_content, f)

        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = True
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": [],
                "yaml_to_pdf": [yaml_file],
            }
            mock_file_manager.get_corresponding_pdf_path.return_value = self.pdf_dir / "test.pdf"
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(self.config)
            results = pipeline.run()

        # Should handle PDF generation failure
        assert results["success"] is False
        assert len(results["errors"]) > 0


class TestPipelineIntegrationAdvanced:
    """Test suite for advanced pipeline integration scenarios."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig(debug=False)

        # Create multiple test recipes
        self.recipe_dir = Path(self.temp_dir) / "recipe"
        self.markdown_dir = self.recipe_dir / "markdown"
        self.yaml_dir = self.recipe_dir / "yaml"
        self.pdf_dir = self.recipe_dir / "pdf"

        for dir_path in [self.markdown_dir, self.yaml_dir, self.pdf_dir]:
            dir_path.mkdir(parents=True)

        # Create multiple test recipes
        self.recipes = {
            "pancakes.md": """# Perfect Pancakes
## Ingredients
- 2 cups flour
- 1 TBL sugar
## Instructions
1. Mix ingredients
2. Cook on griddle
""",
            "cookies.md": """# Chocolate Cookies
## Ingredients
- 2 cups flour
- 1 cup chocolate chips
## Instructions
1. Mix ingredients
2. Bake at 350F
""",
            "soup.md": """# Chicken Soup
## Ingredients
- 1 lb chicken
- 4 cups broth
## Instructions
1. Boil chicken
2. Add broth and simmer
""",
        }

        for filename, content in self.recipes.items():
            (self.markdown_dir / filename).write_text(content)

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("recipe_fmt.parsers.openai_client.OpenAIClient")
    @patch("recipe_fmt.generators.pdf_generator.REPORTLAB_AVAILABLE", True)
    @patch("recipe_fmt.generators.pdf_generator.SimpleDocTemplate")
    def test_batch_processing_multiple_recipes(self, mock_doc_class, mock_openai_client_class):
        """Test processing multiple recipes in batch."""
        # Setup mock responses for different recipes
        mock_responses = {
            "pancakes.md": """title: "Perfect Pancakes"
category: "Breakfast"
servings: 4
ingredients:
  - ingredient: "flour"
    amount: 2
    unit: "cups"
    weight_grams: 240
    purpose: "base"
instructions:
  - "Mix ingredients"
  - "Cook on griddle"
""",
            "cookies.md": """title: "Chocolate Cookies"
category: "Dessert"
servings: 24
ingredients:
  - ingredient: "flour"
    amount: 2
    unit: "cups"
    weight_grams: 240
    purpose: "base"
instructions:
  - "Mix ingredients"
  - "Bake at 350F"
""",
            "soup.md": """title: "Chicken Soup"
category: "Soup"
servings: 6
ingredients:
  - ingredient: "chicken"
    amount: 1
    unit: "lbs"
    weight_grams: 454
    purpose: "protein"
instructions:
  - "Boil chicken"
  - "Add broth and simmer"
""",
        }

        # Setup mock OpenAI client
        mock_client = Mock()

        def mock_parse_side_effect(content):
            # Determine which recipe based on content
            for recipe_file, yaml_content in mock_responses.items():
                recipe_name = recipe_file.replace(".md", "").replace("-", " ").title()
                if recipe_name.lower() in content.lower():
                    return OpenAIResponse(
                        success=True,
                        data={"content": yaml_content},
                        tokens_used=100,
                        cost_estimate=0.002,
                        cached=False,
                    )

            # Default response
            return OpenAIResponse(
                success=True,
                data={"content": list(mock_responses.values())[0]},
                tokens_used=100,
                cost_estimate=0.002,
                cached=False,
            )

        mock_client.parse_recipe_markdown.side_effect = mock_parse_side_effect
        mock_openai_client_class.return_value = mock_client

        # Setup mock PDF generation
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc

        # Configure file manager for batch processing
        md_files = [self.markdown_dir / filename for filename in self.recipes.keys()]

        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = True
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": md_files,
                "yaml_to_pdf": [],
            }

            # Mock path conversion methods
            def mock_get_yaml_path(md_path):
                return self.yaml_dir / md_path.name.replace(".md", ".yaml")

            def mock_get_pdf_path(yaml_path, category="Other"):
                base_name = yaml_path.stem
                return self.pdf_dir / f"{category}-{base_name}.pdf"

            mock_file_manager.get_corresponding_yaml_path.side_effect = mock_get_yaml_path
            mock_file_manager.get_corresponding_pdf_path.side_effect = mock_get_pdf_path

            mock_file_manager_class.return_value = mock_file_manager

            # Run pipeline
            pipeline = RecipePipeline(self.config)

            with patch.object(Path, "stat") as mock_stat:
                mock_stat.return_value.st_size = 15000
                results = pipeline.run()

        # Verify batch processing results
        assert results["success"] is True
        assert results["total_processed"] == len(self.recipes)
        assert len(results["errors"]) == 0

        # Verify metrics accumulation
        metrics = results["metrics"]
        assert metrics["total_tokens_used"] == len(self.recipes) * 100
        assert metrics["total_cost_estimate"] == len(self.recipes) * 0.002

    @patch("recipe_fmt.parsers.openai_client.OpenAIClient")
    def test_partial_failure_handling(self, mock_openai_client_class):
        """Test pipeline handling of partial failures in batch processing."""
        # Setup mock client with mixed success/failure
        mock_client = Mock()

        call_count = 0

        def mock_parse_side_effect(content):
            nonlocal call_count
            call_count += 1

            if call_count == 2:  # Second call fails
                return OpenAIResponse(success=False, error="Temporary API error", tokens_used=0, cost_estimate=0.0)
            else:
                return OpenAIResponse(
                    success=True,
                    data={
                        "content": ("title: Test\\ncategory: Other\\nservings: 4\\ningredients: []\\ninstructions: []")
                    },
                    tokens_used=100,
                    cost_estimate=0.002,
                    cached=False,
                )

        mock_client.parse_recipe_markdown.side_effect = mock_parse_side_effect
        mock_openai_client_class.return_value = mock_client

        # Setup file manager
        md_files = [self.markdown_dir / filename for filename in self.recipes.keys()]

        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = True
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": md_files,
                "yaml_to_pdf": [],
            }
            mock_file_manager.get_corresponding_yaml_path.return_value = self.yaml_dir / "test.yaml"
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(self.config)
            results = pipeline.run()

        # Should handle partial failures
        assert results["success"] is False  # Overall failure due to errors
        assert results["total_processed"] == 2  # Two successful
        assert len(results["errors"]) == 1  # One failure
        assert "Temporary API error" in str(results["errors"])


class TestPipelineIntegrationConfiguration:
    """Test suite for pipeline configuration integration."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_force_rebuild_mode(self):
        """Test pipeline force rebuild functionality."""
        # Create test structure
        recipe_dir = Path(self.temp_dir) / "recipe"
        markdown_dir = recipe_dir / "markdown"
        yaml_dir = recipe_dir / "yaml"
        markdown_dir.mkdir(parents=True)
        yaml_dir.mkdir(parents=True)

        # Create markdown and corresponding YAML (newer)
        md_file = markdown_dir / "test.md"
        yaml_file = yaml_dir / "test.yaml"

        md_file.write_text("# Test Recipe")
        yaml_file.write_text("title: Test Recipe")

        # Make YAML newer than markdown
        import time

        time.sleep(0.1)
        yaml_file.touch()

        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = True

            # In normal mode, should not process (YAML is newer)
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": [],  # Not stale
                "yaml_to_pdf": [],
            }

            mock_file_manager_class.return_value = mock_file_manager

            config = AppConfig()
            pipeline = RecipePipeline(config)
            results = pipeline.run(force_rebuild=False)

            # Should not process anything
            assert results["total_processed"] == 0

            # Now test force rebuild
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": [md_file],  # Force rebuild
                "yaml_to_pdf": [],
            }

            with patch("recipe_fmt.pipeline.OpenAIClient") as mock_openai_client_class:
                mock_client = Mock()
                mock_client.parse_recipe_markdown.return_value = OpenAIResponse(
                    success=True,
                    data={"content": "title: Rebuilt"},
                    tokens_used=50,
                    cost_estimate=0.001,
                )
                mock_openai_client_class.return_value = mock_client
                mock_file_manager.get_corresponding_yaml_path.return_value = yaml_file

                results = pipeline.run(force_rebuild=True)

            # Should process with force rebuild
            assert results["total_processed"] >= 1

    def test_demo_mode(self):
        """Test pipeline demo mode functionality."""
        config = AppConfig()

        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = True
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": [],
                "yaml_to_pdf": [],
            }
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(config)
            results = pipeline.run(demo_mode=True)

            # Demo mode should run successfully
            assert "success" in results

    def test_clean_functionality(self):
        """Test pipeline clean functionality."""
        config = AppConfig()

        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.clean_generated_files.return_value = 5  # 5 files cleaned
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(config)
            clean_results = pipeline.clean()

            assert clean_results["success"] is True
            assert clean_results["files_cleaned"] == 5
            assert len(clean_results["errors"]) == 0


class TestPipelineIntegrationPerformance:
    """Test suite for pipeline performance and scalability."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("recipe_fmt.parsers.openai_client.OpenAIClient")
    def test_pipeline_metrics_accumulation(self, mock_openai_client_class):
        """Test that pipeline correctly accumulates metrics across multiple files."""
        # Setup mock client with varying responses
        mock_client = Mock()

        responses = [
            OpenAIResponse(
                success=True,
                data={"content": "yaml1"},
                tokens_used=100,
                cost_estimate=0.002,
                cached=False,
            ),
            OpenAIResponse(
                success=True,
                data={"content": "yaml2"},
                tokens_used=150,
                cost_estimate=0.003,
                cached=True,
            ),
            OpenAIResponse(
                success=True,
                data={"content": "yaml3"},
                tokens_used=120,
                cost_estimate=0.0025,
                cached=False,
            ),
        ]

        mock_client.parse_recipe_markdown.side_effect = responses
        mock_openai_client_class.return_value = mock_client

        # Create test files
        recipe_dir = Path(self.temp_dir) / "recipe"
        markdown_dir = recipe_dir / "markdown"
        markdown_dir.mkdir(parents=True)

        test_files = []
        for i in range(3):
            md_file = markdown_dir / f"recipe{i}.md"
            md_file.write_text(f"# Recipe {i}")
            test_files.append(md_file)

        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = True
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": test_files,
                "yaml_to_pdf": [],
            }
            mock_file_manager.get_corresponding_yaml_path.side_effect = lambda x: Path(str(x).replace(".md", ".yaml"))
            mock_file_manager_class.return_value = mock_file_manager

            config = AppConfig()
            pipeline = RecipePipeline(config)
            results = pipeline.run()

        # Verify metrics accumulation
        metrics = results["metrics"]
        assert metrics["total_tokens_used"] == 370  # 100 + 150 + 120
        assert metrics["total_cost_estimate"] == 0.0075  # 0.002 + 0.003 + 0.0025
        assert metrics["cached_responses"] == 1  # One cached response

    def test_pipeline_error_accumulation(self):
        """Test that pipeline correctly accumulates errors from different stages."""
        config = AppConfig()

        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = False  # Simulate directory creation failure
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(config)
            results = pipeline.run()

            # Should capture directory creation error
            assert results["success"] is False
            assert len(results["errors"]) > 0
            assert "Failed to create required directories" in results["errors"][0]


class TestPipelineIntegrationEdgeCases:
    """Test suite for pipeline edge cases and error conditions."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig()

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_pipeline_with_no_files_to_process(self):
        """Test pipeline behavior when no files need processing."""
        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.return_value = True
            mock_file_manager.get_stale_pipeline_files.return_value = {
                "markdown_to_yaml": [],
                "yaml_to_pdf": [],
            }
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(self.config)
            results = pipeline.run()

            # Should succeed with no processing
            assert results["success"] is True
            assert results["total_processed"] == 0
            assert len(results["errors"]) == 0

    def test_pipeline_unexpected_exception(self):
        """Test pipeline handling of unexpected exceptions."""
        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.side_effect = Exception("Unexpected error")
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(self.config)
            results = pipeline.run()

            # Should handle unexpected errors gracefully
            assert results["success"] is False
            assert len(results["errors"]) > 0
            assert "Unexpected error" in str(results["errors"])

    def test_pipeline_keyboard_interrupt_handling(self):
        """Test pipeline handling of keyboard interrupts."""
        with patch("recipe_fmt.pipeline.FileManager") as mock_file_manager_class:
            mock_file_manager = Mock()
            mock_file_manager.ensure_directories_exist.side_effect = KeyboardInterrupt()
            mock_file_manager_class.return_value = mock_file_manager

            pipeline = RecipePipeline(self.config)

            # Should propagate KeyboardInterrupt
            with pytest.raises(KeyboardInterrupt):
                pipeline.run()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
