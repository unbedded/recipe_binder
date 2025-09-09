"""OpenAI client with retry logic and error handling.

This module provides a robust OpenAI API client for recipe parsing with
comprehensive error handling, retry logic, and cost optimization features.

Example usage:
    from recipe_fmt.parsers.openai_client import OpenAIClient
    from recipe_fmt.models.config import OpenAIConfig
    
    config = OpenAIConfig()
    client = OpenAIClient(config)
    
    result = client.parse_recipe_markdown(markdown_content)
    if result.success:
        recipe_data = result.data
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional, Any

from ..models.config import OpenAIConfig
from ..utils.logging_setup import get_logger


@dataclass
class OpenAIResponse:
    """Response wrapper for OpenAI API calls."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    cached: bool = False


class OpenAIClient:
    """OpenAI API client with retry logic and error handling."""
    
    def __init__(self, config: OpenAIConfig, cfg_dict: dict = None) -> None:
        """Initialize OpenAI client with configuration.
        
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
        self._openai_client = None
        self._init_openai_client()
        
        # STEP_4: Simple response cache for cost optimization
        self._response_cache = {}
        
        self.logger.info("OpenAI client initialized with model: %s", config.model)
    
    def _apply_config_defaults(self, cfg_dict: dict) -> dict:
        """Apply configuration defaults and log missing keys.
        
        Args:
            cfg_dict: Input configuration dictionary
            
        Returns:
            Configuration with defaults applied
        """
        defaults = {
            "enable_caching": True,
            "cache_max_size": 100,
            "mock_mode": False,
            "cost_tracking": True
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
    
    def _init_openai_client(self) -> None:
        """Initialize the OpenAI client library."""
        try:
            # Check if we have an API key
            if not self.config.api_key:
                self.logger.warning("No OpenAI API key provided - client will operate in mock mode")
                self.cfg_dict["mock_mode"] = True
                return
            
            # Import OpenAI library
            try:
                import openai
                self._openai_client = openai.OpenAI(api_key=self.config.api_key)
                self.logger.info("OpenAI client initialized successfully")
                
            except ImportError:
                self.logger.error("OpenAI library not installed - install with: pip install openai")
                self.cfg_dict["mock_mode"] = True
                
        except Exception as e:
            self.logger.exception("Failed to initialize OpenAI client: %s", e)
            self.cfg_dict["mock_mode"] = True
    
    def _generate_cache_key(self, content: str, prompt_type: str) -> str:
        """Generate cache key for request caching.
        
        Args:
            content: Input content to hash
            prompt_type: Type of prompt being used
            
        Returns:
            Cache key string
        """
        import hashlib
        
        # Create hash of content + config for cache key
        cache_data = f"{content}-{prompt_type}-{self.config.model}-{self.config.temperature}"
        return hashlib.md5(cache_data.encode()).hexdigest()[:16]
    
    def _get_cached_response(self, cache_key: str) -> Optional[OpenAIResponse]:
        """Get cached response if available.
        
        Args:
            cache_key: Cache key to lookup
            
        Returns:
            Cached response or None if not found
        """
        if not self.cfg_dict.get("enable_caching", True):
            return None
        
        cached = self._response_cache.get(cache_key)
        if cached:
            self.logger.debug("Cache hit for key: %s", cache_key)
            cached.cached = True
            return cached
        
        return None
    
    def _cache_response(self, cache_key: str, response: OpenAIResponse) -> None:
        """Cache a successful response.
        
        Args:
            cache_key: Key to cache under
            response: Response to cache
        """
        if not self.cfg_dict.get("enable_caching", True):
            return
        
        # Simple cache size management
        max_cache_size = self.cfg_dict.get("cache_max_size", 100)
        if len(self._response_cache) >= max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._response_cache))
            del self._response_cache[oldest_key]
            self.logger.debug("Cache full - removed oldest entry")
        
        # Cache the response (without the cached flag)
        cached_response = OpenAIResponse(
            success=response.success,
            data=response.data,
            error=response.error,
            tokens_used=response.tokens_used,
            cost_estimate=response.cost_estimate,
            cached=False
        )
        
        self._response_cache[cache_key] = cached_response
        self.logger.debug("Cached response for key: %s", cache_key)
    
    def _make_openai_request(self, messages: list[dict], attempt: int = 1) -> OpenAIResponse:
        """Make a request to OpenAI API with retry logic.
        
        Args:
            messages: List of message dictionaries for the API
            attempt: Current attempt number (for logging)
            
        Returns:
            OpenAI response wrapper
        """
        try:
            if self.cfg_dict.get("mock_mode", False):
                return self._mock_openai_response()
            
            self.logger.debug("Making OpenAI request (attempt %d)", attempt)
            
            # STEP_5: Make the API call
            response = self._openai_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.timeout_seconds
            )
            
            # STEP_6: Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            # STEP_7: Estimate cost (rough calculation)
            cost_estimate = None
            if tokens_used and self.cfg_dict.get("cost_tracking", True):
                # Rough cost estimate for gpt-4o-mini (as of 2024)
                cost_per_1k_tokens = 0.0015  # Adjust based on actual model pricing
                cost_estimate = (tokens_used / 1000) * cost_per_1k_tokens
            
            self.logger.info("OpenAI request successful - tokens: %s, cost: $%.4f", 
                           tokens_used, cost_estimate or 0)
            
            return OpenAIResponse(
                success=True,
                data={"content": content, "raw_response": response},
                tokens_used=tokens_used,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            error_msg = f"OpenAI API request failed: {e}"
            self.logger.error(error_msg)
            return OpenAIResponse(success=False, error=error_msg)
    
    def _mock_openai_response(self) -> OpenAIResponse:
        """Generate mock response for testing without API calls.
        
        Returns:
            Mock OpenAI response
        """
        mock_yaml = """title: "Mock Recipe"
