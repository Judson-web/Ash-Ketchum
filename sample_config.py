import os


class Config(object):
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
    APP_ID = int(os.environ.get("APP_ID", "0") or 0)
    API_HASH = os.environ.get("API_HASH", "")

    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "")
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS")

    AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "").split() if x.strip())
    BANNED_USERS = [int(x) for x in os.environ.get("BANNED_USERS", "").split() if x.strip()]

    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "128"))
    TG_MAX_FILE_SIZE = int(os.environ.get("TG_MAX_FILE_SIZE", "2097152000"))

    OWNER_ID = int(os.environ.get("OWNER_ID", "0") or 0)
    SUPPORT_LINK = os.environ.get("SUPPORT_LINK", "https://t.me/")
    UPDATES_LINK = os.environ.get("UPDATES_LINK", "https://t.me/")

    # Firebase options for persistent thumbnails.
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
    FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH", "")
    FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON", "")
