import logging
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse
from app.services.firebase_store import FirebaseStore
from app.services.gemini_client import GeminiClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("nexus")

settings = get_settings()
app = FastAPI(title="Nexus", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

firebase_store = FirebaseStore()
gemini = GeminiClient()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.app_name})


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", firebase=firebase_store.mode, gemini=gemini.mode)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    session_id = req.session_id or str(uuid.uuid4())
    output = gemini.generate(
        model=req.model,
        messages=req.messages,
        temperature=req.temperature,
        top_p=req.top_p,
        max_output_tokens=req.max_output_tokens,
    )

    if req.user_id:
        firebase_store.save_conversation(
            req.user_id,
            session_id,
            {
                "model": req.model,
                "title": req.messages[-1].content[:70],
                "messages": [m.model_dump() for m in req.messages] + [{"role": "assistant", "content": output}],
            },
        )

    return ChatResponse(session_id=session_id, model=req.model, output_text=output)


@app.get("/api/sessions")
async def list_sessions(user_id: str):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    return {"sessions": firebase_store.list_sessions(user_id)}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, user_id: str):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    session = firebase_store.get_session(user_id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return session


if __name__ == "__main__":
    import uvicorn

    os.makedirs("tmp", exist_ok=True)
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.env == "development")
