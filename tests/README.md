# Tests

This directory contains comprehensive unit tests for the Nexus Gemini web application.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                         # Pytest configuration
├── app/
│   ├── __init__.py
│   ├── test_models.py                  # Tests for Pydantic models
│   ├── test_config.py                  # Tests for configuration
│   ├── test_main.py                    # Tests for FastAPI endpoints
│   └── services/
│       ├── __init__.py
│       ├── test_firebase_store.py      # Tests for Firebase integration
│       └── test_gemini_client.py       # Tests for Gemini AI client
```

## Running Tests

### Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

### Run specific test file:
```bash
pytest tests/app/test_models.py
```

### Run specific test:
```bash
pytest tests/app/test_models.py::TestMessage::test_valid_message_creation
```

## Test Coverage

The test suite includes:

- **Models (23 tests)**: Comprehensive validation testing for all Pydantic models
  - Message validation (roles, content length, required fields)
  - ChatRequest/ChatResponse models
  - HealthResponse model

- **Configuration (6 tests)**: Settings management and caching
  - Default values
  - Environment variable handling
  - LRU cache behavior

- **Services (13 tests)**: External service integrations
  - Firebase Store initialization and operations
  - Gemini AI client initialization and prompt handling

- **API Endpoints (10 tests)**: FastAPI route testing
  - Home page
  - Health check
  - Chat endpoint
  - Session management

**Total: 52 tests, all passing**

## Test Philosophy

Tests focus on:
- Unit testing individual components in isolation
- Mocking external dependencies (Firebase, Gemini API)
- Validation of business logic
- Error handling and edge cases
- API contract verification