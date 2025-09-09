"""YAML recipe validator with comprehensive validation rules.

This module provides robust validation for recipe YAML files including
schema validation, business rule checking, and data consistency verification.

Example usage:
    from recipe_fmt.validators.yaml_validator import YAMLValidator
    
    validator = YAMLValidator()
    result = validator.validate_yaml_file("recipe/yaml/pancakes.yaml")
    
    if result.valid:
        print(f"Valid recipe: {result.recipe.title}")
    else:
        for error in result.errors:
            print(f"Error: {error.message}")
"""

import logging
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union, List
from enum import Enum

from ..models.recipe import Recipe, Ingredient, Nutrition
from ..utils.logging_setup import get_logger


class ValidationSeverity(Enum):
    """Validation error severity levels."""
    ERROR = "error"      # Blocks recipe usage
    WARNING = "warning"  # Suggests improvement
    INFO = "info"        # Informational notice


@dataclass
class ValidationError:
    """Individual validation error or warning."""
    severity: ValidationSeverity
    field: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of YAML validation operation."""
    valid: bool
    recipe: Optional[Recipe] = None
    yaml_data: Optional[dict] = None
    errors: List[ValidationError] = None
    warnings: List[ValidationError] = None
    
    def __post_init__(self):
        """Initialize lists if None."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def has_errors(self) -> bool:
        """Check if result has validation errors."""
        return len(self.errors) > 0
    
    @property 
    def has_warnings(self) -> bool:
        """Check if result has validation warnings."""
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> str:
        """Get summary of validation issues."""
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        
        if error_count > 0 and warning_count > 0:
            return f"{error_count} errors, {warning_count} warnings"
        elif error_count > 0:
            return f"{error_count} errors"
        elif warning_count > 0:
            return f"{warning_count} warnings"
        else:
            return "No issues"


