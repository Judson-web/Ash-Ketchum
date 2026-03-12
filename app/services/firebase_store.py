import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


class FirebaseStore:
    def __init__(self) -> None:
        self.db = None
        self.mode = "disabled"
        self._init_client()

    def _init_client(self) -> None:
        settings = get_settings()
        if not (settings.firebase_credentials_json or settings.firebase_credentials_path):
            self.mode = "disabled"
            return
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            if not firebase_admin._apps:
                if settings.firebase_credentials_json:
                    cred = credentials.Certificate(json.loads(settings.firebase_credentials_json))
                else:
                    cred = credentials.Certificate(settings.firebase_credentials_path)

                firebase_admin.initialize_app(
                    cred,
                    {"projectId": settings.firebase_project_id} if settings.firebase_project_id else None,
                )
            self.db = firestore.client()
            self.mode = "firestore"
        except Exception:
            logger.exception("Failed to initialize Firebase")
            self.mode = "disabled"

    def save_conversation(self, user_id: str, session_id: str, payload: dict[str, Any]) -> None:
        if self.mode != "firestore" or self.db is None:
            return
        now = datetime.now(timezone.utc).isoformat()
        self.db.collection("users").document(user_id).collection("sessions").document(session_id).set(
            {**payload, "updated_at": now}, merge=True
        )

    def list_sessions(self, user_id: str) -> list[dict[str, Any]]:
        if self.mode != "firestore" or self.db is None:
            return []
        docs = (
            self.db.collection("users")
            .document(user_id)
            .collection("sessions")
            .stream()
        )
        return [{"id": d.id, **(d.to_dict() or {})} for d in docs]

    def get_session(self, user_id: str, session_id: str) -> dict[str, Any] | None:
        if self.mode != "firestore" or self.db is None:
            return None
        doc = (
            self.db.collection("users")
            .document(user_id)
            .collection("sessions")
            .document(session_id)
            .get()
        )
        return doc.to_dict() if doc.exists else None
