import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.models import Message


# Synchronous test client for simpler tests
client = TestClient(app)


class TestHomeEndpoint:
    """Test / endpoint."""

    def test_home_returns_html(self):
        """Test home endpoint returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert b"Nexus" in response.content

    def test_home_contains_static_references(self):
        """Test home page contains references to static files."""
        response = client.get("/")
        assert response.status_code == 200
        content = response.text
        assert "/static/styles.css" in content
        assert "/static/app.js" in content
        assert "/static/icon.svg" in content


class TestHealthEndpoint:
    """Test /api/health endpoint."""

    def test_health_check_success(self):
        """Test health check returns success."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "firebase" in data
        assert "gemini" in data
        assert data["status"] == "ok"

    def test_health_check_structure(self):
        """Test health check response structure."""
        response = client.get("/api/health")
        data = response.json()
        assert isinstance(data["status"], str)
        assert isinstance(data["firebase"], str)
        assert isinstance(data["gemini"], str)

    def test_health_check_firebase_modes(self):
        """Test health check shows Firebase mode."""
        response = client.get("/api/health")
        data = response.json()
        # Firebase can be "firestore" or "disabled"
        assert data["firebase"] in ["firestore", "disabled"]

    def test_health_check_gemini_modes(self):
        """Test health check shows Gemini mode."""
        response = client.get("/api/health")
        data = response.json()
        # Gemini can be "google-genai" or "disabled"
        assert data["gemini"] in ["google-genai", "disabled"]


