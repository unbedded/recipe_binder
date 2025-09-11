"""Example usage of test fixtures and sample data.

This module demonstrates how to use the test fixtures and sample data
across different testing scenarios. It serves as both documentation
and as a validation that all fixtures work correctly together.

Run this script to see the fixtures in action:
    python -m tests.fixtures.example_usage
"""

import sys
from pathlib import Path

# Import fixtures and sample data
from tests.fixtures import (
    DEFAULT_CARD_TEMPLATE,
    SAMPLE_PANCAKES,
    SUCCESSFUL_PARSE_RESPONSE,
    FileSystemTestHelper,
    MockFileSystem,
    cleanup_temp_files,
    create_temp_recipe_files,
)
from tests.fixtures.openai_responses import (
    create_markdown_input_samples,
    create_mock_openai_response,
    create_retry_sequence_responses,
    get_mock_response_by_content_type,
)
from tests.fixtures.sample_recipes import (
    create_test_recipe_variations,
    get_sample_markdown,
    get_sample_recipe,
)
from tests.fixtures.template_data import (
    create_template_variations,
    get_invalid_template_names,
    get_template_data,
    get_valid_template_names,
)


def demonstrate_sample_recipes():
    """Demonstrate sample recipe usage."""
    print("=== Sample Recipes Demo ===")

    # Access predefined sample recipes
    pancakes = SAMPLE_PANCAKES
    print(f"Recipe: {pancakes.title}")
    print(f"Category: {pancakes.category}")
    print(f"Ingredients: {len(pancakes.ingredients)}")
    print(f"Instructions: {len(pancakes.instructions)}")

    # Get recipe by name
    beef_stew = get_sample_recipe("beef_stew")
    print(f"\nRecipe by name: {beef_stew.title}")
    print(f"Prep time: {beef_stew.prep_time_minutes} min")
    print(f"Cook time: {beef_stew.cook_time_minutes} min")

    # Get markdown content
    pancakes_md = get_sample_markdown("pancakes")
    print("\nMarkdown preview (first 100 chars):")
    print(pancakes_md[:100] + "...")

    # Create recipe variations for testing
    variations = create_test_recipe_variations()
    print(f"\nCreated {len(variations)} recipe variations for testing")

    # Test different categories
    categories = {recipe.category for recipe in variations}
    print(f"Categories covered: {', '.join(sorted(categories))}")

    print()


def demonstrate_template_data():
    """Demonstrate template data usage."""
    print("=== Template Data Demo ===")

    # Access predefined templates
    default_template = DEFAULT_CARD_TEMPLATE
    print(f"Template: {default_template['template_info']['name']}")
    print(f"Version: {default_template['template_info']['version']}")
    print(f"Card size: {default_template['card']['size']['width']}x{default_template['card']['size']['height']}")

    # Get template by name
    compact_template = get_template_data("compact_card")
    width = compact_template["card"]["size"]["width"]
    height = compact_template["card"]["size"]["height"]
    print(f"\nCompact template dimensions: {width}x{height}")

    # List valid and invalid template names
    valid_names = get_valid_template_names()
    invalid_names = get_invalid_template_names()
    print(f"\nValid templates: {len(valid_names)}")
    print(f"Invalid templates (for error testing): {len(invalid_names)}")

    # Create template variations
    variations = create_template_variations()
    print(f"\nTemplate variations created: {len(variations)}")

    # Example: different card sizes
    size_variations = [var for name, var in variations.items() if name.startswith("size_")]
    print(f"Size variations: {len(size_variations)}")
    for i, var in enumerate(size_variations[:3]):  # Show first 3
        size = var["card"]["size"]
        print(f"  Size {i + 1}: {size['width']}x{size['height']}")

    print()


def demonstrate_openai_responses():
    """Demonstrate OpenAI response mocking."""
    print("=== OpenAI Response Mocking Demo ===")

    # Access predefined responses
    success_response = SUCCESSFUL_PARSE_RESPONSE
    print(f"Success response tokens: {success_response['tokens_used']}")
    print(f"Success response cost: ${success_response['cost_estimate']}")

    # Get response by type
    error_response = get_mock_response_by_content_type("error_rate_limit")
    print(f"Error response status: {error_response['status_code']}")
    print(f"Error message: {error_response['error']['message']}")

    # Create custom mock response
    custom_response = create_mock_openai_response("Custom test content", tokens_used=150)
    print(f"\nCustom response model: {custom_response.model}")
    print(f"Custom response tokens: {custom_response.usage.total_tokens}")

    # Create retry sequence
    retry_responses = create_retry_sequence_responses(failure_count=3, final_success=True)
    print(f"\nRetry sequence created: {len(retry_responses)} responses")
    print(f"Failures + final success: {len(retry_responses) - 1} + 1")

    # Markdown input samples
    markdown_samples = create_markdown_input_samples()
    print(f"\nMarkdown samples: {len(markdown_samples)}")
    for name in list(markdown_samples.keys())[:3]:  # Show first 3
        content = markdown_samples[name]
        print(f"  {name}: {len(content)} characters")

    print()


