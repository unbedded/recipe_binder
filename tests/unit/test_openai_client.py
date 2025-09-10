"""Unit tests for OpenAI client with retry logic and caching.

This test module provides comprehensive testing of the OpenAIClient class
following CLAUDE.md testing standards with mocked API calls and edge cases.

The tests cover:
- API client initialization and configuration
- Retry logic with exponential backoff
- Response caching and cache management
- Mock mode and fallback behavior
- Error handling scenarios
- Cost tracking and token usage

Example usage:
    pytest tests/unit/test_openai_client.py -v
"""

from unittest.mock import Mock, patch

import pytest

from recipe_fmt.models.config import OpenAIConfig
from recipe_fmt.parsers.openai_client import OpenAIClient, OpenAIResponse


class TestOpenAIClientInitialization:
    """Test suite for OpenAI client initialization and configuration."""

    def test_initialization_with_api_key(self):
        """Test client initializes correctly with API key."""
        config = OpenAIConfig(api_key="sk-test-key-123")
        client = OpenAIClient(config)

        assert client.config.api_key == "sk-test-key-123"
        assert client.config.model == "gpt-4o-mini"  # default
        assert client.cfg_dict["enable_caching"] is True
        assert client.cfg_dict["mock_mode"] is False

    def test_initialization_without_api_key(self):
        """Test client initializes in mock mode without API key."""
        config = OpenAIConfig(api_key=None)
        client = OpenAIClient(config)

        assert client.cfg_dict["mock_mode"] is True

    def test_initialization_with_custom_config(self):
        """Test client initializes with custom configuration."""
        config = OpenAIConfig(api_key="sk-test-key", model="gpt-4", max_tokens=2000, temperature=0.8)

        cfg_dict = {"enable_caching": False, "cache_max_size": 50, "cost_tracking": False}

        client = OpenAIClient(config, cfg_dict)

        assert client.config.model == "gpt-4"
        assert client.config.max_tokens == 2000
        assert client.config.temperature == 0.8
        assert client.cfg_dict["enable_caching"] is False
        assert client.cfg_dict["cache_max_size"] == 50
        assert client.cfg_dict["cost_tracking"] is False

    def test_config_defaults_application(self):
        """Test that configuration defaults are applied correctly."""
        config = OpenAIConfig(api_key="sk-test-key")
        client = OpenAIClient(config, {})

        # Check all defaults are applied
        assert client.cfg_dict["enable_caching"] is True
        assert client.cfg_dict["cache_max_size"] == 100
        assert client.cfg_dict["mock_mode"] is False
        assert client.cfg_dict["cost_tracking"] is True

    @patch("openai.OpenAI")
    def test_openai_library_import_success(self, mock_openai):
        """Test successful OpenAI library import and client creation."""
        config = OpenAIConfig(api_key="sk-test-key")
        mock_openai.OpenAI.return_value = Mock()

        client = OpenAIClient(config)

        mock_openai.OpenAI.assert_called_once_with(api_key="sk-test-key")
        assert client.cfg_dict["mock_mode"] is False

    @patch("recipe_fmt.parsers.openai_client.openai", side_effect=ImportError())
    def test_openai_library_import_failure(self, mock_openai):
        """Test graceful handling of missing OpenAI library."""
        config = OpenAIConfig(api_key="sk-test-key")

        client = OpenAIClient(config)

        # Should fall back to mock mode
        assert client.cfg_dict["mock_mode"] is True


