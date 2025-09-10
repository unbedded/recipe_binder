"""Unit tests for template engine and template loader.

This test module provides comprehensive testing of the template system
following CLAUDE.md testing standards with various template scenarios.

The tests cover:
- Template loading and parsing
- Template validation
- Template engine functionality
- Template loader with caching
- Error handling and edge cases
- Configuration management

Example usage:
    pytest tests/unit/test_template_engine.py -v
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from recipe_fmt.templates.template_engine import (
    CardDimensions,
    CardTemplate,
    DisplayOptions,
    LayoutType,
    TemplateEngine,
    TemplateError,
    create_engine,
)
from recipe_fmt.templates.template_loader import (
    DefaultTemplates,
    TemplateLoader,
    create_loader,
)


class TestTemplateEngineInitialization:
    """Test suite for TemplateEngine initialization and configuration."""

    def test_initialization_with_defaults(self):
        """Test template engine initializes with default configuration."""
        engine = TemplateEngine()

        config = engine.get_cfg()
        assert config["cache_templates"] is True
        assert config["validate_templates"] is True
        assert config["strict_validation"] is False
        assert config["default_template"] == "default-card.yaml"

    def test_initialization_with_custom_config(self):
        """Test template engine initialization with custom configuration."""
        custom_config = {
            "cache_templates": False,
            "validate_templates": False,
            "strict_validation": True,
            "default_template": "custom-template.yaml",
        }

        engine = TemplateEngine(custom_config)
        config = engine.get_cfg()

        assert config["cache_templates"] is False
        assert config["validate_templates"] is False
        assert config["strict_validation"] is True
        assert config["default_template"] == "custom-template.yaml"

    def test_template_paths_initialization(self):
        """Test that template search paths are initialized."""
        engine = TemplateEngine()

        # Should have multiple search paths
        assert len(engine.template_paths) >= 3

        # Should include standard paths
        path_strings = [str(p) for p in engine.template_paths]
        assert any("recipe/templates" in path for path in path_strings)

    def test_add_template_path(self):
        """Test adding custom template search paths."""
        engine = TemplateEngine()
        initial_count = len(engine.template_paths)

        custom_path = Path("/custom/template/path")
        engine.add_template_path(custom_path)

        assert len(engine.template_paths) == initial_count + 1
        assert custom_path in engine.template_paths
        # New path should be first (highest priority)
        assert engine.template_paths[0] == custom_path


class TestTemplateEngineTemplateFinding:
    """Test suite for template finding functionality."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = TemplateEngine()
        self.engine.add_template_path(Path(self.temp_dir))

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_find_existing_template(self):
        """Test finding a template that exists."""
        # Create test template
        template_file = Path(self.temp_dir) / "test-template.yaml"
        template_file.write_text("template_info:\n  name: Test Template")

        found_path = self.engine.find_template("test-template.yaml")

        assert found_path is not None
        assert found_path == template_file

    def test_find_nonexistent_template(self):
        """Test finding a template that doesn't exist."""
        found_path = self.engine.find_template("nonexistent-template.yaml")

        assert found_path is None

    def test_template_path_priority(self):
        """Test that template paths are searched in priority order."""
        # Create templates in different paths
        high_priority_dir = tempfile.mkdtemp()
        low_priority_dir = tempfile.mkdtemp()

        template_name = "priority-test.yaml"

        # Create template in low priority path
        low_priority_file = Path(low_priority_dir) / template_name
        low_priority_file.write_text("template_info:\n  name: Low Priority")

        # Create template in high priority path
        high_priority_file = Path(high_priority_dir) / template_name
        high_priority_file.write_text("template_info:\n  name: High Priority")

        # Add paths in reverse order (high priority should be first)
        self.engine.add_template_path(low_priority_dir)
        self.engine.add_template_path(high_priority_dir)

        found_path = self.engine.find_template(template_name)

        # Should find high priority template
        assert found_path == high_priority_file

        # Cleanup
        import shutil

        shutil.rmtree(high_priority_dir)
        shutil.rmtree(low_priority_dir)


