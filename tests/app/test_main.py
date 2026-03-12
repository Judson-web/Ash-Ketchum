import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models import Message


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_firebase():
    """Mock the Firebase store."""
    with patch("app.main.firebase_store") as mock:
        yield mock


@pytest.fixture
def mock_gemini():
    """Mock the Gemini client."""
    with patch("app.main.gemini") as mock:
        yield mock


class TestHomeEndpoint:
    """Test the home page endpoint."""

    def test_home_returns_html(self, client):
        """Test that home endpoint returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_home_contains_app_name(self, client):
        """Test that home page contains the app name."""
        response = client.get("/")
        assert "Nexus" in response.text


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check_success(self, client, mock_firebase, mock_gemini):
        """Test successful health check."""
        mock_firebase.mode = "firestore"
        mock_gemini.mode = "google-genai"

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["firebase"] == "firestore"
        assert data["gemini"] == "google-genai"

    def test_health_check_disabled_services(self, client, mock_firebase, mock_gemini):
        """Test health check when services are disabled."""
        mock_firebase.mode = "disabled"
        mock_gemini.mode = "disabled"

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["firebase"] == "disabled"
        assert data["gemini"] == "disabled"


class TestChatEndpoint:
    """Test the chat endpoint."""

    def test_chat_success(self, client, mock_firebase, mock_gemini):
        """Test successful chat request."""
        mock_gemini.generate.return_value = "Hello! How can I help you?"

        payload = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }

        response = client.post("/api/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["model"] == "gemini-2.5-flash"
        assert data["output_text"] == "Hello! How can I help you?"

    def test_chat_empty_messages_validation(self, client, mock_firebase, mock_gemini):
        """Test that empty messages list returns 400 error."""
        payload = {
            "messages": []
        }

        response = client.post("/api/chat", json=payload)

        assert response.status_code == 400
        assert "messages cannot be empty" in response.json()["detail"]

    def test_chat_saves_to_firebase_with_user_id(self, client, mock_firebase, mock_gemini):
        """Test that conversation is saved to Firebase when user_id is provided."""
        mock_gemini.generate.return_value = "AI response"

        payload = {
            "user_id": "user-123",
            "session_id": "session-456",
            "messages": [
                {"role": "user", "content": "Test message"}
            ]
        }

        response = client.post("/api/chat", json=payload)

        assert response.status_code == 200

        # Verify Firebase save was called
        mock_firebase.save_conversation.assert_called_once()


class TestListSessionsEndpoint:
    """Test the list sessions endpoint."""

    def test_list_sessions_success(self, client, mock_firebase, mock_gemini):
        """Test successful session listing."""
        mock_firebase.list_sessions.return_value = [
            {"id": "session1", "title": "First chat"},
            {"id": "session2", "title": "Second chat"}
        ]

        response = client.get("/api/sessions?user_id=user-123")

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert len(data["sessions"]) == 2


class TestGetSessionEndpoint:
    """Test the get session endpoint."""

    def test_get_session_success(self, client, mock_firebase, mock_gemini):
        """Test successful session retrieval."""
        mock_firebase.get_session.return_value = {
            "title": "Test conversation",
            "model": "gemini-2.5-flash",
            "messages": [{"role": "user", "content": "Hello"}]
        }

        response = client.get("/api/sessions/session-123?user_id=user-456")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test conversation"

    def test_get_session_not_found(self, client, mock_firebase, mock_gemini):
        """Test getting a session that doesn't exist."""
        mock_firebase.get_session.return_value = None

        response = client.get("/api/sessions/nonexistent?user_id=user-123")

        assert response.status_code == 404
        assert "session not found" in response.json()["detail"]