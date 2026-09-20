"""Interfaz CLI de Cleopatra420 — AI Assisteng de ciberseguridad."""

from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

from cleopatra420 import __app_name__, __version__
from cleopatra420.ai_client import AIClientError, CyberAIClient
from cleopatra420.config import PROVIDERS, get_settings, list_configured_providers
from cleopatra420.tools.encoding_tools import (
    decode_base64,
    decode_hex,
    encode_base64,
    encode_hex,
)
from cleopatra420.tools.hash_tools import SUPPORTED, hash_file, hash_text, identify_hash_length
from cleopatra420.tools.network_tools import local_network_info, resolve_host
from cleopatra420.tools.password_tools import analyze_password, generate_password
from cleopatra420.tools.secrets_scan import findings_as_text, scan_text_for_secrets
from cleopatra420.tools.url_check import analyze_url

THEME = Theme(
    {
        "info": "cyan",
        "warn": "yellow",
        "err": "bold red",
        "ok": "bold green",
        "accent": "magenta",
    }
)
console = Console(theme=THEME)

BANNER = r"""
   ____ _                       _              _  _  ____   ___
  / ___| | ___  ___  _ __   __ _| |_ _ __ __ _ | || ||___ \ / _ \
 | |   | |/ _ \/ _ \| '_ \ / _` | __| '__/ _` || || |_ __) | | | |
 | |___| |  __/ (_) | |_) | (_| | |_| | | (_| ||__   _/ __/| |_| |
  \____|_|\___|\___/| .__/ \__,_|\__|_|  \__,_|   |_||_____|\___/
                    |_|   AI Assisteng — Ciberseguridad defensiva
"""


def print_banner() -> None:
    console.print(BANNER, style="accent")
    console.print(
        f"  [info]{__app_name__}[/info] v{__version__}  ·  Solo uso ético y autorizado\n"
    )


def print_menu() -> None:
    table = Table(title="Menú principal", show_header=True, header_style="bold cyan")
    table.add_column("Opción", style="bold", width=8)
    table.add_column("Acción")
    table.add_row("1", "Chat IA de ciberseguridad (multi-proveedor)")
    table.add_row("2", "Generar contraseña segura")
    table.add_row("3", "Analizar fortaleza de contraseña")
    table.add_row("4", "Calcular hash (texto o archivo)")
    table.add_row("5", "Identificar tipo de hash por longitud")
    table.add_row("6", "Analizar URL sospechosa (phishing heuristics)")
    table.add_row("7", "Info de red local / resolver DNS")
    table.add_row("8", "Codificar / decodificar Base64 o Hex")
    table.add_row("9", "Escanear texto en busca de secretos filtrados")
    table.add_row("10", "Checklist de hardening básico")
    table.add_row("11", "Ver / cambiar proveedor de IA")
    table.add_row("0", "Salir")
    console.print(table)


def show_provider_status(ai: CyberAIClient) -> None:
    """Muestra el proveedor activo y las claves detectadas en .env."""
    s = ai.settings
    status = Table(title="Proveedores de IA", show_header=True, header_style="bold cyan")
    status.add_column("ID", style="bold", width=12)
    status.add_column("Nombre")
    status.add_column("Clave", width=10)
    status.add_column("Activo", width=8)

    active = s.provider
    for pid, label, has_key in list_configured_providers():
        key_col = "[ok]sí[/ok]" if has_key else "[warn]no[/warn]"
        act_col = "[ok]●[/ok]" if pid == active else ""
        status.add_row(pid, label, key_col, act_col)

    console.print(status)
    if s.ai_ready:
        console.print(
            f"[ok]Activo:[/ok] [cyan]{s.provider_label}[/cyan] · "
            f"modelo [cyan]{s.model}[/cyan] · base [dim]{s.base_url or '(default SDK)'}[/dim]"
        )
    else:
        console.print(
            Panel(
                s.setup_help(),
                title="IA no configurada",
                border_style="yellow",
            )
        )


