"""Entrypoint FastAPI del POS Maschinario · Bazar (ARCHITECTURE.md §4).

Cableado del shell: sesión, estáticos, plantillas Jinja2 e inclusión de routers.
La lógica de negocio vive en `services/`; las vistas en `templates/`.

    uvicorn app.main:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_DEV_DEFAULT, get_settings
from app.deps import NoOpenTurno, NotAuthenticated, NotAuthorized, templates
from app.routers import (
    auth,
    catalogo,
    cobro,
    configuracion,
    corte,
    devolucion,
    reimpresion,
    reportes,
    usuarios,
    venta,
)

BASE_DIR = Path(__file__).resolve().parent

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("pos")
_settings = get_settings()

# Aviso fuerte si el secreto de sesión sigue siendo el de desarrollo: en ese caso
# las cookies de sesión son falsificables. Debe definirse APP_SECRET_KEY en .env.
if _settings.app_secret_key == SECRET_DEV_DEFAULT:
    log.warning(
        "APP_SECRET_KEY usa el valor de desarrollo: define uno propio en .env "
        "antes de operar (las cookies de sesión deben firmarse con un secreto real)."
    )

app = FastAPI(title="Maschinario · Bazar — POS")
# Cookie de sesión endurecida: httponly (default de Starlette), SameSite=Strict
# (mitiga CSRF en los POST; el POS sirve solo en 127.0.0.1), expiración y, en
# producción tras HTTPS, secure.
app.add_middleware(
    SessionMiddleware,
    secret_key=_settings.app_secret_key,
    same_site="strict",
    https_only=_settings.session_https_only,
    max_age=_settings.session_max_age,
)


@app.middleware("http")
async def _security_headers(request: Request, call_next):
    """Cabeceras de seguridad en todas las respuestas (defensa básica web)."""
    response = await call_next(request)
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    # CSP: solo recursos propios. Se permite 'unsafe-inline' porque las vistas
    # usan estilos y un par de scripts en línea; aun así bloquea fuentes externas
    # y el framing (anti-clickjacking / anti-inyección de recursos remotos).
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data:; "
        "script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
    )
    return response


# Estáticos (CSS de marca, JS mínimo para foco/atajos).
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.exception_handler(NotAuthenticated)
async def _not_authenticated(
    request: Request, exc: NotAuthenticated
) -> RedirectResponse:
    return RedirectResponse("/login", status_code=303)


@app.exception_handler(NoOpenTurno)
async def _no_open_turno(request: Request, exc: NoOpenTurno) -> RedirectResponse:
    return RedirectResponse("/turno", status_code=303)


@app.exception_handler(NotAuthorized)
async def _not_authorized(request: Request, exc: NotAuthorized):
    return templates.TemplateResponse(request, "403.html", {}, status_code=403)


# Routers (HTTP/HTMX) — capa de presentación; sin lógica de negocio aquí.
app.include_router(auth.router)
app.include_router(venta.router)
app.include_router(cobro.router)
app.include_router(devolucion.router)
app.include_router(catalogo.router)
app.include_router(corte.router)
app.include_router(reportes.router)
app.include_router(reimpresion.router)
app.include_router(usuarios.router)
app.include_router(configuracion.router)


@app.get("/")
def home() -> RedirectResponse:
    """Raíz → pantalla de venta (que a su vez exige login/turno)."""
    return RedirectResponse("/venta", status_code=303)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Sonda de vida (no toca DB)."""
    return {"status": "ok", "app": get_settings().app_business_name}