class TestChatEndpoint:
    """Test /api/chat endpoint."""

    def test_chat_minimal_request(self):
        """Test chat with minimal valid request."""
        payload = {"messages": [{"role": "user", "content": "Hello"}]}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "model" in data
        assert "output_text" in data
        assert data["model"] == "gemini-2.5-flash"

    def test_chat_with_all_parameters(self):
        """Test chat with all parameters specified."""
        payload = {
            "session_id": "test-session-123",
            "user_id": "test-user-456",
            "model": "gemini-2.5-pro",
            "temperature": 0.8,
            "top_p": 0.95,
            "max_output_tokens": 4096,
            "messages": [{"role": "user", "content": "What is AI?"}],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert data["model"] == "gemini-2.5-pro"
        assert isinstance(data["output_text"], str)

    def test_chat_generates_session_id(self):
        """Test chat generates session_id if not provided."""
        payload = {"messages": [{"role": "user", "content": "Test"}]}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] is not None
        assert len(data["session_id"]) > 0

    def test_chat_preserves_session_id(self):
        """Test chat preserves provided session_id."""
        session_id = "my-custom-session"
        payload = {
            "session_id": session_id,
            "messages": [{"role": "user", "content": "Test"}],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id

    def test_chat_empty_messages(self):
        """Test chat with empty messages returns 400."""
        payload = {"messages": []}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "empty" in data["detail"].lower()

    def test_chat_missing_messages(self):
        """Test chat without messages field returns 422."""
        payload = {}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 422

    def test_chat_invalid_message_format(self):
        """Test chat with invalid message format returns 422."""
        payload = {"messages": [{"role": "user"}]}  # Missing content
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 422

    def test_chat_invalid_role(self):
        """Test chat with invalid role returns 422."""
        payload = {"messages": [{"role": "invalid", "content": "Test"}]}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 422

    def test_chat_multiple_messages(self):
        """Test chat with multiple messages."""
        payload = {
            "messages": [
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First response"},
                {"role": "user", "content": "Follow-up question"},
            ]
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "output_text" in data

    def test_chat_with_user_id_saves_conversation(self):
        """Test chat with user_id attempts to save conversation."""
        # This test verifies the endpoint accepts user_id
        # Actual saving depends on Firebase being configured
        payload = {
            "user_id": "test-user",
            "messages": [{"role": "user", "content": "Test"}],
        }
        response = client.post("/api/chat", json=payload)
        # Should succeed regardless of Firebase status
        assert response.status_code == 200

    def test_chat_without_user_id(self):
        """Test chat without user_id succeeds."""
        payload = {"messages": [{"role": "user", "content": "Test"}]}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200

    def test_chat_content_validation(self):
        """Test chat validates message content length."""
        # Content too long (> 32000 characters)
        long_content = "x" * 32001
        payload = {"messages": [{"role": "user", "content": long_content}]}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 422

    def test_chat_custom_model(self):
        """Test chat with custom model."""
        payload = {
            "model": "custom-model",
            "messages": [{"role": "user", "content": "Test"}],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "custom-model"

    def test_chat_system_message(self):
        """Test chat with system message."""
        payload = {
            "messages": [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"},
            ]
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200


class TestListSessionsEndpoint:
    """Test /api/sessions endpoint."""

    def test_list_sessions_without_user_id(self):
        """Test list sessions without user_id returns 422 or 400."""
        response = client.get("/api/sessions")
        # FastAPI returns 422 for missing query params in some versions, 400 in others
        assert response.status_code in [400, 422]
        data = response.json()
        assert "detail" in data

    def test_list_sessions_with_user_id(self):
        """Test list sessions with user_id."""
        response = client.get("/api/sessions?user_id=test-user")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    def test_list_sessions_empty_user_id(self):
        """Test list sessions with empty user_id returns 400."""
        response = client.get("/api/sessions?user_id=")
        assert response.status_code == 400

    def test_list_sessions_returns_list(self):
        """Test list sessions returns a list."""
        response = client.get("/api/sessions?user_id=test-user")
        assert response.status_code == 200
        data = response.json()
        # Returns empty list when Firebase is disabled or no sessions exist
        assert isinstance(data["sessions"], list)


class TestGetSessionEndpoint:
    """Test /api/sessions/{session_id} endpoint."""

    def test_get_session_without_user_id(self):
        """Test get session without user_id returns 422 or 400."""
        response = client.get("/api/sessions/session123")
        # FastAPI returns 422 for missing query params in some versions, 400 in others
        assert response.status_code in [400, 422]
        data = response.json()
        assert "detail" in data

    def test_get_session_with_user_id_not_found(self):
        """Test get session returns 404 when session not found."""
        response = client.get("/api/sessions/nonexistent?user_id=test-user")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_session_empty_user_id(self):
        """Test get session with empty user_id returns 400."""
        response = client.get("/api/sessions/session123?user_id=")
        assert response.status_code == 400


class TestStaticFiles:
    """Test static files serving."""

    def test_static_css_exists(self):
        """Test static CSS file is accessible."""
        response = client.get("/static/styles.css")
        # File should exist and be served
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")

    def test_static_js_exists(self):
        """Test static JS file is accessible."""
        response = client.get("/static/app.js")
        assert response.status_code == 200

    def test_static_icon_exists(self):
        """Test static icon file is accessible."""
        response = client.get("/static/icon.svg")
        assert response.status_code == 200

    def test_static_nonexistent_file(self):
        """Test requesting nonexistent static file returns 404."""
        response = client.get("/static/nonexistent.js")
        assert response.status_code == 404


class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers_present(self):
        """Test CORS headers are present in response."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS should allow the request
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_all_origins(self):
        """Test CORS configuration allows all origins."""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://example.com"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_json_request(self):
        """Test invalid JSON in request body."""
        response = client.post(
            "/api/chat",
            data="invalid json",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422

    def test_method_not_allowed(self):
        """Test method not allowed."""
        response = client.delete("/api/chat")
        assert response.status_code == 405

    def test_not_found(self):
        """Test 404 for nonexistent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_full_chat_flow(self):
        """Test complete chat flow."""
        # 1. Health check
        health_response = client.get("/api/health")
        assert health_response.status_code == 200

        # 2. Send first message
        payload1 = {
            "user_id": "integration-test-user",
            "messages": [{"role": "user", "content": "Hello"}],
        }
        chat_response1 = client.post("/api/chat", json=payload1)
        assert chat_response1.status_code == 200
        session_id = chat_response1.json()["session_id"]

        # 3. Continue conversation
        payload2 = {
            "session_id": session_id,
            "user_id": "integration-test-user",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"},
            ],
        }
        chat_response2 = client.post("/api/chat", json=payload2)
        assert chat_response2.status_code == 200
        assert chat_response2.json()["session_id"] == session_id

    def test_multiple_sessions(self):
        """Test creating multiple sessions."""
        payloads = [
            {"messages": [{"role": "user", "content": f"Message {i}"}]}
            for i in range(3)
        ]

        session_ids = set()
        for payload in payloads:
            response = client.post("/api/chat", json=payload)
            assert response.status_code == 200
            session_ids.add(response.json()["session_id"])

        # All sessions should have unique IDs
        assert len(session_ids) == 3

    def test_home_to_api_flow(self):
        """Test accessing home page then using API."""
        # 1. Load home page
        home_response = client.get("/")
        assert home_response.status_code == 200

        # 2. Check health
        health_response = client.get("/api/health")
        assert health_response.status_code == 200

        # 3. Send chat message
        chat_response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Test"}]},
        )
        assert chat_response.status_code == 200