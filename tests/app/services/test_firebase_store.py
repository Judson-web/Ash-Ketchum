import json
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock


class TestFirebaseStoreInit:
    """Test FirebaseStore initialization."""

    def test_init_without_credentials(self):
        """Test that FirebaseStore initializes in disabled mode without credentials."""
        with patch("app.services.firebase_store.get_settings") as mock_settings:
            mock_settings.return_value.firebase_credentials_json = ""
            mock_settings.return_value.firebase_credentials_path = ""

            from app.services.firebase_store import FirebaseStore
            store = FirebaseStore()

            assert store.mode == "disabled"
            assert store.db is None

    def test_init_exception_handling(self):
        """Test that exceptions during initialization set mode to disabled."""
        with patch("app.services.firebase_store.get_settings") as mock_settings:
            mock_settings.return_value.firebase_credentials_json = '{"type": "service_account"}'
            mock_settings.return_value.firebase_credentials_path = ""
            mock_settings.return_value.firebase_project_id = ""

            # Force import error by removing firebase_admin from sys.modules
            with patch.dict("sys.modules", {"firebase_admin": None}):
                from app.services.firebase_store import FirebaseStore
                store = FirebaseStore()

                assert store.mode == "disabled"
                assert store.db is None


class TestFirebaseStoreSaveConversation:
    """Test the save_conversation method."""

    def test_save_conversation_when_disabled(self):
        """Test that save_conversation does nothing when disabled."""
        with patch("app.services.firebase_store.get_settings") as mock_settings:
            mock_settings.return_value.firebase_credentials_json = ""
            mock_settings.return_value.firebase_credentials_path = ""

            from app.services.firebase_store import FirebaseStore
            store = FirebaseStore()
            # Should not raise any errors
            store.save_conversation("user123", "session456", {"title": "Test"})


class TestFirebaseStoreListSessions:
    """Test the list_sessions method."""

    def test_list_sessions_when_disabled(self):
        """Test that list_sessions returns empty list when disabled."""
        with patch("app.services.firebase_store.get_settings") as mock_settings:
            mock_settings.return_value.firebase_credentials_json = ""
            mock_settings.return_value.firebase_credentials_path = ""

            from app.services.firebase_store import FirebaseStore
            store = FirebaseStore()
            result = store.list_sessions("user123")

            assert result == []


class TestFirebaseStoreGetSession:
    """Test the get_session method."""

    def test_get_session_when_disabled(self):
        """Test that get_session returns None when disabled."""
        with patch("app.services.firebase_store.get_settings") as mock_settings:
            mock_settings.return_value.firebase_credentials_json = ""
            mock_settings.return_value.firebase_credentials_path = ""

            from app.services.firebase_store import FirebaseStore
            store = FirebaseStore()
            result = store.get_session("user123", "session456")

            assert result is None