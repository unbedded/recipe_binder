"""Template loader utilities for recipe card templates.

This module provides utilities for loading, caching, and managing recipe card
templates with support for default templates and user customizations.

Example usage:
    from recipe_fmt.templates.template_loader import TemplateLoader

    loader = TemplateLoader()
    template = loader.get_default_template()

    # Load custom template
    custom_template = loader.load_from_file("my-custom-card.yaml")
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ..utils.logging_setup import get_logger
from .template_engine import CardTemplate, TemplateEngine, TemplateError

if TYPE_CHECKING:
    from ..generators.pdf_generator import PDFCardGenerator


@dataclass
class TemplateInfo:
    """Template metadata information."""

    name: str
    filename: str
    version: str
    description: str
    path: Path
    is_default: bool = False
    is_builtin: bool = False


class DefaultTemplates:
    """Built-in default templates."""

    DEFAULT_CARD = "default-card.yaml"
    COMPACT_CARD = "compact-card.yaml"
    MINIMAL_CARD = "minimal-card.yaml"

    @classmethod
    def get_all(cls) -> list[str]:
        """Get list of all default template names.

        Returns:
            List of default template filenames
        """
        return [cls.DEFAULT_CARD, cls.COMPACT_CARD, cls.MINIMAL_CARD]

    @classmethod
    def is_default(cls, template_name: str) -> bool:
        """Check if template is a default template.

        Args:
            template_name: Template filename

        Returns:
            True if template is a default template
        """
        return template_name in cls.get_all()


class TemplateLoader:
    """Template loader with caching and default template management."""

    def __init__(self, cfg_dict: dict = None) -> None:
        """Initialize template loader.

        Args:
            cfg_dict: Configuration dictionary
        """
        # STEP_1: Initialize logging first
        self.logger = get_logger(__name__, cfg_dict)

        # STEP_2: Configuration management
        self.cfg_dict = self._apply_config_defaults(cfg_dict or {})

        # STEP_3: Initialize template engine
        self.engine = TemplateEngine(cfg_dict)

        # STEP_4: Setup template search paths
        self._setup_template_paths()

        # STEP_5: Template cache
        self._template_cache: dict[str, CardTemplate] = {}
        self._template_info_cache: dict[str, TemplateInfo] = {}

        self.logger.info("TemplateLoader initialized with %d search paths", len(self.engine.template_paths))

    def _apply_config_defaults(self, cfg_dict: dict) -> dict:
        """Apply configuration defaults and log missing keys.

        Args:
            cfg_dict: Input configuration dictionary

        Returns:
            Configuration with defaults applied
        """
        defaults = {
            "cache_templates": True,
            "auto_discover": True,
            "prefer_user_templates": True,
            "fallback_to_builtin": True,
            "default_template": DefaultTemplates.DEFAULT_CARD,
        }

        for key, default_value in defaults.items():
            if key not in cfg_dict:
                cfg_dict[key] = default_value
                self.logger.debug("Applied default for missing key %s: %s", key, default_value)

        return cfg_dict

    def _setup_template_paths(self) -> None:
        """Setup template search paths in priority order."""
        # STEP_6: User templates (highest priority)
        user_templates = Path.home() / ".recipe_binder" / "templates"
        if user_templates.exists() or self.cfg_dict.get("prefer_user_templates", True):
            self.engine.add_template_path(user_templates)

        # STEP_7: Project templates
        project_templates = Path("recipe/templates")
        if project_templates.exists():
            self.engine.add_template_path(project_templates)

        # STEP_8: Built-in templates (lowest priority)
        builtin_templates = Path(__file__).parent.parent.parent.parent / "recipe" / "templates"
        if builtin_templates.exists():
            self.engine.add_template_path(builtin_templates)

        self.logger.debug("Template search paths configured")

    def get_cfg(self) -> dict:
        """Return current configuration dictionary.

        Returns:
            Copy of current configuration
        """
        return self.cfg_dict.copy()

    def discover_templates(self) -> list[TemplateInfo]:
        """Discover all available templates.

        Returns:
            List of discovered template information
        """
        templates = []
        seen_names = set()

        for search_path in self.engine.template_paths:
            if not search_path.exists():
                continue

            self.logger.debug("Scanning template directory: %s", search_path)

            for template_file in search_path.glob("*.yaml"):
                # Skip if we've already seen this template name (higher priority wins)
                if template_file.name in seen_names:
                    continue

                try:
                    # Quick metadata extraction without full template loading
                    template_info = self._extract_template_info(template_file)
                    templates.append(template_info)
                    seen_names.add(template_file.name)

                except Exception as e:
                    self.logger.warning("Failed to extract info from %s: %s", template_file, e)

        self.logger.info("Discovered %d templates", len(templates))
        return templates

    def _extract_template_info(self, template_file: Path) -> TemplateInfo:
        """Extract template metadata without full parsing.

        Args:
            template_file: Path to template file

        Returns:
            Template information object
        """
        import yaml

        try:
            with open(template_file, encoding="utf-8") as f:
                # Only read the template_info section
                data = yaml.safe_load(f)

            template_info = data.get("template_info", {})

            return TemplateInfo(
                name=template_info.get("name", template_file.stem),
                filename=template_file.name,
                version=template_info.get("version", "1.0"),
                description=template_info.get("description", "Custom template"),
                path=template_file,
                is_default=DefaultTemplates.is_default(template_file.name),
                is_builtin=self._is_builtin_path(template_file),
            )

        except Exception:
            # Fallback to filename-based info
            return TemplateInfo(
                name=template_file.stem,
                filename=template_file.name,
                version="unknown",
                description="Template info unavailable",
                path=template_file,
                is_default=DefaultTemplates.is_default(template_file.name),
                is_builtin=self._is_builtin_path(template_file),
            )

    def _is_builtin_path(self, template_file: Path) -> bool:
        """Check if template file is in built-in path.

        Args:
            template_file: Template file path

        Returns:
            True if template is built-in
        """
        builtin_path = Path(__file__).parent.parent.parent.parent / "recipe" / "templates"
        try:
            template_file.relative_to(builtin_path)
            return True
        except ValueError:
            return False

    def load_template(self, template_name: str) -> CardTemplate:
        """Load a template by name.

        Args:
            template_name: Template filename or name

        Returns:
            Loaded CardTemplate object

        Raises:
            TemplateError: If template cannot be loaded
        """
        # STEP_9: Check cache first
        if self.cfg_dict.get("cache_templates", True) and template_name in self._template_cache:
            self.logger.debug("Template cache hit: %s", template_name)
            return self._template_cache[template_name]

        try:
            # STEP_10: Load via engine
            template = self.engine.load_template(template_name)

            # STEP_11: Cache if enabled
            if self.cfg_dict.get("cache_templates", True):
                self._template_cache[template_name] = template

            return template

        except TemplateError as e:
            # STEP_12: Fallback to built-in if enabled
            if self.cfg_dict.get("fallback_to_builtin", True) and not template_name.endswith(".yaml"):
                fallback_name = f"{template_name}.yaml"
                if DefaultTemplates.is_default(fallback_name):
                    self.logger.warning("Template not found: %s, trying default: %s", template_name, fallback_name)
                    return self.load_template(fallback_name)

            raise e

    def load_from_file(self, file_path: str | Path) -> CardTemplate:
        """Load template from specific file path.

        Args:
            file_path: Path to template file

        Returns:
            Loaded CardTemplate object

        Raises:
            TemplateError: If template cannot be loaded
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise TemplateError(f"Template file not found: {file_path}")

        return self.engine.load_template(str(file_path))

    def get_default_template(self) -> CardTemplate:
        """Get the default template.

        Returns:
            Default CardTemplate object
        """
        default_name = self.cfg_dict.get("default_template", DefaultTemplates.DEFAULT_CARD)

        try:
            return self.load_template(default_name)
        except TemplateError:
            self.logger.warning("Default template not available, creating minimal template")
            return self._create_minimal_template()

    def _create_minimal_template(self) -> CardTemplate:
        """Create a minimal fallback template.

        Returns:
            Minimal CardTemplate object
        """
        template = CardTemplate(name="Minimal Fallback", version="1.0", description="Auto-generated minimal template")

        self.logger.info("Created minimal fallback template")
        return template

    def list_templates(self, include_builtin: bool = True, include_user: bool = True) -> list[TemplateInfo]:
        """List available templates with filtering.

        Args:
            include_builtin: Include built-in templates
            include_user: Include user templates

        Returns:
            Filtered list of template information
        """
        all_templates = self.discover_templates()

        filtered_templates = []
        for template in all_templates:
            if template.is_builtin and not include_builtin:
                continue
            if not template.is_builtin and not include_user:
                continue
            filtered_templates.append(template)

        return filtered_templates

    def get_template_info(self, template_name: str) -> TemplateInfo | None:
        """Get template information without loading the full template.

        Args:
            template_name: Template filename

        Returns:
            Template information or None if not found
        """
        # Check cache first
        if template_name in self._template_info_cache:
            return self._template_info_cache[template_name]

        # Find and extract info
        template_path = self.engine.find_template(template_name)
        if not template_path:
            return None

        try:
            template_info = self._extract_template_info(template_path)
            self._template_info_cache[template_name] = template_info
            return template_info
        except Exception as e:
            self.logger.warning("Failed to extract template info for %s: %s", template_name, e)
            return None

    def clear_cache(self) -> None:
        """Clear template caches."""
        self._template_cache.clear()
        self._template_info_cache.clear()
        if hasattr(self.engine, "_template_cache"):
            self.engine._template_cache.clear()

        self.logger.debug("Template caches cleared")

    def create_generator(self, template_name: str, **overrides) -> "PDFCardGenerator":
        """Create PDF generator with specified template.

        Args:
            template_name: Template name to use
            **overrides: Configuration overrides

        Returns:
            Configured PDFCardGenerator instance
        """
        template = self.load_template(template_name)
        return self.engine.create_generator(template, **overrides)

    def get_loader_stats(self) -> dict:
        """Get template loader statistics.

        Returns:
            Dictionary with loader statistics
        """
        templates = self.discover_templates()

        return {
            "loader_config": self.cfg_dict.copy(),
            "search_paths": [str(p) for p in self.engine.template_paths],
            "template_count": len(templates),
            "default_templates": DefaultTemplates.get_all(),
            "cache_size": len(self._template_cache),
            "templates_by_type": {
                "builtin": len([t for t in templates if t.is_builtin]),
                "user": len([t for t in templates if not t.is_builtin]),
                "default": len([t for t in templates if t.is_default]),
            },
        }


