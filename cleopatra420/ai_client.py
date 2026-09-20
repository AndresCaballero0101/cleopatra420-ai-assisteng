"""Cliente de IA multi-proveedor (API compatible con OpenAI)."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from cleopatra420.config import SYSTEM_PROMPT, Settings, get_settings


class AIClientError(Exception):
    """Error al hablar con el modelo."""


class CyberAIClient:
    """Chat con cualquier proveedor OpenAI-compatible orientado a ciberseguridad defensiva."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client: OpenAI | None = None
        self._history: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    @property
    def ready(self) -> bool:
        return self.settings.ai_ready

    @property
    def provider_label(self) -> str:
        return self.settings.provider_label

    @property
    def model(self) -> str:
        return self.settings.model

    def _ensure_client(self) -> OpenAI:
        if not self.ready:
            hint = self.settings.key_hint or "AI_API_KEY"
            docs = self.settings.docs_url
            extra = f" ({docs})" if docs else ""
            raise AIClientError(
                f"Falta API key para {self.settings.provider_label}. "
                f"Configura {hint} en .env{extra}."
            )
        if self._client is None:
            kwargs: dict[str, Any] = {"api_key": self.settings.api_key}
            if self.settings.base_url:
                kwargs["base_url"] = self.settings.base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def reset(self) -> None:
        self._history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def reload_settings(self, settings: Settings | None = None) -> None:
        """Recarga configuración (p. ej. tras cambiar de proveedor en runtime)."""
        self.settings = settings or get_settings()
        self._client = None

    def chat(self, user_message: str) -> str:
        client = self._ensure_client()
        self._history.append({"role": "user", "content": user_message})
        try:
            response = client.chat.completions.create(
                model=self.settings.model,
                messages=self._history,  # type: ignore[arg-type]
                temperature=0.4,
            )
        except Exception as exc:  # noqa: BLE001 — superficie amigable en CLI
            self._history.pop()
            raise AIClientError(
                f"Error de API ({self.settings.provider_label}): {exc}"
            ) from exc

        content = (response.choices[0].message.content or "").strip()
        if not content:
            content = "(Sin respuesta del modelo)"
        self._history.append({"role": "assistant", "content": content})
        return content

    def ask_once(self, user_message: str, extra_context: str | None = None) -> str:
        """Consulta sin contaminar el historial de chat interactivo."""
        client = self._ensure_client()
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        if extra_context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Contexto técnico de herramientas locales:\n{extra_context}",
                }
            )
        messages.append({"role": "user", "content": user_message})
        try:
            response = client.chat.completions.create(
                model=self.settings.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=0.3,
            )
        except Exception as exc:  # noqa: BLE001
            raise AIClientError(
                f"Error de API ({self.settings.provider_label}): {exc}"
            ) from exc
        return (response.choices[0].message.content or "").strip()
