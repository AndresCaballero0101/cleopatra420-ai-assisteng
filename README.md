# Cleopatra420 — AI Assisteng de Ciberseguridad

<p align="center">
  <img src="docs/banner.jpg" alt="Cleopatra420 — AI Assisteng de ciberseguridad defensiva" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/AndresCaballero0101/cleopatra420-ai-assisteng/stargazers"><img src="https://img.shields.io/github/stars/AndresCaballero0101/cleopatra420-ai-assisteng?style=for-the-badge" alt="Stars" /></a>
  <a href="https://github.com/AndresCaballero0101/cleopatra420-ai-assisteng/blob/main/LICENSE"><img src="https://img.shields.io/github/license/AndresCaballero0101/cleopatra420-ai-assisteng?style=for-the-badge" alt="License" /></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/IA-SpaceXAI%20%2F%20Grok-magenta?style=for-the-badge" alt="SpaceXAI Grok" />
  <img src="https://img.shields.io/badge/Focus-Defensive%20Security-green?style=for-the-badge" alt="Defensive Security" />
</p>

Asistente de **ciberseguridad defensiva** en Python con herramientas locales y chat IA potenciado por **SpaceXAI / xAI (Grok)**.

> **Uso ético únicamente.** Este proyecto está pensado para proteger sistemas, aprender defensa y hacer análisis legítimos. No incluye exploits ni ayuda a atacar sistemas de terceros.

**Repo:** [github.com/AndresCaballero0101/cleopatra420-ai-assisteng](https://github.com/AndresCaballero0101/cleopatra420-ai-assisteng)

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

### Vista del menú CLI

```
 1  Chat IA de ciberseguridad (SpaceXAI / Grok)
 2  Generar contraseña segura
 3  Analizar fortaleza de contraseña
 4  Calcular hash (texto o archivo)
 5  Identificar tipo de hash por longitud
 6  Analizar URL sospechosa (phishing heuristics)
 7  Info de red local / resolver DNS
 8  Codificar / decodificar Base64 o Hex
 9  Escanear texto en busca de secretos filtrados
10  Checklist de hardening básico
 0  Salir
```

---

## Requisitos

- Python **3.10+** (probado con 3.13)
- Windows, Linux o macOS
- (Opcional) API key de [console.x.ai](https://console.x.ai) para el chat IA

## Instalación

```bash
# Clonar
git clone https://github.com/AndresCaballero0101/cleopatra420-ai-assisteng.git
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
cleopatra420-ai-assisteng/
├── main.py
├── AI assisteng Cleopatra420.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
├── docs/
│   └── banner.jpg
├── scripts/
│   └── smoke_test.py
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
- Si encuentras una vulnerabilidad en este repo, reporta de forma responsable abriendo un [issue](https://github.com/AndresCaballero0101/cleopatra420-ai-assisteng/issues).

---

## Stack

- Python 3  
- [Rich](https://github.com/Textualize/rich) — CLI  
- [OpenAI SDK](https://github.com/openai/openai-python) → API compatible **xAI / SpaceXAI**  
- `python-dotenv`, `requests`

---

## Topics

`cybersecurity` · `python` · `ai` · `security` · `defensive-security` · `ethical-hacking` · `cli` · `xai` · `grok`

---

## Licencia

MIT — ver [LICENSE](LICENSE).

## Autor

**AndresCaballero0101** — [GitHub](https://github.com/AndresCaballero0101)  
**Cleopatra420 / AI Assisteng** — proyecto de ciberseguridad defensiva.

Si te resulta útil, deja una ⭐ en el repositorio. ¡Gracias!
