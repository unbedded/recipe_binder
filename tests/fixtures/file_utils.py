"""File system utilities for testing.

This module provides utilities for creating temporary files, mock file systems,
and file I/O testing scenarios that can be used across all test modules.
"""

import json
import logging
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, ContextManager

import yaml

from .sample_recipes import SAMPLE_MARKDOWN_CONTENT, SAMPLE_YAML_CONTENT
from .template_data import ALL_TEMPLATE_DATA


class MockFileSystem:
    """Mock file system for testing file operations."""

    def __init__(self, base_path: Path | None = None):
        """Initialize mock file system.

        Args:
            base_path: Base directory path (creates temp dir if None)
        """
        self.logger = logging.getLogger(__name__)

        if base_path:
            self.base_path = Path(base_path)
            self._cleanup_on_exit = False
        else:
            self.temp_dir = tempfile.mkdtemp(prefix="recipe_binder_test_")
            self.base_path = Path(self.temp_dir)
            self._cleanup_on_exit = True

        # Create standard directory structure
        self.recipe_dir = self.base_path / "recipe"
        self.markdown_dir = self.recipe_dir / "markdown"
        self.yaml_dir = self.recipe_dir / "yaml"
        self.pdf_dir = self.recipe_dir / "pdf"
        self.templates_dir = self.recipe_dir / "templates"
        self.config_dir = self.recipe_dir / "config"

        # Create directories
        for directory in [
            self.markdown_dir,
            self.yaml_dir,
            self.pdf_dir,
            self.templates_dir,
            self.config_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        self.logger.debug("MockFileSystem created at %s", self.base_path)

    def create_recipe_files(self, recipes: dict[str, str]) -> dict[str, Path]:
        """Create recipe files from content dictionary.

        Args:
            recipes: Dictionary mapping filename to content

        Returns:
            Dictionary mapping filename to created file path
        """
        created_files = {}

        for filename, content in recipes.items():
            # Determine file type and target directory
            if filename.endswith(".md"):
                target_dir = self.markdown_dir
            elif filename.endswith(".yaml") or filename.endswith(".yml"):
                target_dir = self.yaml_dir
            else:
                target_dir = self.base_path

            file_path = target_dir / filename
            file_path.write_text(content, encoding="utf-8")
            created_files[filename] = file_path

            self.logger.debug("Created recipe file: %s", file_path)

        return created_files

    def create_template_files(self, templates: dict[str, dict[str, Any]]) -> dict[str, Path]:
        """Create template YAML files from template data.

        Args:
            templates: Dictionary mapping filename to template data

        Returns:
            Dictionary mapping filename to created file path
        """
        created_files = {}

        for filename, template_data in templates.items():
            if not filename.endswith((".yaml", ".yml")):
                filename += ".yaml"

            file_path = self.templates_dir / filename

            # Write YAML content
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True)

            created_files[filename] = file_path
            self.logger.debug("Created template file: %s", file_path)

        return created_files

    def create_config_files(self, configs: dict[str, dict[str, Any]]) -> dict[str, Path]:
        """Create configuration files.

        Args:
            configs: Dictionary mapping filename to config data

        Returns:
            Dictionary mapping filename to created file path
        """
        created_files = {}

        for filename, config_data in configs.items():
            file_path = self.config_dir / filename

            # Determine format and write file
            if filename.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2)
            elif filename.endswith((".yaml", ".yml")):
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(config_data, f, default_flow_style=False)
            else:
                # Assume text format
                file_path.write_text(str(config_data), encoding="utf-8")

            created_files[filename] = file_path
            self.logger.debug("Created config file: %s", file_path)

        return created_files

    def create_sample_files(self) -> dict[str, dict[str, Path]]:
        """Create all sample files from fixtures.

        Returns:
            Dictionary with categories of created files
        """
        created = {"recipes": {}, "templates": {}, "configs": {}}

        # Create sample recipe markdown files
        markdown_files = {}
        for name, content in SAMPLE_MARKDOWN_CONTENT.items():
            markdown_files[f"{name}.md"] = content
        created["recipes"].update(self.create_recipe_files(markdown_files))

        # Create sample YAML recipe files
        yaml_files = {}
        for name, data in SAMPLE_YAML_CONTENT.items():
            yaml_files[f"{name}.yaml"] = yaml.dump(data, default_flow_style=False)
        created["recipes"].update(self.create_recipe_files(yaml_files))

        # Create sample template files
        template_files = {}
        for name, data in ALL_TEMPLATE_DATA.items():
            if isinstance(data, dict):
                template_files[f"{name}.yaml"] = data
        created["templates"] = self.create_template_files(template_files)

        # Create sample config files
        config_files = {
            "display_config.yaml": {
                "show_weights": True,
                "show_purpose": True,
                "font_family": "Helvetica",
                "color_scheme": "default",
            },
            "pipeline_config.json": {
                "force_rebuild": False,
                "batch_size": 10,
                "parallel_processing": True,
                "cache_openai_responses": True,
            },
        }
        created["configs"] = self.create_config_files(config_files)

        return created

    def create_file_with_timestamp(self, file_path: str | Path, content: str, timestamp: float) -> Path:
        """Create file with specific modification timestamp.

        Args:
            file_path: Path to create file
            content: File content
            timestamp: Unix timestamp to set

        Returns:
            Path to created file
        """
        import os

        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = self.base_path / file_path

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        file_path.write_text(content, encoding="utf-8")

        # Set timestamp
        os.utime(file_path, (timestamp, timestamp))

        self.logger.debug("Created file with timestamp %f: %s", timestamp, file_path)
        return file_path

    def create_staleness_test_files(self) -> dict[str, dict[str, Path]]:
        """Create files for staleness detection testing.

        Returns:
            Dictionary with source and target file paths
        """
        import time

        current_time = time.time()
        old_time = current_time - 3600  # 1 hour ago
        current_time + 3600  # 1 hour in future

        files = {"fresh": {}, "stale": {}, "missing": {}}

        # Fresh files (target newer than source)
        source1 = self.create_file_with_timestamp(
            self.markdown_dir / "fresh_recipe.md",
            "# Fresh Recipe\n## Ingredients\n- flour\n## Instructions\n1. Mix",
            old_time,
        )
        target1 = self.create_file_with_timestamp(self.pdf_dir / "fresh_recipe.pdf", "PDF content", current_time)
        files["fresh"]["source"] = source1
        files["fresh"]["target"] = target1

        # Stale files (source newer than target)
        source2 = self.create_file_with_timestamp(
            self.markdown_dir / "stale_recipe.md",
            "# Stale Recipe\n## Ingredients\n- sugar\n## Instructions\n1. Cook",
            current_time,
        )
        target2 = self.create_file_with_timestamp(self.pdf_dir / "stale_recipe.pdf", "Old PDF content", old_time)
        files["stale"]["source"] = source2
        files["stale"]["target"] = target2

        # Missing target files
        source3 = self.create_file_with_timestamp(
            self.markdown_dir / "missing_target.md",
            "# Missing Target\n## Ingredients\n- salt\n## Instructions\n1. Season",
            current_time,
        )
        files["missing"]["source"] = source3
        files["missing"]["target"] = self.pdf_dir / "missing_target.pdf"  # Not created

        return files

    def create_error_scenario_files(self) -> dict[str, Path]:
        """Create files for testing error scenarios.

        Returns:
            Dictionary mapping scenario to file path
        """
        scenarios = {}

        # Empty file
        empty_file = self.markdown_dir / "empty.md"
        empty_file.write_text("", encoding="utf-8")
        scenarios["empty"] = empty_file

        # Binary file (not text)
        binary_file = self.markdown_dir / "binary.md"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04\x05")
        scenarios["binary"] = binary_file

        # Very large file
        large_content = (
            "# Large Recipe\n"
            + "## Ingredients\n"
            + "\n".join([f"- ingredient_{i}" for i in range(10000)])
            + "\n## Instructions\n"
            + "\n".join([f"{i}. Step {i}" for i in range(1, 5001)])
        )
        large_file = self.markdown_dir / "large.md"
        large_file.write_text(large_content, encoding="utf-8")
        scenarios["large"] = large_file

        # File with special characters in name
        special_name_file = self.markdown_dir / "recipe with spaces & symbols!.md"
        special_name_file.write_text("# Special Name Recipe\n## Ingredients\n- flour\n", encoding="utf-8")
        scenarios["special_name"] = special_name_file

        # Unicode content file
        unicode_file = self.markdown_dir / "unicode.md"
        unicode_content = """# Café Français ☕
## Ingrédients
- café moulu
- eau chaude (85°C)
- sucre blanc
- crème fraîche

## Instructions
1. Chauffez l'eau à 85°C ⏱️
2. Versez sur le café
3. Laissez infuser 3 minutes
4. Ajoutez crème et sucre selon goût

## Notes
- Température optimale: 85°C
- Utilisez des grains fraîchement moulus ☕
"""
        unicode_file.write_text(unicode_content, encoding="utf-8")
        scenarios["unicode"] = unicode_file

        return scenarios

    def get_directory_structure(self) -> dict[str, list[str]]:
        """Get current directory structure for verification.

        Returns:
            Dictionary mapping directory names to file lists
        """
        structure = {}

        for directory in [
            self.markdown_dir,
            self.yaml_dir,
            self.pdf_dir,
            self.templates_dir,
            self.config_dir,
        ]:
            rel_name = directory.relative_to(self.base_path)
            if directory.exists():
                structure[str(rel_name)] = [f.name for f in directory.iterdir() if f.is_file()]
            else:
                structure[str(rel_name)] = []

        return structure

    def cleanup(self) -> None:
        """Clean up temporary files and directories."""
        if self._cleanup_on_exit and hasattr(self, "temp_dir"):
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.debug("Cleaned up MockFileSystem at %s", self.temp_dir)
            except Exception as e:
                self.logger.warning("Failed to cleanup MockFileSystem: %s", e)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