category: "Other"
description: "Generated by mock OpenAI client"
servings: 4
prep_time: "10 minutes"
cook_time: "15 minutes"

ingredients:
  - ingredient: "mock ingredient"
    amount: 1
    unit: "cup"
    weight_grams: 240
    purpose: "base"

instructions:
  - "This is a mock instruction generated for testing"

notes:
  - "Generated in mock mode - no real OpenAI API call made"
"""
        
        self.logger.info("Generated mock OpenAI response (no API key or mock mode enabled)")
        
        return OpenAIResponse(
            success=True,
            data={"content": mock_yaml, "raw_response": None},
            tokens_used=100,  # Mock token count
            cost_estimate=0.0001  # Mock cost
        )
    
    def parse_recipe_markdown(self, markdown_content: str) -> OpenAIResponse:
        """Parse markdown recipe content into structured YAML.
        
        Args:
            markdown_content: Raw markdown recipe text
            
        Returns:
            OpenAI response with parsed YAML data
        """
        try:
            # STEP_8: Check cache first
            cache_key = self._generate_cache_key(markdown_content, "recipe_parse")
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
            
            # STEP_9: Prepare the prompt (will be detailed in next task)
            system_prompt = self._get_recipe_parsing_prompt()
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please parse this recipe:\n\n{markdown_content}"}
            ]
            
            # STEP_10: Make request with retry logic
            max_retries = self.config.max_retries
            base_delay = self.config.retry_delay
            
            for attempt in range(1, max_retries + 1):
                response = self._make_openai_request(messages, attempt)
                
                if response.success:
                    # STEP_11: Cache successful response
                    self._cache_response(cache_key, response)
                    return response
                
                # STEP_12: Handle retry logic
                if attempt < max_retries:
                    delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
                    self.logger.warning("Request failed, retrying in %.1f seconds (attempt %d/%d)", 
                                      delay, attempt, max_retries)
                    time.sleep(delay)
                else:
                    self.logger.error("All retry attempts exhausted")
            
            return response  # Return the last failed response
            
        except Exception as e:
            error_msg = f"Recipe parsing failed: {e}"
            self.logger.exception(error_msg)
            return OpenAIResponse(success=False, error=error_msg)
    
    def _get_recipe_parsing_prompt(self) -> str:
        """Get the system prompt for recipe parsing.
        
        Returns:
            Comprehensive system prompt for markdown to YAML conversion
        """
        return """You are an expert recipe parsing assistant specializing in converting markdown recipes into structured YAML format for an AI-powered recipe card system.

## TASK
Convert the provided markdown recipe into valid YAML following the exact schema below. Pay careful attention to data types, unit standardization, and weight estimation.

## OUTPUT SCHEMA
```yaml
title: string (recipe name, max 100 characters)
category: string (must be one of: Meat, Side, Main, Soup, Sauce, Breakfast, Salad, Baking, Dessert, Other)
description: string (brief description from recipe intro, max 500 chars, optional)
servings: integer (number of servings, default 4 if not specified)
prep_time: string (e.g., "10 minutes", optional)
cook_time: string (e.g., "15 minutes", optional)

ingredients:
  - ingredient: string (ingredient name, cleaned and standardized)
    amount: number (numeric value only, convert fractions like "1 1/2" to 1.5)
    unit: string (standardized - see unit guide below)
    weight_grams: integer (estimated weight in grams for precision weighing)
    purpose: string (ingredient's role: base, seasoning, garnish, filling, etc.)

instructions:
  - string (each step as separate list item, clean and concise)

notes: (optional)
  - string (additional tips, storage info, variations)
```

