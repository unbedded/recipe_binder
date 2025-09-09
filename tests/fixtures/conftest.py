"""pytest configuration and shared fixtures for Recipe Binder tests.

This module provides pytest configuration and shared fixtures that can be used
across all test modules. These fixtures leverage the sample data and utilities
from the fixtures package to provide consistent test environments.
"""

import pytest
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Import fixture data and utilities
from .sample_recipes import (
    SAMPLE_PANCAKES, SAMPLE_BEEF_STEW, SAMPLE_CHOCOLATE_CAKE,
    SAMPLE_MARKDOWN_CONTENT, ALL_SAMPLE_RECIPES
)
from .template_data import (
    DEFAULT_CARD_TEMPLATE, COMPACT_CARD_TEMPLATE,
    ALL_TEMPLATE_DATA, get_valid_template_names
)
from .openai_responses import (
    SUCCESSFUL_PARSE_RESPONSE, ERROR_RATE_LIMIT_RESPONSE,
    create_mock_openai_response, create_retry_sequence_responses
)
from .file_utils import MockFileSystem, FileSystemTestHelper

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise during testing
    format='%(levelname)s:%(name)s:%(message)s'
)

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "openai: mark test as requiring OpenAI API"
    )
    config.addinivalue_line(
        "markers", "file_io: mark test as requiring file I/O"
    )

# Session-scoped fixtures (created once per test session)

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration dictionary."""
    return {
        "log_level": "WARNING",
        "cache_templates": True,
        "validate_templates": True,
        "strict_validation": False,
        "force_rebuild": False,
        "parallel_processing": False,  # Disable for testing
        "openai_api_key": "test-key-not-real",
        "test_mode": True
    }

@pytest.fixture(scope="session") 
def sample_recipe_data():
    """Provide all sample recipe data."""
    return ALL_SAMPLE_RECIPES

@pytest.fixture(scope="session")
def sample_template_data():
    """Provide all sample template data."""
    return ALL_TEMPLATE_DATA

# Function-scoped fixtures (created for each test function)

@pytest.fixture
def temp_dir():
    """Provide temporary directory that's cleaned up after test."""
    temp_path = tempfile.mkdtemp(prefix="recipe_binder_test_")
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def mock_file_system():
    """Provide MockFileSystem instance with cleanup."""
    with MockFileSystem() as fs:
        yield fs

@pytest.fixture
def sample_recipe_files(mock_file_system):
    """Provide sample recipe files in mock file system."""
    # Create markdown files
    markdown_files = {}
    for name, content in SAMPLE_MARKDOWN_CONTENT.items():
        markdown_files[f"{name}.md"] = content
    
    created_files = mock_file_system.create_recipe_files(markdown_files)
    return created_files

@pytest.fixture
def sample_template_files(mock_file_system):
    """Provide sample template files in mock file system."""
    # Only include valid templates for general testing
    valid_templates = {
        name: data for name, data in ALL_TEMPLATE_DATA.items()
        if name in get_valid_template_names()
    }
    
    created_files = mock_file_system.create_template_files(valid_templates)
    return created_files

@pytest.fixture
def staleness_test_files(mock_file_system):
    """Provide files for staleness detection testing."""
    return mock_file_system.create_staleness_test_files()

@pytest.fixture
def error_scenario_files(mock_file_system):
    """Provide files for error scenario testing."""
    return mock_file_system.create_error_scenario_files()

# Mock fixtures for external dependencies

@pytest.fixture
def mock_openai_client():
    """Provide mocked OpenAI client."""
    with patch('openai.OpenAI') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Setup default successful response
        mock_response = create_mock_openai_response(
            SUCCESSFUL_PARSE_RESPONSE["raw_response"]["choices"][0]["message"]["content"],
            570
        )
        mock_client.chat.completions.create.return_value = mock_response
        
        yield mock_client

@pytest.fixture
def mock_openai_error_responses():
    """Provide mock OpenAI client with error responses."""
    with patch('openai.OpenAI') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Setup error responses for testing retry logic
        error_responses = create_retry_sequence_responses(
            failure_count=2, final_success=True
        )
        mock_client.chat.completions.create.side_effect = error_responses
        
        yield mock_client

