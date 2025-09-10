"""CLI interface for nutrition enhancement.

Usage:
    python -m recipe_fmt.nutrition recipe.yaml
    python -m recipe_fmt.nutrition recipe/yaml/*.yaml
    python -m recipe_fmt.nutrition --help
"""

import argparse
import sys
from pathlib import Path

import yaml

from ..utils.logging_setup import get_logger
from .calculator import NutritionCalculator


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enhance YAML recipe files with nutrition information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhance single recipe
  python -m recipe_fmt.nutrition recipe.yaml
  
  # Enhance multiple recipes
  python -m recipe_fmt.nutrition recipe/yaml/*.yaml
  
  # Use custom API key
  python -m recipe_fmt.nutrition --api-key YOUR_KEY recipe.yaml
  
  # Dry run (show what would be calculated)
  python -m recipe_fmt.nutrition --dry-run recipe.yaml
        """,
    )

    parser.add_argument("files", nargs="+", help="YAML recipe files to enhance")

    parser.add_argument("--api-key", help="USDA API key (uses DEMO_KEY if not provided)")

    parser.add_argument("--dry-run", action="store_true", help="Show nutrition calculation without modifying files")

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    cfg_dict = {"log_level": "INFO" if args.verbose else "WARNING"}
    logger = get_logger(__name__, cfg_dict)

    try:
        # Initialize calculator
        calculator = NutritionCalculator(api_key=args.api_key, cfg_dict=cfg_dict)

        # Process files
        processed_files = []
        errors = []

        for file_pattern in args.files:
            file_path = Path(file_pattern)

            if file_path.exists():
                files_to_process = [file_path]
            else:
                # Handle glob patterns
                files_to_process = list(Path(".").glob(file_pattern))

            for yaml_file in files_to_process:
                if yaml_file.suffix.lower() not in [".yaml", ".yml"]:
                    logger.warning("Skipping non-YAML file: %s", yaml_file)
                    continue

                try:
                    if args.dry_run:
                        result = dry_run_nutrition(yaml_file, calculator)
                        print(f"\n📄 {yaml_file}")
                        print("=" * 50)
                        print(result)
                    else:
                        calculator.enhance_yaml_file(yaml_file)
                        processed_files.append(yaml_file)
                        print(f"✅ Enhanced: {yaml_file}")

                except Exception as e:
                    error_msg = f"❌ Error processing {yaml_file}: {e}"
                    errors.append(error_msg)
                    print(error_msg)

        # Summary
        if not args.dry_run:
            print("\n📊 Summary:")
            print(f"  Files processed: {len(processed_files)}")
            print(f"  Errors: {len(errors)}")

            # Cache stats
            stats = calculator.get_cache_stats()
            print(f"  Cached ingredients: {stats['cached_ingredients']}")
            print(f"  API key: {stats['api_key_type']}")

        if errors:
            print("\n❌ Errors encountered:")
            for error in errors:
                print(f"  {error}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)


def dry_run_nutrition(yaml_file: Path, calculator: NutritionCalculator) -> str:
    """Perform dry run nutrition calculation.

    Args:
        yaml_file: Path to YAML file
        calculator: NutritionCalculator instance

    Returns:
        Formatted nutrition information
    """
    with open(yaml_file, encoding="utf-8") as f:
        recipe_data = yaml.safe_load(f)

    # Calculate nutrition without modifying original
    enhanced_data = calculator.enhance_recipe(recipe_data.copy())
    nutrition = enhanced_data.get("nutrition", {}).get("per_serving", {})

    # Format output
    output = []
    output.append(f"Title: {recipe_data.get('title', 'Unknown')}")
    output.append(f"Servings: {recipe_data.get('servings', 1)}")
    output.append(f"Ingredients: {len(recipe_data.get('ingredients', []))}")
    output.append("")
    output.append("Nutrition per serving:")

    for key, value in nutrition.items():
        display_name = key.replace("_", " ").title()
        output.append(f"  {display_name}: {value}")

    output.append("")
    output.append("YAML format:")
    output.append("nutrition:")
    output.append("  per_serving:")
    for key, value in nutrition.items():
        output.append(f"    {key}: {value}")

    return "\n".join(output)


if __name__ == "__main__":
    main()
