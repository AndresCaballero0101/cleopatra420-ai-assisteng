"""Smoke test rápido de herramientas locales."""

from __future__ import annotations

import sys
from pathlib import Path

# Permite ejecutar: py -3 scripts/smoke_test.py desde la raíz del repo
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cleopatra420 import __version__
from cleopatra420.config import get_settings
from cleopatra420.tools.encoding_tools import decode_base64, encode_base64
from cleopatra420.tools.hash_tools import hash_text
from cleopatra420.tools.network_tools import local_network_info
from cleopatra420.tools.password_tools import analyze_password, generate_password
from cleopatra420.tools.secrets_scan import scan_text_for_secrets
from cleopatra420.tools.url_check import analyze_url


def main() -> None:
    p = generate_password(16)
    r = analyze_password(p)
    h = hash_text("cleopatra420", "sha256")
    u = analyze_url("http://192.168.1.1/login/paypal-secure-verify.zip")
    s = scan_text_for_secrets("api_key = AKIAIOSFODNN7EXAMPLEXX")
    print("version", __version__)
    print("pwd_ok", len(p) == 16, r.strength)
    print("hash", h[:16])
    print("url_risk", u.risk_level, u.risk_score)
    print("secrets", len(s))
    print("b64", decode_base64(encode_base64("hola")))
    print("settings_ai", get_settings().ai_ready)
    print(local_network_info().splitlines()[0])
    print("ALL_OK")


if __name__ == "__main__":
    main()
