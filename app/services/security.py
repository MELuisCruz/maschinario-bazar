"""Hash y verificación de PIN de cajeros (CLAUDE.md §7: secretos nunca en claro).

Usa la librería `bcrypt` directamente. El PIN se guarda solo como `pin_hash`
(DATA_MODEL.md). bcrypt limita a 72 bytes; un PIN siempre cabe.
"""

from __future__ import annotations

import bcrypt


def hash_pin(pin: str) -> str:
    """Devuelve el hash bcrypt de un PIN."""
    return bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verifica un PIN contra su hash; nunca lanza por hash inválido."""
    try:
        return bcrypt.checkpw(pin.encode("utf-8"), pin_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False
