import pytest
from unittest.mock import Mock, patch

from app.models import Message


class TestGeminiClientInit:
    """Test GeminiClient initialization."""

    def test_init_without_api_key(self):
        """Test that GeminiClient initializes in disabled mode without API key."""
        with patch("app.services.gemini_client.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = ""

            from app.services.gemini_client import GeminiClient
            client = GeminiClient()

            assert client.mode == "disabled"
            assert client.client is None

    def test_init_with_api_key_import_error(self):
        """Test that import errors are handled gracefully."""
        with patch("app.services.gemini_client.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = "test-api-key"

            # Remove google module to simulate import error
            with patch.dict("sys.modules", {"google": None, "google.genai": None}):
                from app.services.gemini_client import GeminiClient
                client = GeminiClient()

                assert client.mode == "disabled"
                assert client.client is None


class TestGeminiClientFlattenPrompt:
    """Test the _flatten_prompt method."""

    def test_flatten_single_message(self):
        """Test flattening a single message."""
        with patch("app.services.gemini_client.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = ""

            from app.services.gemini_client import GeminiClient
            client = GeminiClient()
            messages = [Message(role="user", content="Hello")]

            result = client._flatten_prompt(messages)

            assert result == "[USER]\nHello"

    def test_flatten_multiple_messages(self):
        """Test flattening multiple messages."""
        with patch("app.services.gemini_client.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = ""

            from app.services.gemini_client import GeminiClient
            client = GeminiClient()
            messages = [
                Message(role="system", content="You are helpful"),
                Message(role="user", content="What is Python?"),
                Message(role="assistant", content="Python is a programming language"),
                Message(role="user", content="Tell me more")
            ]

            result = client._flatten_prompt(messages)

            expected = (
                "[SYSTEM]\n"
                "You are helpful\n\n"
                "[USER]\n"
                "What is Python?\n\n"
                "[ASSISTANT]\n"
                "Python is a programming language\n\n"
                "[USER]\n"
                "Tell me more"
            )

            assert result == expected

    def test_flatten_empty_messages(self):
        """Test flattening empty message list."""
        with patch("app.services.gemini_client.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = ""

            from app.services.gemini_client import GeminiClient
            client = GeminiClient()
            messages = []

            result = client._flatten_prompt(messages)

            assert result == ""

    def test_flatten_message_with_special_characters(self):
        """Test flattening messages containing special characters."""
        with patch("app.services.gemini_client.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = ""

            from app.services.gemini_client import GeminiClient
            client = GeminiClient()
            messages = [
                Message(role="user", content="Hello\nWorld\n\nMultiple lines!"),
            ]

            result = client._flatten_prompt(messages)

            assert result == "[USER]\nHello\nWorld\n\nMultiple lines!"

    def test_flatten_message_with_unicode(self):
        """Test flattening messages with Unicode characters."""
        with patch("app.services.gemini_client.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = ""

            from app.services.gemini_client import GeminiClient
            client = GeminiClient()
            messages = [
                Message(role="user", content="Hello 世界 🌍"),
            ]

            result = client._flatten_prompt(messages)

            assert result == "[USER]\nHello 世界 🌍"


class TestGeminiClientGenerate:
    """Test the generate method."""

    def test_generate_when_disabled(self):
        """Test that generate returns error message when client is disabled."""
        with patch("app.services.gemini_client.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = ""

            from app.services.gemini_client import GeminiClient
            client = GeminiClient()
            messages = [Message(role="user", content="Hello")]

            result = client.generate(
                model="gemini-2.5-flash",
                messages=messages,
                temperature=0.7,
                top_p=0.9,
                max_output_tokens=2048
            )

            assert result == "Gemini is not configured. Set GEMINI_API_KEY to enable live responses."