import logging

from app.config import get_settings
from app.models import Message

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.mode = "disabled"
        self.client = None
        self._init()

    def _init(self) -> None:
        if not self.settings.gemini_api_key:
            return
        try:
            from google import genai

            self.client = genai.Client(api_key=self.settings.gemini_api_key)
            self.mode = "google-genai"
        except Exception:
            logger.exception("Could not initialize Gemini client")

    def _flatten_prompt(self, messages: list[Message]) -> str:
        chunks = []
        for m in messages:
            chunks.append(f"[{m.role.upper()}]\n{m.content}")
        return "\n\n".join(chunks)

    def generate(self, *, model: str, messages: list[Message], temperature: float, top_p: float, max_output_tokens: int) -> str:
        if self.mode != "google-genai" or not self.client:
            return "Gemini is not configured. Set GEMINI_API_KEY to enable live responses."

        prompt = self._flatten_prompt(messages)
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_output_tokens,
            },
        )
        return (getattr(response, "text", "") or "").strip() or "No text response returned by model."