class TestOpenAIClientCaching:
    """Test suite for response caching functionality."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(api_key="sk-test-key")
        self.client = OpenAIClient(self.config, {"enable_caching": True})

    def test_cache_key_generation(self):
        """Test cache key generation for content."""
        key1 = self.client._generate_cache_key("test content", "recipe_parse")
        key2 = self.client._generate_cache_key("test content", "recipe_parse")
        key3 = self.client._generate_cache_key("different content", "recipe_parse")

        # Same content should generate same key
        assert key1 == key2
        # Different content should generate different key
        assert key1 != key3
        # Key should be reasonable length (16 chars as per implementation)
        assert len(key1) == 16

    def test_cache_storage_and_retrieval(self):
        """Test storing and retrieving cached responses."""
        cache_key = "test_key_123456"
        response = OpenAIResponse(success=True, data={"content": "test yaml"}, tokens_used=100, cost_estimate=0.001)

        # Store in cache
        self.client._cache_response(cache_key, response)

        # Retrieve from cache
        cached = self.client._get_cached_response(cache_key)

        assert cached is not None
        assert cached.success is True
        assert cached.data["content"] == "test yaml"
        assert cached.tokens_used == 100
        assert cached.cost_estimate == 0.001
        assert cached.cached is True  # Should be marked as cached

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cached = self.client._get_cached_response("nonexistent_key")
        assert cached is None

    def test_cache_disabled(self):
        """Test caching behavior when disabled."""
        client = OpenAIClient(self.config, {"enable_caching": False})

        cache_key = "test_key"
        response = OpenAIResponse(success=True, data={"content": "test"})

        # Try to cache (should be ignored)
        client._cache_response(cache_key, response)

        # Try to retrieve (should return None)
        cached = client._get_cached_response(cache_key)
        assert cached is None

    def test_cache_size_limit(self):
        """Test cache size management with FIFO eviction."""
        # Set small cache size for testing
        client = OpenAIClient(self.config, {"cache_max_size": 2})

        # Add entries up to limit
        response1 = OpenAIResponse(success=True, data={"content": "test1"})
        response2 = OpenAIResponse(success=True, data={"content": "test2"})
        response3 = OpenAIResponse(success=True, data={"content": "test3"})

        client._cache_response("key1", response1)
        client._cache_response("key2", response2)

        # Both should be cached
        assert client._get_cached_response("key1") is not None
        assert client._get_cached_response("key2") is not None

        # Add third entry (should evict first)
        client._cache_response("key3", response3)

        # First should be evicted, others should remain
        assert client._get_cached_response("key1") is None
        assert client._get_cached_response("key2") is not None
        assert client._get_cached_response("key3") is not None


class TestOpenAIClientMockMode:
    """Test suite for mock mode functionality."""

    def test_mock_response_generation(self):
        """Test mock response generation when in mock mode."""
        config = OpenAIConfig(api_key=None)  # No API key triggers mock mode
        client = OpenAIClient(config)

        response = client._mock_openai_response()

        assert response.success is True
        assert response.data is not None
        assert "content" in response.data
        assert "Mock Recipe" in response.data["content"]
        assert response.tokens_used == 100
        assert response.cost_estimate == 0.0001

    def test_parse_recipe_in_mock_mode(self):
        """Test recipe parsing in mock mode."""
        config = OpenAIConfig(api_key=None)
        client = OpenAIClient(config)

        markdown_content = "# Test Recipe\n\n- 1 cup flour\n\n1. Mix ingredients"
        response = client.parse_recipe_markdown(markdown_content)

        assert response.success is True
        assert "Mock Recipe" in response.data["content"]
        assert response.tokens_used == 100

    def test_api_key_validation_in_mock_mode(self):
        """Test API key validation returns True in mock mode."""
        config = OpenAIConfig(api_key=None)
        client = OpenAIClient(config)

        assert client.validate_api_key() is True


class TestOpenAIClientRetryLogic:
    """Test suite for retry logic and error handling."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(
            api_key="sk-test-key",
            max_retries=3,
            retry_delay=0.1,  # Fast retry for testing
        )

    @patch("openai.OpenAI")
    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_successful_request_no_retry(self, mock_sleep, mock_openai):
        """Test successful request on first attempt."""
        # Setup mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "test: response"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 150

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(self.config)

        # Mock the request method to use our mocked client
        with patch.object(client, "_openai_client", mock_client):
            response = client.parse_recipe_markdown("# Test Recipe")

        assert response.success is True
        assert response.data["content"] == "test: response"
        assert response.tokens_used == 150
        assert mock_client.chat.completions.create.call_count == 1
        mock_sleep.assert_not_called()  # No retries needed

    @patch("openai.OpenAI")
    @patch("time.sleep")
    def test_retry_logic_with_eventual_success(self, mock_sleep, mock_openai):
        """Test retry logic with success on second attempt."""
        # Setup mock to fail first, succeed second
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),  # First attempt fails
            self._create_mock_response("success: response", 120),  # Second succeeds
        ]
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(self.config)

        with patch.object(client, "_openai_client", mock_client):
            response = client.parse_recipe_markdown("# Test Recipe")

        assert response.success is True
        assert response.data["content"] == "success: response"
        assert mock_client.chat.completions.create.call_count == 2
        mock_sleep.assert_called_once_with(0.1)  # One retry delay

    @patch("openai.OpenAI")
    @patch("time.sleep")
    def test_retry_exhaustion(self, mock_sleep, mock_openai):
        """Test behavior when all retries are exhausted."""
        # Setup mock to always fail
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Persistent API Error")
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(self.config)

        with patch.object(client, "_openai_client", mock_client):
            response = client.parse_recipe_markdown("# Test Recipe")

        assert response.success is False
        assert "Persistent API Error" in response.error
        assert mock_client.chat.completions.create.call_count == 3  # max_retries
        assert mock_sleep.call_count == 2  # 2 retry delays

    @patch("openai.OpenAI")
    @patch("time.sleep")
    def test_exponential_backoff(self, mock_sleep, mock_openai):
        """Test exponential backoff in retry delays."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(self.config)

        with patch.object(client, "_openai_client", mock_client):
            client.parse_recipe_markdown("# Test Recipe")

        # Check exponential backoff: 0.1, 0.2 seconds
        expected_calls = [
            pytest.approx(0.1, rel=1e-2),  # First retry: base_delay * 2^0
            pytest.approx(0.2, rel=1e-2),  # Second retry: base_delay * 2^1
        ]

        actual_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert actual_calls == expected_calls

    def _create_mock_response(self, content: str, tokens: int):
        """Helper to create mock OpenAI response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = content
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = tokens
        return mock_response


