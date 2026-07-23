"""Utilidades de hashing para verificación de integridad (uso legítimo)."""

from __future__ import annotations

import hashlib
from pathlib import Path


SUPPORTED = ("md5", "sha1", "sha256", "sha384", "sha512", "blake2b", "blake2s")


def hash_text(text: str, algorithm: str = "sha256") -> str:
    algo = algorithm.lower().strip()
    if algo not in SUPPORTED:
        raise ValueError(f"Algoritmo no soportado: {algo}. Usa: {', '.join(SUPPORTED)}")
    data = text.encode("utf-8")
    if algo == "blake2b":
        return hashlib.blake2b(data).hexdigest()
    if algo == "blake2s":
        return hashlib.blake2s(data).hexdigest()
    h = hashlib.new(algo)
    h.update(data)
    return h.hexdigest()


def hash_file(path: str | Path, algorithm: str = "sha256", chunk_size: int = 1024 * 1024) -> str:
    algo = algorithm.lower().strip()
    if algo not in SUPPORTED:
        raise ValueError(f"Algoritmo no soportado: {algo}. Usa: {', '.join(SUPPORTED)}")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"No existe el archivo: {p}")

    if algo == "blake2b":
        h = hashlib.blake2b()
    elif algo == "blake2s":
        h = hashlib.blake2s()
    else:
        h = hashlib.new(algo)

    with p.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def identify_hash_length(hex_hash: str) -> list[str]:
    """Infiere algoritmos posibles por longitud del hex (heurística)."""
    cleaned = hex_hash.strip().lower().replace("0x", "")
    if not cleaned or any(c not in "0123456789abcdef" for c in cleaned):
        return ["No parece un hash hexadecimal válido."]
    mapping = {
        32: ["MD5", "NTLM (a veces)"],
        40: ["SHA-1"],
        56: ["SHA-224"],
        64: ["SHA-256", "BLAKE2s"],
        96: ["SHA-384"],
        128: ["SHA-512", "BLAKE2b"],
    }
    candidates = mapping.get(len(cleaned), [f"Longitud {len(cleaned)} hex chars — desconocido"])
    return [f"Longitud {len(cleaned)} → posible: {', '.join(candidates)}"]