def demonstrate_file_operations():
    """Demonstrate file system operations."""
    print("=== File System Operations Demo ===")

    # Create temporary recipe files
    recipe_files = {
        "pancakes.md": get_sample_markdown("pancakes"),
        "beef_stew.md": get_sample_markdown("beef_stew"),
        "test_recipe.md": "# Simple Test Recipe\n## Ingredients\n- flour\n## Instructions\n1. Mix",
    }

    temp_files = create_temp_recipe_files(recipe_files)
    print(f"Created {len(temp_files)} temporary recipe files")

    # Use FileSystemTestHelper
    helper = FileSystemTestHelper()

    for filename, filepath in temp_files.items():
        print(f"  {filename}: {filepath}")
        helper.assert_file_exists(filepath)

        # Check file content
        if filename == "test_recipe.md":
            helper.assert_file_content_equals(filepath, recipe_files[filename])
            print("    Content verified ✓")

    # Cleanup
    cleanup_temp_files(temp_files)
    print("Temporary files cleaned up")

    print()


def demonstrate_mock_file_system():
    """Demonstrate MockFileSystem usage."""
    print("=== Mock File System Demo ===")

    with MockFileSystem() as fs:
        print(f"Mock file system created at: {fs.base_path}")

        # Create sample files
        sample_files = fs.create_sample_files()

        print("Sample files created:")
        for category, files in sample_files.items():
            print(f"  {category}: {len(files)} files")

        # Show directory structure
        structure = fs.get_directory_structure()
        print("\nDirectory structure:")
        for directory, files in structure.items():
            print(f"  {directory}/: {len(files)} files")
            for filename in files[:3]:  # Show first 3
                print(f"    - {filename}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")

        # Create staleness test files
        staleness_files = fs.create_staleness_test_files()
        print("\nStaleness test files created:")
        for scenario, file_info in staleness_files.items():
            print(f"  {scenario}: {len(file_info)} files")

        # Create error scenario files
        error_files = fs.create_error_scenario_files()
        print(f"\nError scenario files: {len(error_files)}")
        for scenario, filepath in error_files.items():
            print(f"  {scenario}: {filepath.name}")

    print("Mock file system automatically cleaned up")
    print()


def demonstrate_integration_scenarios():
    """Demonstrate complex integration testing scenarios."""
    print("=== Integration Scenarios Demo ===")

    # Recipe processing pipeline simulation
    print("1. Recipe Processing Pipeline:")

    # Start with markdown
    markdown_content = get_sample_markdown("pancakes")
    print(f"   Input: Markdown ({len(markdown_content)} chars)")

    # Mock OpenAI parsing
    openai_response = SUCCESSFUL_PARSE_RESPONSE
    print(f"   OpenAI: Parsed successfully ({openai_response['tokens_used']} tokens)")

    # Template selection
    template = get_template_data("default_card")
    print(f"   Template: {template['template_info']['name']}")

    # Final output simulation
    print("   Output: PDF card (8.5x4 inch)")

    print("\n2. Error Handling Scenarios:")

    # Test different error scenarios
    error_scenarios = [
        ("rate_limit", "OpenAI API rate limit"),
        ("malformed_yaml", "Invalid YAML response"),
        ("invalid_template", "Template validation error"),
        ("file_permission", "File access error"),
    ]

    for scenario, description in error_scenarios:
        print(f"   {scenario}: {description}")

    print("\n3. Performance Testing Scenarios:")

    # Batch processing simulation
    batch_sizes = [1, 10, 100, 1000]
    for size in batch_sizes:
        estimated_time = size * 0.5  # Mock timing
        print(f"   Batch size {size}: ~{estimated_time:.1f} seconds")

    print()


def demonstrate_parameterized_testing():
    """Demonstrate parameterized testing scenarios."""
    print("=== Parameterized Testing Demo ===")

    # Recipe categories
    categories = ["Breakfast", "Meat", "Dessert", "Vegetarian", "Seafood"]
    print(f"Recipe categories for testing: {len(categories)}")
    for cat in categories:
        print(f"  - {cat}")

    # Card dimensions
    dimensions = [
        ("business", 3.5, 2.5),
        ("index", 6.0, 4.0),
        ("standard", 8.5, 4.0),
        ("large", 11.0, 8.5),
    ]
    print(f"\nCard dimensions for testing: {len(dimensions)}")
    for name, width, height in dimensions:
        print(f"  - {name}: {width}x{height}")

    # Font sizes
    font_sizes = [6, 8, 10, 12, 14, 16, 18, 20]
    print(f"\nFont sizes for testing: {len(font_sizes)}")
    print(f"  Range: {min(font_sizes)}-{max(font_sizes)} pt")

    # Error conditions
    error_conditions = [
        "empty_file",
        "malformed_yaml",
        "missing_ingredients",
        "invalid_template",
        "api_error",
    ]
    print(f"\nError conditions for testing: {len(error_conditions)}")
    for condition in error_conditions:
        print(f"  - {condition}")

    print()


def main():
    """Run all demonstrations."""
    # Add project root to path for imports
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    print("Recipe Binder Test Fixtures Demo")
    print("=" * 40)

    try:
        demonstrate_sample_recipes()
        demonstrate_template_data()
        demonstrate_openai_responses()
        demonstrate_file_operations()
        demonstrate_mock_file_system()
        demonstrate_integration_scenarios()
        demonstrate_parameterized_testing()

        print("✅ All demonstrations completed successfully!")
        print("\nThe test fixtures are ready for use across the test suite.")
        print("\nKey benefits:")
        print("- Consistent test data across all test modules")
        print("- Reduced test setup duplication")
        print("- Comprehensive edge case and error scenario coverage")
        print("- Easy parameterized testing with realistic data")
        print("- Mock file system for isolated testing")
        print("- OpenAI API mocking for reliable tests")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