def create_loader(template_paths: list[str | Path] = None) -> TemplateLoader:
    """Create a TemplateLoader with custom configuration.

    Args:
        template_paths: Additional template search paths

    Returns:
        Configured TemplateLoader instance
    """
    loader = TemplateLoader()

    if template_paths:
        for path in template_paths:
            loader.engine.add_template_path(path)

    return loader


if __name__ == "__main__":
    # Example usage and testing
    import sys

    # Create loader
    loader = create_loader()

    # Show statistics
    stats = loader.get_loader_stats()
    print("Template Loader Statistics:")
    print(f"  Search paths: {len(stats['search_paths'])}")
    print(f"  Templates found: {stats['template_count']}")
    print(f"  Built-in: {stats['templates_by_type']['builtin']}")
    print(f"  User: {stats['templates_by_type']['user']}")

    # List templates
    print("\nAvailable templates:")
    for template in loader.list_templates():
        type_str = "builtin" if template.is_builtin else "user"
        default_str = " (default)" if template.is_default else ""
        print(f"  {template.name} - {template.description} [{type_str}]{default_str}")

    # Load default template
    try:
        default_template = loader.get_default_template()
        print(f"\nDefault template: {default_template.name} v{default_template.version}")

    except Exception as e:
        print(f"Failed to load default template: {e}")
        sys.exit(1)