@contextmanager
def temporary_recipe_files(recipes: dict[str, str]) -> ContextManager[dict[str, Path]]:
    """Context manager for temporary recipe files.

    Args:
        recipes: Dictionary mapping filename to content

    Yields:
        Dictionary mapping filename to file path
    """
    with MockFileSystem() as fs:
        created_files = fs.create_recipe_files(recipes)
        yield created_files


@contextmanager
def temporary_template_files(
    templates: dict[str, dict[str, Any]],
) -> ContextManager[dict[str, Path]]:
    """Context manager for temporary template files.

    Args:
        templates: Dictionary mapping filename to template data

    Yields:
        Dictionary mapping filename to file path
    """
    with MockFileSystem() as fs:
        created_files = fs.create_template_files(templates)
        yield created_files


def create_temp_recipe_files(recipes: dict[str, str]) -> dict[str, Path]:
    """Create temporary recipe files (caller responsible for cleanup).

    Args:
        recipes: Dictionary mapping filename to content

    Returns:
        Dictionary mapping filename to file path
    """
    temp_dir = tempfile.mkdtemp(prefix="recipe_test_")
    base_path = Path(temp_dir)

    created_files = {}
    for filename, content in recipes.items():
        file_path = base_path / filename
        file_path.write_text(content, encoding="utf-8")
        created_files[filename] = file_path

    return created_files


