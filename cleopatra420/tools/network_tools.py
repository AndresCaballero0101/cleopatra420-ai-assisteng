"""Información de red local y resolución DNS (diagnóstico legítimo)."""

from __future__ import annotations

import platform
import socket
from dataclasses import dataclass


@dataclass
class HostResolution:
    host: str
    ip: str | None
    reverse: str | None
    error: str | None = None

    def as_text(self) -> str:
        if self.error:
            return f"Host: {self.host}\nError: {self.error}"
        lines = [f"Host: {self.host}", f"IP: {self.ip or 'N/A'}"]
        if self.reverse:
            lines.append(f"Reverse DNS: {self.reverse}")
        return "\n".join(lines)


def local_network_info() -> str:
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except OSError:
        local_ip = "desconocida"

    # IP de salida típica hacia Internet (sin enviar tráfico real de ataque)
    outbound_ip = "desconocida"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("1.1.1.1", 80))
        outbound_ip = s.getsockname()[0]
        s.close()
    except OSError:
        pass

    lines = [
        f"Sistema: {platform.system()} {platform.release()} ({platform.machine()})",
        f"Hostname: {hostname}",
        f"IP local (gethostbyname): {local_ip}",
        f"IP de interfaz de salida: {outbound_ip}",
        f"Python socket family preferida: {socket.AF_INET}",
        "",
        "Nota: esta vista es solo diagnóstica del equipo local.",
        "No se realiza escaneo de puertos ni ataques a terceros.",
    ]
    return "\n".join(lines)


def resolve_host(host: str) -> HostResolution:
    host = host.strip()
    if not host:
        return HostResolution(host=host, ip=None, reverse=None, error="Host vacío.")
    # Bloquear patrones claramente maliciosos de inyección
    if any(c in host for c in " \t\n\r;|&`$"):
        return HostResolution(
            host=host, ip=None, reverse=None, error="Host inválido (caracteres no permitidos)."
        )
    try:
        ip = socket.gethostbyname(host)
    except OSError as exc:
        return HostResolution(host=host, ip=None, reverse=None, error=str(exc))
    reverse = None
    try:
        reverse = socket.gethostbyaddr(ip)[0]
    except OSError:
        reverse = None
    return HostResolution(host=host, ip=ip, reverse=reverse)
