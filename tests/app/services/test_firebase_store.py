import os
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app.services.firebase_store import FirebaseStore


class TestFirebaseStore:
    """Test FirebaseStore class."""

    def test_init_without_credentials(self):
        """Test FirebaseStore initialization without credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.firebase_credentials_json = ""
                mock_settings.firebase_credentials_path = ""
                mock_settings.firebase_project_id = ""
                mock_get_settings.return_value = mock_settings

                store = FirebaseStore()
                assert store.mode == "disabled"
                assert store.db is None

    def test_init_firebase_failure(self):
        """Test FirebaseStore initialization when Firebase fails."""
        credentials_json = json.dumps({"type": "service_account"})

        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.firebase_credentials_json = credentials_json
                mock_settings.firebase_credentials_path = ""
                mock_settings.firebase_project_id = ""
                mock_get_settings.return_value = mock_settings

                with patch.dict("sys.modules", {"firebase_admin": MagicMock(), "firebase_admin.credentials": MagicMock(), "firebase_admin.firestore": MagicMock()}):
                    import firebase_admin
                    firebase_admin._apps = {}
                    firebase_admin.credentials.Certificate.side_effect = Exception("Init failed")

                    store = FirebaseStore()
                    assert store.mode == "disabled"
                    assert store.db is None

    def test_save_conversation_when_disabled(self):
        """Test save_conversation when Firebase is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.firebase_credentials_json = ""
                mock_settings.firebase_credentials_path = ""
                mock_settings.firebase_project_id = ""
                mock_get_settings.return_value = mock_settings

                store = FirebaseStore()
                # Should not raise error, just return
                result = store.save_conversation("user123", "session456", {"data": "test"})
                assert result is None

    def test_save_conversation_success(self):
        """Test successful save_conversation."""
        # Create a properly initialized store with mocked Firebase
        store = FirebaseStore()
        store.mode = "firestore"

        # Mock the db and document chain
        mock_doc_ref = Mock()
        mock_session_col = Mock()
        mock_session_col.document.return_value = mock_doc_ref
        mock_user_doc = Mock()
        mock_user_doc.collection.return_value = mock_session_col
        mock_users_col = Mock()
        mock_users_col.document.return_value = mock_user_doc
        mock_db = Mock()
        mock_db.collection.return_value = mock_users_col
        store.db = mock_db

        payload = {"model": "gemini-2.5-flash", "messages": []}
        store.save_conversation("user123", "session456", payload)

        # Verify the chain of calls
        mock_db.collection.assert_called_with("users")
        mock_users_col.document.assert_called_with("user123")
        mock_user_doc.collection.assert_called_with("sessions")
        mock_session_col.document.assert_called_with("session456")

        # Verify set was called with merged data
        call_args = mock_doc_ref.set.call_args
        assert call_args[1]["merge"] is True
        saved_data = call_args[0][0]
        assert "updated_at" in saved_data
        assert saved_data["model"] == "gemini-2.5-flash"
        assert saved_data["messages"] == []

    def test_list_sessions_when_disabled(self):
        """Test list_sessions when Firebase is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.firebase_credentials_json = ""
                mock_settings.firebase_credentials_path = ""
                mock_settings.firebase_project_id = ""
                mock_get_settings.return_value = mock_settings

                store = FirebaseStore()
                result = store.list_sessions("user123")
                assert result == []

    def test_list_sessions_success(self):
        """Test successful list_sessions."""
        store = FirebaseStore()
        store.mode = "firestore"

        # Create mock documents
        mock_doc1 = Mock()
        mock_doc1.id = "session1"
        mock_doc1.to_dict.return_value = {"title": "Chat 1", "messages": []}

        mock_doc2 = Mock()
        mock_doc2.id = "session2"
        mock_doc2.to_dict.return_value = {"title": "Chat 2", "messages": []}

        mock_session_col = Mock()
        mock_session_col.stream.return_value = [mock_doc1, mock_doc2]
        mock_user_doc = Mock()
        mock_user_doc.collection.return_value = mock_session_col
        mock_users_col = Mock()
        mock_users_col.document.return_value = mock_user_doc
        mock_db = Mock()
        mock_db.collection.return_value = mock_users_col
        store.db = mock_db

        result = store.list_sessions("user123")

        assert len(result) == 2
        assert result[0]["id"] == "session1"
        assert result[0]["title"] == "Chat 1"
        assert result[1]["id"] == "session2"
        assert result[1]["title"] == "Chat 2"

    def test_list_sessions_empty(self):
        """Test list_sessions with no sessions."""
        store = FirebaseStore()
        store.mode = "firestore"

        mock_session_col = Mock()
        mock_session_col.stream.return_value = []
        mock_user_doc = Mock()
        mock_user_doc.collection.return_value = mock_session_col
        mock_users_col = Mock()
        mock_users_col.document.return_value = mock_user_doc
        mock_db = Mock()
        mock_db.collection.return_value = mock_users_col
        store.db = mock_db

        result = store.list_sessions("user123")
        assert result == []

    def test_get_session_when_disabled(self):
        """Test get_session when Firebase is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.config.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.firebase_credentials_json = ""
                mock_settings.firebase_credentials_path = ""
                mock_settings.firebase_project_id = ""
                mock_get_settings.return_value = mock_settings

                store = FirebaseStore()
                result = store.get_session("user123", "session456")
                assert result is None

    def test_get_session_exists(self):
        """Test get_session when session exists."""
        store = FirebaseStore()
        store.mode = "firestore"

        mock_doc_snapshot = Mock()
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = {
            "title": "Chat 1",
            "messages": [{"role": "user", "content": "Hello"}],
        }

        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc_snapshot
        mock_session_col = Mock()
        mock_session_col.document.return_value = mock_doc_ref
        mock_user_doc = Mock()
        mock_user_doc.collection.return_value = mock_session_col
        mock_users_col = Mock()
        mock_users_col.document.return_value = mock_user_doc
        mock_db = Mock()
        mock_db.collection.return_value = mock_users_col
        store.db = mock_db

        result = store.get_session("user123", "session456")

        assert result is not None
        assert result["title"] == "Chat 1"
        assert len(result["messages"]) == 1

    def test_get_session_not_exists(self):
        """Test get_session when session does not exist."""
        store = FirebaseStore()
        store.mode = "firestore"

        mock_doc_snapshot = Mock()
        mock_doc_snapshot.exists = False

        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc_snapshot
        mock_session_col = Mock()
        mock_session_col.document.return_value = mock_doc_ref
        mock_user_doc = Mock()
        mock_user_doc.collection.return_value = mock_session_col
        mock_users_col = Mock()
        mock_users_col.document.return_value = mock_user_doc
        mock_db = Mock()
        mock_db.collection.return_value = mock_users_col
        store.db = mock_db

        result = store.get_session("user123", "session456")
        assert result is None