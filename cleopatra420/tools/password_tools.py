"""Generación y análisis de contraseñas (uso legítimo / hardening)."""

from __future__ import annotations

import math
import re
import secrets
import string
from dataclasses import dataclass


COMMON_PASSWORDS = frozenset(
    {
        "123456",
        "password",
        "12345678",
        "qwerty",
        "123456789",
        "12345",
        "1234",
        "111111",
        "1234567",
        "dragon",
        "123123",
        "baseball",
        "abc123",
        "football",
        "monkey",
        "letmein",
        "shadow",
        "master",
        "666666",
        "qwertyuiop",
        "123321",
        "mustang",
        "1234567890",
        "michael",
        "654321",
        "superman",
        "1qaz2wsx",
        "7777777",
        "121212",
        "000000",
        "qazwsx",
        "123qwe",
        "killer",
        "trustno1",
        "jordan",
        "jennifer",
        "zxcvbnm",
        "asdfgh",
        "hunter",
        "buster",
        "soccer",
        "harley",
        "batman",
        "andrew",
        "tigger",
        "sunshine",
        "iloveyou",
        "2000",
        "charlie",
        "robert",
        "thomas",
        "hockey",
        "ranger",
        "daniel",
        "starwars",
        "klaster",
        "112233",
        "george",
        "computer",
        "michelle",
        "jessica",
        "pepper",
        "1111",
        "zxcvbn",
        "555555",
        "11111111",
        "131313",
        "freedom",
        "777777",
        "pass",
        "maggie",
        "159753",
        "aaaaaa",
        "ginger",
        "princess",
        "joshua",
        "cheese",
        "amanda",
        "summer",
        "love",
        "ashley",
        "nicole",
        "chelsea",
        "biteme",
        "matthew",
        "access",
        "yankees",
        "987654321",
        "dallas",
        "austin",
        "thunder",
        "taylor",
        "matrix",
        "mobile",
        "admin",
        "root",
        "toor",
        "passw0rd",
        "p@ssw0rd",
        "welcome",
        "login",
    }
)


@dataclass
class PasswordReport:
    password_len: int
    score: int  # 0-100
    strength: str
    entropy_bits: float
    issues: list[str]
    recommendations: list[str]

    def as_text(self) -> str:
        lines = [
            f"Longitud: {self.password_len}",
            f"Puntuación: {self.score}/100 ({self.strength})",
            f"Entropía estimada: {self.entropy_bits:.1f} bits",
            "",
            "Problemas detectados:",
        ]
        if self.issues:
            lines.extend(f"  - {i}" for i in self.issues)
        else:
            lines.append("  (ninguno grave)")
        lines.append("")
        lines.append("Recomendaciones:")
        lines.extend(f"  - {r}" for r in self.recommendations)
        return "\n".join(lines)


def generate_password(
    length: int = 20,
    *,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = True,
) -> str:
    """Genera una contraseña criptográficamente segura."""
    if length < 8:
        raise ValueError("La longitud mínima recomendada es 8 (usa al menos 16 en producción).")
    if length > 128:
        raise ValueError("Longitud máxima: 128.")

    alphabet = ""
    required: list[str] = []
    if use_lower:
        pool = string.ascii_lowercase
        if exclude_ambiguous:
            pool = pool.replace("l", "").replace("o", "")
        alphabet += pool
        required.append(secrets.choice(pool))
    if use_upper:
        pool = string.ascii_uppercase
        if exclude_ambiguous:
            pool = pool.replace("I", "").replace("O", "")
        alphabet += pool
        required.append(secrets.choice(pool))
    if use_digits:
        pool = string.digits
        if exclude_ambiguous:
            pool = pool.replace("0", "").replace("1", "")
        alphabet += pool
        required.append(secrets.choice(pool))
    if use_symbols:
        pool = "!@#$%^&*()-_=+[]{};:,.?/"
        alphabet += pool
        required.append(secrets.choice(pool))

    if not alphabet:
        raise ValueError("Debes habilitar al menos un tipo de carácter.")

    remaining = [secrets.choice(alphabet) for _ in range(length - len(required))]
    chars = required + remaining
    # Mezcla Fisher-Yates con secrets
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def analyze_password(password: str) -> PasswordReport:
    issues: list[str] = []
    recommendations: list[str] = []
    score = 0
    length = len(password)

    if length == 0:
        return PasswordReport(
            password_len=0,
            score=0,
            strength="Vacía",
            entropy_bits=0.0,
            issues=["No se proporcionó contraseña."],
            recommendations=["Usa un gestor de contraseñas y genera una de 16+ caracteres."],
        )

    # Conjuntos de caracteres
    classes = 0
    if re.search(r"[a-z]", password):
        classes += 1
        score += 10
    else:
        issues.append("Sin minúsculas.")
    if re.search(r"[A-Z]", password):
        classes += 1
        score += 10
    else:
        issues.append("Sin mayúsculas.")
    if re.search(r"\d", password):
        classes += 1
        score += 10
    else:
        issues.append("Sin dígitos.")
    if re.search(r"[^A-Za-z0-9]", password):
        classes += 1
        score += 15
    else:
        issues.append("Sin símbolos especiales.")

    # Longitud
    if length < 8:
        issues.append("Demasiado corta (< 8).")
        score += max(0, length * 2)
    elif length < 12:
        issues.append("Corta para estándares modernos (< 12).")
        score += 15
    elif length < 16:
        score += 25
    else:
        score += 35

    # Patrones débiles
    lower = password.lower()
    if lower in COMMON_PASSWORDS or password in COMMON_PASSWORDS:
        issues.append("Aparece en listas comunes de contraseñas filtradas.")
        score = min(score, 15)
    if re.search(r"(.)\1{2,}", password):
        issues.append("Repetición de caracteres (aaa, 111...).")
        score -= 10
    if re.search(
        r"(0123|1234|2345|3456|4567|5678|6789|7890|abcd|bcde|cdef|qwer|asdf|zxcv)",
        lower,
    ):
        issues.append("Secuencia predecible detectada.")
        score -= 10
    if re.search(r"(19|20)\d{2}", password):
        issues.append("Parece incluir un año (fácil de adivinar).")
        score -= 5

    # Entropía aproximada
    pool = 0
    if re.search(r"[a-z]", password):
        pool += 26
    if re.search(r"[A-Z]", password):
        pool += 26
    if re.search(r"\d", password):
        pool += 10
    if re.search(r"[^A-Za-z0-9]", password):
        pool += 32
    entropy = length * math.log2(pool) if pool else 0.0

    score = max(0, min(100, score))
    if score >= 80:
        strength = "Muy fuerte"
    elif score >= 60:
        strength = "Fuerte"
    elif score >= 40:
        strength = "Media"
    elif score >= 20:
        strength = "Débil"
    else:
        strength = "Muy débil"

    recommendations.append("Usa un gestor de contraseñas (Bitwarden, 1Password, KeePassXC...).")
    recommendations.append("Activa 2FA/MFA en todas las cuentas importantes.")
    recommendations.append("Nunca reutilices la misma contraseña en varios sitios.")
    if length < 16:
        recommendations.append("Apunta a 16–24 caracteres aleatorios o una passphrase larga.")
    if classes < 3:
        recommendations.append("Combina mayúsculas, minúsculas, números y símbolos.")
    if entropy < 60:
        recommendations.append("Aumenta longitud: cada carácter extra suma mucha entropía.")

    return PasswordReport(
        password_len=length,
        score=score,
        strength=strength,
        entropy_bits=entropy,
        issues=issues,
        recommendations=recommendations,
    )
