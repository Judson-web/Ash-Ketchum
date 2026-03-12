import json
import logging
import os
from typing import Optional

from sample_config import Config

logger = logging.getLogger(__name__)

_firestore_db = None
_thumb_cache = {}


def _init_firebase():
    global _firestore_db
    if _firestore_db is not None:
        return _firestore_db

    creds_json = os.environ.get("FIREBASE_CREDENTIALS_JSON", "").strip()
    creds_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "").strip()
    project_id = os.environ.get("FIREBASE_PROJECT_ID", "").strip() or None

    if not creds_json and not creds_path:
        logger.warning("Firebase credentials not provided; using in-memory thumbnail store.")
        _firestore_db = False
        return _firestore_db

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            if creds_json:
                cred_info = json.loads(creds_json)
                cred = credentials.Certificate(cred_info)
            else:
                cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred, {"projectId": project_id} if project_id else None)

        _firestore_db = firestore.client()
        logger.info("Connected to Firebase Firestore for thumbnail persistence.")
    except Exception as exc:
        logger.exception("Could not initialize Firebase. Falling back to in-memory store: %s", exc)
        _firestore_db = False
    return _firestore_db


class ThumbDoc:
    def __init__(self, user_id: int, msg_id: int):
        self.id = user_id
        self.msg_id = msg_id


async def df_thumb(user_id: int, msg_id: int):
    db = _init_firebase()
    _thumb_cache[user_id] = msg_id
    if not db:
        return
    db.collection("thumbnails").document(str(user_id)).set({"msg_id": msg_id})


async def del_thumb(user_id: int):
    _thumb_cache.pop(user_id, None)
    db = _init_firebase()
    if not db:
        return
    db.collection("thumbnails").document(str(user_id)).delete()


async def thumb(user_id: int) -> Optional[ThumbDoc]:
    if user_id in _thumb_cache:
        return ThumbDoc(user_id, _thumb_cache[user_id])

    db = _init_firebase()
    if not db:
        return None

    doc = db.collection("thumbnails").document(str(user_id)).get()
    if not doc.exists:
        return None

    data = doc.to_dict() or {}
    msg_id = data.get("msg_id")
    if msg_id is None:
        return None

    _thumb_cache[user_id] = int(msg_id)
    return ThumbDoc(user_id, int(msg_id))
