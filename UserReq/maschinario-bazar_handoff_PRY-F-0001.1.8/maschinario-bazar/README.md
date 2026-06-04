# Maschinario · Bazar — POS (semilla de repo)

Punto de venta web que corre **localmente** en una caja. Stack: **FastAPI + Uvicorn · Jinja2 + HTMX (no SPA) · PostgreSQL (docker-compose) · SQLAlchemy + Alembic · python-escpos · Mercado Pago API de Orders**.

> Este paquete es el **residuo de diseño** (proyecto PRY-F-0001.1.8, cerrado) listo para que **Claude Code** genere la app. No contiene código de la app todavía: lo produce Claude Code consumiendo estos documentos.

## Orden de lectura (para Claude Code)
1. `CLAUDE.md` (raíz) — reglas de construcción, versionado, pruebas, GitHub.
2. `docs/PRD.md` — alcance v1 y no-goals.
3. `docs/ARCHITECTURE.md` — stack, topología híbrida, estructura de carpetas, ADRs.
4. `docs/DATA_MODEL.md` — esquema PostgreSQL, invariantes, IVA 16%.
5. `docs/INTEGRATION_MP_POINT.md` — contrato API de Orders (idempotencia, offline, reembolso).
6. `docs/THERMAL_TICKET_SPEC.md` — ticket ESC/POS 80 mm (RP850), reimpresión.
7. `docs/PERIPHERALS.md` — lector NETUM C750 (HID wedge), foco, teclado/mouse.
8. `docs/UI_SPEC.md` — pantallas, componentes, tokens, foco del lector, parciales HTMX.
9. `docs/ACCEPTANCE_TESTS.md` — criterios Dado/Cuando/Entonces → pytest.

`docs/mockup/` es **referencia visual** (prototipo React). **No se copia como código**: la UI de producción es Jinja2 + HTMX según `UI_SPEC.md` (ADR-005). Abrir `docs/mockup/index.html` en un navegador para ver el look & feel (PIN demo: 2 4 6 8).

`handoff/` contiene el checklist y la guía paso a paso para arrancar Claude Code (operador).

## Arranque (resumen; detalle en `CLAUDE.md` §4)
```bash
docker compose up -d db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Notas de estado del residuo (leer antes de construir)
- `docs/UI_SPEC.md` está en **v2.0 reconstruido** desde el mockup v2 y las referencias cruzadas (el v1.0 original no estaba disponible). **Pendiente de validación del titular.** Los otros 8 documentos son los aprobados.
- Encabezados de versión: `ARCHITECTURE.md` y `DATA_MODEL.md` muestran "0.1 (borrador)" en su título aunque el cierre del proyecto (Acta v3) los marca **final 1.0**. Su contenido es el aprobado; solo el rótulo quedó sin actualizar.
- Pendientes externos (no bloquean el código): vincular Point Smart 2 (`terminal_id`), leer `idVendor/idProduct` y codepage de la RP850 (`lsusb`), credenciales MP de producción (MX/MXN), validación CFDI con contador.

---
*Semilla de repo · PRY-F-0001.1.8 Maschinario – Bazar · 01-jun-2026.*
