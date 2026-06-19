"""Entrypoint FastAPI del POS Maschinario · Bazar (ARCHITECTURE.md §4).

Cableado del shell: sesión, estáticos, plantillas Jinja2 e inclusión de routers.
La lógica de negocio vive en `services/`; las vistas en `templates/`.

    uvicorn app.main:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
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

app = FastAPI(title="Maschinario · Bazar — POS")
app.add_middleware(SessionMiddleware, secret_key=get_settings().app_secret_key)

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
