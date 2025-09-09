"""File management utilities with staleness detection.

This module provides intelligent file processing that only rebuilds files
when the source is newer than the output, enabling efficient incremental builds.

Example usage:
    from recipe_fmt.utils.file_manager import FileManager
    
    file_manager = FileManager()
    
    # Check if YAML needs updating from markdown
    if file_manager.is_stale("recipe/markdown/pancakes.md", "recipe/yaml/pancakes.yaml"):
        print("YAML file needs rebuilding")
    
    # Get all stale files in pipeline
    stale_files = file_manager.get_stale_pipeline_files()
"""

import logging
import os
from pathlib import Path
from typing import Optional


class FileManager:
    """Manages file operations and staleness detection for the recipe pipeline."""
    
    def __init__(self, cfg_dict: dict = None) -> None:
        """Initialize FileManager with configuration.
        
        Args:
            cfg_dict: Configuration dictionary with file management settings
        """
        # STEP_1: Initialize logging first
        self.logger = logging.getLogger(__name__)
        
        # STEP_2: Configuration management
        self.cfg_dict = self._apply_config_defaults(cfg_dict or {})
        
        self.logger.info("FileManager initialized with config: %s", self.cfg_dict)
    
    def _apply_config_defaults(self, cfg_dict: dict) -> dict:
        """Apply configuration defaults and log missing keys.
        
        Args:
            cfg_dict: Input configuration dictionary
            
        Returns:
            Configuration with defaults applied
        """
        defaults = {
            "recipe_dir": "recipe",
            "markdown_subdir": "markdown",
            "yaml_subdir": "yaml", 
            "pdf_subdir": "pdf",
            "templates_subdir": "templates",
            "force_rebuild": False,
            "verbose_logging": False
        }
        
        for key, default_value in defaults.items():
            if key not in cfg_dict:
                cfg_dict[key] = default_value
                self.logger.debug("Applied default for missing key %s: %s", key, default_value)
        
        return cfg_dict
    
    def get_cfg(self) -> dict:
        """Return current configuration dictionary.
        
        Returns:
            Copy of current configuration
        """
        return self.cfg_dict.copy()
    
    def is_stale(self, source_path: str | Path, target_path: str | Path) -> bool:
        """Check if target file is stale compared to source file.
        
        A target file is considered stale if:
        - Target doesn't exist
        - Source is newer than target (based on modification time)
        - Force rebuild is enabled in config
        
        Args:
            source_path: Path to source file
            target_path: Path to target file
            
        Returns:
            True if target needs rebuilding, False otherwise
        """
        try:
            source = Path(source_path)
            target = Path(target_path)
            
            # STEP_3: Force rebuild if configured
            if self.cfg_dict.get("force_rebuild", False):
                self.logger.debug("Force rebuild enabled - marking %s as stale", target)
                return True
            
            # STEP_4: Target doesn't exist - definitely stale
            if not target.exists():
                self.logger.debug("Target file doesn't exist: %s", target)
                return True
            
            # STEP_5: Source doesn't exist - not stale (target is valid)
            if not source.exists():
                self.logger.warning("Source file doesn't exist: %s", source)
                return False
            
            # STEP_6: Compare modification times
            source_mtime = source.stat().st_mtime
            target_mtime = target.stat().st_mtime
            
            is_stale = source_mtime > target_mtime
            
            if self.cfg_dict.get("verbose_logging", False):
                self.logger.debug(
                    "Staleness check: %s (%.2f) vs %s (%.2f) = %s",
                    source, source_mtime, target, target_mtime, is_stale
                )
            
            return is_stale
            
        except Exception as e:
            error_msg = f"Error checking staleness: {source_path} -> {target_path}: {e}"
            self.logger.exception(error_msg)
            # On error, assume stale to be safe
            return True
    
    def get_recipe_files(self) -> list[Path]:
        """Get all markdown recipe files in the recipe directory.
        
        Returns:
            List of Path objects for all .md files in markdown directory
        """
        try:
            markdown_dir = Path(self.cfg_dict["recipe_dir"]) / self.cfg_dict["markdown_subdir"]
            
            if not markdown_dir.exists():
                self.logger.warning("Markdown directory doesn't exist: %s", markdown_dir)
                return []
            
            # STEP_7: Find all markdown files
            recipe_files = list(markdown_dir.glob("*.md"))
            
            self.logger.info("Found %d recipe files in %s", len(recipe_files), markdown_dir)
            return sorted(recipe_files)
            
        except Exception as e:
            error_msg = f"Error getting recipe files: {e}"
            self.logger.exception(error_msg)
            return []
    
    def get_corresponding_yaml_path(self, markdown_path: Path) -> Path:
        """Get the corresponding YAML path for a markdown file.
        
        Args:
            markdown_path: Path to markdown file
            
        Returns:
            Path to corresponding YAML file
        """
        recipe_dir = Path(self.cfg_dict["recipe_dir"])
        yaml_dir = recipe_dir / self.cfg_dict["yaml_subdir"]
        
        # Change extension from .md to .yaml and update directory
        yaml_filename = markdown_path.stem + ".yaml"
        return yaml_dir / yaml_filename
    
    def get_corresponding_pdf_path(self, yaml_path: Path, category: Optional[str] = None) -> Path:
        """Get the corresponding PDF path for a YAML file.
        
        Args:
            yaml_path: Path to YAML file
            category: Recipe category for filename prefix (e.g., "Breakfast")
            
        Returns:
            Path to corresponding PDF file with category prefix
        """
        recipe_dir = Path(self.cfg_dict["recipe_dir"])
        pdf_dir = recipe_dir / self.cfg_dict["pdf_subdir"]
        
        # Create category-prefixed filename
        base_filename = yaml_path.stem
        if category:
            pdf_filename = f"{category}-{base_filename}.pdf"
        else:
            pdf_filename = f"{base_filename}.pdf"
            
        return pdf_dir / pdf_filename
    
    def get_stale_pipeline_files(self) -> dict[str, list[Path]]:
        """Get all files that need processing in the pipeline.
        
        Returns:
            Dictionary with keys 'markdown_to_yaml' and 'yaml_to_pdf' 
            containing lists of stale source files
        """
        stale_files = {
            "markdown_to_yaml": [],
            "yaml_to_pdf": []
        }
        
        try:
            # STEP_8: Check markdown -> YAML conversions
            for md_file in self.get_recipe_files():
                yaml_file = self.get_corresponding_yaml_path(md_file)
                
                if self.is_stale(md_file, yaml_file):
                    stale_files["markdown_to_yaml"].append(md_file)
                    self.logger.debug("Stale MD->YAML: %s", md_file)
            
            # STEP_9: Check YAML -> PDF conversions
            yaml_dir = Path(self.cfg_dict["recipe_dir"]) / self.cfg_dict["yaml_subdir"]
            if yaml_dir.exists():
                for yaml_file in yaml_dir.glob("*.yaml"):
                    # Note: We'll need category info to determine exact PDF path
                    # For now, check against basic PDF path
                    pdf_file = self.get_corresponding_pdf_path(yaml_file)
                    
                    if self.is_stale(yaml_file, pdf_file):
                        stale_files["yaml_to_pdf"].append(yaml_file)
                        self.logger.debug("Stale YAML->PDF: %s", yaml_file)
            
            total_stale = len(stale_files["markdown_to_yaml"]) + len(stale_files["yaml_to_pdf"])
            self.logger.info("Found %d stale files requiring processing", total_stale)
            
            return stale_files
            
        except Exception as e:
            error_msg = f"Error getting stale pipeline files: {e}"
            self.logger.exception(error_msg)
            return stale_files
    
    def ensure_directories_exist(self) -> bool:
        """Ensure all required pipeline directories exist.
        
        Returns:
            True if all directories were created/exist successfully
        """
        try:
            recipe_dir = Path(self.cfg_dict["recipe_dir"])
            
            # STEP_10: Create all pipeline directories
            directories = [
                recipe_dir / self.cfg_dict["markdown_subdir"],
                recipe_dir / self.cfg_dict["yaml_subdir"], 
                recipe_dir / self.cfg_dict["pdf_subdir"],
                recipe_dir / self.cfg_dict["templates_subdir"]
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug("Ensured directory exists: %s", directory)
            
            self.logger.info("All pipeline directories verified/created")
            return True
            
        except Exception as e:
            error_msg = f"Error creating directories: {e}"
            self.logger.exception(error_msg)
            return False
    
    def clean_generated_files(self, file_types: list[str] = None) -> int:
        """Clean generated files from the pipeline.
        
        Args:
            file_types: List of file types to clean ('yaml', 'pdf'). 
                       If None, cleans all generated files.
                       
        Returns:
            Number of files cleaned
        """
        if file_types is None:
            file_types = ['pdf']  # Default to cleaning PDFs only
        
        files_cleaned = 0
        
        try:
            recipe_dir = Path(self.cfg_dict["recipe_dir"])
            
            # STEP_11: Clean specified file types
            for file_type in file_types:
                if file_type == 'yaml':
                    target_dir = recipe_dir / self.cfg_dict["yaml_subdir"]
                    pattern = "*.yaml"
                elif file_type == 'pdf':
                    target_dir = recipe_dir / self.cfg_dict["pdf_subdir"]
                    pattern = "*.pdf"
                else:
                    self.logger.warning("Unknown file type for cleaning: %s", file_type)
                    continue
                
                if target_dir.exists():
                    for file_path in target_dir.glob(pattern):
                        file_path.unlink()
                        files_cleaned += 1
                        self.logger.debug("Cleaned file: %s", file_path)
            
            self.logger.info("Cleaned %d files of types: %s", files_cleaned, file_types)
            return files_cleaned
            
        except Exception as e:
            error_msg = f"Error cleaning files: {e}"
            self.logger.exception(error_msg)
            return files_cleaned