class TestTemplateEngineTemplateLoading:
    """Test suite for template loading and parsing."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = TemplateEngine({"cache_templates": False})  # Disable cache for testing
        self.engine.add_template_path(Path(self.temp_dir))

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_load_valid_template(self):
        """Test loading a valid template file."""
        # Create valid template
        template_file = Path(self.temp_dir) / "valid-template.yaml"
        template_data = {
            "template_info": {
                "name": "Valid Template",
                "version": "1.0",
                "description": "A valid test template",
            },
            "card": {
                "size": {"width": 8.5, "height": 4.0},
                "margins": {"top": 0.25, "bottom": 0.25},
                "layout": "two_sided",
            },
            "typography": {"title": {"font_size": 18, "alignment": "center"}},
            "display": {"show_weights": True, "show_category_banner": True},
        }

        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        template = self.engine.load_template("valid-template.yaml")

        assert isinstance(template, CardTemplate)
        assert template.name == "Valid Template"
        assert template.version == "1.0"
        assert template.description == "A valid test template"
        assert template.layout == LayoutType.TWO_SIDED
        assert template.display_options.show_weights is True

    def test_load_malformed_yaml(self):
        """Test loading template with malformed YAML."""
        template_file = Path(self.temp_dir) / "malformed.yaml"
        malformed_yaml = """template_info:
  name: "Malformed Template"
card:
  size:
    width: 8.5
    height: 4.0"  # Missing opening quote
"""
        template_file.write_text(malformed_yaml)

        with pytest.raises(TemplateError) as exc_info:
            self.engine.load_template("malformed.yaml")

        assert "YAML parsing error" in str(exc_info.value)

    def test_load_nonexistent_template(self):
        """Test loading a template that doesn't exist."""
        with pytest.raises(TemplateError) as exc_info:
            self.engine.load_template("nonexistent.yaml")

        assert "Template not found" in str(exc_info.value)

    def test_load_template_with_absolute_path(self):
        """Test loading template with absolute path."""
        template_file = Path(self.temp_dir) / "absolute-path.yaml"
        template_data = {"template_info": {"name": "Absolute Path Template"}}

        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        template = self.engine.load_template(str(template_file))

        assert template.name == "Absolute Path Template"

    def test_template_caching(self):
        """Test template caching functionality."""
        # Enable caching
        cached_engine = TemplateEngine({"cache_templates": True})
        cached_engine.add_template_path(Path(self.temp_dir))

        template_file = Path(self.temp_dir) / "cached.yaml"
        template_data = {"template_info": {"name": "Cached Template"}}

        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        # Load template twice
        template1 = cached_engine.load_template("cached.yaml")
        template2 = cached_engine.load_template("cached.yaml")

        # Should return the same object from cache
        assert template1 is template2

    def test_template_validation_enabled(self):
        """Test template validation when enabled."""
        validating_engine = TemplateEngine({"validate_templates": True})
        validating_engine.add_template_path(Path(self.temp_dir))

        # Create template with invalid dimensions
        template_file = Path(self.temp_dir) / "invalid.yaml"
        invalid_template = {
            "template_info": {"name": "Invalid Template"},
            "card": {
                "size": {"width": -1, "height": -1}  # Invalid dimensions
            },
        }

        with open(template_file, "w") as f:
            yaml.dump(invalid_template, f)

        with pytest.raises(TemplateError) as exc_info:
            validating_engine.load_template("invalid.yaml")

        assert "Invalid card dimensions" in str(exc_info.value)

    def test_template_validation_disabled(self):
        """Test template behavior when validation is disabled."""
        non_validating_engine = TemplateEngine({"validate_templates": False})
        non_validating_engine.add_template_path(Path(self.temp_dir))

        # Create template with invalid dimensions
        template_file = Path(self.temp_dir) / "no-validation.yaml"
        template_data = {
            "template_info": {"name": "No Validation Template"},
            "card": {"size": {"width": -1, "height": -1}},
        }

        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        # Should load without validation errors
        template = non_validating_engine.load_template("no-validation.yaml")
        assert template.name == "No Validation Template"


