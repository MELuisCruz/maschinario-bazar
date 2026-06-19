"""Configuración de la app leída desde el entorno (CLAUDE.md §3).

Secretos solo vía entorno; jamás en código ni en commits. La plantilla de
variables vive en `.env.example`; el `.env` real no se versiona.
"""

from __future__ import annotations

from functools import lru_cache
from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Valor centinela del secreto de desarrollo: si sigue en uso, se avisa al
# arrancar (no debe usarse en producción).
SECRET_DEV_DEFAULT = "dev-secret-change-me"


class Settings(BaseSettings):
    """Variables de entorno de la aplicación."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos
    database_url: str = "postgresql+psycopg://pos:pos@localhost:5432/maschinario"

    # Mercado Pago Point (API de Orders)
    mp_access_token: str = ""
    mp_terminal_id: str = ""

    # Impresora térmica ESC/POS (USB)
    printer_usb_vendor: str = ""
    printer_usb_product: str = ""

    # Negocio / fiscal
    app_business_name: str = "Maschinario · Bazar"
    app_iva_rate: Decimal = Decimal("0.16")

    # Sesión (cookie firmada). En producción debe venir del entorno; el default
    # solo sirve para desarrollo/pruebas locales.
    app_secret_key: str = SECRET_DEV_DEFAULT
    # Endurecimiento de sesión. `session_https_only=True` SOLO detrás de HTTPS
    # (con HTTP la cookie no viajaría y nadie podría iniciar sesión).
    session_https_only: bool = False
    session_max_age: int = 60 * 60 * 12  # la sesión expira sola (12 h)
    # Anti fuerza bruta del PIN: N intentos fallidos → bloqueo temporal (seg).
    login_max_intentos: int = 5
    login_bloqueo_seg: int = 300


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración (cacheada) de la app."""
    return Settings()
