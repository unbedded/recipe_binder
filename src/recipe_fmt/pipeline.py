"""Main recipe processing pipeline orchestrator.

This module coordinates the recipe pipeline: YAML → PDF.
It processes YAML recipe files and generates formatted PDF cards.

Example usage:
    # Command line usage
    python -m recipe_fmt.pipeline

    # Programmatic usage
    from recipe_fmt.pipeline import RecipePipeline

    pipeline = RecipePipeline()
    results = pipeline.run()
"""

import argparse
import logging
import sys
from pathlib import Path

from .models import AppConfig
from .utils.file_manager import FileManager


class RecipePipeline:
    """Main pipeline orchestrator for recipe processing."""

    def __init__(self, config: AppConfig | None = None) -> None:
        """Initialize the recipe pipeline.

        Args:
            config: Application configuration. If None, loads from environment.
        """
        # STEP_1: Initialize logging first
        self.logger = logging.getLogger(__name__)

        # STEP_2: Configuration management
        self.config = config or AppConfig()
        self.file_manager = FileManager(self._get_file_manager_config())

        self.logger.info("RecipePipeline initialized with config")

    def _get_file_manager_config(self) -> dict:
        """Extract file manager configuration from main config.

        Returns:
            Configuration dictionary for FileManager
        """
        return {
            "recipe_dir": "recipe",
            "markdown_subdir": "markdown",
            "yaml_subdir": "yaml",
            "pdf_subdir": "pdf",
            "templates_subdir": "templates",
            "force_rebuild": False,
            "verbose_logging": self.config.debug,
        }

    def run(self, force_rebuild: bool = False, demo_mode: bool = False, specific_files: list = None) -> dict:
        """Run the complete recipe processing pipeline.

        Args:
            force_rebuild: If True, rebuild all files regardless of staleness
            demo_mode: If True, run with demo recipes and settings
            specific_files: If provided, only process these YAML files

        Returns:
            Dictionary with processing results and statistics
        """
        results = {
            "processed_files": {"markdown_to_yaml": [], "yaml_to_pdf": []},
            "errors": [],
            "total_processed": 0,
            "success": False,
            "metrics": {
                "total_tokens_used": 0,
                "total_cost_estimate": 0.0,
                "cached_responses": 0,
                "total_pdf_pages": 0,
                "total_pdf_size_bytes": 0,
            },
        }

        try:
            self.logger.info("Starting recipe pipeline (force_rebuild=%s, demo=%s)", force_rebuild, demo_mode)

            # STEP_3: Ensure directories exist
            if not self.file_manager.ensure_directories_exist():
                error_msg = "Failed to create required directories"
                self.logger.error(error_msg)
                results["errors"].append(error_msg)
                return results

            # STEP_4: Update file manager config if force rebuild
            if force_rebuild:
                current_config = self.file_manager.get_cfg()
                current_config["force_rebuild"] = True
                self.file_manager = FileManager(current_config)
                self.logger.info("Enabled force rebuild mode")

            # STEP_5: Handle demo mode
            if demo_mode:
                return self._run_demo_mode()

            # STEP_6: Get files that need processing
            if specific_files:
                # Process only specified files (convert paths to Path objects)
                from pathlib import Path

                yaml_files = [Path(f) for f in specific_files if f.endswith(".yaml")]
                md_files = [Path(f) for f in specific_files if f.endswith(".md")]
                stale_files = {"markdown_to_yaml": md_files, "yaml_to_pdf": yaml_files}
                self.logger.info(
                    "Processing %d specific files (%d MD, %d YAML)",
                    len(specific_files),
                    len(md_files),
                    len(yaml_files),
                )
            else:
                # Process all stale files
                stale_files = self.file_manager.get_stale_pipeline_files()

            if not stale_files["markdown_to_yaml"] and not stale_files["yaml_to_pdf"]:
                self.logger.info("No files need processing - all up to date")
                results["success"] = True
                return results

            # STEP_7: Process markdown -> YAML conversions
            for md_file in stale_files["markdown_to_yaml"]:
                try:
                    yaml_result = self._process_markdown_to_yaml(md_file)
                    if yaml_result["success"]:
                        results["processed_files"]["markdown_to_yaml"].append(str(md_file))
                        results["total_processed"] += 1

                        # Track OpenAI metrics
                        results["metrics"]["total_tokens_used"] += yaml_result.get("tokens_used", 0)
                        results["metrics"]["total_cost_estimate"] += yaml_result.get("cost_estimate", 0.0)
                        if yaml_result.get("cached", False):
                            results["metrics"]["cached_responses"] += 1
                    else:
                        results["errors"].extend(yaml_result["errors"])

                except Exception as e:
                    error_msg = f"Failed to process {md_file}: {e}"
                    self.logger.exception(error_msg)
                    results["errors"].append(error_msg)

            # STEP_8: Process YAML -> PDF conversions
            for yaml_file in stale_files["yaml_to_pdf"]:
                try:
                    pdf_result = self._process_yaml_to_pdf(yaml_file)
                    if pdf_result["success"]:
                        results["processed_files"]["yaml_to_pdf"].append(str(yaml_file))
                        results["total_processed"] += 1

                        # Track PDF metrics
                        results["metrics"]["total_pdf_pages"] += pdf_result.get("pages_generated", 0)
                        results["metrics"]["total_pdf_size_bytes"] += pdf_result.get("file_size", 0)
                    else:
                        results["errors"].extend(pdf_result["errors"])

                except Exception as e:
                    error_msg = f"Failed to process {yaml_file}: {e}"
                    self.logger.exception(error_msg)
                    results["errors"].append(error_msg)

            # STEP_9: Determine overall success
            results["success"] = len(results["errors"]) == 0

            # STEP_10: Log comprehensive results
            metrics = results["metrics"]
            self.logger.info(
                "Pipeline completed: %d files processed, %d errors",
                results["total_processed"],
                len(results["errors"]),
            )

            if metrics["total_tokens_used"] > 0:
                self.logger.info(
                    "OpenAI usage: %d tokens, $%.4f, %d cached responses",
                    metrics["total_tokens_used"],
                    metrics["total_cost_estimate"],
                    metrics["cached_responses"],
                )

            if metrics["total_pdf_pages"] > 0:
                self.logger.info(
                    "PDF generation: %d pages, %.1f MB total",
                    metrics["total_pdf_pages"],
                    metrics["total_pdf_size_bytes"] / (1024 * 1024),
                )

            return results

        except Exception as e:
            error_msg = f"Pipeline failed with unexpected error: {e}"
            self.logger.exception(error_msg)
            results["errors"].append(error_msg)
            return results

    def _process_markdown_to_yaml(self, md_file: Path) -> dict:
        """Process a single markdown file to YAML using OpenAI.

        Args:
            md_file: Path to markdown file

        Returns:
            Processing result dictionary
        """
        result = {"success": False, "errors": [], "tokens_used": 0, "cost_estimate": 0.0}

        try:
            self.logger.info("Processing markdown to YAML: %s", md_file)

            # STEP_10: Import parser components
            from .parsers.markdown_parser import create_parser_from_env
            from .validators.yaml_validator import create_validator

            # STEP_11: Create parser and validator
            parser = create_parser_from_env({"validate_yaml": True})
            validator = create_validator(strict=True, check_weights=True)

            # STEP_12: Parse markdown to YAML
            parse_result = parser.parse_recipe_file(md_file)

            if not parse_result.success:
                result["errors"].append(f"OpenAI parsing failed: {parse_result.error}")
                return result

            # STEP_13: Get corresponding YAML file path
            yaml_file = self.file_manager.get_corresponding_yaml_path(md_file)
            yaml_file.parent.mkdir(parents=True, exist_ok=True)

            # STEP_14: Validate parsed YAML
            if parse_result.yaml_content:
                validation_result = validator.validate_yaml_content(parse_result.yaml_content, f"parsed_{md_file.name}")

                if not validation_result.valid:
                    error_details = [f"{e.field}: {e.message}" for e in validation_result.errors]
                    result["errors"].append(f"YAML validation failed: {'; '.join(error_details)}")
                    return result

                # Log validation warnings
                for warning in validation_result.warnings:
                    self.logger.warning(
                        "YAML validation warning for %s [%s]: %s",
                        md_file.name,
                        warning.field,
                        warning.message,
                    )

            # STEP_15: Write validated YAML file
            yaml_file.write_text(parse_result.yaml_content)

            # STEP_16: Log success with metrics
            self.logger.info("Successfully processed %s → %s", md_file.name, yaml_file.name)
            if parse_result.tokens_used:
                self.logger.info(
                    "OpenAI usage: %d tokens, $%.4f",
                    parse_result.tokens_used,
                    parse_result.cost_estimate or 0,
                )

            result["success"] = True
            result["tokens_used"] = parse_result.tokens_used or 0
            result["cost_estimate"] = parse_result.cost_estimate or 0.0
            result["cached"] = parse_result.cached

        except Exception as e:
            error_msg = f"Failed to process markdown {md_file}: {e}"
            self.logger.exception(error_msg)
            result["errors"].append(error_msg)

        return result

    def _process_yaml_to_pdf(self, yaml_file: Path) -> dict:
        """Process a single YAML file to PDF using the template system.

        Args:
            yaml_file: Path to YAML file

        Returns:
            Processing result dictionary
        """
        result = {"success": False, "errors": [], "pages_generated": 0, "file_size": 0}

        try:
            self.logger.info("Processing YAML to PDF: %s", yaml_file)

            # STEP_17: Import PDF generation components

            from .templates.template_loader import create_loader
            from .validators.yaml_validator import create_validator

            # STEP_18: Load and validate YAML
            validator = create_validator(strict=False, check_weights=True)
            validation_result = validator.validate_yaml_file(yaml_file)

            if not validation_result.valid:
                error_details = [f"{e.field}: {e.message}" for e in validation_result.errors]
                result["errors"].append(f"YAML validation failed: {'; '.join(error_details)}")
                return result

            # Log validation warnings
            for warning in validation_result.warnings:
                self.logger.warning(
                    "YAML validation warning for %s [%s]: %s",
                    yaml_file.name,
                    warning.field,
                    warning.message,
                )

            recipe = validation_result.recipe
            if not recipe:
                result["errors"].append("Failed to create Recipe object from YAML")
                return result

            # STEP_19: Create PDF generator with template
            template_loader = create_loader()

            try:
                generator = template_loader.create_generator(
                    "default-card.yaml",
                    show_weights=self.config.display.show_weights if hasattr(self.config, "display") else True,
                )
            except Exception as e:
                self.logger.warning("Failed to load template, using default generator: %s", e)
                from .generators.pdf_generator import create_generator

                generator = create_generator(show_weights=True)

            # STEP_20: Determine PDF file path with category prefix
            category = recipe.category
            pdf_file = self.file_manager.get_corresponding_pdf_path(yaml_file, category)
            pdf_file.parent.mkdir(parents=True, exist_ok=True)

            # STEP_21: Generate PDF
            generation_result = generator.generate_card(recipe, pdf_file)

            if not generation_result.success:
                result["errors"].append(f"PDF generation failed: {generation_result.error}")
                return result

            # STEP_22: Log success with metrics
            self.logger.info("Successfully generated PDF: %s → %s", yaml_file.name, pdf_file.name)
            self.logger.info(
                "PDF stats: %d pages, %d bytes",
                generation_result.pages_generated,
                generation_result.file_size_bytes or 0,
            )

            result["success"] = True
            result["pages_generated"] = generation_result.pages_generated
            result["file_size"] = generation_result.file_size_bytes or 0
            result["output_path"] = str(pdf_file)

        except Exception as e:
            error_msg = f"Failed to process YAML {yaml_file}: {e}"
            self.logger.exception(error_msg)
            result["errors"].append(error_msg)

        return result

    def _run_demo_mode(self) -> dict:
        """Run pipeline in demo mode with sample data.

        Returns:
            Demo processing results
        """
        self.logger.info("Running pipeline in demo mode")

        # For now, just process existing sample recipes
        return self.run(force_rebuild=True)

    def clean(self, file_types: list[str] = None) -> dict:
        """Clean generated files from the pipeline.

        Args:
            file_types: File types to clean ('yaml', 'pdf'). Default: ['pdf']

        Returns:
            Cleaning results
        """
        try:
            files_cleaned = self.file_manager.clean_generated_files(file_types)

            self.logger.info("Cleaned %d files", files_cleaned)

            return {"success": True, "files_cleaned": files_cleaned, "errors": []}

        except Exception as e:
            error_msg = f"Failed to clean files: {e}"
            self.logger.exception(error_msg)
            return {"success": False, "files_cleaned": 0, "errors": [error_msg]}


