
"""Local Ollama inference adapter for Sellbird."""

from __future__ import annotations

import asyncio
import logging

import httpx

logger = logging.getLogger("sellbird.ollama")

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3:4b"


class OllamaError(Exception):
    """Raised when the local Ollama service cannot complete a request."""


class OllamaClient:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
    ):
        self.model = model or DEFAULT_MODEL
        self.base_url = base_url.rstrip("/")

    async def generate(
        self,
        prompt: str,
        *,
        timeout: float = 300,
        expect_json: bool = False,
    ) -> str:
        """Generate a response using the local Ollama model."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if expect_json:
            payload["format"] = "json"
            # Qwen3 otherwise spends the generation budget in its thinking
            # channel, leaving response empty and done_reason="length".
            # Ollama's API-level think=false disables that channel reliably;
            # /no_think in the prompt alone is not sufficient on all versions.
            payload["think"] = False
            payload["options"] = {
                "num_ctx": 4096,
                "num_predict": 1024,
                "temperature": 0,
            }
        # SELLBIRD_QWEN3_STRUCTURED_OUTPUT_FIX_V2
            # Qwen3: disable its reasoning channel for structured JSON calls.
            payload["think"] = False
        # SELLBIRD_QWEN_JSON_MODE_FIX_V1\n
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(
                connect=10.0,
                read=timeout,
                write=30.0,
                pool=10.0,
            )
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            result = data.get("response", "")
            if not isinstance(result, str):
                raise OllamaError("Ollama returned an invalid response.")

            return result.strip()

        except (httpx.HTTPError, ValueError, OSError) as exc:
            logger.exception("Ollama inference failed")
            raise OllamaError(str(exc)) from exc

    async def preflight(self) -> None:
        """Check that Ollama is reachable and the configured model exists."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/api/tags"
                )
                response.raise_for_status()
                data = response.json()

            models = data.get("models", [])
            available = {
                item.get("name")
                for item in models
                if isinstance(item, dict)
            }

            if self.model not in available:
                raise OllamaError(
                    f"Model '{self.model}' is not installed. "
                    "Run: ollama pull " + self.model
                )

        except OllamaError:
            raise
        except (httpx.HTTPError, ValueError, OSError) as exc:
            raise OllamaError(
                f"Cannot connect to Ollama at {self.base_url}: {exc}"
            ) from exc
