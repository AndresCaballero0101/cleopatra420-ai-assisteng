"""Codificación / decodificación para análisis forense ligero."""

from __future__ import annotations

import base64
import binascii


def encode_base64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def decode_base64(data: str) -> str:
    cleaned = "".join(data.strip().split())
    # padding
    pad = (-len(cleaned)) % 4
    cleaned += "=" * pad
    try:
        raw = base64.b64decode(cleaned, validate=False)
    except binascii.Error as exc:
        raise ValueError(f"Base64 inválido: {exc}") from exc
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.hex()


def encode_hex(text: str) -> str:
    return text.encode("utf-8").hex()


def decode_hex(data: str) -> str:
    cleaned = data.strip().replace(" ", "").replace("0x", "")
    try:
        raw = bytes.fromhex(cleaned)
    except ValueError as exc:
        raise ValueError(f"Hex inválido: {exc}") from exc
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")