def create_temp_template_files(templates: dict[str, dict[str, Any]]) -> dict[str, Path]:
    """Create temporary template files (caller responsible for cleanup).

    Args:
        templates: Dictionary mapping filename to template data

    Returns:
        Dictionary mapping filename to file path
    """
    temp_dir = tempfile.mkdtemp(prefix="template_test_")
    base_path = Path(temp_dir)

    created_files = {}
    for filename, template_data in templates.items():
        if not filename.endswith((".yaml", ".yml")):
            filename += ".yaml"

        file_path = base_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True)

        created_files[filename] = file_path

    return created_files


def cleanup_temp_files(file_paths: list[Path] | dict[str, Path]) -> None:
    """Clean up temporary files and their parent directories.

    Args:
        file_paths: List or dictionary of file paths to clean up
    """
    if isinstance(file_paths, dict):
        paths = list(file_paths.values())
    else:
        paths = file_paths

    # Get unique parent directories
    parent_dirs = set()
    for path in paths:
        if path.exists():
            parent_dirs.add(path.parent)

    # Remove parent directories (which will remove files)
    for parent_dir in parent_dirs:
        if parent_dir.exists() and "test_" in str(parent_dir):
            try:
                shutil.rmtree(parent_dir)
            except Exception as e:
                logging.warning("Failed to cleanup temp directory %s: %s", parent_dir, e)


