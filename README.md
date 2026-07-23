# Cleopatra420 — AI Assisteng de Ciberseguridad

Asistente de **ciberseguridad defensiva** en Python con herramientas locales y chat IA potenciado por **SpaceXAI / xAI (Grok)**.

> **Uso ético únicamente.** Este proyecto está pensado para proteger sistemas, aprender defensa y hacer análisis legítimos. No incluye exploits ni ayuda a atacar sistemas de terceros.

---

## Características

| Módulo | Descripción |
|--------|-------------|
| **Chat IA** | Consultas de hardening, phishing, logs, buenas prácticas (Grok vía API xAI) |
| **Contraseñas** | Generador criptográficamente seguro + análisis de fortaleza/entropía |
| **Hashes** | MD5, SHA-1/256/384/512, BLAKE2 (texto y archivos) + identificación por longitud |
| **URLs** | Heurísticas anti-phishing (IP literal, TLD abusados, suplantación de marca…) |
| **Red** | Info de red local y resolución DNS |
| **Encoding** | Base64 y Hex (encode/decode) para análisis forense ligero |
| **Secret scan** | Detecta API keys, JWT, tokens y claves privadas en texto pegado |
| **Checklist** | Hardening básico de estación de trabajo y cuentas |

---

## Requisitos

- Python **3.10+** (probado con 3.13)
- Windows, Linux o macOS
- (Opcional) API key de [console.x.ai](https://console.x.ai) para el chat IA

## Instalación

```bash
# Clonar
git clone https://github.com/TU_USUARIO/cleopatra420-ai-assisteng.git
cd cleopatra420-ai-assisteng

# Dependencias
py -3 -m pip install -r requirements.txt

# Configurar API (opcional pero recomendado para el chat)
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
# Edita .env y pega XAI_API_KEY=...
```

## Uso

```bash
py -3 main.py
# o
py -3 -m cleopatra420
# o
py -3 "AI assisteng Cleopatra420.py"
```

Menú interactivo:

1. Chat IA de ciberseguridad  
2. Generar contraseña  
3. Analizar contraseña  
4. Calcular hash  
5. Identificar hash  
6. Analizar URL  
7. Red local / DNS  
8. Base64 / Hex  
9. Escanear secretos  
10. Checklist de hardening  
0. Salir  

### Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `XAI_API_KEY` | Clave de API xAI / SpaceXAI | — |
| `XAI_MODEL` | Modelo | `grok-4.5` |
| `XAI_BASE_URL` | Endpoint OpenAI-compatible | `https://api.x.ai/v1` |

Sin API key puedes usar **todas las herramientas locales** (opciones 2–10).

---

## Estructura del proyecto

```
AI assisteng/
├── main.py
├── AI assisteng Cleopatra420.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
└── cleopatra420/
    ├── __init__.py
    ├── __main__.py
    ├── config.py
    ├── ai_client.py
    ├── cli.py
    └── tools/
        ├── password_tools.py
        ├── hash_tools.py
        ├── network_tools.py
        ├── url_check.py
        ├── encoding_tools.py
        └── secrets_scan.py
```

---

## Política de seguridad y ética

- Solo opera en **sistemas propios** o con **autorización escrita**.
- El prompt del modelo **rechaza** pedidos ofensivos (exploits, malware, intrusión).
- No subas tu `.env` ni claves reales a Git (ya está en `.gitignore`).
- Si encuentras una vulnerabilidad en este repo, reporta de forma responsable al maintainer.

---

## Stack

- Python 3  
- [Rich](https://github.com/Textualize/rich) — CLI  
- [OpenAI SDK](https://github.com/openai/openai-python) → API compatible **xAI / SpaceXAI**  
- `python-dotenv`, `requests`

---

## Licencia

MIT — ver [LICENSE](LICENSE).

## Autor

**Cleopatra420 / AI Assisteng** — proyecto de ciberseguridad defensiva.
