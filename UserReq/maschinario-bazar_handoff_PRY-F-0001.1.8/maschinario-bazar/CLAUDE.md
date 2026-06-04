# CLAUDE.md · Instrucciones para Claude Code — POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 1.0 (para aprobación del titular)
**Fecha:** 01-jun-2026

> Documento que gobierna **cómo Claude Code construye, versiona, prueba y publica** la app. Consume el resto del residuo: `PRD.md`, `ARCHITECTURE.md`, `DATA_MODEL.md`, `INTEGRATION_MP_POINT.md`, `THERMAL_TICKET_SPEC.md`, `PERIPHERALS.md`, `ACCEPTANCE_TESTS.md`, `UI_SPEC.md`.

---

## 1. Qué construir

Un **POS de bazar** web que corre **localmente** en una caja: FastAPI + Uvicorn, Jinja2 + HTMX (no SPA), PostgreSQL (docker-compose), SQLAlchemy + Alembic, `python-escpos`, integración Mercado Pago **API de Orders** para Point. Alcance v1 en `PRD.md`. **No** rediseñar: las decisiones están congeladas; ante disonancia real, **detente y pregunta**.

---

## 2. Estructura del repo

Seguir la estructura de `ARCHITECTURE.md` §4. Repo **privado**.

```
maschinario-bazar/
├── docker-compose.yml      # servicio db (postgres) + volumen
├── .env.example            # plantilla de variables (sin secretos reales)
├── requirements.txt
├── alembic/                # migraciones
├── app/                    # main, config, db, models, routers, services, templates, static
└── tests/                  # pytest
```

---

## 3. Variables de entorno (`.env`)

`.env` **nunca** se versiona (va en `.gitignore`); se versiona `.env.example`.

```
DATABASE_URL=postgresql+psycopg://pos:pos@localhost:5432/maschinario
MP_ACCESS_TOKEN=        # token de Mercado Pago (secreto)
MP_TERMINAL_ID=         # id de la terminal Point
PRINTER_USB_VENDOR=     # idVendor de la impresora (hex)
PRINTER_USB_PRODUCT=    # idProduct de la impresora (hex)
APP_BUSINESS_NAME=Maschinario · Bazar
APP_IVA_RATE=0.16
```

---

## 4. Arranque local

```bash
# 1) Base de datos (contenedor)
docker compose up -d db

# 2) App (nativa en el host, para acceso USB a la impresora)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La DB es **precondición**: la app no inicia operaciones de venta sin `db` arriba (ver `ARCHITECTURE.md` §6).

---

## 5. Respaldo y restauración

```bash
# Respaldo
docker compose exec db pg_dump -U pos maschinario > backup_$(date +%F).sql
# Restauración
cat backup_YYYY-MM-DD.sql | docker compose exec -T db psql -U pos maschinario
```

`SUPUESTO` Respaldo manual/diario en v1; automatizar (cron) si el titular lo pide.

---

## 6. Pruebas

- Framework: **pytest**. Implementar los criterios de `ACCEPTANCE_TESTS.md`.
- Integración MP: contra **simulate-order** / mocks; **nunca** cobros reales en CI.
- Impresión: mock de `python-escpos` (verificar comandos, no hardware).
- Política de redondeo monetario: **HALF_UP a 2 decimales**, probada explícitamente.

```bash
pytest -q
```

---

## 7. Convenciones de código

- **Python** con type hints; formateo **black**; lint **ruff**; imports ordenados.
- Capas claras: `routers` (HTTP/HTMX) → `services` (lógica) → `models` (ORM). Sin lógica de negocio en plantillas.
- Plantillas Jinja2 con **parciales** para los swaps HTMX (ver `UI_SPEC.md` §7).
- Migraciones: **toda** modificación de esquema pasa por **Alembic** (no `create_all` en producción).
- Secretos solo vía entorno; jamás en código ni en commits.

---

## 8. Versionado (SemVer) y commits

- **SemVer** para la app: `MAJOR.MINOR.PATCH`. v1 = primer release funcional; features diferidas (p. ej. registro de clientes) entran como `MINOR` (v1.1+).
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, etc. Scope opcional (`feat(venta): ...`).
- Un cambio lógico por commit; mensajes en presente, imperativo.

---

## 9. Flujo de GitHub

- Repo **privado**.
- Rama `main` protegida; trabajo en ramas `feat/*`, `fix/*`; PR a `main`.
- PR exige **pytest en verde**.
- Tags de release `vX.Y.Z` alineados con SemVer.

---

## 10. CI (opcional)

`SUPUESTO` **GitHub Actions mínima y opcional** (decisión 01-jun-2026): workflow que instala dependencias y corre `pytest` en cada PR. No bloquea v1 si el titular prefiere prescindir de CI al inicio.

```yaml
# .github/workflows/ci.yml (mínimo)
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_USER: pos, POSTGRES_PASSWORD: pos, POSTGRES_DB: maschinario }
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: alembic upgrade head
      - run: pytest -q
```

---

## 11. Empaquetado y entrega

- v1: **venv + docker-compose** (sin PyInstaller). PyInstaller queda como opción futura si se quiere un ejecutable único.
- Entregar README con los pasos de §4–§6 para que el titular opere la caja.

---

## 12. Disciplina

- **No reabrir** decisiones congeladas (stack, despliegue, alcance, CFDI sin timbrado). Ante disonancia real, **detenerse y consultar** al titular.
- Marcar como `SUPUESTO` cualquier cosa no confirmada (modelo de impresora/terminal, atajos de teclado, política de stock 0, redondeo si difiere).
- **CFDI:** la app **no timbra**; solo marca y exporta a RFC genérico (`ARCHITECTURE.md` ADR-004). Validación fiscal es responsabilidad del titular/contador.

---

*CLAUDE.md · PRY-F-0001.1.8 Maschinario – Bazar · v1.0 · 01-jun-2026 · Residuo para Claude Code.*
