from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Nexus"
    env: str = os.getenv("ENV", "production")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8080"))

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_default_model: str = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash")

    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    firebase_credentials_json: str = os.getenv("FIREBASE_CREDENTIALS_JSON", "")
    firebase_credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