## UNIT STANDARDIZATION GUIDE
- Tablespoons: "TBL" (convert tbsp, tablespoon, tablespoons)
- Teaspoons: "tsp" (convert t, teaspoon, teaspoons)
- Cups: "cups" (keep as-is)
- Pounds: "lbs" (convert lb, pound, pounds)
- Ounces: "oz" (convert ounce, ounces)
- Fluid ounces: "fl oz"
- Milliliters: "ml"
- Liters: "L"
- Grams: "g"
- Kilograms: "kg"
- Items/pieces: "count" (for "2 eggs", use amount: 2, unit: "count")

## WEIGHT ESTIMATION GUIDE (for weight_grams field)
Common ingredient weights per cup:
- All-purpose flour: 120g/cup
- White sugar: 200g/cup
- Brown sugar (packed): 220g/cup
- Butter: 225g/cup
- Milk: 240g/cup
- Water: 240g/cup
- Vegetable oil: 220g/cup
- Honey: 340g/cup
- Salt: 300g/cup
- Baking powder: 160g/cup

For tablespoons: divide cup weight by 16
For teaspoons: divide cup weight by 48
For other ingredients: use reasonable estimates based on density

## CATEGORY INFERENCE RULES
Analyze the recipe type and assign appropriate category:
- Breakfast: pancakes, waffles, eggs, cereals, breakfast breads
- Dessert: cookies, cakes, pies, ice cream, candy
- Baking: breads, muffins, pastries (non-dessert baked goods)
- Main: primary dinner dishes, pasta, stir-fries
- Meat: dishes where meat is the star ingredient
- Soup: all liquid-based dishes including stews
- Salad: fresh vegetable-based dishes
- Side: accompaniments, vegetables, rice dishes
- Sauce: condiments, dressings, gravies, salsas
- Other: anything that doesn't fit above categories

## INSTRUCTIONS PROCESSING
- Convert numbered/bulleted lists to clean array items
- Remove step numbers (convert "1. Mix flour" to "Mix flour")
- Keep instructions concise but complete
- Split complex steps if needed
- Preserve cooking temperatures and times

## NOTES EXTRACTION
Extract from "Notes", "Tips", "Variations" sections or recipe comments:
- Storage instructions
- Cooking tips
- Recipe variations
- Serving suggestions
- Make-ahead instructions

## DATA TYPE REQUIREMENTS
- amounts: MUST be numbers (float/int), never strings
- servings: MUST be integer
- weight_grams: MUST be integer (whole grams)
- Convert fractions to decimals (1/2 → 0.5, 1/4 → 0.25, 3/4 → 0.75)
- Handle mixed numbers (2 1/2 → 2.5)

## QUALITY STANDARDS
- Clean ingredient names (remove extra words like "fresh", "large" unless essential)
- Standardize measurements consistently
- Provide reasonable weight estimates for ALL ingredients
- Assign meaningful purpose categories
- Keep instructions actionable and clear
- Preserve important cooking details (temperatures, times, techniques)

## RESPONSE FORMAT
Return ONLY the YAML output. Do not include code blocks, explanations, or additional text. Start directly with the YAML content."""
    
    def validate_api_key(self) -> bool:
        """Validate that the OpenAI API key is working.
        
        Returns:
            True if API key is valid and working
        """
        if self.cfg_dict.get("mock_mode", False):
            self.logger.info("API key validation skipped - running in mock mode")
            return True
        
        if not self.config.api_key:
            self.logger.warning("No API key provided for validation")
            return False
        
        try:
            # Make a simple test request
            test_response = self.parse_recipe_markdown("# Test Recipe\n\nTest ingredient: 1 cup")
            
            if test_response.success:
                self.logger.info("API key validation successful")
                return True
            else:
                self.logger.error("API key validation failed: %s", test_response.error)
                return False
                
        except Exception as e:
            self.logger.exception("API key validation error: %s", e)
            return False
    
    def get_usage_stats(self) -> dict:
        """Get usage statistics for the client.
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            "cache_size": len(self._response_cache),
            "cache_enabled": self.cfg_dict.get("enable_caching", True),
            "mock_mode": self.cfg_dict.get("mock_mode", False),
            "model": self.config.model,
            "max_retries": self.config.max_retries
        }