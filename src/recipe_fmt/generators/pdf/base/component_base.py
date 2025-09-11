"""Base class for all PDF generation components.

Provides common functionality like logging, configuration management,
and validation patterns used across all components.
"""

from typing import Any

from ....utils.logging_setup import get_logger
from ..types import ValidationResult


class ComponentBase:
    """Base class for all PDF generation components.

    Provides common functionality including:
    - Logging setup and management
    - Configuration validation and defaults
    - Error handling patterns
    - Component lifecycle management
    """

    def __init__(self, cfg_dict: dict = None) -> None:
        """Initialize component with configuration.

        Args:
            cfg_dict: Component-specific configuration dictionary
        """
        # STEP_1: Initialize logging first (following CLAUDE.md pattern)
        self.logger = get_logger(self.__class__.__name__, cfg_dict)

        # STEP_2: Configuration management
        self.cfg_dict = self._apply_config_defaults(cfg_dict or {})

        # STEP_3: Component initialization
        self._initialized = False
        self._validation_cache = {}

        self.logger.debug("%s initialized with config", self.__class__.__name__)

    def _apply_config_defaults(self, cfg_dict: dict) -> dict:
        """Apply configuration defaults and log missing keys.

        Subclasses should override get_config_defaults() to provide
        component-specific defaults.

        Args:
            cfg_dict: Input configuration dictionary

        Returns:
            Configuration with defaults applied
        """
        defaults = self.get_config_defaults()

        for key, default_value in defaults.items():
            if key not in cfg_dict:
                cfg_dict[key] = default_value
                self.logger.debug("Applied default for missing key %s: %s", key, default_value)

        return cfg_dict

    def get_config_defaults(self) -> dict:
        """Get default configuration values for this component.

        Subclasses should override this to provide component-specific defaults.

        Returns:
            Dictionary of default configuration values
        """
        return {
            "debug": False,
            "strict_validation": False,
            "cache_validations": True,
        }

    def get_cfg(self) -> dict:
        """Return current configuration dictionary.

        Returns:
            Copy of current configuration
        """
        return self.cfg_dict.copy()

    def validate_component(self) -> ValidationResult:
        """Validate this component's configuration and state.

        Returns:
            ValidationResult with any errors or warnings
        """
        # Check cache first if enabled
        if self.cfg_dict.get("cache_validations", True):
            cache_key = f"{self.__class__.__name__}_validation"
            if cache_key in self._validation_cache:
                self.logger.debug("Validation cache hit for %s", self.__class__.__name__)
                return self._validation_cache[cache_key]

        # Perform validation
        result = self._perform_validation()

        # Cache result if enabled
        if self.cfg_dict.get("cache_validations", True):
            self._validation_cache[cache_key] = result

        return result

    def _perform_validation(self) -> ValidationResult:
        """Perform actual validation logic.

        Subclasses should override this to provide component-specific validation.

        Returns:
            ValidationResult with validation outcome
        """
        errors = []
        warnings = []

        # Basic configuration validation
        if not isinstance(self.cfg_dict, dict):
            errors.append("Configuration must be a dictionary")

        # Validate required configuration keys
        required_keys = self.get_required_config_keys()
        for key in required_keys:
            if key not in self.cfg_dict:
                errors.append(f"Missing required configuration key: {key}")

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def get_required_config_keys(self) -> list[str]:
        """Get list of required configuration keys.

        Subclasses should override this to specify required configuration.

        Returns:
            List of required configuration key names
        """
        return []

    def initialize(self) -> bool:
        """Initialize the component.

        Performs validation and any component-specific initialization.
        Should be called before using the component.

        Returns:
            True if initialization successful
        """
        if self._initialized:
            self.logger.debug("Component already initialized")
            return True

        try:
            # Validate configuration
            validation = self.validate_component()
            if not validation.valid:
                self.logger.error("Component validation failed: %s", validation.errors)
                return False

            # Log any warnings
            for warning in validation.warnings:
                self.logger.warning("Component validation warning: %s", warning)

            # Component-specific initialization
            if not self._component_initialize():
                self.logger.error("Component-specific initialization failed")
                return False

            self._initialized = True
            self.logger.info("Component %s initialized successfully", self.__class__.__name__)
            return True

        except Exception as e:
            self.logger.exception("Component initialization failed: %s", e)
            return False

    def _component_initialize(self) -> bool:
        """Component-specific initialization logic.

        Subclasses should override this to perform any initialization
        beyond basic validation.

        Returns:
            True if component initialization successful
        """
        return True  # Default: no additional initialization needed

    def is_initialized(self) -> bool:
        """Check if the component has been initialized.

        Returns:
            True if component is ready for use
        """
        return self._initialized

    def get_component_info(self) -> dict[str, Any]:
        """Get information about this component.

        Returns:
            Dictionary with component metadata
        """
        return {
            "component_name": self.__class__.__name__,
            "component_module": self.__class__.__module__,
            "initialized": self._initialized,
            "config_keys": list(self.cfg_dict.keys()),
            "version": getattr(self.__class__, "__version__", "unknown"),
        }

    def cleanup(self) -> None:
        """Cleanup component resources.

        Should be called when the component is no longer needed.
        """
        self._validation_cache.clear()
        self._initialized = False
        self.logger.debug("Component %s cleaned up", self.__class__.__name__)