class YAMLValidator:
    """Comprehensive YAML recipe validator."""
    
    def __init__(self, cfg_dict: dict = None) -> None:
        """Initialize YAML validator with configuration.
        
        Args:
            cfg_dict: Configuration dictionary
        """
        # STEP_1: Initialize logging first
        self.logger = get_logger(__name__, cfg_dict)
        
        # STEP_2: Configuration management
        self.cfg_dict = self._apply_config_defaults(cfg_dict or {})
        
        # STEP_3: Initialize validation rules
        self._init_validation_rules()
        
        self.logger.info("YAMLValidator initialized with strict mode: %s", 
                        self.cfg_dict.get("strict_validation", True))
    
    def _apply_config_defaults(self, cfg_dict: dict) -> dict:
        """Apply configuration defaults and log missing keys.
        
        Args:
            cfg_dict: Input configuration dictionary
            
        Returns:
            Configuration with defaults applied
        """
        defaults = {
            "strict_validation": True,
            "check_weights": True,
            "check_nutrition": False,
            "allow_unknown_categories": True,
            "min_ingredients": 1,
            "max_ingredients": 50,
            "min_instructions": 1,
            "max_instructions": 20,
            "weight_tolerance": 0.1  # 10% tolerance for weight estimates
        }
        
        for key, default_value in defaults.items():
            if key not in cfg_dict:
                cfg_dict[key] = default_value
                self.logger.debug("Applied default for missing key %s: %s", key, default_value)
        
        return cfg_dict
    
    def _init_validation_rules(self) -> None:
        """Initialize validation rules and lookup tables."""
        # STEP_4: Standard unit conversions for weight validation
        self.unit_weights = {
            # Cups to grams (approximate)
            'cups': {
                'all-purpose flour': 120,
                'flour': 120,
                'sugar': 200,
                'granulated sugar': 200,
                'brown sugar': 220,
                'butter': 225,
                'milk': 240,
                'water': 240,
                'oil': 220,
                'vegetable oil': 220,
                'honey': 340,
                'salt': 300,
                'baking powder': 160,
                'baking soda': 160
            },
            # Tablespoons to grams
            'TBL': {
                'flour': 7.5,
                'sugar': 12.5,
                'butter': 14,
                'oil': 13.5,
                'honey': 21,
                'salt': 18
            },
            # Teaspoons to grams  
            'tsp': {
                'flour': 2.5,
                'sugar': 4,
                'salt': 6,
                'baking powder': 3.5,
                'baking soda': 3.5,
                'vanilla': 4
            }
        }
        
        # STEP_5: Valid recipe categories
        self.valid_categories = {
            'Meat', 'Side', 'Main', 'Soup', 'Sauce', 'Breakfast', 
            'Salad', 'Baking', 'Dessert', 'Other'
        }
        
        # STEP_6: Common ingredient purpose categories
        self.common_purposes = {
            'base', 'protein', 'vegetable', 'grain', 'dairy', 'fat', 
            'seasoning', 'spice', 'herb', 'sweetener', 'leavening',
            'liquid', 'garnish', 'topping', 'filling', 'sauce'
        }
    
    def get_cfg(self) -> dict:
        """Return current configuration dictionary.
        
        Returns:
            Copy of current configuration
        """
        return self.cfg_dict.copy()
    
    def validate_yaml_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """Validate a YAML recipe file.
        
        Args:
            file_path: Path to YAML recipe file
            
        Returns:
            Validation result with recipe and any errors/warnings
        """
        try:
            file_path = Path(file_path)
            
            # STEP_7: Validate input file
            if not file_path.exists():
                return ValidationResult(
                    valid=False,
                    errors=[ValidationError(
                        severity=ValidationSeverity.ERROR,
                        field="file",
                        message=f"YAML file not found: {file_path}"
                    )]
                )
            
            if not file_path.suffix.lower() in ['.yaml', '.yml']:
                return ValidationResult(
                    valid=False,
                    errors=[ValidationError(
                        severity=ValidationSeverity.ERROR,
                        field="file",
                        message=f"Invalid file type: {file_path.suffix}. Expected .yaml or .yml"
                    )]
                )
            
            self.logger.info("Validating YAML file: %s", file_path)
            
            # STEP_8: Read YAML content
            try:
                yaml_content = file_path.read_text(encoding='utf-8')
                if not yaml_content.strip():
                    return ValidationResult(
                        valid=False,
                        errors=[ValidationError(
                            severity=ValidationSeverity.ERROR,
                            field="file",
                            message=f"YAML file is empty: {file_path}"
                        )]
                    )
                    
            except Exception as e:
                return ValidationResult(
                    valid=False,
                    errors=[ValidationError(
                        severity=ValidationSeverity.ERROR,
                        field="file",
                        message=f"Failed to read YAML file {file_path}: {e}"
                    )]
                )
            
            # STEP_9: Validate YAML content
            return self.validate_yaml_content(yaml_content, str(file_path))
            
        except Exception as e:
            self.logger.exception("Unexpected error validating YAML file: %s", file_path)
            return ValidationResult(
                valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.ERROR,
                    field="validation",
                    message=f"Unexpected validation error: {e}"
                )]
            )
    
    def validate_yaml_content(self, yaml_content: str, source_name: str = "content") -> ValidationResult:
        """Validate YAML recipe content.
        
        Args:
            yaml_content: Raw YAML content string
            source_name: Name for logging purposes
            
        Returns:
            Validation result with recipe and any errors/warnings
        """
        try:
            self.logger.debug("Validating YAML content from: %s", source_name)
            
            # STEP_10: Parse YAML
            try:
                yaml_data = yaml.safe_load(yaml_content)
                if not isinstance(yaml_data, dict):
                    return ValidationResult(
                        valid=False,
                        errors=[ValidationError(
                            severity=ValidationSeverity.ERROR,
                            field="yaml",
                            message="Invalid YAML structure: expected dictionary at root level"
                        )]
                    )
                    
            except yaml.YAMLError as e:
                return ValidationResult(
                    valid=False,
                    errors=[ValidationError(
                        severity=ValidationSeverity.ERROR,
                        field="yaml",
                        message=f"YAML parsing error: {e}"
                    )]
                )
            
            # STEP_11: Clean common OpenAI response issues
            yaml_data = self._clean_yaml_data(yaml_data, source_name)
            
            # STEP_12: Perform comprehensive validation
            return self._validate_recipe_data(yaml_data, source_name)
            
        except Exception as e:
            self.logger.exception("Unexpected error validating YAML content")
            return ValidationResult(
                valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.ERROR,
                    field="validation",
                    message=f"Unexpected validation error: {e}"
                )]
            )
    
    def _clean_yaml_data(self, yaml_data: dict, source_name: str) -> dict:
        """Clean common OpenAI response issues in YAML data.
        
        Args:
            yaml_data: Raw YAML data from OpenAI
            source_name: Source name for logging
            
        Returns:
            Cleaned YAML data
        """
        try:
            # Fix ingredients with null/missing amounts
            if 'ingredients' in yaml_data and isinstance(yaml_data['ingredients'], list):
                for ingredient in yaml_data['ingredients']:
                    if isinstance(ingredient, dict):
                        # Fix null amounts for garnish ingredients
                        if ingredient.get('amount') is None:
                            ingredient_name = ingredient.get('ingredient', '').lower()
                            if any(word in ingredient_name for word in ['garnish', 'for serving', 'optional', 'to taste']):
                                ingredient['amount'] = 0.25
                                ingredient['unit'] = 'portion'
                                self.logger.debug("Fixed null amount for garnish ingredient in %s: %s", 
                                               source_name, ingredient.get('ingredient'))
                            else:
                                ingredient['amount'] = 1.0
                                ingredient['unit'] = 'count'
                                self.logger.warning("Fixed null amount for ingredient in %s: %s", 
                                                  source_name, ingredient.get('ingredient'))
                        
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
                    self.logger.warning("Fixed dict instructions for %s, converted to list", source_name)
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
            self.logger.warning("Error cleaning YAML data for %s: %s", source_name, e)
            return yaml_data
    
    def _validate_recipe_data(self, yaml_data: dict, source_name: str) -> ValidationResult:
        """Perform comprehensive validation of recipe data.
        
        Args:
            yaml_data: Parsed YAML data
            source_name: Source name for logging
            
        Returns:
            Validation result with detailed error/warning information
        """
        errors = []
        warnings = []
        
        try:
            # STEP_12: Basic schema validation with Pydantic
            try:
                recipe = Recipe(**yaml_data)
                self.logger.debug("Pydantic validation passed for: %s", source_name)
                
            except Exception as e:
                errors.append(ValidationError(
                    severity=ValidationSeverity.ERROR,
                    field="schema",
                    message=f"Schema validation failed: {e}",
                    suggestion="Check required fields and data types"
                ))
                
                # If strict validation, stop here
                if self.cfg_dict.get("strict_validation", True):
                    return ValidationResult(
                        valid=False,
                        yaml_data=yaml_data,
                        errors=errors,
                        warnings=warnings
                    )
                
                # Continue with partial validation
                recipe = None
            
            # STEP_13: Business rule validation
            self._validate_business_rules(yaml_data, errors, warnings)
            
            # STEP_14: Weight consistency validation
            if self.cfg_dict.get("check_weights", True) and recipe:
                self._validate_weight_consistency(recipe, warnings)
            
            # STEP_15: Nutrition validation
            if self.cfg_dict.get("check_nutrition", False) and recipe:
                self._validate_nutrition_data(recipe, warnings)
            
            # STEP_16: Determine overall validity
            is_valid = len(errors) == 0
            
            if is_valid:
                self.logger.info("Validation successful for %s: %s (%d warnings)", 
                               source_name, recipe.title if recipe else "unknown", len(warnings))
            else:
                self.logger.warning("Validation failed for %s: %d errors, %d warnings", 
                                  source_name, len(errors), len(warnings))
            
            return ValidationResult(
                valid=is_valid,
                recipe=recipe,
                yaml_data=yaml_data,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            self.logger.exception("Unexpected error during recipe validation")
            errors.append(ValidationError(
                severity=ValidationSeverity.ERROR,
                field="validation",
                message=f"Unexpected validation error: {e}"
            ))
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
    
    def _validate_business_rules(self, yaml_data: dict, errors: List[ValidationError], warnings: List[ValidationError]) -> None:
        """Validate business rules and logical consistency.
        
        Args:
            yaml_data: Recipe data to validate
            errors: List to append errors to
            warnings: List to append warnings to
        """
        # STEP_17: Category validation
        category = yaml_data.get('category', '')
        if category and category not in self.valid_categories:
            if self.cfg_dict.get("allow_unknown_categories", True):
                warnings.append(ValidationError(
                    severity=ValidationSeverity.WARNING,
                    field="category",
                    message=f"Unknown category: {category}",
                    suggestion=f"Consider using one of: {', '.join(sorted(self.valid_categories))}"
                ))
            else:
                errors.append(ValidationError(
                    severity=ValidationSeverity.ERROR,
                    field="category",
                    message=f"Invalid category: {category}",
                    suggestion=f"Must be one of: {', '.join(sorted(self.valid_categories))}"
                ))
        
        # STEP_18: Ingredient count validation
        ingredients = yaml_data.get('ingredients', [])
        min_ingredients = self.cfg_dict.get("min_ingredients", 1)
        max_ingredients = self.cfg_dict.get("max_ingredients", 50)
        
        if len(ingredients) < min_ingredients:
            errors.append(ValidationError(
                severity=ValidationSeverity.ERROR,
                field="ingredients",
                message=f"Too few ingredients: {len(ingredients)} (minimum: {min_ingredients})"
            ))
        elif len(ingredients) > max_ingredients:
            warnings.append(ValidationError(
                severity=ValidationSeverity.WARNING,
                field="ingredients",
                message=f"Many ingredients: {len(ingredients)} (consider splitting recipe)"
            ))
        
        # STEP_19: Instructions count validation
        instructions = yaml_data.get('instructions', [])
        min_instructions = self.cfg_dict.get("min_instructions", 1)
        max_instructions = self.cfg_dict.get("max_instructions", 20)
        
        if len(instructions) < min_instructions:
            errors.append(ValidationError(
                severity=ValidationSeverity.ERROR,
                field="instructions",
                message=f"Too few instructions: {len(instructions)} (minimum: {min_instructions})"
            ))
        elif len(instructions) > max_instructions:
            warnings.append(ValidationError(
                severity=ValidationSeverity.WARNING,
                field="instructions",
                message=f"Many instructions: {len(instructions)} (consider simplifying)"
            ))
        
        # STEP_20: Servings validation
        servings = yaml_data.get('servings', 0)
        if servings < 1:
            errors.append(ValidationError(
                severity=ValidationSeverity.ERROR,
                field="servings",
                message="Servings must be at least 1"
            ))
        elif servings > 100:
            warnings.append(ValidationError(
                severity=ValidationSeverity.WARNING,
                field="servings",
                message=f"Large serving count: {servings} (consider if accurate)"
            ))
    
    def _validate_weight_consistency(self, recipe: Recipe, warnings: List[ValidationError]) -> None:
        """Validate weight estimates for consistency.
        
        Args:
            recipe: Recipe object to validate
            warnings: List to append warnings to
        """
        for i, ingredient in enumerate(recipe.ingredients):
            if not ingredient.weight_grams:
                continue
                
            # STEP_21: Check weight reasonableness
            expected_weight = self._estimate_ingredient_weight(ingredient)
            if expected_weight is None:
                continue
                
            tolerance = self.cfg_dict.get("weight_tolerance", 0.1)
            weight_diff = abs(ingredient.weight_grams - expected_weight) / expected_weight
            
            if weight_diff > tolerance:
                warnings.append(ValidationError(
                    severity=ValidationSeverity.WARNING,
                    field=f"ingredients[{i}].weight_grams",
                    message=f"Weight estimate may be inaccurate for {ingredient.ingredient}: "
                           f"{ingredient.weight_grams}g (expected ~{expected_weight}g)",
                    suggestion="Verify weight calculation or ingredient density"
                ))
    
    def _estimate_ingredient_weight(self, ingredient: Ingredient) -> Optional[int]:
        """Estimate weight for an ingredient based on amount and unit.
        
        Args:
            ingredient: Ingredient to estimate weight for
            
        Returns:
            Estimated weight in grams or None if unable to estimate
        """
        unit = ingredient.unit.lower()
        ingredient_name = ingredient.ingredient.lower()
        
        # STEP_22: Look up weight per unit
        if unit in self.unit_weights:
            unit_weights = self.unit_weights[unit]
            
            # Try exact match first
            if ingredient_name in unit_weights:
                return int(ingredient.amount * unit_weights[ingredient_name])
            
            # Try partial matches
            for key, weight_per_unit in unit_weights.items():
                if key in ingredient_name or ingredient_name in key:
                    return int(ingredient.amount * weight_per_unit)
        
        return None
    
    def _validate_nutrition_data(self, recipe: Recipe, warnings: List[ValidationError]) -> None:
        """Validate nutrition information if present.
        
        Args:
            recipe: Recipe object to validate
            warnings: List to append warnings to
        """
        if not recipe.nutrition:
            return
            
        nutrition = recipe.nutrition
        
        # STEP_23: Basic nutrition sanity checks
        if nutrition.calories and nutrition.calories < 0:
            warnings.append(ValidationError(
                severity=ValidationSeverity.WARNING,
                field="nutrition.calories",
                message="Calories cannot be negative"
            ))
        
        if nutrition.calories and nutrition.calories > 2000:
            warnings.append(ValidationError(
                severity=ValidationSeverity.WARNING,
                field="nutrition.calories",
                message=f"High calorie count per serving: {nutrition.calories}"
            ))
        
        # STEP_24: Macronutrient balance check
        if all([nutrition.protein_g, nutrition.carbs_g, nutrition.fat_g]):
            total_macro_calories = (
                nutrition.protein_g * 4 +  # 4 cal/g protein
                nutrition.carbs_g * 4 +    # 4 cal/g carbs  
                nutrition.fat_g * 9        # 9 cal/g fat
            )
            
            if nutrition.calories and abs(nutrition.calories - total_macro_calories) > 50:
                warnings.append(ValidationError(
                    severity=ValidationSeverity.WARNING,
                    field="nutrition",
                    message=f"Calorie count ({nutrition.calories}) doesn't match macronutrients "
                           f"(calculated: {total_macro_calories:.0f})",
                    suggestion="Verify nutrition calculations"
                ))
    
    def get_validation_stats(self) -> dict:
        """Get validation statistics and configuration.
        
        Returns:
            Dictionary with validation statistics
        """
        return {
            "validator_config": self.cfg_dict.copy(),
            "supported_categories": sorted(list(self.valid_categories)),
            "supported_units": list(self.unit_weights.keys()),
            "validation_rules": {
                "min_ingredients": self.cfg_dict.get("min_ingredients", 1),
                "max_ingredients": self.cfg_dict.get("max_ingredients", 50),
                "min_instructions": self.cfg_dict.get("min_instructions", 1),
                "max_instructions": self.cfg_dict.get("max_instructions", 20),
                "weight_tolerance": self.cfg_dict.get("weight_tolerance", 0.1)
            }
        }


def create_validator(strict: bool = True, check_weights: bool = True) -> YAMLValidator:
    """Create a YAMLValidator with common configuration.
    
    Args:
        strict: Enable strict validation mode
        check_weights: Enable weight consistency checking
        
    Returns:
        Configured YAMLValidator instance
    """
    config = {
        "strict_validation": strict,
        "check_weights": check_weights,
        "check_nutrition": False,
        "allow_unknown_categories": True
    }
    return YAMLValidator(config)


if __name__ == "__main__":
    # Example usage and testing
    import sys
    from pathlib import Path
    
    if len(sys.argv) != 2:
        print("Usage: python -m recipe_fmt.validators.yaml_validator <recipe_file.yaml>")
        sys.exit(1)
    
    yaml_file = Path(sys.argv[1])
    
    # Create validator
    validator = create_validator(strict=True, check_weights=True)
    
    # Validate recipe
    result = validator.validate_yaml_file(yaml_file)
    
    print(f"Validation result: {'✅ Valid' if result.valid else '❌ Invalid'}")
    print(f"Summary: {result.get_error_summary()}")
    
    if result.recipe:
        print(f"Recipe: {result.recipe.title} ({result.recipe.category})")
    
    for error in result.errors:
        print(f"ERROR [{error.field}]: {error.message}")
        if error.suggestion:
            print(f"  Suggestion: {error.suggestion}")
    
    for warning in result.warnings:
        print(f"WARNING [{warning.field}]: {warning.message}")
        if warning.suggestion:
            print(f"  Suggestion: {warning.suggestion}")
    
    sys.exit(0 if result.valid else 1)