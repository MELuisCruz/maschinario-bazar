# Maschinario · Bazar — POS

Punto de venta web que corre **localmente** en una caja. Stack: **FastAPI + Uvicorn ·
Jinja2 + HTMX (no SPA) · PostgreSQL (docker-compose) · SQLAlchemy + Alembic ·
python-escpos · Mercado Pago API de Orders**. Proyecto `PRY-F-0001.1.8`.

El diseño aprobado vive en `docs/` (PRD, arquitectura, modelo de datos, integración
MP, ticket térmico, periféricos, UI y criterios de aceptación) y las reglas de
construcción en `CLAUDE.md` (raíz). Esta app implementa el alcance v1.

## Arranque (detalle en CLAUDE.md §4)

```bash
# 1) Base de datos (contenedor)
docker compose up -d db

# 2) App nativa en el host (para el USB de la impresora)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ajusta credenciales/impresora
alembic upgrade head          # migraciones
python -m app.seed            # admin inicial + productos demo ([DEMO]/DEMO-####)
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000`. Login inicial: usuario `admin`, PIN `2468`
(**cámbialo**; define otro con `SEED_ADMIN_PIN=...` antes del seed).

> Nota: si el host ya usa el puerto 5432, publica el contenedor en otro puerto con
> `DB_HOST_PORT=5433` en `.env` (el `DATABASE_URL` debe apuntar a ese puerto).

## Datos demo

Los productos de demostración están identificados con nombre `«[DEMO] …»` y `sku`
`DEMO-####`. Para eliminarlos sin tocar datos reales:

```bash
python -m app.seed --purge-demo
```

## Pruebas

```bash
pytest -q
```

La integración con Mercado Pago se prueba contra **mocks / `simulate-order`**;
**nunca** se realizan cobros reales (CLAUDE.md §6).

## Respaldo / restauración (CLAUDE.md §5)

```bash
docker compose exec db pg_dump -U pos maschinario > backup_$(date +%F).sql
cat backup_YYYY-MM-DD.sql | docker compose exec -T db psql -U pos maschinario
```

## Roles

- **administrador:** gestiona catálogo, importa CSV, administra cajeros y roles.
- **cajero:** opera venta, cobro, devolución y corte; consulta catálogo y reportes.

## Estructura del repo

```
maschinario-bazar/
├── CLAUDE.md            # reglas de construcción (Claude Code lo lee solo)
├── README.md           # esta guía operativa
├── docker-compose.yml  # servicio db (postgres) + volumen
├── .env.example        # plantilla de variables; .gitignore evita versionar el .env real
├── requirements.txt · alembic.ini
├── alembic/            # migraciones
├── app/
│   ├── main.py · config.py · db.py · deps.py · seed.py
│   ├── models/         # ORM (docs/DATA_MODEL.md)
│   ├── routers/        # auth, venta, cobro, devolucion, catalogo, corte, reportes, reimpresion, usuarios
│   ├── services/       # money, turnos, ventas, cobro, mp_point, stock, devoluciones, corte, catalogo, reportes, fiscal_export, printing, cajeros, security
│   ├── templates/      # Jinja2 + parciales HTMX
│   └── static/         # CSS de marca, JS de foco/atajos, htmx vendorizado
├── docs/               # diseño aprobado + mockup/ (referencia visual) + handoff/ (guías)
│   ├── PRD.md · ARCHITECTURE.md · DATA_MODEL.md · INTEGRATION_MP_POINT.md
│   ├── THERMAL_TICKET_SPEC.md · PERIPHERALS.md · UI_SPEC.md · ACCEPTANCE_TESTS.md
│   ├── mockup/         # prototipo React (look & feel; no es la UI de producción)
│   └── handoff/        # checklist y guía de arranque del operador
└── tests/              # pytest (lógica + HTTP; MP mockeado)
```

### Documentos de diseño (`docs/`, orden de lectura)
`CLAUDE.md` → `docs/PRD.md` → `docs/ARCHITECTURE.md` → `docs/DATA_MODEL.md` →
`docs/INTEGRATION_MP_POINT.md` → `docs/THERMAL_TICKET_SPEC.md` → `docs/PERIPHERALS.md` →
`docs/UI_SPEC.md` → `docs/ACCEPTANCE_TESTS.md`. El prototipo visual está en
`docs/mockup/` (abre `index.html`, PIN demo `2468`).

**Preparación de hardware (primer uso):** `docs/HARDWARE_SETUP.md` — guía paso a paso
para estrenar impresora térmica, lector NETUM y terminal Mercado Pago Point Smart 2 en
Ubuntu, con prueba end-to-end de todos los módulos.

---
*POS Maschinario · Bazar · v1 · ticket = nota de compra (no CFDI); la app no timbra.*
