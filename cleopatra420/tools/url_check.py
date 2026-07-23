"""Heurísticas defensivas para detectar URLs sospechosas / phishing."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

# TLDs y marcas frecuentemente abusadas en phishing (lista educativa, no exhaustiva)
SUSPICIOUS_TLDS = frozenset(
    {
        "zip",
        "mov",
        "tk",
        "ml",
        "ga",
        "cf",
        "gq",
        "xyz",
        "top",
        "work",
        "click",
        "country",
        "stream",
        "download",
        "racing",
        "review",
        "science",
        "work",
    }
)

BRAND_KEYWORDS = (
    "paypal",
    "apple",
    "microsoft",
    "google",
    "amazon",
    "facebook",
    "instagram",
    "whatsapp",
    "netflix",
    "banco",
    "bank",
    "secure",
    "login",
    "verify",
    "update",
    "account",
    "support",
    "wallet",
    "crypto",
    "binance",
    "metamask",
)


@dataclass
class UrlReport:
    url: str
    normalized: str
    risk_score: int  # 0-100
    risk_level: str
    findings: list[str] = field(default_factory=list)
    tips: list[str] = field(default_factory=list)

    def as_text(self) -> str:
        lines = [
            f"URL: {self.url}",
            f"Normalizada: {self.normalized}",
            f"Riesgo: {self.risk_score}/100 ({self.risk_level})",
            "",
            "Hallazgos:",
        ]
        if self.findings:
            lines.extend(f"  - {f}" for f in self.findings)
        else:
            lines.append("  (sin señales fuertes)")
        lines.append("")
        lines.append("Consejos:")
        lines.extend(f"  - {t}" for t in self.tips)
        return "\n".join(lines)


def _ensure_scheme(url: str) -> str:
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        return "https://" + url
    return url


def analyze_url(url: str) -> UrlReport:
    raw = url.strip()
    normalized = _ensure_scheme(raw)
    findings: list[str] = []
    score = 0

    try:
        parsed = urlparse(normalized)
    except Exception:  # noqa: BLE001
        return UrlReport(
            url=raw,
            normalized=normalized,
            risk_score=80,
            risk_level="Alto",
            findings=["No se pudo parsear la URL."],
            tips=["No abras enlaces malformados. Verifica con el remitente por otro canal."],
        )

    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    scheme = (parsed.scheme or "").lower()

    if not host:
        findings.append("Sin hostname válido.")
        score += 40

    if scheme == "http":
        findings.append("Usa HTTP sin cifrado (no HTTPS).")
        score += 20
    elif scheme not in ("https", "http"):
        findings.append(f"Esquema poco habitual: {scheme}")
        score += 15

    # IP literal en lugar de dominio
    if host:
        try:
            ipaddress.ip_address(host)
            findings.append("El host es una dirección IP literal (común en phishing).")
            score += 25
        except ValueError:
            pass

    if host.count(".") >= 4:
        findings.append("Muchos subdominios (posible engaño visual).")
        score += 15

    if "@" in raw.split("://", 1)[-1].split("/", 1)[0]:
        findings.append("Contiene '@' en la parte de autoridad (técnica clásica de phishing).")
        score += 30

    if re.search(r"%[0-9a-fA-F]{2}", raw):
        findings.append("Contiene URL-encoding (a veces oculta el destino real).")
        score += 10

    if re.search(r"[^\x00-\x7F]", host):
        findings.append("Caracteres no ASCII en el dominio (posible homoglyph / IDN spoofing).")
        score += 25

    tld = host.rsplit(".", 1)[-1] if host and "." in host else ""
    if tld in SUSPICIOUS_TLDS:
        findings.append(f"TLD frecuentemente abusado en campañas: .{tld}")
        score += 15

    # Marcas en subdominios raros
    for brand in BRAND_KEYWORDS:
        if brand in host and not host.endswith(f"{brand}.com") and not host.endswith(
            f"{brand}.net"
        ):
            # Heurística blanda: marca en host pero no es el dominio oficial simple
            if brand in host.replace(".", " "):
                findings.append(
                    f"Posible suplantación de marca «{brand}» en el dominio/subdominio."
                )
                score += 20
                break

    if len(raw) > 120:
        findings.append("URL muy larga.")
        score += 10

    if re.search(r"(login|verify|secure|update|password|wallet|seed|mnemonic)", path + query, re.I):
        findings.append("Ruta/query con palabras típicas de phishing (login/verify/wallet...).")
        score += 10

    if re.search(r"\.(exe|scr|bat|cmd|ps1|js|vbs|apk|msi)(\?|$)", path, re.I):
        findings.append("Apunta a un ejecutable o script.")
        score += 25

    score = max(0, min(100, score))
    if score >= 70:
        level = "Crítico"
    elif score >= 45:
        level = "Alto"
    elif score >= 25:
        level = "Medio"
    else:
        level = "Bajo"

    tips = [
        "Pasa el ratón (no hagas clic) y mira el dominio real antes de abrir.",
        "Escribe manualmente el sitio oficial en el navegador en vez de usar el enlace del correo.",
        "Activa 2FA y desconfía de urgencia artificial («tu cuenta se cierra en 1 hora»).",
        "En empresas, reporta el correo al SOC / phishing@ de tu organización.",
    ]
    if score >= 45:
        tips.insert(0, "No inicies sesión ni descargues nada desde este enlace.")

    return UrlReport(
        url=raw,
        normalized=normalized,
        risk_score=score,
        risk_level=level,
        findings=findings,
        tips=tips,
    )