class TestTemplateEngineTemplateValidation:
    """Test suite for template validation."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.engine = TemplateEngine({"validate_templates": True})

    def test_validate_valid_template(self):
        """Test validation of a valid template."""
        valid_template = CardTemplate(
            name="Valid Template",
            dimensions=CardDimensions(width=8.5, height=4.0, margin_top=0.25),
            layout=LayoutType.TWO_SIDED,
        )

        # Should not raise exception
        self.engine._validate_template(valid_template)

    def test_validate_invalid_dimensions(self):
        """Test validation of template with invalid dimensions."""
        invalid_template = CardTemplate(
            dimensions=CardDimensions(width=0, height=0)  # Invalid
        )

        with pytest.raises(TemplateError) as exc_info:
            self.engine._validate_template(invalid_template)

        assert "Invalid card dimensions" in str(exc_info.value)

    def test_validate_invalid_margins(self):
        """Test validation of template with invalid margins."""
        invalid_template = CardTemplate(
            dimensions=CardDimensions(
                width=8.5,
                height=4.0,
                margin_top=-1,
                margin_bottom=-1,  # Invalid
            )
        )

        with pytest.raises(TemplateError) as exc_info:
            self.engine._validate_template(invalid_template)

        assert "Invalid margin values" in str(exc_info.value)

    def test_validate_invalid_font_size(self):
        """Test validation of template with invalid font sizes."""
        invalid_template = CardTemplate()
        invalid_template.title_style.font_size = -10  # Invalid

        with pytest.raises(TemplateError) as exc_info:
            self.engine._validate_template(invalid_template)

        assert "Invalid font size" in str(exc_info.value)

    def test_validate_invalid_alignment_strict(self):
        """Test validation of invalid alignment in strict mode."""
        strict_engine = TemplateEngine({"validate_templates": True, "strict_validation": True})

        invalid_template = CardTemplate()
        invalid_template.title_style.alignment = "invalid_alignment"

        with pytest.raises(TemplateError) as exc_info:
            strict_engine._validate_template(invalid_template)

        assert "Invalid text alignment" in str(exc_info.value)

    def test_validate_invalid_alignment_lenient(self):
        """Test validation of invalid alignment in lenient mode."""
        lenient_engine = TemplateEngine({"validate_templates": True, "strict_validation": False})

        invalid_template = CardTemplate()
        invalid_template.title_style.alignment = "invalid_alignment"

        # Should not raise exception in lenient mode
        lenient_engine._validate_template(invalid_template)


class TestTemplateEngineGeneratorCreation:
    """Test suite for PDF generator creation from templates."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.engine = TemplateEngine()

    @patch("recipe_fmt.templates.template_engine.PDFCardGenerator")
    @patch("recipe_fmt.templates.template_engine.DisplayConfig")
    def test_create_generator_from_template(self, mock_display_config, mock_pdf_generator):
        """Test creating PDF generator from template."""
        # Create test template
        template = CardTemplate(
            name="Test Template",
            layout=LayoutType.SINGLE_SIDED,
            display_options=DisplayOptions(show_weights=False, show_purpose=True),
        )

        # Mock the dependencies
        mock_config_instance = Mock()
        mock_display_config.return_value = mock_config_instance
        mock_generator_instance = Mock()
        mock_pdf_generator.return_value = mock_generator_instance

        generator = self.engine.create_generator(template, show_weights=True)

        # Verify DisplayConfig was created with correct parameters
        mock_display_config.assert_called_once()
        call_kwargs = mock_display_config.call_args[1]
        assert call_kwargs["show_weights"] is True  # Override
        assert call_kwargs["show_purpose"] is True  # From template

        # Verify PDFCardGenerator was created
        mock_pdf_generator.assert_called_once()

        assert generator == mock_generator_instance

    def test_layout_mapping(self):
        """Test that template layouts are correctly mapped to generator layouts."""
        from recipe_fmt.generators.pdf_generator import CardLayout

        layout_mappings = [
            (LayoutType.TWO_SIDED, CardLayout.TWO_SIDED),
            (LayoutType.SINGLE_SIDED, CardLayout.SINGLE_SIDED),
            (LayoutType.INGREDIENTS_ONLY, CardLayout.INGREDIENTS_ONLY),
            (LayoutType.INSTRUCTIONS_ONLY, CardLayout.INSTRUCTIONS_ONLY),
        ]

        for template_layout, expected_generator_layout in layout_mappings:
            template = CardTemplate(layout=template_layout)

            with patch("recipe_fmt.templates.template_engine.PDFCardGenerator") as mock_generator:
                self.engine.create_generator(template)

                # Check the generator config passed
                call_args = mock_generator.call_args
                generator_config = call_args[0][1]  # Second argument
                assert generator_config["card_layout"] == expected_generator_layout


