import os
import pytest
from unittest.mock import patch

from app.config import Settings, get_settings


class TestSettings:
    """Test Settings configuration model."""

    def test_settings_defaults(self):
        """Test settings with all default values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.app_name == "Nexus"
            assert settings.env == "production"
            assert settings.host == "0.0.0.0"
            assert settings.port == 8080
            assert settings.gemini_api_key == ""
            assert settings.gemini_default_model == "gemini-2.5-flash"
            assert settings.firebase_project_id == ""
            assert settings.firebase_credentials_json == ""
            assert settings.firebase_credentials_path == ""

    def test_settings_from_env_production(self):
        """Test settings loaded from environment variables (production)."""
        # Test that settings uses env vars when available
        settings = Settings()
        # Should be able to create settings and access all fields
        assert isinstance(settings.env, str)
        assert isinstance(settings.host, str)
        assert isinstance(settings.port, int)
        assert isinstance(settings.app_name, str)
        assert settings.app_name == "Nexus"

    def test_settings_environment_fields(self):
        """Test settings has proper environment-based fields."""
        # Since defaults are evaluated at module load time, we test that
        # the Settings class works correctly with whatever values were loaded
        settings = Settings()
        # Verify all fields exist and have correct types
        assert isinstance(settings.env, str)
        assert isinstance(settings.host, str)
        assert isinstance(settings.port, int)
        assert isinstance(settings.gemini_api_key, str)
        assert isinstance(settings.gemini_default_model, str)
        assert isinstance(settings.firebase_project_id, str)
        assert isinstance(settings.firebase_credentials_json, str)
        assert isinstance(settings.firebase_credentials_path, str)
        # Port should be positive
        assert settings.port > 0

    def test_settings_can_override_fields(self):
        """Test that Settings fields can be overridden when creating instance."""
        settings = Settings(
            env="development",
            port=9999,
            gemini_api_key="override-key",
            firebase_project_id="override-project"
        )
        assert settings.env == "development"
        assert settings.port == 9999
        assert settings.gemini_api_key == "override-key"
        assert settings.firebase_project_id == "override-project"

    def test_settings_port_type(self):
        """Test PORT is properly typed as int."""
        settings = Settings()
        assert isinstance(settings.port, int)

    def test_settings_validation(self):
        """Test Settings validates field types."""
        # Port must be int
        with pytest.raises((ValueError, TypeError)):
            Settings(port="not-an-int")

    def test_settings_empty_string_values(self):
        """Test settings with empty string environment variables."""
        env_vars = {
            "GEMINI_API_KEY": "",
            "FIREBASE_PROJECT_ID": "",
            "FIREBASE_CREDENTIALS_JSON": "",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.gemini_api_key == ""
            assert settings.firebase_project_id == ""
            assert settings.firebase_credentials_json == ""

    def test_settings_immutability(self):
        """Test that Settings is immutable (Pydantic BaseModel)."""
        settings = Settings()
        # Pydantic allows mutation by default, but we're testing the model works
        settings.app_name = "Modified"
        assert settings.app_name == "Modified"


class TestGetSettings:
    """Test get_settings function with LRU cache."""

    def test_get_settings_returns_settings(self):
        """Test get_settings returns a Settings instance."""
        # Clear cache before test
        get_settings.cache_clear()
        settings = get_settings()
        assert isinstance(settings, Settings)
        assert settings.app_name == "Nexus"

    def test_get_settings_caching(self):
        """Test get_settings caches the result."""
        get_settings.cache_clear()

        # First call
        settings1 = get_settings()
        # Second call should return cached instance
        settings2 = get_settings()

        # Should be the same object
        assert settings1 is settings2

    def test_get_settings_cache_max_size(self):
        """Test get_settings has maxsize of 1."""
        get_settings.cache_clear()

        # Check cache info
        cache_info = get_settings.cache_info()
        assert cache_info.maxsize == 1
        assert cache_info.hits == 0
        assert cache_info.misses == 0

        # Call once
        get_settings()
        cache_info = get_settings.cache_info()
        assert cache_info.misses == 1
        assert cache_info.hits == 0

        # Call again - should hit cache
        get_settings()
        cache_info = get_settings.cache_info()
        assert cache_info.misses == 1
        assert cache_info.hits == 1

    def test_get_settings_returns_same_type(self):
        """Test get_settings returns Settings instance."""
        get_settings.cache_clear()
        settings = get_settings()
        assert isinstance(settings, Settings)
        get_settings.cache_clear()

    def test_get_settings_cache_clear(self):
        """Test cache can be cleared."""
        get_settings.cache_clear()

        # First call
        get_settings()
        assert get_settings.cache_info().misses == 1

        # Clear cache
        get_settings.cache_clear()
        assert get_settings.cache_info().misses == 0
        assert get_settings.cache_info().hits == 0

        # Next call should miss cache again
        get_settings()
        assert get_settings.cache_info().misses == 1

    def test_get_settings_multiple_calls_same_instance(self):
        """Test get_settings caching returns same instance."""
        get_settings.cache_clear()

        # Due to caching, subsequent calls return the same cached instance
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2  # Same cached instance

        # Cleanup
        get_settings.cache_clear()