class FileSystemTestHelper:
    """Helper class for common file system testing operations."""

    @staticmethod
    def create_directory_tree(base_path: Path, tree: dict[str, Any]) -> None:
        """Create directory tree from nested dictionary.

        Args:
            base_path: Base directory path
            tree: Nested dictionary defining directory structure
        """
        for name, content in tree.items():
            path = base_path / name

            if isinstance(content, dict):
                # Directory with subdirectories/files
                path.mkdir(exist_ok=True)
                FileSystemTestHelper.create_directory_tree(path, content)
            else:
                # File with content
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, str):
                    path.write_text(content, encoding="utf-8")
                else:
                    path.write_bytes(content)

    @staticmethod
    def assert_file_exists(file_path: Path, message: str = None) -> None:
        """Assert that file exists.

        Args:
            file_path: Path to check
            message: Custom assertion message

        Raises:
            AssertionError: If file doesn't exist
        """
        if message is None:
            message = f"File should exist: {file_path}"

        assert file_path.exists(), message
        assert file_path.is_file(), f"Path should be a file: {file_path}"

    @staticmethod
    def assert_file_not_exists(file_path: Path, message: str = None) -> None:
        """Assert that file does not exist.

        Args:
            file_path: Path to check
            message: Custom assertion message

        Raises:
            AssertionError: If file exists
        """
        if message is None:
            message = f"File should not exist: {file_path}"

        assert not file_path.exists(), message

    @staticmethod
    def assert_file_content_equals(file_path: Path, expected_content: str) -> None:
        """Assert that file content matches expected.

        Args:
            file_path: Path to file
            expected_content: Expected file content

        Raises:
            AssertionError: If content doesn't match
        """
        FileSystemTestHelper.assert_file_exists(file_path)
        actual_content = file_path.read_text(encoding="utf-8")
        assert actual_content == expected_content, f"File content mismatch in {file_path}"

    @staticmethod
    def assert_yaml_file_valid(file_path: Path) -> dict[str, Any]:
        """Assert that YAML file is valid and return parsed content.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML content

        Raises:
            AssertionError: If YAML is invalid
        """
        FileSystemTestHelper.assert_file_exists(file_path)

        try:
            with open(file_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise AssertionError(f"Invalid YAML in {file_path}: {e}")

    @staticmethod
    def get_file_modification_time(file_path: Path) -> float:
        """Get file modification time.

        Args:
            file_path: Path to file

        Returns:
            Modification time as Unix timestamp
        """
        FileSystemTestHelper.assert_file_exists(file_path)
        return file_path.stat().st_mtime

    @staticmethod
    def wait_for_file_modification_time_change(file_path: Path, timeout: float = 2.0) -> None:
        """Wait for file modification time to change (useful for testing file updates).

        Args:
            file_path: Path to file
            timeout: Maximum time to wait in seconds
        """
        import time

        if not file_path.exists():
            return

        original_mtime = file_path.stat().st_mtime
        start_time = time.time()

        while time.time() - start_time < timeout:
            time.sleep(0.01)  # Small delay
            if not file_path.exists() or file_path.stat().st_mtime != original_mtime:
                return

        # Force a small time difference if needed (for testing)
        if file_path.exists():
            import os

            current_time = time.time()
            os.utime(file_path, (current_time, current_time))


# Export commonly used utilities
__all__ = [
    "MockFileSystem",
    "temporary_recipe_files",
    "temporary_template_files",
    "create_temp_recipe_files",
    "create_temp_template_files",
    "cleanup_temp_files",
    "FileSystemTestHelper",
]
