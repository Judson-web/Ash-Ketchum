import pytest
from pydantic import ValidationError

from app.models import Message, ChatRequest, ChatResponse, HealthResponse


class TestMessage:
    """Test Message model validation."""

    def test_message_valid_user(self):
        """Test valid user message creation."""
        msg = Message(role="user", content="Hello world")
        assert msg.role == "user"
        assert msg.content == "Hello world"

    def test_message_valid_assistant(self):
        """Test valid assistant message creation."""
        msg = Message(role="assistant", content="Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"

    def test_message_valid_system(self):
        """Test valid system message creation."""
        msg = Message(role="system", content="You are a helpful assistant")
        assert msg.role == "system"
        assert msg.content == "You are a helpful assistant"

    def test_message_invalid_role(self):
        """Test message with invalid role raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="invalid", content="test")
        assert "Input should be" in str(exc_info.value)

    def test_message_empty_content(self):
        """Test message with empty content raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user", content="")
        assert "at least 1 character" in str(exc_info.value)

    def test_message_content_too_long(self):
        """Test message with content exceeding max length."""
        long_content = "x" * 32001
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user", content=long_content)
        assert "at most 32000 characters" in str(exc_info.value)

    def test_message_content_at_max_length(self):
        """Test message with content at exactly max length."""
        max_content = "x" * 32000
        msg = Message(role="user", content=max_content)
        assert len(msg.content) == 32000

    def test_message_missing_required_fields(self):
        """Test message missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            Message(role="user")
        with pytest.raises(ValidationError):
            Message(content="test")


class TestChatRequest:
    """Test ChatRequest model validation."""

    def test_chat_request_minimal(self):
        """Test minimal valid chat request."""
        req = ChatRequest(messages=[Message(role="user", content="Hello")])
        assert req.session_id is None
        assert req.user_id is None
        assert req.model == "gemini-2.5-flash"
        assert req.temperature == 0.7
        assert req.top_p == 0.9
        assert req.max_output_tokens == 2048
        assert len(req.messages) == 1

    def test_chat_request_all_fields(self):
        """Test chat request with all fields specified."""
        req = ChatRequest(
            session_id="test-session-123",
            user_id="user-456",
            model="gemini-2.5-pro",
            temperature=0.5,
            top_p=0.95,
            max_output_tokens=4096,
            messages=[
                Message(role="system", content="You are helpful"),
                Message(role="user", content="Hello"),
            ],
        )
        assert req.session_id == "test-session-123"
        assert req.user_id == "user-456"
        assert req.model == "gemini-2.5-pro"
        assert req.temperature == 0.5
        assert req.top_p == 0.95
        assert req.max_output_tokens == 4096
        assert len(req.messages) == 2

    def test_chat_request_empty_messages(self):
        """Test chat request with empty messages list."""
        # Pydantic allows empty list, validation happens in endpoint
        req = ChatRequest(messages=[])
        assert req.messages == []

    def test_chat_request_multiple_messages(self):
        """Test chat request with multiple messages."""
        messages = [
            Message(role="user", content="First message"),
            Message(role="assistant", content="Response"),
            Message(role="user", content="Follow-up"),
        ]
        req = ChatRequest(messages=messages)
        assert len(req.messages) == 3
        assert req.messages[0].content == "First message"
        assert req.messages[1].content == "Response"
        assert req.messages[2].content == "Follow-up"

    def test_chat_request_missing_messages(self):
        """Test chat request without messages raises ValidationError."""
        with pytest.raises(ValidationError):
            ChatRequest()

    def test_chat_request_invalid_temperature(self):
        """Test chat request accepts any float for temperature."""
        # No validation on temperature range in the model
        req = ChatRequest(temperature=-1.0, messages=[Message(role="user", content="test")])
        assert req.temperature == -1.0

    def test_chat_request_invalid_message_type(self):
        """Test chat request with invalid message type raises ValidationError."""
        with pytest.raises(ValidationError):
            ChatRequest(messages=[{"role": "user"}])  # Missing content

    def test_chat_request_optional_fields_none(self):
        """Test optional fields can be None."""
        req = ChatRequest(
            session_id=None,
            user_id=None,
            messages=[Message(role="user", content="test")],
        )
        assert req.session_id is None
        assert req.user_id is None

    def test_chat_request_custom_model(self):
        """Test chat request with custom model string."""
        req = ChatRequest(
            model="custom-model-v2",
            messages=[Message(role="user", content="test")],
        )
        assert req.model == "custom-model-v2"


class TestChatResponse:
    """Test ChatResponse model validation."""

    def test_chat_response_valid(self):
        """Test valid chat response creation."""
        resp = ChatResponse(
            session_id="session-123",
            model="gemini-2.5-flash",
            output_text="This is a response",
        )
        assert resp.session_id == "session-123"
        assert resp.model == "gemini-2.5-flash"
        assert resp.output_text == "This is a response"

    def test_chat_response_empty_output(self):
        """Test chat response with empty output text."""
        resp = ChatResponse(
            session_id="session-123",
            model="gemini-2.5-flash",
            output_text="",
        )
        assert resp.output_text == ""

    def test_chat_response_long_output(self):
        """Test chat response with very long output text."""
        long_text = "x" * 100000
        resp = ChatResponse(
            session_id="session-123",
            model="gemini-2.5-flash",
            output_text=long_text,
        )
        assert len(resp.output_text) == 100000

    def test_chat_response_missing_fields(self):
        """Test chat response missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            ChatResponse(session_id="session-123", model="gemini-2.5-flash")
        with pytest.raises(ValidationError):
            ChatResponse(session_id="session-123", output_text="text")
        with pytest.raises(ValidationError):
            ChatResponse(model="gemini-2.5-flash", output_text="text")


class TestHealthResponse:
    """Test HealthResponse model validation."""

    def test_health_response_valid(self):
        """Test valid health response creation."""
        resp = HealthResponse(
            status="ok",
            firebase="firestore",
            gemini="google-genai",
        )
        assert resp.status == "ok"
        assert resp.firebase == "firestore"
        assert resp.gemini == "google-genai"

    def test_health_response_disabled_services(self):
        """Test health response with disabled services."""
        resp = HealthResponse(
            status="ok",
            firebase="disabled",
            gemini="disabled",
        )
        assert resp.status == "ok"
        assert resp.firebase == "disabled"
        assert resp.gemini == "disabled"

    def test_health_response_degraded_status(self):
        """Test health response with different status values."""
        resp = HealthResponse(
            status="degraded",
            firebase="firestore",
            gemini="disabled",
        )
        assert resp.status == "degraded"

    def test_health_response_missing_fields(self):
        """Test health response missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            HealthResponse(firebase="firestore", gemini="google-genai")
        with pytest.raises(ValidationError):
            HealthResponse(status="ok", gemini="google-genai")
        with pytest.raises(ValidationError):
            HealthResponse(status="ok", firebase="firestore")

    def test_health_response_serialization(self):
        """Test health response can be serialized."""
        resp = HealthResponse(
            status="ok",
            firebase="firestore",
            gemini="google-genai",
        )
        data = resp.model_dump()
        assert data == {
            "status": "ok",
            "firebase": "firestore",
            "gemini": "google-genai",
        }