"""OpenAI API response data for testing.

This module provides comprehensive mock OpenAI API responses that can be used
across all OpenAI client tests. Includes successful responses, error scenarios,
and edge cases for thorough testing coverage.
"""

from typing import Any
from unittest.mock import Mock

# Successful OpenAI Parse Response - Perfect Pancakes
SUCCESSFUL_PARSE_RESPONSE = {
    "raw_response": {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": """```yaml
title: "Perfect Pancakes"
category: "Breakfast"
description: "Fluffy buttermilk pancakes that are perfect for weekend mornings"
prep_time_minutes: 10
cook_time_minutes: 15
servings: 4
difficulty: "Easy"
ingredients:
  - ingredient: "all-purpose flour"
    amount: 2.0
    unit: "cups"
    weight_grams: 240
    purpose: "base"
  - ingredient: "granulated sugar"
    amount: 2.0
    unit: "TBL"
    weight_grams: 25
    purpose: "sweetening"
  - ingredient: "baking powder"
    amount: 2.0
    unit: "tsp"
    weight_grams: 8
    purpose: "leavening"
  - ingredient: "salt"
    amount: 1.0
    unit: "tsp"
    weight_grams: 5
    purpose: "flavor enhancement"
  - ingredient: "buttermilk"
    amount: 1.5
    unit: "cups"
    weight_grams: 360
    purpose: "liquid"
  - ingredient: "large eggs"
    amount: 2.0
    unit: "whole"
    weight_grams: 100
    purpose: "binding"
  - ingredient: "unsalted butter"
    amount: 4.0
    unit: "TBL"
    weight_grams: 56
    purpose: "fat"
instructions:
  - "In a large bowl, whisk together flour, sugar, baking powder, and salt."
  - "In a separate bowl, whisk buttermilk, eggs, and melted butter until combined."
  - "Pour wet ingredients into dry ingredients and stir until just combined. Don't overmix - lumps are okay."
  - "Heat a griddle or large skillet over medium heat. Lightly grease with butter or oil."
  - "Pour 1/4 cup batter for each pancake. Cook until bubbles form on surface and edges look set, about 2-3 minutes."
  - "Flip and cook until golden brown on other side, 1-2 minutes more."
  - "Serve immediately with butter and maple syrup."
notes:
  - "Don't overmix the batter - lumpy is good!"
  - "Keep cooked pancakes warm in 200°F oven"
tags:
  - "breakfast"
  - "pancakes"
  - "weekend"
  - "family-friendly"
source: "Family Recipe Collection"
```""",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 150, "completion_tokens": 420, "total_tokens": 570},
    },
    "parsed_yaml": {
        "title": "Perfect Pancakes",
        "category": "Breakfast",
        "description": "Fluffy buttermilk pancakes that are perfect for weekend mornings",
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient": "all-purpose flour",
                "amount": 2.0,
                "unit": "cups",
                "weight_grams": 240,
                "purpose": "base",
            },
            {
                "ingredient": "granulated sugar",
                "amount": 2.0,
                "unit": "TBL",
                "weight_grams": 25,
                "purpose": "sweetening",
            },
            {
                "ingredient": "baking powder",
                "amount": 2.0,
                "unit": "tsp",
                "weight_grams": 8,
                "purpose": "leavening",
            },
            {
                "ingredient": "salt",
                "amount": 1.0,
                "unit": "tsp",
                "weight_grams": 5,
                "purpose": "flavor enhancement",
            },
            {
                "ingredient": "buttermilk",
                "amount": 1.5,
                "unit": "cups",
                "weight_grams": 360,
                "purpose": "liquid",
            },
            {
                "ingredient": "large eggs",
                "amount": 2.0,
                "unit": "whole",
                "weight_grams": 100,
                "purpose": "binding",
            },
            {
                "ingredient": "unsalted butter",
                "amount": 4.0,
                "unit": "TBL",
                "weight_grams": 56,
                "purpose": "fat",
            },
        ],
        "instructions": [
            "In a large bowl, whisk together flour, sugar, baking powder, and salt.",
            "In a separate bowl, whisk buttermilk, eggs, and melted butter until combined.",
            "Pour wet ingredients into dry ingredients and stir until just combined. Don't overmix - lumps are okay.",
            "Heat a griddle or large skillet over medium heat. Lightly grease with butter or oil.",
            "Pour 1/4 cup batter for each pancake. Cook until bubbles form on surface and edges look set, 2-3 minutes.",
            "Flip and cook until golden brown on other side, 1-2 minutes more.",
            "Serve immediately with butter and maple syrup.",
        ],
        "notes": [
            "Don't overmix the batter - lumpy is good!",
            "Keep cooked pancakes warm in 200°F oven",
        ],
        "tags": ["breakfast", "pancakes", "weekend", "family-friendly"],
        "source": "Family Recipe Collection",
    },
    "tokens_used": 570,
    "cost_estimate": 0.0171,
}

# Error Response - API Rate Limit
ERROR_RATE_LIMIT_RESPONSE = {
    "error": {
        "message": "Rate limit reached for requests",
        "type": "rate_limit_error",
        "param": None,
        "code": None,
    },
    "status_code": 429,
}

# Error Response - Invalid API Key
ERROR_INVALID_KEY_RESPONSE = {
    "error": {
        "message": "Invalid API key provided",
        "type": "invalid_request_error",
        "param": None,
        "code": "invalid_api_key",
    },
    "status_code": 401,
}

# Error Response - Content Policy Violation
ERROR_CONTENT_POLICY_RESPONSE = {
    "error": {
        "message": "Your request was rejected as a result of our safety system",
        "type": "invalid_request_error",
        "param": None,
        "code": "content_policy_violation",
    },
    "status_code": 400,
}

# Error Response - Server Error
ERROR_SERVER_RESPONSE = {
    "error": {
        "message": "The server had an error while processing your request",
        "type": "server_error",
        "param": None,
        "code": None,
    },
    "status_code": 500,
}

# Partial Parse Response - Missing Some Fields
PARTIAL_PARSE_RESPONSE = {
    "raw_response": {
        "id": "chatcmpl-partial123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": """```yaml
title: "Incomplete Recipe"
category: "Other"
ingredients:
  - ingredient: "flour"
    amount: 2.0
    unit: "cups"
instructions:
  - "Mix ingredients"
  - "Cook until done"
```""",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180},
    },
    "parsed_yaml": {
        "title": "Incomplete Recipe",
        "category": "Other",
        "ingredients": [{"ingredient": "flour", "amount": 2.0, "unit": "cups"}],
        "instructions": ["Mix ingredients", "Cook until done"],
    },
    "tokens_used": 180,
    "cost_estimate": 0.0054,
}

# Malformed YAML Response
MALFORMED_YAML_RESPONSE = {
    "raw_response": {
        "id": "chatcmpl-malformed123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": """```yaml
title: "Malformed Recipe"
category: "Breakfast
ingredients:
  - ingredient: "flour
    amount: 2.0
    unit: "cups"
  - ingredient: "sugar"
    amount: invalid_number
    unit: "tsp"
instructions:
  - "This YAML is malformed"
  - "Missing closing quotes
```""",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 120, "completion_tokens": 95, "total_tokens": 215},
    },
    "yaml_error": "YAML parsing error: invalid syntax",
    "tokens_used": 215,
    "cost_estimate": 0.00645,
}

# Response with No YAML Markers
NO_YAML_MARKERS_RESPONSE = {
    "raw_response": {
        "id": "chatcmpl-nomarkers123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": (
                        "I'm sorry, but I cannot parse this recipe as it seems to be incomplete or malformed. "
                        "Please provide a properly formatted recipe with clear ingredients and instructions."
                    ),
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 80, "completion_tokens": 35, "total_tokens": 115},
    },
    "error": "No YAML content found in response",
    "tokens_used": 115,
    "cost_estimate": 0.00345,
}


# Very Large Response - For testing limits
def _build_large_recipe_content():
    """Build large recipe content to avoid long lines."""
    # Build ingredients list
    ingredients_list = []
    for i in range(1, 101):
        ingredient_entry = f'  - ingredient: "ingredient_{i}"\n    amount: {i}.0\n    unit: "unit_{i}"'
        ingredients_list.append(ingredient_entry)
    ingredients_yaml = chr(10).join(ingredients_list)

    # Build instructions list
    instructions_list = []
    for i in range(1, 151):
        instruction = (
            f'  - "Step {i}: Very detailed instruction with lots of explanation '
            f'about technique, timing, and what to look for during this step of the cooking process."'
        )
        instructions_list.append(instruction)
    instructions_yaml = chr(10).join(instructions_list)

    # Build notes and tags
    notes_yaml = chr(10).join([f'  - "Note {i}: Additional information and tips"' for i in range(1, 51)])
    tags_yaml = chr(10).join([f'  - "tag_{i}"' for i in range(1, 21)])

    return f"""```yaml
title: "Complex Multi-Course Meal"
category: "Other"
description: "A very complex recipe with many steps and ingredients"
prep_time_minutes: 180
cook_time_minutes: 240
servings: 20
difficulty: "Hard"
ingredients:
{ingredients_yaml}
instructions:
{instructions_yaml}
notes:
{notes_yaml}
tags:
{tags_yaml}
```"""


LARGE_RECIPE_RESPONSE = {
    "raw_response": {
        "id": "chatcmpl-large123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": _build_large_recipe_content(),
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 200, "completion_tokens": 4500, "total_tokens": 4700},
    },
    "tokens_used": 4700,
    "cost_estimate": 0.141,
}

# Response with Unicode Characters
UNICODE_RECIPE_RESPONSE = {
    "raw_response": {
        "id": "chatcmpl-unicode123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": """```yaml
title: "Café Français ☕"
category: "Breakfast"
description: "Traditional French café with crème"
prep_time_minutes: 5
cook_time_minutes: 3
servings: 2
difficulty: "Easy"
ingredients:
  - ingredient: "café noir"
    amount: 2.0
    unit: "tasses"
    weight_grams: 480
  - ingredient: "crème fraîche"
    amount: 50.0
    unit: "ml"
    weight_grams: 50
  - ingredient: "sucre blanc"
    amount: 2.0
    unit: "cuillères à café"
    weight_grams: 8
instructions:
  - "Chauffez l'eau à 85°C"
  - "Versez sur le café moulu"
  - "Laissez infuser 3 minutes ⏱️"
  - "Ajoutez la crème et le sucre selon goût"
notes:
  - "Température optimale: 85°C (185°F)"
  - "Utilisez des grains fraîchement moulus ☕"
tags:
  - "café"
  - "français"
  - "petit-déjeuner"
  - "boisson"
source: "Café de Paris"
```""",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 120, "completion_tokens": 280, "total_tokens": 400},
    },
    "parsed_yaml": {
        "title": "Café Français ☕",
        "category": "Breakfast",
        "description": "Traditional French café with crème",
        "prep_time_minutes": 5,
        "cook_time_minutes": 3,
        "servings": 2,
        "difficulty": "Easy",
        "ingredients": [
            {"ingredient": "café noir", "amount": 2.0, "unit": "tasses", "weight_grams": 480},
            {"ingredient": "crème fraîche", "amount": 50.0, "unit": "ml", "weight_grams": 50},
            {
                "ingredient": "sucre blanc",
                "amount": 2.0,
                "unit": "cuillères à café",
                "weight_grams": 8,
            },
        ],
        "instructions": [
            "Chauffez l'eau à 85°C",
            "Versez sur le café moulu",
            "Laissez infuser 3 minutes ⏱️",
            "Ajoutez la crème et le sucre selon goût",
        ],
        "notes": [
            "Température optimale: 85°C (185°F)",
            "Utilisez des grains fraîchement moulus ☕",
        ],
        "tags": ["café", "français", "petit-déjeuner", "boisson"],
        "source": "Café de Paris",
    },
    "tokens_used": 400,
    "cost_estimate": 0.012,
}

# Collection of all mock responses
ALL_MOCK_RESPONSES = {
    "successful_parse": SUCCESSFUL_PARSE_RESPONSE,
    "error_rate_limit": ERROR_RATE_LIMIT_RESPONSE,
    "error_invalid_key": ERROR_INVALID_KEY_RESPONSE,
    "error_content_policy": ERROR_CONTENT_POLICY_RESPONSE,
    "error_server": ERROR_SERVER_RESPONSE,
    "partial_parse": PARTIAL_PARSE_RESPONSE,
    "malformed_yaml": MALFORMED_YAML_RESPONSE,
    "no_yaml_markers": NO_YAML_MARKERS_RESPONSE,
    "large_recipe": LARGE_RECIPE_RESPONSE,
    "unicode_recipe": UNICODE_RECIPE_RESPONSE,
}


def create_mock_openai_response(
    content: str, tokens_used: int = 100, model: str = "gpt-4", finish_reason: str = "stop"
) -> Mock:
    """Create a mock OpenAI response object.

    Args:
        content: The response content
        tokens_used: Number of tokens used
        model: Model name used
        finish_reason: Finish reason for the response

    Returns:
        Mock OpenAI response object
    """
    mock_response = Mock()
    mock_response.id = f"chatcmpl-mock{hash(content) % 10000}"
    mock_response.object = "chat.completion"
    mock_response.created = 1677652288
    mock_response.model = model

    # Mock choices
    mock_choice = Mock()
    mock_choice.index = 0
    mock_choice.finish_reason = finish_reason

    # Mock message
    mock_message = Mock()
    mock_message.role = "assistant"
    mock_message.content = content
    mock_choice.message = mock_message

    mock_response.choices = [mock_choice]

    # Mock usage
    mock_usage = Mock()
    mock_usage.prompt_tokens = max(10, tokens_used // 4)
    mock_usage.completion_tokens = tokens_used - mock_usage.prompt_tokens
    mock_usage.total_tokens = tokens_used
    mock_response.usage = mock_usage

    return mock_response


def create_mock_error_response(error_message: str, error_type: str = "api_error", status_code: int = 500) -> Exception:
    """Create a mock OpenAI error response.

    Args:
        error_message: Error message
        error_type: Type of error
        status_code: HTTP status code

    Returns:
        Exception that mimics OpenAI errors
    """
    from openai import APIError

    error = APIError(error_message)
    error.status_code = status_code
    error.type = error_type
    return error


def get_mock_response_by_content_type(content_type: str) -> dict[str, Any]:
    """Get mock response by content type for testing different scenarios.

    Args:
        content_type: Type of content to mock

    Returns:
        Mock response data dictionary

    Raises:
        KeyError: If content type not found
    """
    if content_type not in ALL_MOCK_RESPONSES:
        raise KeyError(f"Mock response type '{content_type}' not found. Available: {list(ALL_MOCK_RESPONSES.keys())}")

    return ALL_MOCK_RESPONSES[content_type]


def create_retry_sequence_responses(
    failure_count: int, final_success: bool = True, error_type: str = "rate_limit_error"
) -> list[Any]:
    """Create a sequence of responses for testing retry logic.

    Args:
        failure_count: Number of failures before success
        final_success: Whether final attempt should succeed
        error_type: Type of error for failures

    Returns:
        List of mock responses/exceptions
    """
    responses = []

    # Add failure responses
    for i in range(failure_count):
        if error_type == "rate_limit_error":
            responses.append(create_mock_error_response("Rate limit reached", "rate_limit_error", 429))
        elif error_type == "server_error":
            responses.append(create_mock_error_response("Server error", "server_error", 500))
        else:
            responses.append(create_mock_error_response(f"API error {i}", error_type, 400))

    # Add final response
    if final_success:
        responses.append(
            create_mock_openai_response(
                SUCCESSFUL_PARSE_RESPONSE["raw_response"]["choices"][0]["message"]["content"], 570
            )
        )
    else:
        responses.append(create_mock_error_response("Final failure", "api_error", 500))

    return responses


def create_caching_test_responses() -> dict[str, Mock]:
    """Create responses specifically for testing caching behavior.

    Returns:
        Dictionary of mock responses for caching tests
    """
    # Same content but different response objects to test caching
    content = SUCCESSFUL_PARSE_RESPONSE["raw_response"]["choices"][0]["message"]["content"]

    return {
        "first_request": create_mock_openai_response(content, 570, "gpt-4"),
        "cache_hit": create_mock_openai_response(content, 570, "gpt-4"),
        "different_content": create_mock_openai_response(
            PARTIAL_PARSE_RESPONSE["raw_response"]["choices"][0]["message"]["content"], 180, "gpt-4"
        ),
    }


def create_cost_calculation_responses() -> list[dict[str, Any]]:
    """Create responses with different token counts for cost calculation testing.

    Returns:
        List of response data for cost testing
    """
    return [
        {
            "tokens": 100,
            "expected_cost": 0.003,
            "response": create_mock_openai_response("Short response", 100),
        },
        {
            "tokens": 1000,
            "expected_cost": 0.03,
            "response": create_mock_openai_response("Medium response", 1000),
        },
        {
            "tokens": 5000,
            "expected_cost": 0.15,
            "response": create_mock_openai_response("Long response", 5000),
        },
    ]


def create_markdown_input_samples() -> dict[str, str]:
    """Create sample markdown inputs for testing different parsing scenarios.

    Returns:
        Dictionary of markdown content samples
    """
    return {
        "simple_recipe": """# Simple Pancakes
## Ingredients
- 2 cups flour
- 1 cup milk
## Instructions
1. Mix ingredients
2. Cook on griddle
""",
        "complex_recipe": """# Complex Beef Wellington
*An elegant dish for special occasions*

**Category:** Meat
**Prep Time:** 60 minutes
**Cook Time:** 45 minutes
**Servings:** 8
**Difficulty:** Hard

## Ingredients
- 2 pounds beef tenderloin
- 1 sheet puff pastry
- 8 oz mushroom duxelles
- 4 slices prosciutto
- 2 TBL Dijon mustard

## Instructions
1. Season beef and sear on all sides
2. Brush with mustard and cool completely
3. Wrap in prosciutto and mushroom mixture
4. Enclose in puff pastry
5. Bake at 400°F for 25-30 minutes

## Notes
- Use meat thermometer for doneness
- Rest 10 minutes before slicing
""",
        "malformed_recipe": """# Incomplete Recipe
## Ingredients
- flour
-
## Instructions
1. Mix
2.
""",
        "empty_content": "",
        "no_ingredients": """# Recipe Without Ingredients
## Instructions
1. Do something
2. Do something else
""",
        "no_instructions": """# Recipe Without Instructions
## Ingredients
- 2 cups flour
- 1 cup milk
""",
        "unicode_recipe": """# Café au Lait ☕
*Boisson française traditionnelle*

## Ingrédients
- 1 tasse café fort
- ½ tasse lait chaud
- 1 cuillère à café sucre

## Instructions
1. Préparez le café à 85°C
2. Chauffez le lait sans bouillir
3. Mélangez délicatement
""",
    }


# Export commonly used test data
__all__ = [
    "SUCCESSFUL_PARSE_RESPONSE",
    "ERROR_RATE_LIMIT_RESPONSE",
    "ERROR_INVALID_KEY_RESPONSE",
    "ERROR_CONTENT_POLICY_RESPONSE",
    "ERROR_SERVER_RESPONSE",
    "PARTIAL_PARSE_RESPONSE",
    "MALFORMED_YAML_RESPONSE",
    "NO_YAML_MARKERS_RESPONSE",
    "LARGE_RECIPE_RESPONSE",
    "UNICODE_RECIPE_RESPONSE",
    "ALL_MOCK_RESPONSES",
    "create_mock_openai_response",
    "create_mock_error_response",
    "get_mock_response_by_content_type",
    "create_retry_sequence_responses",
    "create_caching_test_responses",
    "create_cost_calculation_responses",
    "create_markdown_input_samples",
]
