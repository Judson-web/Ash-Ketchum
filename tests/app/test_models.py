import pytest
from pydantic import ValidationError

from app.models import Message, ChatRequest, ChatResponse, HealthResponse


class TestMessage:
    """Test the Message model."""

    def test_valid_message_creation(self):
        """Test creating a valid message with all roles."""
        msg_user = Message(role="user", content="Hello")
        assert msg_user.role == "user"
        assert msg_user.content == "Hello"

        msg_assistant = Message(role="assistant", content="Hi there")
        assert msg_assistant.role == "assistant"
        assert msg_assistant.content == "Hi there"

        msg_system = Message(role="system", content="You are a helpful assistant")
        assert msg_system.role == "system"
        assert msg_system.content == "You are a helpful assistant"

    def test_message_content_validation_min_length(self):
        """Test that message content must be at least 1 character."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user", content="")
        assert "content" in str(exc_info.value)

    def test_message_content_validation_max_length(self):
        """Test that message content cannot exceed 32000 characters."""
        long_content = "a" * 32001
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user", content=long_content)
        assert "content" in str(exc_info.value)

    def test_message_content_exactly_max_length(self):
        """Test that message content can be exactly 32000 characters."""
        max_content = "a" * 32000
        msg = Message(role="user", content=max_content)
        assert len(msg.content) == 32000

    def test_message_invalid_role(self):
        """Test that invalid role values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="invalid_role", content="Hello")
        assert "role" in str(exc_info.value)

    def test_message_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError):
            Message(role="user")

        with pytest.raises(ValidationError):
            Message(content="Hello")

    def test_message_serialization(self):
        """Test that Message can be serialized to dict."""
        msg = Message(role="user", content="Hello")
        msg_dict = msg.model_dump()
        assert msg_dict == {"role": "user", "content": "Hello"}


class TestChatRequest:
    """Test the ChatRequest model."""

    def test_valid_chat_request_with_defaults(self):
        """Test creating a valid ChatRequest with default values."""
        messages = [Message(role="user", content="Hello")]
        req = ChatRequest(messages=messages)

        assert req.session_id is None
        assert req.user_id is None
        assert req.model == "gemini-2.5-flash"
        assert req.temperature == 0.7
        assert req.top_p == 0.9
        assert req.max_output_tokens == 2048
        assert len(req.messages) == 1
        assert req.messages[0].content == "Hello"

    def test_valid_chat_request_with_custom_values(self):
        """Test creating a ChatRequest with custom values."""
        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hello")
        ]
        req = ChatRequest(
            session_id="test-session-123",
            user_id="user-456",
            model="gemini-2.5-pro",
            temperature=0.5,
            top_p=0.95,
            max_output_tokens=4096,
            messages=messages
        )

        assert req.session_id == "test-session-123"
        assert req.user_id == "user-456"
        assert req.model == "gemini-2.5-pro"
        assert req.temperature == 0.5
        assert req.top_p == 0.95
        assert req.max_output_tokens == 4096
        assert len(req.messages) == 2

    def test_chat_request_empty_messages_list(self):
        """Test that empty messages list is allowed by Pydantic but caught by endpoint."""
        # Empty list is valid for Pydantic, endpoint logic handles this
        req = ChatRequest(messages=[])
        assert req.messages == []

    def test_chat_request_with_multiple_messages(self):
        """Test ChatRequest with conversation history."""
        messages = [
            Message(role="user", content="What is Python?"),
            Message(role="assistant", content="Python is a programming language."),
            Message(role="user", content="Tell me more")
        ]
        req = ChatRequest(messages=messages)
        assert len(req.messages) == 3

    def test_chat_request_temperature_bounds(self):
        """Test temperature parameter accepts various values."""
        messages = [Message(role="user", content="Hello")]

        # Test minimum
        req_min = ChatRequest(messages=messages, temperature=0.0)
        assert req_min.temperature == 0.0

        # Test maximum (Gemini typically allows 0-2)
        req_max = ChatRequest(messages=messages, temperature=2.0)
        assert req_max.temperature == 2.0

    def test_chat_request_serialization(self):
        """Test that ChatRequest can be serialized."""
        messages = [Message(role="user", content="Hello")]
        req = ChatRequest(
            session_id="test-123",
            user_id="user-456",
            messages=messages
        )
        req_dict = req.model_dump()

        assert req_dict["session_id"] == "test-123"
        assert req_dict["user_id"] == "user-456"
        assert req_dict["messages"][0]["content"] == "Hello"


class TestChatResponse:
    """Test the ChatResponse model."""

    def test_valid_chat_response(self):
        """Test creating a valid ChatResponse."""
        resp = ChatResponse(
            session_id="session-123",
            model="gemini-2.5-flash",
            output_text="Hello! How can I help you?"
        )

        assert resp.session_id == "session-123"
        assert resp.model == "gemini-2.5-flash"
        assert resp.output_text == "Hello! How can I help you?"

    def test_chat_response_empty_output(self):
        """Test ChatResponse with empty output text."""
        resp = ChatResponse(
            session_id="session-123",
            model="gemini-2.5-flash",
            output_text=""
        )
        assert resp.output_text == ""

    def test_chat_response_long_output(self):
        """Test ChatResponse with very long output text."""
        long_text = "a" * 10000
        resp = ChatResponse(
            session_id="session-123",
            model="gemini-2.5-flash",
            output_text=long_text
        )
        assert len(resp.output_text) == 10000

    def test_chat_response_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError):
            ChatResponse(session_id="test", model="test")

        with pytest.raises(ValidationError):
            ChatResponse(session_id="test", output_text="test")

        with pytest.raises(ValidationError):
            ChatResponse(model="test", output_text="test")

    def test_chat_response_serialization(self):
        """Test ChatResponse serialization."""
        resp = ChatResponse(
            session_id="session-123",
            model="gemini-2.5-flash",
            output_text="Response text"
        )
        resp_dict = resp.model_dump()

        assert resp_dict["session_id"] == "session-123"
        assert resp_dict["model"] == "gemini-2.5-flash"
        assert resp_dict["output_text"] == "Response text"


class TestHealthResponse:
    """Test the HealthResponse model."""

    def test_valid_health_response(self):
        """Test creating a valid HealthResponse."""
        health = HealthResponse(
            status="ok",
            firebase="firestore",
            gemini="google-genai"
        )

        assert health.status == "ok"
        assert health.firebase == "firestore"
        assert health.gemini == "google-genai"

    def test_health_response_disabled_services(self):
        """Test HealthResponse with disabled services."""
        health = HealthResponse(
            status="ok",
            firebase="disabled",
            gemini="disabled"
        )

        assert health.status == "ok"
        assert health.firebase == "disabled"
        assert health.gemini == "disabled"

    def test_health_response_degraded_status(self):
        """Test HealthResponse with various status values."""
        health = HealthResponse(
            status="degraded",
            firebase="firestore",
            gemini="disabled"
        )
        assert health.status == "degraded"

    def test_health_response_missing_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            HealthResponse(status="ok", firebase="firestore")

        with pytest.raises(ValidationError):
            HealthResponse(status="ok", gemini="google-genai")

        with pytest.raises(ValidationError):
            HealthResponse(firebase="firestore", gemini="google-genai")

    def test_health_response_serialization(self):
        """Test HealthResponse serialization."""
        health = HealthResponse(
            status="ok",
            firebase="firestore",
            gemini="google-genai"
        )
        health_dict = health.model_dump()

        assert health_dict["status"] == "ok"
        assert health_dict["firebase"] == "firestore"
        assert health_dict["gemini"] == "google-genai"