class TestOpenAIClientCostTracking:
    """Test suite for cost tracking and token usage."""

    def setup_method(self):
        """Setup test environment before each test method."""
        self.config = OpenAIConfig(api_key="sk-test-key")

    @patch("openai.OpenAI")
    def test_cost_calculation(self, mock_openai):
        """Test cost calculation based on token usage."""
        mock_response = self._create_mock_response("test: content", 500)
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(self.config, {"cost_tracking": True})

        with patch.object(client, "_openai_client", mock_client):
            response = client.parse_recipe_markdown("# Test Recipe")

        assert response.success is True
        assert response.tokens_used == 500
        # Cost should be calculated: (500 / 1000) * 0.0015 = 0.00075
        assert response.cost_estimate == pytest.approx(0.00075, rel=1e-3)

    @patch("openai.OpenAI")
    def test_cost_tracking_disabled(self, mock_openai):
        """Test cost tracking when disabled."""
        self._create_mock_response("test: content", 300)
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_client
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(self.config, {"cost_tracking": False})

        with patch.object(client, "_openai_client", mock_client):
            response = client.parse_recipe_markdown("# Test Recipe")

        assert response.cost_estimate is None

    def test_usage_stats(self):
        """Test usage statistics reporting."""
        client = OpenAIClient(self.config)
        stats = client.get_usage_stats()

        assert "cache_size" in stats
        assert "cache_enabled" in stats
        assert "mock_mode" in stats
        assert "model" in stats
        assert "max_retries" in stats

        assert stats["model"] == self.config.model
        assert stats["max_retries"] == self.config.max_retries

    def _create_mock_response(self, content: str, tokens: int):
        """Helper to create mock OpenAI response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = content
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = tokens
        return mock_response


class TestOpenAIClientEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_empty_content_handling(self):
        """Test handling of empty markdown content."""
        config = OpenAIConfig(api_key=None)  # Use mock mode
        client = OpenAIClient(config)

        response = client.parse_recipe_markdown("")

        # Should still work in mock mode
        assert response.success is True

    def test_very_long_content(self):
        """Test handling of very long markdown content."""
        config = OpenAIConfig(api_key=None)
        client = OpenAIClient(config)

        # Create very long content (10KB)
        long_content = "# Long Recipe\n" + "- ingredient\n" * 1000
        response = client.parse_recipe_markdown(long_content)

        assert response.success is True

    def test_unicode_content_handling(self):
        """Test handling of unicode characters in content."""
        config = OpenAIConfig(api_key=None)
        client = OpenAIClient(config)

        unicode_content = "# Café Français\n- 2 cuillères à café de sucre\n1. Mélanger"
        response = client.parse_recipe_markdown(unicode_content)

        assert response.success is True

    @patch("openai.OpenAI")
    def test_malformed_api_response(self, mock_openai):
        """Test handling of malformed API responses."""
        # Response missing expected fields
        mock_response = Mock()
        mock_response.choices = []  # Empty choices
        mock_response.usage = None

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        config = OpenAIConfig(api_key="sk-test-key")
        client = OpenAIClient(config)

        with patch.object(client, "_openai_client", mock_client):
            response = client.parse_recipe_markdown("# Test Recipe")

        assert response.success is False
        assert "failed" in response.error.lower() or "error" in response.error.lower()


class TestOpenAIClientIntegration:
    """Test suite for integration scenarios."""

    def test_full_pipeline_mock_mode(self):
        """Test complete pipeline in mock mode."""
        config = OpenAIConfig(api_key=None)
        client = OpenAIClient(config)

        # Test full parse -> cache -> retrieve cycle
        markdown_content = """# Chocolate Chip Cookies

