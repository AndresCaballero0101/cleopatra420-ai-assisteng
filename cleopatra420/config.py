"""Configuración y carga de variables de entorno (multi-proveedor IA)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Carga .env desde la raíz del proyecto
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")

# Placeholders que no cuentan como clave real
_PLACEHOLDERS = frozenset(
    {
        "",
        "tu_api_key_aqui",
        "your_api_key_here",
        "sk-xxx",
        "changeme",
    }
)


@dataclass(frozen=True)
class ProviderSpec:
    """Metadatos de un proveedor OpenAI-compatible."""

    id: str
    label: str
    env_key: str
    env_model: str
    env_base_url: str
    default_model: str
    default_base_url: str
    docs_url: str
    key_hint: str


# Proveedores conocidos (todos usan el SDK OpenAI / chat.completions)
PROVIDERS: dict[str, ProviderSpec] = {
    "xai": ProviderSpec(
        id="xai",
        label="SpaceXAI / xAI (Grok)",
        env_key="XAI_API_KEY",
        env_model="XAI_MODEL",
        env_base_url="XAI_BASE_URL",
        default_model="grok-4.5",
        default_base_url="https://api.x.ai/v1",
        docs_url="https://console.x.ai",
        key_hint="XAI_API_KEY",
    ),
    "deepseek": ProviderSpec(
        id="deepseek",
        label="DeepSeek",
        env_key="DEEPSEEK_API_KEY",
        env_model="DEEPSEEK_MODEL",
        env_base_url="DEEPSEEK_BASE_URL",
        default_model="deepseek-chat",
        default_base_url="https://api.deepseek.com",
        docs_url="https://platform.deepseek.com",
        key_hint="DEEPSEEK_API_KEY",
    ),
    "opencloud": ProviderSpec(
        id="opencloud",
        label="OpenCloud (OpenAI-compatible)",
        env_key="OPENCLOUD_API_KEY",
        env_model="OPENCLOUD_MODEL",
        env_base_url="OPENCLOUD_BASE_URL",
        default_model="gpt-4o-mini",
        default_base_url="https://api.opencloud.ai/v1",
        docs_url="https://opencloud.ai",
        key_hint="OPENCLOUD_API_KEY + OPENCLOUD_BASE_URL",
    ),
    "openai": ProviderSpec(
        id="openai",
        label="OpenAI",
        env_key="OPENAI_API_KEY",
        env_model="OPENAI_MODEL",
        env_base_url="OPENAI_BASE_URL",
        default_model="gpt-4o-mini",
        default_base_url="https://api.openai.com/v1",
        docs_url="https://platform.openai.com/api-keys",
        key_hint="OPENAI_API_KEY",
    ),
    "openrouter": ProviderSpec(
        id="openrouter",
        label="OpenRouter",
        env_key="OPENROUTER_API_KEY",
        env_model="OPENROUTER_MODEL",
        env_base_url="OPENROUTER_BASE_URL",
        default_model="openrouter/auto",
        default_base_url="https://openrouter.ai/api/v1",
        docs_url="https://openrouter.ai/keys",
        key_hint="OPENROUTER_API_KEY",
    ),
    "custom": ProviderSpec(
        id="custom",
        label="Custom (cualquier API OpenAI-compatible)",
        env_key="CUSTOM_API_KEY",
        env_model="CUSTOM_MODEL",
        env_base_url="CUSTOM_BASE_URL",
        default_model="gpt-4o-mini",
        default_base_url="",
        docs_url="",
        key_hint="CUSTOM_API_KEY + CUSTOM_BASE_URL + CUSTOM_MODEL",
    ),
}

# Orden de auto-detección si AI_PROVIDER no está definido
_AUTODETECT_ORDER = ("xai", "deepseek", "opencloud", "openai", "openrouter", "custom")


def _is_real_key(value: str | None) -> bool:
    key = (value or "").strip()
    return bool(key) and key.lower() not in _PLACEHOLDERS


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name, default) or default).strip()


def _resolve_provider_id() -> str:
    """Elige el proveedor: AI_PROVIDER explícito o primera clave disponible."""
    raw = _env("AI_PROVIDER").lower()
    # Alias amigables
    aliases = {
        "spacexai": "xai",
        "grok": "xai",
        "x-ai": "xai",
        "ds": "deepseek",
        "open-cloud": "opencloud",
        "oc": "opencloud",
        "or": "openrouter",
    }
    if raw:
        pid = aliases.get(raw, raw)
        if pid in PROVIDERS:
            return pid
        # Proveedor desconocido: se trata como custom con overrides unificados
        return "custom"

    for pid in _AUTODETECT_ORDER:
        spec = PROVIDERS[pid]
        # Clave específica del proveedor
        if _is_real_key(_env(spec.env_key)):
            return pid
        # Clave unificada AI_API_KEY solo cuenta si hay base URL o modelo unificado
        # (evita ambigüedad); se resuelve más abajo en get_settings.
    # Último recurso: AI_API_KEY genérica → custom/xai según base URL
    if _is_real_key(_env("AI_API_KEY")):
        base = _env("AI_BASE_URL") or _env("XAI_BASE_URL")
        if "deepseek" in base.lower():
            return "deepseek"
        if "openrouter" in base.lower():
            return "openrouter"
        if "openai.com" in base.lower():
            return "openai"
        if "opencloud" in base.lower():
            return "opencloud"
        if "x.ai" in base.lower() or not base:
            return "xai"
        return "custom"
    return "xai"


@dataclass(frozen=True)
class Settings:
    """Ajustes de la aplicación leídos del entorno."""

    provider: str
    provider_label: str
    api_key: str
    model: str
    base_url: str
    docs_url: str
    key_hint: str
    project_root: Path

    # Compatibilidad hacia atrás con código que leía xai_*
    @property
    def xai_api_key(self) -> str:
        return self.api_key if self.provider == "xai" else ""

    @property
    def xai_model(self) -> str:
        return self.model

    @property
    def xai_base_url(self) -> str:
        return self.base_url

    @property
    def ai_ready(self) -> bool:
        if not _is_real_key(self.api_key):
            return False
        # custom exige base_url
        if self.provider == "custom" and not (self.base_url or "").strip():
            return False
        return True

    def setup_help(self) -> str:
        """Texto de ayuda para configurar la API en la CLI."""
        lines = [
            "Configura un proveedor en [cyan].env[/cyan] (copia desde [cyan].env.example[/cyan]):",
            "",
            "  [bold]Opción A — unificado[/bold]",
            "  AI_PROVIDER=deepseek   # xai | deepseek | opencloud | openai | openrouter | custom",
            "  AI_API_KEY=tu_clave",
            "  AI_MODEL=deepseek-chat          # opcional",
            "  AI_BASE_URL=https://api.deepseek.com   # opcional / obligatorio en custom",
            "",
            "  [bold]Opción B — por proveedor[/bold]",
        ]
        for pid in _AUTODETECT_ORDER:
            spec = PROVIDERS[pid]
            extra = ""
            if pid in {"opencloud", "custom"}:
                extra = f"  + {spec.env_base_url}"
            lines.append(f"  {spec.env_key}{extra}  → {spec.label}")
        lines.extend(
            [
                "",
                "Sin API key puedes usar las herramientas locales (2–10).",
            ]
        )
        return "\n".join(lines)


def get_settings() -> Settings:
    provider_id = _resolve_provider_id()
    spec = PROVIDERS.get(provider_id, PROVIDERS["custom"])

    # Resolución: específica del proveedor > unificada (AI_*) > defaults.
    # Así, con varias claves en .env, cambiar AI_PROVIDER usa la clave correcta.
    api_key = _env(spec.env_key) or _env("AI_API_KEY")
    model = _env(spec.env_model) or _env("AI_MODEL") or spec.default_model
    base_url = _env(spec.env_base_url) or _env("AI_BASE_URL") or spec.default_base_url

    # Si AI_PROVIDER forzó un id desconocido, etiqueta custom con lo unificado
    label = spec.label
    if provider_id == "custom" and _env("AI_PROVIDER") and _env("AI_PROVIDER").lower() not in {
        "custom",
        *PROVIDERS.keys(),
        "spacexai",
        "grok",
        "x-ai",
        "ds",
        "open-cloud",
        "oc",
        "or",
    }:
        label = f"Custom ({_env('AI_PROVIDER')})"

    return Settings(
        provider=spec.id if provider_id in PROVIDERS else "custom",
        provider_label=label,
        api_key=api_key,
        model=model or spec.default_model,
        base_url=base_url,
        docs_url=spec.docs_url,
        key_hint=spec.key_hint,
        project_root=_ROOT,
    )


def list_configured_providers() -> list[tuple[str, str, bool]]:
    """Lista (id, label, has_key) de todos los proveedores conocidos."""
    rows: list[tuple[str, str, bool]] = []
    active = _resolve_provider_id()
    unified_key = _is_real_key(_env("AI_API_KEY"))
    for pid in _AUTODETECT_ORDER:
        spec = PROVIDERS[pid]
        has = _is_real_key(_env(spec.env_key))
        # La clave unificada cuenta para el proveedor activo (o el único elegido)
        if not has and unified_key and pid == active:
            has = True
        rows.append((pid, spec.label, has))
    return rows


SYSTEM_PROMPT = """Eres Cleopatra420, un asistente de ciberseguridad DEFENSIVA y ética.

Tu misión:
- Ayudar a proteger sistemas, redes, cuentas y datos.
- Enseñar buenas prácticas, hardening, detección y respuesta.
- Explicar vulnerabilidades solo con fines educativos y de defensa.
- Analizar contraseñas, hashes, URLs, cabeceras HTTP y logs de forma legítima.
- Guiar en OSINT defensivo, compliance básico y concienciación (phishing, ingeniería social).

Reglas estrictas:
- NO des exploits listos para usar, malware, ransomware ni instrucciones de ataque.
- NO ayudes a invadir sistemas, cuentas o redes sin autorización explícita del dueño.
- Si piden algo ofensivo, rechaza y ofrece la alternativa defensiva (mitigación, detección, hardening).
- Menciona siempre el marco legal: solo opera en sistemas propios o con permiso escrito.
- Responde en el idioma del usuario (español por defecto). Sé claro, técnico y práctico.
- Cuando sea útil, estructura la respuesta con pasos numerados y checklist.

Identidad: Cleopatra420 — AI Assisteng de ciberseguridad.
"""
