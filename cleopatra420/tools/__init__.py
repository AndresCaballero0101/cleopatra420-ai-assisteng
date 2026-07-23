"""Herramientas locales de ciberseguridad defensiva."""

from cleopatra420.tools.encoding_tools import decode_base64, encode_base64, decode_hex, encode_hex
from cleopatra420.tools.hash_tools import hash_text, identify_hash_length
from cleopatra420.tools.network_tools import local_network_info, resolve_host
from cleopatra420.tools.password_tools import analyze_password, generate_password
from cleopatra420.tools.secrets_scan import scan_text_for_secrets
from cleopatra420.tools.url_check import analyze_url

__all__ = [
    "analyze_password",
    "generate_password",
    "hash_text",
    "identify_hash_length",
    "local_network_info",
    "resolve_host",
    "analyze_url",
    "encode_base64",
    "decode_base64",
    "encode_hex",
    "decode_hex",
    "scan_text_for_secrets",
]
