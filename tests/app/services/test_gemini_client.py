import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.gemini_client import GeminiClient
from app.models import Message


class TestGeminiClient:
    """Test GeminiClient class."""

    def test_init_without_api_key(self):
        """Test GeminiClient initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.gemini_api_key = ""
                mock_get_settings.return_value = mock_settings

                client = GeminiClient()
                assert client.mode == "disabled"
                assert client.client is None

    def test_init_with_api_key_failure(self):
        """Test GeminiClient initialization when Gemini client fails."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.gemini_api_key = "test-key-123"
                mock_get_settings.return_value = mock_settings

                with patch("google.genai.Client") as mock_client_class:
                    mock_client_class.side_effect = Exception("Connection failed")

                    client = GeminiClient()
                    assert client.mode == "disabled"
                    assert client.client is None

    def test_flatten_prompt_single_message(self):
        """Test _flatten_prompt with a single message."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.gemini_api_key = ""
                mock_get_settings.return_value = mock_settings

                client = GeminiClient()
                messages = [Message(role="user", content="Hello world")]
                result = client._flatten_prompt(messages)
                assert result == "[USER]\nHello world"

    def test_flatten_prompt_multiple_messages(self):
        """Test _flatten_prompt with multiple messages."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.gemini_api_key = ""
                mock_get_settings.return_value = mock_settings

                client = GeminiClient()
                messages = [
                    Message(role="system", content="You are helpful"),
                    Message(role="user", content="What is AI?"),
                    Message(role="assistant", content="AI stands for..."),
                ]
                result = client._flatten_prompt(messages)
                expected = "[SYSTEM]\nYou are helpful\n\n[USER]\nWhat is AI?\n\n[ASSISTANT]\nAI stands for..."
                assert result == expected

    def test_flatten_prompt_empty_list(self):
        """Test _flatten_prompt with empty message list."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.gemini_api_key = ""
                mock_get_settings.return_value = mock_settings

                client = GeminiClient()
                result = client._flatten_prompt([])
                assert result == ""

    def test_generate_when_disabled(self):
        """Test generate method when client is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.gemini_api_key = ""
                mock_get_settings.return_value = mock_settings

                client = GeminiClient()
                messages = [Message(role="user", content="Hello")]
                result = client.generate(
                    model="gemini-2.5-flash",
                    messages=messages,
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=2048,
                )
                assert result == "Gemini is not configured. Set GEMINI_API_KEY to enable live responses."

    def test_generate_success(self):
        """Test successful generate method call."""
        # Create a properly initialized client with mocked Gemini
        client = GeminiClient()
        client.mode = "google-genai"

        mock_response = Mock()
        mock_response.text = "This is a test response"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        client.client = mock_client

        messages = [Message(role="user", content="Hello")]
        result = client.generate(
            model="gemini-2.5-flash",
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=2048,
        )

        assert result == "This is a test response"
        mock_client.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash",
            contents="[USER]\nHello",
            config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 2048,
            },
        )

    def test_generate_empty_response(self):
        """Test generate when model returns empty response."""
        client = GeminiClient()
        client.mode = "google-genai"

        mock_response = Mock()
        mock_response.text = ""
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        client.client = mock_client

        messages = [Message(role="user", content="Hello")]
        result = client.generate(
            model="gemini-2.5-flash",
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=2048,
        )

        assert result == "No text response returned by model."

    def test_generate_whitespace_response(self):
        """Test generate when model returns whitespace only."""
        client = GeminiClient()
        client.mode = "google-genai"

        mock_response = Mock()
        mock_response.text = "   \n\t  "
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        client.client = mock_client

        messages = [Message(role="user", content="Hello")]
        result = client.generate(
            model="gemini-2.5-flash",
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=2048,
        )

        assert result == "No text response returned by model."

    def test_generate_no_text_attribute(self):
        """Test generate when response has no text attribute."""
        client = GeminiClient()
        client.mode = "google-genai"

        mock_response = Mock(spec=[])  # No text attribute
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        client.client = mock_client

        messages = [Message(role="user", content="Hello")]
        result = client.generate(
            model="gemini-2.5-flash",
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=2048,
        )

        assert result == "No text response returned by model."

    def test_generate_with_custom_parameters(self):
        """Test generate with custom temperature, top_p, and max_output_tokens."""
        client = GeminiClient()
        client.mode = "google-genai"

        mock_response = Mock()
        mock_response.text = "Custom response"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        client.client = mock_client

        messages = [Message(role="user", content="Test")]
        result = client.generate(
            model="gemini-2.5-pro",
            messages=messages,
            temperature=1.2,
            top_p=0.95,
            max_output_tokens=4096,
        )

        assert result == "Custom response"
        call_args = mock_client.models.generate_content.call_args
        assert call_args[1]["model"] == "gemini-2.5-pro"
        assert call_args[1]["config"]["temperature"] == 1.2
        assert call_args[1]["config"]["top_p"] == 0.95
        assert call_args[1]["config"]["max_output_tokens"] == 4096

    def test_generate_with_response_strip(self):
        """Test generate strips whitespace from response."""
        client = GeminiClient()
        client.mode = "google-genai"

        mock_response = Mock()
        mock_response.text = "  Response with spaces  \n"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        client.client = mock_client

        messages = [Message(role="user", content="Test")]
        result = client.generate(
            model="gemini-2.5-flash",
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=2048,
        )

        assert result == "Response with spaces"