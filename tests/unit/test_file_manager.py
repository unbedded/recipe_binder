"""Unit tests for FileManager staleness detection.

This test module provides comprehensive testing of the FileManager class
following CLAUDE.md testing standards with edge cases and various scenarios.

The tests cover:
- Staleness detection logic
- File path conversions
- Directory management
- Error handling scenarios
- Configuration management

Example usage:
    pytest tests/unit/test_file_manager.py -v
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from recipe_fmt.utils.file_manager import FileManager


class TestFileManagerStalenessDetection:
    """Test suite for FileManager staleness detection functionality."""
    
    def setup_method(self):
        """Setup test environment before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            "recipe_dir": self.temp_dir,
            "markdown_subdir": "markdown",
            "yaml_subdir": "yaml",
            "pdf_subdir": "pdf",
            "force_rebuild": False,
            "verbose_logging": True
        }
        self.file_manager = FileManager(self.test_config)
    
    def teardown_method(self):
        """Cleanup after each test method."""
        # Clean up temporary files
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_default_config(self):
        """Test FileManager initializes with default configuration."""
        fm = FileManager()
        config = fm.get_cfg()
        
        assert config["recipe_dir"] == "recipe"
        assert config["markdown_subdir"] == "markdown"
        assert config["yaml_subdir"] == "yaml"
        assert config["pdf_subdir"] == "pdf"
        assert config["force_rebuild"] is False
        assert config["verbose_logging"] is False
    
    def test_initialization_with_custom_config(self):
        """Test FileManager initializes with custom configuration."""
        custom_config = {
            "recipe_dir": "custom_recipes",
            "force_rebuild": True,
            "verbose_logging": True
        }
        fm = FileManager(custom_config)
        config = fm.get_cfg()
        
        assert config["recipe_dir"] == "custom_recipes"
        assert config["force_rebuild"] is True
        assert config["verbose_logging"] is True
        # Should still have defaults for missing keys
        assert config["markdown_subdir"] == "markdown"
    
    def test_is_stale_target_does_not_exist(self):
        """Test staleness when target file doesn't exist."""
        source_file = Path(self.temp_dir) / "source.txt"
        target_file = Path(self.temp_dir) / "target.txt"
        
        # Create source file
        source_file.write_text("test content")
        
        # Target doesn't exist - should be stale
        assert self.file_manager.is_stale(source_file, target_file) is True
    
    def test_is_stale_source_newer_than_target(self):
        """Test staleness when source is newer than target."""
        source_file = Path(self.temp_dir) / "source.txt"
        target_file = Path(self.temp_dir) / "target.txt"
        
        # Create target file first
        target_file.write_text("old content")
        time.sleep(0.1)  # Ensure time difference
        
        # Create source file after (newer)
        source_file.write_text("new content")
        
        # Source is newer - should be stale
        assert self.file_manager.is_stale(source_file, target_file) is True
    
    def test_is_stale_target_newer_than_source(self):
        """Test staleness when target is newer than source."""
        source_file = Path(self.temp_dir) / "source.txt"
        target_file = Path(self.temp_dir) / "target.txt"
        
        # Create source file first
        source_file.write_text("old content")
        time.sleep(0.1)  # Ensure time difference
        
        # Create target file after (newer)
        target_file.write_text("new content")
        
        # Target is newer - should not be stale
        assert self.file_manager.is_stale(source_file, target_file) is False
    
    def test_is_stale_source_does_not_exist(self):
        """Test staleness when source file doesn't exist."""
        source_file = Path(self.temp_dir) / "nonexistent.txt"
        target_file = Path(self.temp_dir) / "target.txt"
        
        # Create target file
        target_file.write_text("content")
        
        # Source doesn't exist - should not be stale
        assert self.file_manager.is_stale(source_file, target_file) is False
    
    def test_is_stale_force_rebuild_enabled(self):
        """Test staleness when force rebuild is enabled."""
        source_file = Path(self.temp_dir) / "source.txt"
        target_file = Path(self.temp_dir) / "target.txt"
        
        # Create both files with target newer
        source_file.write_text("old content")
        time.sleep(0.1)
        target_file.write_text("new content")
        
        # Enable force rebuild
        config = self.file_manager.get_cfg()
        config["force_rebuild"] = True
        fm_force = FileManager(config)
        
        # Should be stale due to force rebuild
        assert fm_force.is_stale(source_file, target_file) is True
    
    def test_is_stale_with_file_access_error(self):
        """Test staleness detection handles file access errors gracefully."""
        with patch('pathlib.Path.stat', side_effect=OSError("Permission denied")):
            # Should return True (stale) on error to be safe
            result = self.file_manager.is_stale("source.txt", "target.txt")
            assert result is True
    
    def test_get_recipe_files_empty_directory(self):
        """Test getting recipe files from empty directory."""
        markdown_dir = Path(self.temp_dir) / "markdown"
        markdown_dir.mkdir()
        
        recipe_files = self.file_manager.get_recipe_files()
        assert recipe_files == []
    
    def test_get_recipe_files_with_markdown_files(self):
        """Test getting recipe files from directory with markdown files."""
        markdown_dir = Path(self.temp_dir) / "markdown"
        markdown_dir.mkdir()
        
        # Create test markdown files
        (markdown_dir / "recipe1.md").write_text("# Recipe 1")
        (markdown_dir / "recipe2.md").write_text("# Recipe 2")
        (markdown_dir / "not_recipe.txt").write_text("Not a recipe")
        
        recipe_files = self.file_manager.get_recipe_files()
        
        assert len(recipe_files) == 2
        assert all(f.suffix == ".md" for f in recipe_files)
        assert any(f.name == "recipe1.md" for f in recipe_files)
        assert any(f.name == "recipe2.md" for f in recipe_files)
    
    def test_get_recipe_files_nonexistent_directory(self):
        """Test getting recipe files when markdown directory doesn't exist."""
        recipe_files = self.file_manager.get_recipe_files()
        assert recipe_files == []
    
    def test_get_recipe_files_with_error(self):
        """Test getting recipe files handles errors gracefully."""
        with patch('pathlib.Path.glob', side_effect=OSError("Access denied")):
            recipe_files = self.file_manager.get_recipe_files()
            assert recipe_files == []
    
    def test_get_corresponding_yaml_path(self):
        """Test conversion from markdown path to YAML path."""
        md_path = Path(self.temp_dir) / "markdown" / "test-recipe.md"
        expected_yaml = Path(self.temp_dir) / "yaml" / "test-recipe.yaml"
        
        yaml_path = self.file_manager.get_corresponding_yaml_path(md_path)
        
        assert yaml_path == expected_yaml
        assert yaml_path.suffix == ".yaml"
    
    def test_get_corresponding_pdf_path_without_category(self):
        """Test conversion from YAML path to PDF path without category."""
        yaml_path = Path(self.temp_dir) / "yaml" / "test-recipe.yaml"
        expected_pdf = Path(self.temp_dir) / "pdf" / "test-recipe.pdf"
        
        pdf_path = self.file_manager.get_corresponding_pdf_path(yaml_path)
        
        assert pdf_path == expected_pdf
    
    def test_get_corresponding_pdf_path_with_category(self):
        """Test conversion from YAML path to PDF path with category prefix."""
        yaml_path = Path(self.temp_dir) / "yaml" / "pancakes.yaml"
        expected_pdf = Path(self.temp_dir) / "pdf" / "Breakfast-pancakes.pdf"
        
        pdf_path = self.file_manager.get_corresponding_pdf_path(yaml_path, "Breakfast")
        
        assert pdf_path == expected_pdf
        assert "Breakfast-" in pdf_path.name
    
    def test_get_stale_pipeline_files_empty(self):
        """Test getting stale pipeline files when no files exist."""
        stale_files = self.file_manager.get_stale_pipeline_files()
        
        assert stale_files["markdown_to_yaml"] == []
        assert stale_files["yaml_to_pdf"] == []
    
    def test_get_stale_pipeline_files_with_stale_markdown(self):
        """Test getting stale files when markdown files need YAML conversion."""
        # Create markdown directory and files
        markdown_dir = Path(self.temp_dir) / "markdown"
        yaml_dir = Path(self.temp_dir) / "yaml"
        markdown_dir.mkdir()
        yaml_dir.mkdir()
        
        # Create markdown file
        md_file = markdown_dir / "recipe.md"
        md_file.write_text("# Test Recipe")
        
        # No corresponding YAML file - should be stale
        stale_files = self.file_manager.get_stale_pipeline_files()
        
        assert len(stale_files["markdown_to_yaml"]) == 1
        assert md_file in stale_files["markdown_to_yaml"]
    
    def test_get_stale_pipeline_files_with_current_yaml(self):
        """Test getting stale files when YAML files are current."""
        # Create directories and files
        markdown_dir = Path(self.temp_dir) / "markdown"
        yaml_dir = Path(self.temp_dir) / "yaml"
        markdown_dir.mkdir()
        yaml_dir.mkdir()
        
        # Create markdown file
        md_file = markdown_dir / "recipe.md"
        md_file.write_text("# Test Recipe")
        
        time.sleep(0.1)
        
        # Create corresponding YAML file (newer)
        yaml_file = yaml_dir / "recipe.yaml"
        yaml_file.write_text("title: Test Recipe")
        
        # YAML is newer - should not be stale
        stale_files = self.file_manager.get_stale_pipeline_files()
        
        assert len(stale_files["markdown_to_yaml"]) == 0
    
    def test_ensure_directories_exist_creates_missing_dirs(self):
        """Test that ensure_directories_exist creates missing directories."""
        # Remove temp directory
        import shutil
        shutil.rmtree(self.temp_dir)
        
        # Should create all required directories
        result = self.file_manager.ensure_directories_exist()
        
        assert result is True
        assert Path(self.temp_dir).exists()
        assert (Path(self.temp_dir) / "markdown").exists()
        assert (Path(self.temp_dir) / "yaml").exists()
        assert (Path(self.temp_dir) / "pdf").exists()
        assert (Path(self.temp_dir) / "templates").exists()
        assert (Path(self.temp_dir) / "config").exists()
    
    def test_ensure_directories_exist_with_existing_dirs(self):
        """Test ensure_directories_exist when directories already exist."""
        # Directories already exist from setup_method
        result = self.file_manager.ensure_directories_exist()
        assert result is True
    
    def test_ensure_directories_exist_handles_errors(self):
        """Test ensure_directories_exist handles permission errors."""
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Access denied")):
            result = self.file_manager.ensure_directories_exist()
            assert result is False
    
    def test_clean_generated_files_pdf_only(self):
        """Test cleaning PDF files only (default behavior)."""
        pdf_dir = Path(self.temp_dir) / "pdf"
        yaml_dir = Path(self.temp_dir) / "yaml"
        pdf_dir.mkdir()
        yaml_dir.mkdir()
        
        # Create test files
        (pdf_dir / "test1.pdf").write_text("PDF content")
        (pdf_dir / "test2.pdf").write_text("PDF content")
        (yaml_dir / "test.yaml").write_text("YAML content")
        
        # Clean PDFs only
        cleaned_count = self.file_manager.clean_generated_files()
        
        assert cleaned_count == 2
        assert not (pdf_dir / "test1.pdf").exists()
        assert not (pdf_dir / "test2.pdf").exists()
        assert (yaml_dir / "test.yaml").exists()  # Should not be cleaned
    
    def test_clean_generated_files_multiple_types(self):
        """Test cleaning multiple file types."""
        pdf_dir = Path(self.temp_dir) / "pdf"
        yaml_dir = Path(self.temp_dir) / "yaml"
        pdf_dir.mkdir()
        yaml_dir.mkdir()
        
        # Create test files
        (pdf_dir / "test.pdf").write_text("PDF content")
        (yaml_dir / "test.yaml").write_text("YAML content")
        
        # Clean both types
        cleaned_count = self.file_manager.clean_generated_files(['pdf', 'yaml'])
        
        assert cleaned_count == 2
        assert not (pdf_dir / "test.pdf").exists()
        assert not (yaml_dir / "test.yaml").exists()
    
    def test_clean_generated_files_unknown_type(self):
        """Test cleaning with unknown file type logs warning."""
        with patch('logging.Logger.warning') as mock_warning:
            cleaned_count = self.file_manager.clean_generated_files(['unknown'])
            
            assert cleaned_count == 0
            mock_warning.assert_called_once()
    
    def test_clean_generated_files_handles_errors(self):
        """Test clean_generated_files handles file deletion errors."""
        pdf_dir = Path(self.temp_dir) / "pdf"
        pdf_dir.mkdir()
        (pdf_dir / "test.pdf").write_text("PDF content")
        
        with patch('pathlib.Path.unlink', side_effect=PermissionError("Access denied")):
            cleaned_count = self.file_manager.clean_generated_files()
            # Should return 0 due to error, but not crash
            assert cleaned_count == 0


class TestFileManagerEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    def test_configuration_parameter_validation(self):
        """Test that configuration parameters are properly validated."""
        # Test with various config scenarios
        configs_to_test = [
            {},  # Empty config
            {"recipe_dir": ""},  # Empty string
            {"unknown_key": "value"},  # Unknown key
            None  # None config
        ]
        
        for config in configs_to_test:
            fm = FileManager(config)
            # Should not crash and should have valid configuration
            cfg = fm.get_cfg()
            assert isinstance(cfg, dict)
            assert "recipe_dir" in cfg
    
    def test_path_handling_with_special_characters(self):
        """Test path handling with special characters in filenames."""
        fm = FileManager()
        
        # Test various special characters
        special_names = [
            "recipe with spaces.md",
            "recipe-with-dashes.md", 
            "recipe_with_underscores.md",
            "recipe.with.dots.md"
        ]
        
        for name in special_names:
            md_path = Path("recipe/markdown") / name
            yaml_path = fm.get_corresponding_yaml_path(md_path)
            
            # Should handle special characters correctly
            assert yaml_path.suffix == ".yaml"
            assert yaml_path.stem == md_path.stem
    
    def test_concurrent_file_access(self):
        """Test behavior under simulated concurrent file access."""
        import threading
        import tempfile
        
        temp_dir = tempfile.mkdtemp()
        fm = FileManager({"recipe_dir": temp_dir})
        
        results = []
        errors = []
        
        def worker():
            try:
                # Simulate concurrent staleness checks
                result = fm.is_stale("source.txt", "target.txt")
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should not have errors and should have results
        assert len(errors) == 0
        assert len(results) == 10
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)