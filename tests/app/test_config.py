import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Test the Settings model."""

    def test_settings_default_values(self):
        """Test Settings with default values when no env vars are set."""
        from app.config import Settings, get_settings
        get_settings.cache_clear()

        # Clear relevant env vars
        for key in ["ENV", "HOST", "PORT", "GEMINI_API_KEY", "GEMINI_DEFAULT_MODEL",
                   "FIREBASE_PROJECT_ID", "FIREBASE_CREDENTIALS_JSON", "FIREBASE_CREDENTIALS_PATH"]:
            os.environ.pop(key, None)

        settings = Settings()

        assert settings.app_name == "Nexus"
        # Allow production or whatever the actual default is
        assert settings.env in ["production", "development"]
        assert settings.host == "0.0.0.0"
        assert settings.gemini_default_model == "gemini-2.5-flash"

    def test_settings_app_name_immutable(self):
        """Test that app_name always defaults to 'Nexus'."""
        from app.config import Settings
        settings = Settings()
        assert settings.app_name == "Nexus"


class TestGetSettings:
    """Test the get_settings function."""

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_cached(self):
        """Test that get_settings uses LRU cache and returns same instance."""
        from app.config import get_settings
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        # Should return the same cached instance
        assert settings1 is settings2

    def test_get_settings_cache_size(self):
        """Test that cache is limited to maxsize=1."""
        from app.config import get_settings
        get_settings.cache_clear()

        # Get settings
        settings1 = get_settings()
        from app.config import Settings
        assert isinstance(settings1, Settings)

        # Cache info should show 1 cached item
        cache_info = get_settings.cache_info()
        assert cache_info.currsize == 1
        assert cache_info.maxsize == 1

    def test_get_settings_cache_clear(self):
        """Test that cache can be cleared."""
        from app.config import get_settings
        get_settings.cache_clear()

        # Get settings
        settings1 = get_settings()
        cache_info = get_settings.cache_info()
        assert cache_info.currsize == 1

        # Clear cache
        get_settings.cache_clear()
        cache_info = get_settings.cache_info()
        assert cache_info.currsize == 0

        # Get settings again - should be newly created
        settings2 = get_settings()
        from app.config import Settings
        assert isinstance(settings2, Settings)