"""Markdown recipe parser with OpenAI integration and weight conversion.

This module provides intelligent parsing of markdown recipe files using OpenAI
for structured data extraction with automatic weight estimation and validation.

Example usage:
    from recipe_fmt.parsers.markdown_parser import MarkdownParser
    from recipe_fmt.models.config import OpenAIConfig
    
    config = OpenAIConfig()
    parser = MarkdownParser(config)
    
    result = parser.parse_recipe_file("recipe/markdown/pancakes.md")
    if result.success:
        recipe_data = result.recipe
"""

import logging
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union

from ..models.config import OpenAIConfig
from ..models.recipe import Recipe
from ..utils.logging_setup import get_logger
from .openai_client import OpenAIClient, OpenAIResponse


@dataclass
class ParseResult:
    """Result wrapper for markdown parsing operations."""
    success: bool
    recipe: Optional[Recipe] = None
    yaml_content: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    cached: bool = False


class MarkdownParser:
    """Intelligent markdown recipe parser with OpenAI integration."""
    
    def __init__(self, config: OpenAIConfig, cfg_dict: dict = None) -> None:
        """Initialize markdown parser with OpenAI configuration.
        
        Args:
            config: OpenAI configuration settings
            cfg_dict: Additional configuration dictionary
        """
        # STEP_1: Initialize logging first
        self.logger = get_logger(__name__, cfg_dict)
        
        # STEP_2: Configuration management
        self.config = config
        self.cfg_dict = self._apply_config_defaults(cfg_dict or {})
        
        # STEP_3: Initialize OpenAI client
        self.openai_client = OpenAIClient(config, cfg_dict)
        
        self.logger.info("MarkdownParser initialized with OpenAI model: %s", config.model)
    
    def _apply_config_defaults(self, cfg_dict: dict) -> dict:
        """Apply configuration defaults and log missing keys.
        
        Args:
            cfg_dict: Input configuration dictionary
            
        Returns:
            Configuration with defaults applied
        """
        defaults = {
            "validate_yaml": True,
            "allow_partial_parsing": False,
            "strict_validation": True,
            "preserve_markdown": False
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
    
    def parse_recipe_file(self, file_path: Union[str, Path]) -> ParseResult:
        """Parse a markdown recipe file into structured Recipe object.
        
        Args:
            file_path: Path to markdown recipe file
            
        Returns:
            Parse result with recipe data or error information
        """
        try:
            file_path = Path(file_path)
            
            # STEP_4: Validate input file
            if not file_path.exists():
                error_msg = f"Recipe file not found: {file_path}"
                self.logger.error(error_msg)
                return ParseResult(success=False, error=error_msg)
            
            if not file_path.suffix.lower() in ['.md', '.markdown']:
                error_msg = f"Invalid file type: {file_path.suffix}. Expected .md or .markdown"
                self.logger.error(error_msg)
                return ParseResult(success=False, error=error_msg)
            
            self.logger.info("Parsing recipe file: %s", file_path)
            
            # STEP_5: Read markdown content
            try:
                markdown_content = file_path.read_text(encoding='utf-8')
                if not markdown_content.strip():
                    error_msg = f"Recipe file is empty: {file_path}"
                    self.logger.error(error_msg)
                    return ParseResult(success=False, error=error_msg)
                    
            except Exception as e:
                error_msg = f"Failed to read recipe file {file_path}: {e}"
                self.logger.exception(error_msg)
                return ParseResult(success=False, error=error_msg)
            
            # STEP_6: Parse with OpenAI
            return self._parse_markdown_content(markdown_content, file_path.name)
            
        except Exception as e:
            error_msg = f"Unexpected error parsing {file_path}: {e}"
            self.logger.exception(error_msg)
            return ParseResult(success=False, error=error_msg)
    
    def parse_recipe_content(self, markdown_content: str, recipe_name: str = "unknown") -> ParseResult:
        """Parse markdown recipe content directly.
        
        Args:
            markdown_content: Raw markdown recipe text
            recipe_name: Name for logging purposes
            
        Returns:
            Parse result with recipe data or error information
        """
        try:
            self.logger.info("Parsing recipe content: %s", recipe_name)
            
            if not markdown_content.strip():
                error_msg = "Recipe content is empty"
                self.logger.error(error_msg)
                return ParseResult(success=False, error=error_msg)
            
            return self._parse_markdown_content(markdown_content, recipe_name)
            
        except Exception as e:
            error_msg = f"Unexpected error parsing recipe content: {e}"
            self.logger.exception(error_msg)
            return ParseResult(success=False, error=error_msg)
    
    def _parse_markdown_content(self, markdown_content: str, recipe_name: str) -> ParseResult:
        """Internal method to parse markdown content using OpenAI.
        
        Args:
            markdown_content: Raw markdown recipe text
            recipe_name: Recipe name for logging
            
        Returns:
            Parse result with recipe data
        """
        try:
            # STEP_7: Call OpenAI for parsing
            self.logger.debug("Sending recipe to OpenAI for parsing: %s", recipe_name)
            
            openai_response = self.openai_client.parse_recipe_markdown(markdown_content)
            
            if not openai_response.success:
                error_msg = f"OpenAI parsing failed for {recipe_name}: {openai_response.error}"
                self.logger.error(error_msg)
                return ParseResult(
                    success=False,
                    error=error_msg,
                    tokens_used=openai_response.tokens_used,
                    cost_estimate=openai_response.cost_estimate
                )
            
            # STEP_8: Extract YAML content
            yaml_content = openai_response.data.get("content", "")
            if not yaml_content.strip():
                error_msg = f"OpenAI returned empty content for {recipe_name}"
                self.logger.error(error_msg)
                return ParseResult(success=False, error=error_msg)
            
            self.logger.debug("OpenAI parsing successful for %s (%d tokens, $%.4f)", 
                           recipe_name, 
                           openai_response.tokens_used or 0,
                           openai_response.cost_estimate or 0)
            
            # STEP_9: Validate and parse YAML
            if self.cfg_dict.get("validate_yaml", True):
                return self._validate_and_parse_yaml(
                    yaml_content,
                    recipe_name,
                    openai_response.tokens_used,
                    openai_response.cost_estimate,
                    openai_response.cached
                )
            else:
                # Skip validation - just return raw YAML
                return ParseResult(
                    success=True,
                    yaml_content=yaml_content,
                    tokens_used=openai_response.tokens_used,
                    cost_estimate=openai_response.cost_estimate,
                    cached=openai_response.cached
                )
                
        except Exception as e:
            error_msg = f"Failed to parse markdown content for {recipe_name}: {e}"
            self.logger.exception(error_msg)
            return ParseResult(success=False, error=error_msg)
    
    def _clean_openai_response(self, yaml_data: dict, recipe_name: str) -> dict:
        """Clean and fix common OpenAI response issues.
        
        Args:
            yaml_data: Raw YAML data from OpenAI
            recipe_name: Recipe name for logging
            
        Returns:
            Cleaned YAML data
        """
        try:
            # Fix ingredients with null/missing amounts
            if 'ingredients' in yaml_data and isinstance(yaml_data['ingredients'], list):
                for i, ingredient in enumerate(yaml_data['ingredients']):
                    if isinstance(ingredient, dict):
                        # Fix null amounts for garnish ingredients
                        if ingredient.get('amount') is None:
                            ingredient_name = ingredient.get('ingredient', '').lower()
                            if any(word in ingredient_name for word in ['garnish', 'for serving', 'optional', 'to taste']):
                                ingredient['amount'] = 0.25
                                ingredient['unit'] = 'portion'
                                self.logger.debug("Fixed null amount for garnish ingredient in %s: %s", 
                                               recipe_name, ingredient.get('ingredient'))
                            else:
                                ingredient['amount'] = 1.0
                                ingredient['unit'] = 'count'
                                self.logger.warning("Fixed null amount for ingredient in %s: %s", 
                                                  recipe_name, ingredient.get('ingredient'))
                        
                        # Ensure weight_grams is integer
                        if 'weight_grams' in ingredient and ingredient['weight_grams'] is not None:
                            try:
                                ingredient['weight_grams'] = int(float(ingredient['weight_grams']))
                            except (ValueError, TypeError):
                                ingredient['weight_grams'] = 10  # Default small weight
            
            # Fix instructions if they're returned as dict instead of list
            if 'instructions' in yaml_data:
                instructions = yaml_data['instructions']
                if isinstance(instructions, dict):
                    # Convert dict to list of strings
                    instruction_list = []
                    for key, value in instructions.items():
                        if isinstance(value, str):
                            instruction_list.append(f"{key}: {value}")
                        else:
                            instruction_list.append(str(key))
                    yaml_data['instructions'] = instruction_list
                    self.logger.warning("Fixed dict instructions for %s, converted to list", recipe_name)
                elif isinstance(instructions, list):
                    # Ensure all instructions are strings
                    fixed_instructions = []
                    for instr in instructions:
                        if isinstance(instr, dict):
                            # Convert dict instruction to string
                            if len(instr) == 1:
                                key, value = next(iter(instr.items()))
                                fixed_instructions.append(f"{key}: {value}" if isinstance(value, str) else str(key))
                            else:
                                fixed_instructions.append(str(instr))
                        else:
                            fixed_instructions.append(str(instr))
                    yaml_data['instructions'] = fixed_instructions
                    
            return yaml_data
            
        except Exception as e:
            self.logger.warning("Error cleaning OpenAI response for %s: %s", recipe_name, e)
            return yaml_data
    
    def _validate_and_parse_yaml(
        self, 
        yaml_content: str, 
        recipe_name: str,
        tokens_used: Optional[int],
        cost_estimate: Optional[float],
        cached: bool
    ) -> ParseResult:
        """Validate YAML content and create Recipe object.
        
        Args:
            yaml_content: YAML content from OpenAI
            recipe_name: Recipe name for logging
            tokens_used: Number of tokens used in OpenAI call
            cost_estimate: Estimated cost of OpenAI call
            cached: Whether result was cached
            
        Returns:
            Parse result with validated Recipe object
        """
        try:
            # STEP_10: Parse YAML
            self.logger.debug("Validating YAML content for %s", recipe_name)
            
            try:
                yaml_data = yaml.safe_load(yaml_content)
                if not isinstance(yaml_data, dict):
                    error_msg = f"Invalid YAML structure for {recipe_name}: expected dictionary"
                    self.logger.error(error_msg)
                    return ParseResult(
                        success=False,
                        error=error_msg,
                        yaml_content=yaml_content,
                        tokens_used=tokens_used,
                        cost_estimate=cost_estimate,
                        cached=cached
                    )
                    
            except yaml.YAMLError as e:
                error_msg = f"YAML parsing error for {recipe_name}: {e}"
                self.logger.error(error_msg)
                return ParseResult(
                    success=False,
                    error=error_msg,
                    yaml_content=yaml_content,
                    tokens_used=tokens_used,
                    cost_estimate=cost_estimate,
                    cached=cached
                )
            
            # STEP_11: Clean and validate YAML data
            yaml_data = self._clean_openai_response(yaml_data, recipe_name)
            
            # STEP_12: Validate with Pydantic model
            try:
                recipe = Recipe(**yaml_data)
                
                self.logger.info("Successfully parsed recipe: %s (category: %s, %d ingredients)", 
                               recipe.title, recipe.category, len(recipe.ingredients))
                
                # STEP_12: Log weight conversion stats
                ingredients_with_weights = sum(1 for ing in recipe.ingredients if ing.weight_grams)
                self.logger.debug("Weight conversion coverage: %d/%d ingredients have weights", 
                               ingredients_with_weights, len(recipe.ingredients))
                
                return ParseResult(
                    success=True,
                    recipe=recipe,
                    yaml_content=yaml_content,
                    tokens_used=tokens_used,
                    cost_estimate=cost_estimate,
                    cached=cached
                )
                
            except Exception as e:
                error_msg = f"Recipe validation error for {recipe_name}: {e}"
                self.logger.error(error_msg)
                
                # STEP_13: Handle partial parsing if enabled
                if self.cfg_dict.get("allow_partial_parsing", False):
                    self.logger.warning("Returning partial YAML content due to validation error")
                    return ParseResult(
                        success=False,
                        error=error_msg,
                        yaml_content=yaml_content,
                        tokens_used=tokens_used,
                        cost_estimate=cost_estimate,
                        cached=cached
                    )
                else:
                    return ParseResult(
                        success=False,
                        error=error_msg,
                        tokens_used=tokens_used,
                        cost_estimate=cost_estimate,
                        cached=cached
                    )
                    
        except Exception as e:
            error_msg = f"Unexpected error during YAML validation for {recipe_name}: {e}"
            self.logger.exception(error_msg)
            return ParseResult(success=False, error=error_msg)
    
    def get_parsing_stats(self) -> dict:
        """Get parsing statistics from the OpenAI client.
        
        Returns:
            Dictionary with parsing statistics
        """
        openai_stats = self.openai_client.get_usage_stats()
        
        return {
            "openai_stats": openai_stats,
            "parser_config": {
                "validate_yaml": self.cfg_dict.get("validate_yaml", True),
                "allow_partial_parsing": self.cfg_dict.get("allow_partial_parsing", False),
                "strict_validation": self.cfg_dict.get("strict_validation", True)
            }
        }
    
    def validate_api_key(self) -> bool:
        """Validate that the OpenAI API key is working.
        
        Returns:
            True if API key is valid and working
        """
        return self.openai_client.validate_api_key()


def create_parser_from_env(cfg_dict: dict = None) -> MarkdownParser:
    """Create a MarkdownParser using environment configuration.
    
    Args:
        cfg_dict: Additional configuration overrides
        
    Returns:
        Configured MarkdownParser instance
    """
    config = OpenAIConfig()
    return MarkdownParser(config, cfg_dict)


if __name__ == "__main__":
    # Example usage and testing
    import sys
    from pathlib import Path
    
    if len(sys.argv) != 2:
        print("Usage: python -m recipe_fmt.parsers.markdown_parser <recipe_file.md>")
        sys.exit(1)
    
    recipe_file = Path(sys.argv[1])
    
    # Create parser
    parser = create_parser_from_env({"validate_yaml": True})
    
    # Parse recipe
    result = parser.parse_recipe_file(recipe_file)
    
    if result.success:
        print(f"✅ Successfully parsed: {result.recipe.title}")
        print(f"   Category: {result.recipe.category}")
        print(f"   Ingredients: {len(result.recipe.ingredients)}")
        print(f"   Instructions: {len(result.recipe.instructions)}")
        if result.tokens_used:
            print(f"   Tokens used: {result.tokens_used}")
        if result.cost_estimate:
            print(f"   Cost estimate: ${result.cost_estimate:.4f}")
    else:
        print(f"❌ Parsing failed: {result.error}")
        sys.exit(1)