class TestTemplateEngineTemplateDiscovery:
    """Test suite for template discovery functionality."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = TemplateEngine()
        self.engine.add_template_path(Path(self.temp_dir))

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_list_templates(self):
        """Test listing available templates."""
        # Create test templates
        template1_file = Path(self.temp_dir) / "template1.yaml"
        template1_data = {
            "template_info": {
                "name": "Template 1",
                "version": "1.0",
                "description": "First test template",
            }
        }
        with open(template1_file, "w") as f:
            yaml.dump(template1_data, f)

        template2_file = Path(self.temp_dir) / "template2.yaml"
        template2_data = {
            "template_info": {
                "name": "Template 2",
                "version": "2.0",
                "description": "Second test template",
            }
        }
        with open(template2_file, "w") as f:
            yaml.dump(template2_data, f)

        templates = self.engine.list_templates()

        # Should find both templates
        template_names = [t["name"] for t in templates]
        assert "Template 1" in template_names
        assert "Template 2" in template_names

    def test_list_templates_with_errors(self):
        """Test listing templates when some have errors."""
        # Create valid template
        valid_file = Path(self.temp_dir) / "valid.yaml"
        valid_data = {"template_info": {"name": "Valid Template"}}
        with open(valid_file, "w") as f:
            yaml.dump(valid_data, f)

        # Create invalid template
        invalid_file = Path(self.temp_dir) / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: content:")

        templates = self.engine.list_templates()

        # Should find valid template, skip invalid one
        template_names = [t["name"] for t in templates]
        assert "Valid Template" in template_names
        assert len(template_names) >= 1


class TestTemplateLoader:
    """Test suite for TemplateLoader functionality."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = TemplateLoader()
        self.loader.engine.add_template_path(Path(self.temp_dir))

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_loader_initialization(self):
        """Test template loader initialization."""
        loader = TemplateLoader()

        config = loader.get_cfg()
        assert config["cache_templates"] is True
        assert config["auto_discover"] is True
        assert config["prefer_user_templates"] is True
        assert config["fallback_to_builtin"] is True

    def test_discover_templates(self):
        """Test template discovery functionality."""
        # Create test template
        template_file = Path(self.temp_dir) / "discovered.yaml"
        template_data = {
            "template_info": {
                "name": "Discovered Template",
                "version": "1.0",
                "description": "A discovered template",
            }
        }
        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        templates = self.loader.discover_templates()

        # Should find the template
        template_names = [t.name for t in templates]
        assert "Discovered Template" in template_names

    def test_load_template_with_caching(self):
        """Test template loading with caching."""
        # Create template
        template_file = Path(self.temp_dir) / "cached.yaml"
        template_data = {"template_info": {"name": "Cached Template"}}
        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        # Load twice
        template1 = self.loader.load_template("cached.yaml")
        template2 = self.loader.load_template("cached.yaml")

        # Should be cached
        assert template1 is template2

    def test_get_template_info_without_loading(self):
        """Test getting template information without full loading."""
        # Create template
        template_file = Path(self.temp_dir) / "info-only.yaml"
        template_data = {
            "template_info": {
                "name": "Info Only Template",
                "version": "1.5",
                "description": "Template for info testing",
            }
        }
        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        info = self.loader.get_template_info("info-only.yaml")

        assert info is not None
        assert info.name == "Info Only Template"
        assert info.version == "1.5"
        assert info.description == "Template for info testing"
        assert info.filename == "info-only.yaml"

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Create and load template
        template_file = Path(self.temp_dir) / "clearable.yaml"
        template_data = {"template_info": {"name": "Clearable Template"}}
        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        template1 = self.loader.load_template("clearable.yaml")

        # Clear cache
        self.loader.clear_cache()

        # Load again - should be different object
        template2 = self.loader.load_template("clearable.yaml")
        assert template1 is not template2

    def test_get_loader_stats(self):
        """Test loader statistics reporting."""
        stats = self.loader.get_loader_stats()

        assert "loader_config" in stats
        assert "search_paths" in stats
        assert "template_count" in stats
        assert "default_templates" in stats
        assert "cache_size" in stats
        assert "templates_by_type" in stats

        # Check default templates
        default_templates = stats["default_templates"]
        assert DefaultTemplates.DEFAULT_CARD in default_templates