@pytest.fixture
def mock_reportlab():
    """Provide mocked ReportLab components."""
    mocks = {}
    
    # Mock Canvas
    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas_class:
        mock_canvas = Mock()
        mock_canvas_class.return_value = mock_canvas
        mocks['canvas_class'] = mock_canvas_class
        mocks['canvas'] = mock_canvas
        
        # Mock common methods
        mock_canvas.drawString = Mock()
        mock_canvas.drawRightString = Mock()
        mock_canvas.drawCentredString = Mock()
        mock_canvas.setFont = Mock()
        mock_canvas.setFillColor = Mock()
        mock_canvas.rect = Mock()
        mock_canvas.showPage = Mock()
        mock_canvas.save = Mock()
        
        yield mocks

# Recipe model fixtures

@pytest.fixture
def pancakes_recipe():
    """Provide pancakes recipe instance."""
    return SAMPLE_PANCAKES

@pytest.fixture
def beef_stew_recipe():
    """Provide beef stew recipe instance."""
    return SAMPLE_BEEF_STEW

@pytest.fixture
def chocolate_cake_recipe():
    """Provide chocolate cake recipe instance."""
    return SAMPLE_CHOCOLATE_CAKE

@pytest.fixture(params=[SAMPLE_PANCAKES, SAMPLE_BEEF_STEW, SAMPLE_CHOCOLATE_CAKE])
def sample_recipe(request):
    """Parametrized fixture providing different sample recipes."""
    return request.param

# Template fixtures

@pytest.fixture
def default_card_template():
    """Provide default card template data."""
    return DEFAULT_CARD_TEMPLATE.copy()

@pytest.fixture
def compact_card_template():
    """Provide compact card template data."""
    return COMPACT_CARD_TEMPLATE.copy()

@pytest.fixture(params=get_valid_template_names())
def template_name(request):
    """Parametrized fixture providing different template names."""
    return request.param

# Component fixtures

@pytest.fixture
def file_manager(test_config, mock_file_system):
    """Provide FileManager instance with test configuration."""
    from recipe_fmt.utils.file_manager import FileManager
    return FileManager(test_config)

@pytest.fixture
def openai_client(test_config, mock_openai_client):
    """Provide OpenAIClient instance with mocked API."""
    from recipe_fmt.parsers.openai_client import OpenAIClient
    return OpenAIClient(test_config)

@pytest.fixture
def markdown_parser(test_config, openai_client):
    """Provide MarkdownParser instance."""
    from recipe_fmt.parsers.markdown_parser import MarkdownParser
    return MarkdownParser(test_config)

@pytest.fixture
def yaml_validator(test_config):
    """Provide YAMLValidator instance."""
    from recipe_fmt.validators.yaml_validator import YAMLValidator
    return YAMLValidator(test_config)

@pytest.fixture
def template_engine(test_config, sample_template_files):
    """Provide TemplateEngine instance with sample templates."""
    from recipe_fmt.templates.template_engine import TemplateEngine
    engine = TemplateEngine(test_config)
    # Add the mock file system template path
    if sample_template_files:
        template_dir = list(sample_template_files.values())[0].parent
        engine.add_template_path(template_dir)
    return engine

@pytest.fixture
def pdf_generator(test_config, mock_reportlab):
    """Provide PDFCardGenerator instance with mocked ReportLab."""
    from recipe_fmt.generators.pdf_generator import PDFCardGenerator
    from recipe_fmt.models.config import DisplayConfig
    
    display_config = DisplayConfig(
        show_weights=True,
        show_purpose=True,
        font_family="Helvetica",
        color_scheme="default"
    )
    
    return PDFCardGenerator(display_config, test_config)

@pytest.fixture
def pipeline(test_config, mock_file_system):
    """Provide Pipeline instance with test environment."""
    from recipe_fmt.pipeline.pipeline import Pipeline
    return Pipeline(test_config)

# Utility fixtures

@pytest.fixture
def assert_file_helper():
    """Provide FileSystemTestHelper for file assertions."""
    return FileSystemTestHelper

@pytest.fixture
def capture_logs():
    """Provide log capturing utility."""
    import logging
    from io import StringIO
    
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger('recipe_fmt')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    yield log_stream
    
    logger.removeHandler(handler)

# Performance testing fixtures