## Ingredients
- 2 cups flour
- 1 cup sugar
- 1/2 cup butter

## Instructions
1. Mix dry ingredients
2. Add wet ingredients
3. Bake at 350°F for 12 minutes
"""

        # First call - should generate response
        response1 = client.parse_recipe_markdown(markdown_content)
        assert response1.success is True
        assert not response1.cached

        # Second call with same content - should use cache
        response2 = client.parse_recipe_markdown(markdown_content)
        assert response2.success is True
        assert response2.cached

        # Content should be identical
        assert response1.data["content"] == response2.data["content"]

    def test_configuration_override_chain(self):
        """Test configuration override behavior."""
        base_config = OpenAIConfig(api_key="sk-test")
        cfg_overrides = {"enable_caching": False, "mock_mode": True, "cost_tracking": False}

        client = OpenAIClient(base_config, cfg_overrides)

        # Verify overrides took effect
        assert client.cfg_dict["enable_caching"] is False
        assert client.cfg_dict["mock_mode"] is True
        assert client.cfg_dict["cost_tracking"] is False

        # Verify base config unchanged
        assert base_config.api_key == "sk-test"

    def test_concurrent_access_simulation(self):
        """Test client behavior under simulated concurrent access."""
        import threading

        config = OpenAIConfig(api_key=None)  # Mock mode for predictable results
        client = OpenAIClient(config)

        results = []
        errors = []

        def worker(worker_id):
            try:
                response = client.parse_recipe_markdown(f"# Recipe {worker_id}\n- ingredient")
                results.append((worker_id, response.success))
            except Exception as e:
                errors.append((worker_id, str(e)))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All should succeed without errors
        assert len(errors) == 0
        assert len(results) == 5
        assert all(success for _, success in results)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