class TestDefaultTemplates:
    """Test suite for DefaultTemplates utility class."""

    def test_get_all_default_templates(self):
        """Test getting all default template names."""
        all_defaults = DefaultTemplates.get_all()

        assert DefaultTemplates.DEFAULT_CARD in all_defaults
        assert DefaultTemplates.COMPACT_CARD in all_defaults
        assert DefaultTemplates.MINIMAL_CARD in all_defaults

    def test_is_default_template(self):
        """Test checking if template is a default template."""
        assert DefaultTemplates.is_default(DefaultTemplates.DEFAULT_CARD) is True
        assert DefaultTemplates.is_default("custom-template.yaml") is False


class TestFactoryFunctions:
    """Test suite for factory functions."""

    def test_create_engine_factory(self):
        """Test template engine factory function."""
        custom_paths = ["/path1", "/path2"]
        engine = create_engine(custom_paths)

        assert isinstance(engine, TemplateEngine)
        # Should have added custom paths
        path_strings = [str(p) for p in engine.template_paths]
        assert "/path1" in path_strings
        assert "/path2" in path_strings

    def test_create_loader_factory(self):
        """Test template loader factory function."""
        custom_paths = ["/loader/path1", "/loader/path2"]
        loader = create_loader(custom_paths)

        assert isinstance(loader, TemplateLoader)
        # Should have added custom paths
        path_strings = [str(p) for p in loader.engine.template_paths]
        assert "/loader/path1" in path_strings
        assert "/loader/path2" in path_strings


class TestTemplateEngineEdgeCases:
    """Test suite for edge cases and error conditions."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = TemplateEngine()
        self.engine.add_template_path(Path(self.temp_dir))

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_empty_template_file(self):
        """Test loading empty template file."""
        empty_file = Path(self.temp_dir) / "empty.yaml"
        empty_file.write_text("")

        with pytest.raises(TemplateError):
            self.engine.load_template("empty.yaml")

    def test_non_dict_yaml_root(self):
        """Test loading YAML that doesn't have dict at root."""
        invalid_file = Path(self.temp_dir) / "non-dict.yaml"
        invalid_file.write_text("- item1\n- item2")  # List instead of dict

        with pytest.raises(TemplateError) as exc_info:
            self.engine.load_template("non-dict.yaml")

        assert "expected dictionary at root level" in str(exc_info.value)

    def test_unicode_template_content(self):
        """Test loading template with unicode content."""
        unicode_file = Path(self.temp_dir) / "unicode.yaml"
        unicode_data = {
            "template_info": {
                "name": "Modèle Unicode ☕",
                "description": "Template with unicode characters",
            }
        }

        with open(unicode_file, "w", encoding="utf-8") as f:
            yaml.dump(unicode_data, f, allow_unicode=True)

        template = self.engine.load_template("unicode.yaml")
        assert "☕" in template.name

    def test_very_large_template(self):
        """Test loading very large template file."""
        large_file = Path(self.temp_dir) / "large.yaml"
        large_data = {
            "template_info": {"name": "Large Template"},
            "large_section": {f"key_{i}": f"value_{i}" for i in range(1000)},
        }

        with open(large_file, "w") as f:
            yaml.dump(large_data, f)

        template = self.engine.load_template("large.yaml")
        assert template.name == "Large Template"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