@pytest.fixture
def performance_timer():
    """Provide performance timing utility."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
            return self.elapsed
        
        @property
        def elapsed(self):
            if self.start_time is None:
                return 0
            if self.end_time is None:
                return time.perf_counter() - self.start_time
            return self.end_time - self.start_time
    
    return Timer()

# Integration test fixtures

@pytest.fixture
def end_to_end_environment(mock_file_system, test_config):
    """Provide complete environment for end-to-end testing."""
    # Create full sample file structure
    sample_files = mock_file_system.create_sample_files()
    
    # Create all components
    from recipe_fmt.utils.file_manager import FileManager
    from recipe_fmt.parsers.markdown_parser import MarkdownParser
    from recipe_fmt.validators.yaml_validator import YAMLValidator
    from recipe_fmt.templates.template_engine import TemplateEngine
    from recipe_fmt.generators.pdf_generator import PDFCardGenerator
    from recipe_fmt.pipeline.pipeline import Pipeline
    from recipe_fmt.models.config import DisplayConfig
    
    components = {
        'file_manager': FileManager(test_config),
        'markdown_parser': MarkdownParser(test_config),
        'yaml_validator': YAMLValidator(test_config),
        'template_engine': TemplateEngine(test_config),
        'display_config': DisplayConfig(
            show_weights=True,
            show_purpose=True,
            font_family="Helvetica",
            color_scheme="default"
        ),
        'pipeline': Pipeline(test_config)
    }
    
    # Setup template engine with sample templates
    if sample_files['templates']:
        template_dir = list(sample_files['templates'].values())[0].parent
        components['template_engine'].add_template_path(template_dir)
    
    return {
        'file_system': mock_file_system,
        'sample_files': sample_files,
        'components': components,
        'config': test_config
    }

# Parameterized test data fixtures

@pytest.fixture(params=[
    ("valid_small", 10),
    ("valid_medium", 100),
    ("valid_large", 1000)
])
def recipe_batch_sizes(request):
    """Parametrized fixture for testing different batch sizes."""
    name, size = request.param
    return name, size

@pytest.fixture(params=[
    "Breakfast", "Meat", "Dessert", "Vegetarian", "Seafood",
    "Appetizer", "Soup", "Salad", "Side", "Other"
])
def recipe_category(request):
    """Parametrized fixture for testing different recipe categories."""
    return request.param

@pytest.fixture(params=[
    ("8.5x4", 8.5, 4.0),
    ("6x4", 6.0, 4.0),
    ("5x3", 5.0, 3.0),
    ("letter", 8.5, 11.0)
])
def card_dimensions(request):
    """Parametrized fixture for testing different card dimensions."""
    name, width, height = request.param
    return {"name": name, "width": width, "height": height}

# Cleanup fixtures

@pytest.fixture(autouse=True)
def cleanup_test_artifacts():
    """Auto-used fixture to clean up test artifacts after each test."""
    yield
    
    # Clean up any test files that might have been created
    import os
    import glob
    
    test_patterns = [
        "test_*.pdf",
        "test_*.yaml", 
        "test_*.md",
        "*_test_*"
    ]
    
    for pattern in test_patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
            except OSError:
                pass  # Ignore cleanup errors

# Example usage documentation
"""
Example usage of these fixtures in test modules:

def test_recipe_parsing(pancakes_recipe, markdown_parser):
    # Test using the pancakes recipe fixture and markdown parser
    result = markdown_parser.parse_recipe(pancakes_recipe.title)
    assert result.success

def test_template_loading(template_engine, template_name):
    # Parametrized test that runs for each valid template
    template = template_engine.load_template(f"{template_name}.yaml")
    assert template.name is not None

def test_file_operations(sample_recipe_files, assert_file_helper):
    # Test using sample files and file assertion helper
    for filename, filepath in sample_recipe_files.items():
        assert_file_helper.assert_file_exists(filepath)

def test_end_to_end_processing(end_to_end_environment):
    # Integration test using complete environment
    env = end_to_end_environment
    pipeline = env['components']['pipeline']
    result = pipeline.process_all_recipes()
    assert result.success

@pytest.mark.slow
def test_performance(performance_timer, large_recipe_batch):
    # Performance test with timing
    timer.start()
    process_recipes(large_recipe_batch)
    elapsed = timer.stop()
    assert elapsed < 30.0  # Should complete within 30 seconds
"""