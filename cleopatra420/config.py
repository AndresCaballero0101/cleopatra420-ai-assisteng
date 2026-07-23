"""Configuración y carga de variables de entorno."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Carga .env desde la raíz del proyecto
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Ajustes de la aplicación leídos del entorno."""

    xai_api_key: str
    xai_model: str
    xai_base_url: str
    project_root: Path

    @property
    def ai_ready(self) -> bool:
        key = (self.xai_api_key or "").strip()
        return bool(key) and key != "tu_api_key_aqui"


def get_settings() -> Settings:
    return Settings(
        xai_api_key=os.getenv("XAI_API_KEY", "").strip(),
        xai_model=os.getenv("XAI_MODEL", "grok-4.5").strip() or "grok-4.5",
        xai_base_url=os.getenv("XAI_BASE_URL", "https://api.x.ai/v1").strip()
        or "https://api.x.ai/v1",
        project_root=_ROOT,
    )


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