def setup_logging(log_level: str = "WARNING") -> None:
    """Setup logging configuration for the pipeline.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("recipe_pipeline.log", mode="a")],
    )


def main() -> int:
    """Main entry point for command-line usage.

    Returns:
        Exit code: 0 for success, 1 for failure
    """
    parser = argparse.ArgumentParser(description="Recipe Binder - AI-Powered Recipe Card Pipeline")

    parser.add_argument("--force", "-f", action="store_true", help="Force rebuild all files regardless of staleness")

    parser.add_argument("--demo", "-d", action="store_true", help="Run in demo mode with sample recipes")

    parser.add_argument("--clean", "-c", action="store_true", help="Clean generated PDF files")

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (equivalent to --log-level INFO)",
    )

    parser.add_argument(
        "--log-level",
        "-l",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )

    parser.add_argument("--md-to-yaml", action="store_true", help="Convert markdown file to YAML")

    parser.add_argument("--yaml-to-pdf", action="store_true", help="Convert YAML file to PDF")

    parser.add_argument("files", nargs="*", help="Specific recipe files to process")

    args = parser.parse_args()

    # Handle verbose flag
    if args.verbose:
        args.log_level = "INFO"

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = AppConfig()
        config.log_level = args.log_level

        # Initialize pipeline
        pipeline = RecipePipeline(config)

        # Handle clean operation
        if args.clean:
            clean_result = pipeline.clean()
            if clean_result["success"]:
                print(f"✅ Cleaned {clean_result['files_cleaned']} files")
                return 0
            else:
                print(f"❌ Clean failed: {clean_result['errors']}")
                return 1

        # Determine specific files based on processing mode
        specific_files = None
        if args.md_to_yaml or args.yaml_to_pdf:
            if not args.files:
                print("❌ Error: Must specify files when using --md-to-yaml or --yaml-to-pdf")
                return 1
            specific_files = args.files
        elif args.files:
            specific_files = args.files

        # Run pipeline
        results = pipeline.run(force_rebuild=args.force, demo_mode=args.demo, specific_files=specific_files)

        # Report results
        if results["success"]:
            if results["total_processed"] > 0:
                print(f"✅ Successfully processed {results['total_processed']} files")
                for category, files in results["processed_files"].items():
                    if files:
                        print(f"  {category}: {len(files)} files")
            else:
                print("✅ All files are up to date")
            return 0
        else:
            print(f"❌ Pipeline failed with {len(results['errors'])} errors:")
            for error in results["errors"]:
                print(f"  - {error}")
            return 1

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        print("\n⏸️  Pipeline interrupted")
        return 1

    except Exception as e:
        logger.exception("Pipeline failed with unexpected error")
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
