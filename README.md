# Nexus — AI Chatbot Web App

Nexus is a production-style AI chatbot website using **Gemini models**, **Firebase integration**, **IndexedDB offline/session storage**, and a modern hybrid UX inspired by Grok + ChatGPT layouts.

## Highlights
- FastAPI backend with clean API boundaries.
- Gemini integration via latest `google-genai` SDK.
- Firebase Firestore integration for cloud chat history.
- IndexedDB persistence for local sessions and preferences.
- Multi-theme UI (Dark, Light, Nexus Neon), transitions, custom icon + favicon.
- Chat productivity features:
  - New chat
  - Session history search
  - Export current chat as JSON
  - Persistent user preferences (theme)
  - Model + temperature control
  - `/api/health`, `/api/chat`, session APIs

## Architecture
- `app/main.py` — FastAPI app + routes.
- `app/services/gemini_client.py` — Gemini request pipeline.
- `app/services/firebase_store.py` — Firestore persistence adapter.
- `app/static/*` — frontend UI, theme system, IndexedDB client logic.
- `docs/CLOUD_RUN_DEPLOYMENT.md` — deployment runbook.

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8080
```
Open: `http://localhost:8080`

## Environment Variables
Required:
- `GEMINI_API_KEY`

Optional:
- `GEMINI_DEFAULT_MODEL` (default `gemini-2.5-flash`)
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CREDENTIALS_JSON` or `FIREBASE_CREDENTIALS_PATH`
- `ENV` (development/production)
- `PORT`

## Cloud Run
See: [`docs/CLOUD_RUN_DEPLOYMENT.md`](docs/CLOUD_RUN_DEPLOYMENT.md)

## Industry Practices Included
- Structured services and models.
- Strict payload schemas with Pydantic.
- Environment-based configuration.
- Cloud-native containerization (`Dockerfile`).
- Separation of UI and API concerns.

## Next Recommended Enhancements
- Streaming token responses (SSE/WebSocket).
- Firebase Auth for user identity and RBAC.
- Prompt/response guardrails and moderation hooks.
- Observability stack (OpenTelemetry + trace sampling).
