"""Model adapter boundary for provider-backed and local stub inference."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from time import perf_counter
from typing import Protocol
from urllib import error, request


class ModelAdapterError(RuntimeError):
    """Raised when a configured provider call fails."""


class ModelAdapterConfigError(ValueError):
    """Raised when model configuration is invalid."""


@dataclass
class ModelResult:
    text: str
    provider: str
    model: str
    latency_ms: int


class ModelAdapter(Protocol):
    def generate(self, prompt: str) -> ModelResult:
        ...


@dataclass
class ModelConfig:
    provider: str
    default_model: str
    timeout_seconds: float
    openai_api_key: str
    openai_base_url: str

    @classmethod
    def from_env(cls) -> "ModelConfig":
        return cls(
            provider=os.getenv("MODEL_PROVIDER", "stub").strip().lower(),
            default_model=os.getenv("DEFAULT_MODEL", "gpt-4.1-mini").strip(),
            timeout_seconds=float(os.getenv("MODEL_TIMEOUT_SECONDS", "30")),
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        )


class StubModelAdapter:
    def __init__(self, model_name: str = "v0-echo") -> None:
        self.model_name = model_name

    def generate(self, prompt: str) -> ModelResult:
        started = perf_counter()
        text = f"v0> {prompt.strip()}"
        latency_ms = int((perf_counter() - started) * 1000)
        return ModelResult(text=text, provider="stub", model=self.model_name, latency_ms=latency_ms)


class OpenAIModelAdapter:
    def __init__(self, api_key: str, model: str, timeout_seconds: float, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.base_url = base_url

    def generate(self, prompt: str) -> ModelResult:
        started = perf_counter()
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ModelAdapterError(f"OpenAI HTTP {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise ModelAdapterError(f"OpenAI network error: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ModelAdapterError("OpenAI request timed out") from exc

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelAdapterError("OpenAI response format was unexpected") from exc

        latency_ms = int((perf_counter() - started) * 1000)
        return ModelResult(text=text, provider="openai", model=self.model, latency_ms=latency_ms)


def build_model_adapter(config: ModelConfig | None = None) -> ModelAdapter:
    cfg = config or ModelConfig.from_env()
    if cfg.provider in {"", "stub"}:
        return StubModelAdapter()
    if cfg.provider == "openai":
        if not cfg.openai_api_key:
            raise ModelAdapterConfigError("MODEL_PROVIDER=openai requires OPENAI_API_KEY")
        return OpenAIModelAdapter(
            api_key=cfg.openai_api_key,
            model=cfg.default_model,
            timeout_seconds=cfg.timeout_seconds,
            base_url=cfg.openai_base_url,
        )
    raise ModelAdapterConfigError(f"Unsupported MODEL_PROVIDER: {cfg.provider}")
