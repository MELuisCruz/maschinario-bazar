"""Hash y verificación de PIN de cajeros (CLAUDE.md §7: secretos nunca en claro).

Usa la librería `bcrypt` directamente. El PIN se guarda solo como `pin_hash`
(DATA_MODEL.md). bcrypt limita a 72 bytes; un PIN siempre cabe.
"""

from __future__ import annotations

import time

import bcrypt

# Factor de costo de bcrypt (rounds). 12 es el default robusto; explícito para no
# debilitarlo por accidente y poder subirlo en el futuro.
BCRYPT_ROUNDS = 12


def hash_pin(pin: str) -> str:
    """Devuelve el hash bcrypt de un PIN."""
    return bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt(BCRYPT_ROUNDS)).decode(
        "ascii"
    )


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verifica un PIN contra su hash; nunca lanza por hash inválido."""
    try:
        return bcrypt.checkpw(pin.encode("utf-8"), pin_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False


# --- Anti fuerza bruta del PIN (estado en memoria del proceso) ---------------
# El PIN es una credencial corta y brute-forceable. Tras N fallos por usuario en
# la ventana, se bloquea temporalmente. Estado en memoria: el POS es un único
# proceso uvicorn; al reiniciar se limpia (aceptable para este caso de uso).

_fallos: dict[str, list[float]] = {}
_bloqueo_hasta: dict[str, float] = {}


def login_segundos_bloqueo(usuario: str, *, ahora: float | None = None) -> int:
    """Segundos restantes de bloqueo para `usuario` (0 si no está bloqueado)."""
    ahora = time.monotonic() if ahora is None else ahora
    return max(0, int(_bloqueo_hasta.get(usuario, 0.0) - ahora))


def registrar_login_fallido(
    usuario: str, *, max_intentos: int, bloqueo_seg: int, ahora: float | None = None
) -> None:
    """Anota un intento fallido; al superar `max_intentos` activa el bloqueo."""
    ahora = time.monotonic() if ahora is None else ahora
    recientes = [t for t in _fallos.get(usuario, []) if ahora - t < bloqueo_seg]
    recientes.append(ahora)
    if len(recientes) >= max_intentos:
        _bloqueo_hasta[usuario] = ahora + bloqueo_seg
        _fallos[usuario] = []
    else:
        _fallos[usuario] = recientes


def registrar_login_exitoso(usuario: str) -> None:
    """Limpia el contador de fallos/bloqueo tras un login correcto."""
    _fallos.pop(usuario, None)
    _bloqueo_hasta.pop(usuario, None)


def reset_login_guard() -> None:
    """Limpia todo el estado anti-fuerza-bruta (uso en pruebas)."""
    _fallos.clear()
    _bloqueo_hasta.clear()