def switch_provider(ai: CyberAIClient) -> None:
    """Cambia el proveedor en runtime (solo sesión actual; no reescribe .env)."""
    show_provider_status(ai)
    ids = list(PROVIDERS.keys())
    console.print(
        "\n[info]Cambio solo para esta sesión.[/info] "
        "Para hacerlo permanente, edita [cyan]AI_PROVIDER[/cyan] en [cyan].env[/cyan].\n"
    )
    choice = Prompt.ask(
        "Proveedor",
        choices=ids + ["cancelar"],
        default=ai.settings.provider if ai.settings.provider in ids else "xai",
    )
    if choice == "cancelar":
        console.print("[info]Sin cambios.[/info]")
        return

    os.environ["AI_PROVIDER"] = choice
    # Relee .env sin pisar el AI_PROVIDER que acabamos de fijar en la sesión
    load_dotenv(ai.settings.project_root / ".env", override=False)
    new_settings = get_settings()
    ai.reload_settings(new_settings)
    ai.reset()

    if ai.ready:
        console.print(
            f"[ok]Proveedor: {ai.provider_label}[/ok] · modelo [cyan]{ai.model}[/cyan]"
        )
    else:
        console.print(
            f"[warn]Proveedor {choice} seleccionado, pero falta API key "
            f"({new_settings.key_hint}).[/warn]"
        )
        console.print(
            Panel(new_settings.setup_help(), title="Configuración", border_style="yellow")
        )


