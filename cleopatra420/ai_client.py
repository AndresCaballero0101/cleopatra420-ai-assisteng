"""Cliente de IA SpaceXAI / xAI (API compatible con OpenAI)."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from cleopatra420.config import SYSTEM_PROMPT, Settings, get_settings


class AIClientError(Exception):
    """Error al hablar con el modelo."""


class CyberAIClient:
    """Chat con Grok orientado a ciberseguridad defensiva."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client: OpenAI | None = None
        self._history: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    @property
    def ready(self) -> bool:
        return self.settings.ai_ready

    def _ensure_client(self) -> OpenAI:
        if not self.ready:
            raise AIClientError(
                "Falta XAI_API_KEY. Copia .env.example a .env y pega tu clave de "
                "https://console.x.ai"
            )
        if self._client is None:
            self._client = OpenAI(
                api_key=self.settings.xai_api_key,
                base_url=self.settings.xai_base_url,
            )
        return self._client

    def reset(self) -> None:
        self._history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def chat(self, user_message: str) -> str:
        client = self._ensure_client()
        self._history.append({"role": "user", "content": user_message})
        try:
            response = client.chat.completions.create(
                model=self.settings.xai_model,
                messages=self._history,  # type: ignore[arg-type]
                temperature=0.4,
            )
        except Exception as exc:  # noqa: BLE001 — superficie amigable en CLI
            # Quitar el mensaje fallido del historial
            self._history.pop()
            raise AIClientError(f"Error de API xAI: {exc}") from exc

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
                model=self.settings.xai_model,
                messages=messages,  # type: ignore[arg-type]
                temperature=0.3,
            )
        except Exception as exc:  # noqa: BLE001
            raise AIClientError(f"Error de API xAI: {exc}") from exc
        return (response.choices[0].message.content or "").strip()
