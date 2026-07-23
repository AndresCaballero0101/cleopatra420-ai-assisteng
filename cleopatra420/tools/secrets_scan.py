"""Detección heurística de secretos en texto (prevención de fugas)."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SecretFinding:
    kind: str
    preview: str
    line: int


PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "Generic API key assignment",
        re.compile(
            r"(?i)(api[_-]?key|apikey|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"
        ),
    ),
    (
        "JWT",
        re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ),
    (
        "Private key block",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "GitHub token",
        re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    ),
    (
        "Slack token",
        re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    ),
    (
        "Telegram bot token",
        re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{30,}\b"),
    ),
    (
        "Password assignment",
        re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]"),
    ),
]


def scan_text_for_secrets(text: str) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in PATTERNS:
            for match in pattern.finditer(line):
                preview = match.group(0)
                if len(preview) > 48:
                    preview = preview[:24] + "…" + preview[-8:]
                findings.append(SecretFinding(kind=kind, preview=preview, line=line_no))
    return findings


def findings_as_text(findings: list[SecretFinding]) -> str:
    if not findings:
        return "No se detectaron secretos con las heurísticas actuales."
    lines = [f"Se encontraron {len(findings)} posible(s) secreto(s):", ""]
    for f in findings:
        lines.append(f"  L{f.line}: [{f.kind}] {f.preview}")
    lines.extend(
        [
            "",
            "Recomendaciones:",
            "  - Rota las credenciales expuestas de inmediato.",
            "  - Usa variables de entorno o un vault (nunca commits en Git).",
            "  - Añade secret scanning en CI (gitleaks, trufflehog, GitHub secret scanning).",
        ]
    )
    return "\n".join(lines)