def chat_loop(ai: CyberAIClient) -> None:
    if not ai.ready:
        console.print(
            Panel(
                ai.settings.setup_help(),
                title="IA no configurada",
                border_style="yellow",
            )
        )
        return

    console.print(
        f"[ok]Chat activo[/ok] · [cyan]{ai.provider_label}[/cyan] · "
        f"modelo [cyan]{ai.model}[/cyan]\n"
        "Escribe tu consulta de ciberseguridad. "
        "Comandos: [cyan]/reset[/cyan] limpia historial, "
        "[cyan]/provider[/cyan] muestra proveedor, "
        "[cyan]/back[/cyan] vuelve al menú.\n"
    )
    while True:
        try:
            user = Prompt.ask("[bold magenta]Tú[/bold magenta]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if not user:
            continue
        if user.lower() in {"/back", "/menu", "salir", "exit"}:
            break
        if user.lower() == "/reset":
            ai.reset()
            console.print("[info]Historial reiniciado.[/info]")
            continue
        if user.lower() in {"/provider", "/prov"}:
            show_provider_status(ai)
            continue
        try:
            with console.status(
                f"[info]Consultando {ai.provider_label}…[/info]", spinner="dots"
            ):
                answer = ai.chat(user)
            console.print(Panel(Markdown(answer), title="Cleopatra420", border_style="magenta"))
        except AIClientError as exc:
            console.print(f"[err]{exc}[/err]")


def tool_generate_password() -> None:
    length_s = Prompt.ask("Longitud", default="20")
    try:
        length = int(length_s)
        pwd = generate_password(length)
    except (ValueError, TypeError) as exc:
        console.print(f"[err]{exc}[/err]")
        return
    console.print(Panel(pwd, title="Contraseña generada", border_style="green"))
    console.print("[warn]Cópiala a un gestor de contraseñas. No la envíes por chat.[/warn]")


def tool_analyze_password() -> None:
    console.print("[info]La entrada no se guarda ni se envía a la IA.[/info]")
    try:
        pwd = getpass.getpass("Contraseña a analizar (oculta): ")
    except Exception:  # noqa: BLE001
        pwd = Prompt.ask("Contraseña a analizar")
    report = analyze_password(pwd)
    console.print(Panel(report.as_text(), title="Análisis de contraseña", border_style="cyan"))


def tool_hash() -> None:
    mode = Prompt.ask("¿Texto o archivo?", choices=["texto", "archivo"], default="texto")
    algo = Prompt.ask("Algoritmo", choices=list(SUPPORTED), default="sha256")
    try:
        if mode == "texto":
            text = Prompt.ask("Texto")
            digest = hash_text(text, algo)
        else:
            path = Prompt.ask("Ruta del archivo")
            digest = hash_file(path, algo)
        console.print(Panel(f"{algo}: {digest}", title="Hash", border_style="green"))
    except (ValueError, FileNotFoundError, OSError) as exc:
        console.print(f"[err]{exc}[/err]")


def tool_identify_hash() -> None:
    h = Prompt.ask("Pega el hash (hex)")
    hints = identify_hash_length(h)
    console.print(Panel("\n".join(hints), title="Posibles algoritmos", border_style="cyan"))


def tool_url() -> None:
    url = Prompt.ask("URL a analizar")
    report = analyze_url(url)
    style = "green" if report.risk_score < 25 else "yellow" if report.risk_score < 45 else "red"
    console.print(Panel(report.as_text(), title="Análisis de URL", border_style=style))


def tool_network() -> None:
    choice = Prompt.ask("¿Local o DNS?", choices=["local", "dns"], default="local")
    if choice == "local":
        console.print(Panel(local_network_info(), title="Red local", border_style="cyan"))
    else:
        host = Prompt.ask("Hostname o dominio")
        res = resolve_host(host)
        console.print(Panel(res.as_text(), title="Resolución DNS", border_style="cyan"))


def tool_encoding() -> None:
    action = Prompt.ask(
        "Acción",
        choices=["b64-enc", "b64-dec", "hex-enc", "hex-dec"],
        default="b64-enc",
    )
    data = Prompt.ask("Datos")
    try:
        if action == "b64-enc":
            out = encode_base64(data)
        elif action == "b64-dec":
            out = decode_base64(data)
        elif action == "hex-enc":
            out = encode_hex(data)
        else:
            out = decode_hex(data)
        console.print(Panel(out, title="Resultado", border_style="green"))
    except ValueError as exc:
        console.print(f"[err]{exc}[/err]")


def tool_secrets() -> None:
    console.print(
        "Pega el texto a escanear. Termina con una línea que contenga solo "
        "[cyan]END[/cyan] y Enter."
    )
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    text = "\n".join(lines)
    findings = scan_text_for_secrets(text)
    console.print(
        Panel(findings_as_text(findings), title="Escaneo de secretos", border_style="yellow")
    )


def tool_hardening_checklist() -> None:
    md = """
## Checklist de hardening básico (estación de trabajo / cuenta)

1. **Sistema**
   - Actualizaciones automáticas de SO y apps activadas
   - Firewall del host encendido
   - Disco cifrado (BitLocker / FileVault / LUKS)
2. **Identidad**
   - Gestor de contraseñas + contraseñas únicas
   - MFA en correo, banco, GitHub, cloud
   - Cuentas con privilegio mínimo (no vivir como admin)
3. **Red**
   - Wi‑Fi WPA3/WPA2-AES, contraseña fuerte del router
   - VPN corporativa solo a redes de confianza
   - Revisar dispositivos conectados al router
4. **Código / Dev**
   - `.env` y secretos fuera de Git (`.gitignore`)
   - Secret scanning en CI
   - Dependencias con `pip audit` / Dependabot
5. **Email y phishing**
   - No abrir adjuntos inesperados
   - Verificar dominio real de enlaces
   - Reportar sospechas al equipo de seguridad
6. **Backup y respuesta**
   - Copias 3-2-1 (3 copias, 2 medios, 1 offsite)
   - Plan básico: qué desconectar y a quién avisar

> Solo aplica cambios en sistemas que te pertenecen o con autorización.
"""
    console.print(Panel(Markdown(md), title="Hardening", border_style="green"))


def run() -> int:
    print_banner()
    settings = get_settings()
    ai = CyberAIClient(settings)

    if settings.ai_ready:
        console.print(
            f"[ok]IA lista[/ok] · [cyan]{settings.provider_label}[/cyan] · "
            f"modelo [cyan]{settings.model}[/cyan]"
        )
    else:
        console.print("[warn]IA sin API key — modo herramientas locales[/warn]")

    actions = {
        "1": lambda: chat_loop(ai),
        "2": tool_generate_password,
        "3": tool_analyze_password,
        "4": tool_hash,
        "5": tool_identify_hash,
        "6": tool_url,
        "7": tool_network,
        "8": tool_encoding,
        "9": tool_secrets,
        "10": tool_hardening_checklist,
        "11": lambda: switch_provider(ai),
    }

    while True:
        print_menu()
        try:
            choice = Prompt.ask("Elige opción", default="0").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[info]Hasta luego.[/info]")
            return 0
        if choice in {"0", "salir", "exit", "q"}:
            console.print("[info]Sesión terminada. Opera siempre con ética.[/info]")
            return 0
        action = actions.get(choice)
        if not action:
            console.print("[err]Opción no válida.[/err]")
            continue
        try:
            action()
        except KeyboardInterrupt:
            console.print("\n[warn]Operación cancelada.[/warn]")
        console.print()


def main() -> None:
    # Asegura imports relativos al proyecto
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    raise SystemExit(run())


if __name__ == "__main__":
    main()
