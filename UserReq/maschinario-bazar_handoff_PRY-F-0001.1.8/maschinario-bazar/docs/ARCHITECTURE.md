# ARCHITECTURE · POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 0.1 (borrador)
**Fecha:** 01-jun-2026
**Consumidor:** Claude Code

---

## 1. Stack

| Capa | Tecnología |
|---|---|
| Backend | **FastAPI** sobre **Uvicorn** |
| Render | **Jinja2 + HTMX** (HTML renderizado en servidor; **no SPA**) |
| Estilos | CSS propio aplicando el manual de marca de Maschinario (ver `UI_SPEC.md`) |
| Base de datos | **PostgreSQL** |
| Acceso a datos | SQLAlchemy + **Alembic** (migraciones) |
| Impresión | `python-escpos` (ESC/POS por USB) |
| Lector | HID keyboard-wedge (entra como teclado en el navegador; sin capa de driver) |
| Integración cobro | Mercado Pago **API de Orders** (cliente HTTP propio) |
| Pruebas | pytest |

---

## 2. Topología de despliegue (híbrido)

Una sola caja. Dos procesos en la misma máquina:

```
┌───────────────────────── Host (la caja) ─────────────────────────┐
│                                                                   │
│  Navegador  ──HTTP──▶  App FastAPI (uvicorn, NATIVA en el host)   │
│   (cajero)             │   │                                      │
│   ▲  escaneo HID       │   ├── USB ──▶  Impresora térmica 80 mm   │
│   │  (keyboard-wedge)   │   └── HTTPS ─▶ Mercado Pago Orders (nube)│
│                         │                                          │
│                         └── TCP 5432 ──▶ PostgreSQL (CONTENEDOR    │
│                                          docker-compose)           │
└───────────────────────────────────────────────────────────────────┘
```

**Por qué híbrido:** la base de datos vive en docker-compose por reproducibilidad (versión fija, volumen, arranque y respaldo de un comando); la app corre **nativa** porque necesita acceso directo al **USB de la impresora**, que el passthrough a contenedor no garantiza de forma portable (especialmente en Docker Desktop sobre macOS/Windows). Ver ADR-002.

El **lector** no toca al contenedor ni al backend por USB: emula teclado y escribe en el navegador del host; el dato viaja al backend por HTTP.

---

## 3. Ejecución local

```bash
# 1) Base de datos
docker compose up -d db          # PostgreSQL con volumen persistente

# 2) App (host)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head             # migraciones
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Detalle de comandos, respaldo (`pg_dump`), variables de entorno y troubleshooting en `CLAUDE.md`.

---

## 4. Estructura de carpetas (propuesta)

```
maschinario-bazar/
├── docker-compose.yml          # servicio db (postgres) + volumen
├── .env.example                # DSN, puerto, config impresora
├── requirements.txt
├── alembic/                    # migraciones
├── app/
│   ├── main.py                 # entrypoint FastAPI
│   ├── config.py
│   ├── db.py                   # engine/session SQLAlchemy
│   ├── models/                 # ORM: productos, ventas, pagos, cortes, cajeros
│   ├── routers/                # venta, cobro, devolucion, catalogo, corte, reportes, auth
│   ├── services/
│   │   ├── mp_point.py         # cliente API de Orders
│   │   ├── printing.py         # ESC/POS (python-escpos)
│   │   ├── stock.py
│   │   └── fiscal_export.py    # export para timbrado externo
│   ├── templates/              # Jinja2 (parciales HTMX)
│   └── static/                 # CSS marca, JS mínimo
└── tests/                      # pytest
```

---

## 5. Decisiones de arquitectura (ADRs)

### ADR-001 · PostgreSQL en lugar de SQLite
**Contexto:** se evaluó SQLite (archivo embebido, cero proceso) frente a PostgreSQL.
**Decisión:** PostgreSQL.
**Consecuencias:** suma un proceso de base de datos (vía docker-compose) y migraciones con Alembic; a cambio, motor robusto, tipos ricos y camino de crecimiento. La operación sigue siendo local; no requiere internet.

### ADR-002 · Despliegue híbrido (DB en Docker, app nativa)
**Contexto:** la app debe manejar una **impresora USB**; el passthrough de USB a contenedor no es portable entre SO.
**Decisión:** PostgreSQL en docker-compose; **app FastAPI nativa en el host**.
**Consecuencias:** reproducibilidad donde importa (datos) sin sacrificar el acceso al hardware; arranque en dos pasos (`compose up db` + `uvicorn`), documentado en `CLAUDE.md`. Agnóstico al SO.

### ADR-003 · Mercado Pago API de Orders (no legacy)
**Contexto:** la API Point legacy se descontinúa para integraciones nuevas.
**Decisión:** integrar contra la **API de Orders**.
**Consecuencias:** el contrato exacto (endpoints, payloads, webhook/polling, idempotencia, cancelación, reembolso) se especifica en `INTEGRATION_MP_POINT.md` con base en la documentación oficial vigente.

### ADR-004 · CFDI sin PAC: la app no timbra
**Contexto:** el timbrado exige PAC, CSD y manejo del esquema SAT — desproporcionado para el bazar.
**Decisión:** la app **marca y exporta**; el timbrado (factura global a RFC genérico) ocurre fuera.
**Consecuencias:** v1 evita toda la integración fiscal; el modelo de datos guarda el flag fiscal y el export. Sujeto a validación con contador.

### ADR-005 · Jinja2 + HTMX en lugar de SPA
**Contexto:** POS de una caja, flujos lineales, prioridad a robustez local y baja complejidad.
**Decisión:** render en servidor con HTMX para interactividad puntual; sin framework SPA.
**Consecuencias:** menos piezas, menos build de frontend, mejor encaje con el lector keyboard-wedge (foco en inputs HTML). Las "vistas de GUI" son plantillas HTML; los prompts de generación las producen como tal (ver `UI_SPEC.md`).

---

## 6. Manejo de fallos (resumen)

- **Sin internet:** efectivo opera normal; el cobro con tarjeta se bloquea con aviso claro y la venta puede cerrarse en efectivo o quedar en espera.
- **Point no responde / orden ambigua:** estado de cobro conciliado por consulta de estado; nunca se cierra la venta como pagada sin confirmación de aprobado (detalle en `INTEGRATION_MP_POINT.md`).
- **Impresora no disponible:** la venta se persiste igual; el ticket queda disponible para **reimpresión**.
- **DB caída:** la app no inicia operaciones de venta hasta que `compose up db` esté arriba (precondición de arranque).
