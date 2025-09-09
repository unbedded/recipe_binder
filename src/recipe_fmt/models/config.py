"""Configuration models for Recipe Binder settings.

This module defines Pydantic models for managing application configuration
including display options, OpenAI settings, and template preferences.

Example usage:
    from recipe_fmt.models.config import AppConfig, DisplayConfig
    
    display_config = DisplayConfig(
        show_weights=True,
        weight_unit="grams",
        show_nutrition=False
    )
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class DisplayConfig(BaseSettings):
    """Configuration for PDF display options."""
    
    show_weights: bool = Field(True, description="Show ingredient weights alongside measurements")
    weight_unit: str = Field("grams", description="Unit for weight display (grams, ounces)")
    show_nutrition: bool = Field(False, description="Display nutrition information on cards")
    show_purpose: bool = Field(True, description="Show ingredient purpose in tables")
    
    @field_validator('weight_unit')
    def validate_weight_unit(cls, v: str) -> str:
        """Ensure valid weight unit."""
        valid_units = {'grams', 'ounces', 'g', 'oz'}
        if v.lower() not in valid_units:
            raise ValueError(f"Weight unit must be one of: {valid_units}")
        return v.lower()
    
    model_config = {"env_prefix": "RECIPE_DISPLAY_", "case_sensitive": False}


class OpenAIConfig(BaseSettings):
    """Configuration for OpenAI API integration."""
    
    api_key: Optional[str] = Field(None, env="OPENAI_API_KEY", description="OpenAI API key")
    model: str = Field("gpt-4o-mini", description="OpenAI model to use for parsing")
    max_tokens: int = Field(2000, ge=100, le=8000, description="Maximum tokens per request")
    temperature: float = Field(0.1, ge=0.0, le=2.0, description="Sampling temperature")
    timeout_seconds: int = Field(30, ge=5, le=300, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=1, le=10, description="Maximum retry attempts")
    retry_delay: float = Field(1.0, ge=0.1, le=60.0, description="Base delay between retries")
    
    @field_validator('api_key')
    def validate_api_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate API key format."""
        if v and not v.startswith('sk-'):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v
    
    model_config = {"env_prefix": "OPENAI_", "case_sensitive": False}


class TemplateConfig(BaseSettings):
    """Configuration for PDF template settings."""
    
    default_template: str = Field("default_card", description="Default template name")
    card_width: float = Field(8.5, description="Card width in inches")
    card_height: float = Field(4.0, description="Card height in inches")
    margin_lr: float = Field(0.3, description="Left/right margins in inches")
    margin_tb: float = Field(0.15, description="Top/bottom margins in inches")
    header_height: float = Field(0.4, description="Header banner height in inches")
    
    # Font settings
    title_font_size: int = Field(16, ge=8, le=24, description="Title font size in points")
    category_font_size: int = Field(12, ge=8, le=16, description="Category font size in points")
    body_font_size: int = Field(11, ge=8, le=14, description="Body text font size in points")
    instruction_font_size: int = Field(12, ge=8, le=16, description="Instruction font size in points")
    
    model_config = {"env_prefix": "RECIPE_TEMPLATE_", "case_sensitive": False}


class AppConfig(BaseSettings):
    """Main application configuration combining all settings."""
    
    # General settings
    debug: bool = Field(False, description="Enable debug logging")
    log_level: str = Field("WARNING", description="Logging level")
    
    # Component configurations
    display: Optional[DisplayConfig] = Field(None, description="Display configuration")
    openai: Optional[OpenAIConfig] = Field(None, description="OpenAI configuration")
    template: Optional[TemplateConfig] = Field(None, description="Template configuration")
    
    def __init__(self, **kwargs):
        """Initialize with sub-configs to avoid env variable conflicts."""
        # Initialize nested configs separately to avoid env parsing conflicts
        if 'display' not in kwargs:
            kwargs['display'] = DisplayConfig()
        if 'openai' not in kwargs:
            kwargs['openai'] = OpenAIConfig()  
        if 'template' not in kwargs:
            kwargs['template'] = TemplateConfig()
        super().__init__(**kwargs)
    
    @field_validator('log_level')
    def validate_log_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid log level: {v}. Must be one of: {valid_levels}')
        return v.upper()
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "validate_assignment": True,
        "json_schema_extra": {
            "example": {
                "debug": False,
                "log_level": "WARNING",
                "display": {
                    "show_weights": True,
                    "weight_unit": "grams",
                    "show_nutrition": False
                },
                "openai": {
                    "model": "gpt-4o-mini",
                    "max_tokens": 2000,
                    "temperature": 0.1
                }
            }
        }
    }