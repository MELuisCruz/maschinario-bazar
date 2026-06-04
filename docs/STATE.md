# STATE — Estado del proyecto y cómo retomar

**Proyecto:** PRY-F-0001.1.8 `Maschinario · Bazar` (POS local)
**Última actualización:** 2026-06-04
**Resumen:** v1 funcional completa (los 9 módulos), **82 tests verdes**, ruff/black
limpios, release `v1.0.0` publicado. Falta la **prueba de fuego con hardware real** y
la **app de prueba (TEST) de Mercado Pago**.

---

## 1. Qué está TERMINADO

- **Stack e infraestructura:** FastAPI + Uvicorn · Jinja2 + HTMX · PostgreSQL
  (docker-compose) · SQLAlchemy + Alembic · python-escpos · cliente MP API de Orders.
- **Esquema:** 9 tablas + 5 enums; migraciones Alembic (`07105cfdb907`,
  `9e479b911218`); `alembic check` sin drift.
- **Módulos (alcance v1) con tests (ACCEPTANCE_TESTS):**
  auth/turno, venta, cobro efectivo, cobro tarjeta (MP mockeado), devolución, corte de
  caja, catálogo/stock + import CSV, reportes + export fiscal, ticket/reimpresión (ESC/POS).
- **RBAC:** solo admin gestiona catálogo, import CSV y usuarios/roles (con salvaguarda
  de "último admin"). Cajero opera venta/cobro/devolución/corte y consulta.
- **Seed:** `python -m app.seed` (admin + 14 productos demo identificados `[DEMO]`/`DEMO-####`; `--purge-demo`).
- **Docs:** residuo integrado en `docs/`, `CLAUDE.md` en la raíz, `README.md` operativo,
  `docs/HARDWARE_SETUP.md` (guía de primer uso, afinada a RP850 / NETUM C750 / sin TEST).
- **Calidad:** primer code review aplicado (ver §3). 82 tests, lint/format OK.
- **GitHub:** `MELuisCruz/maschinario-bazar` (público), `main` protegida por ruleset
  (PR obligatorio, bypass admin), tag `v1.0.0`.

---

## 2. Qué FALTA (para cerrar el proyecto)

1. **Prueba de fuego con hardware real** — primer uso de los 3 dispositivos siguiendo
   `docs/HARDWARE_SETUP.md`: impresora **Rongta RP850**, lector **NETUM C750**, terminal
   **Mercado Pago Point Smart 2**. Recorrer el checklist de 13 puntos (§4 de esa guía).
2. **App de prueba (TEST) de Mercado Pago** — el titular eligió el **Camino A**: crear
   una aplicación de prueba en el panel de desarrollador de MP para obtener credenciales
   **TEST** y **simular** el cobro con tarjeta sin dinero real (`HARDWARE_SETUP §3.2/§3.5`).
   *Pendiente de que el titular entregue el `MP_ACCESS_TOKEN` TEST y su `terminal_id`.*
3. **Ajustes post-prueba** — corregir hallazgos del hardware (p. ej. fijar el *codepage*
   real de la RP850 para acentos/`$` en `app/services/printing.py`).
4. **Publicar al remoto** los commits locales pendientes (ver §4) vía PR a `main`.
5. **Acceso directo con ícono** en el escritorio del P52s (Ubuntu) — a crear durante la prueba.
6. **3 manuales** (entregables nuevos): Manual de usuario, Manual de mantenimiento/
   actualización de código, Manual de uso del API.
7. **Plan cross-platform** (Windows/Mac) — solo planeación, no corto plazo.

---

## 3. Decisiones tomadas en esta sesión

- **IVA "incluido"** (precio al público): `total = Σ(precio·cant) − desc`,
  `subtotal = total/1.16`, `iva = total − subtotal`. Redondeo **HALF_UP 2 decimales**.
- **Descuento v1:** solo **monto** ($), por línea y global (el % se difiere a MINOR).
- **Reglas de venta:** stock 0 → avisa sin bloquear; mismo código escaneado → incrementa
  cantidad; `recibido < total` → no permite cerrar.
- **Atajos:** F1–F6 solo navegación (se evita el conflicto F2/F3 de UI_SPEC §9).
- **Repo público + ruleset** en lugar de privado: el plan Free no permite proteger `main`
  en repos privados; el titular optó por hacerlo público (sin secretos versionados).
- **Entorno local:** el host ocupa el 5432, así que el contenedor de la DB se publica en
  **5433** vía `DB_HOST_PORT` y un `.env` local (no versionado).
- **Técnicas:** PIN con `bcrypt` directo (passlib incompatible con bcrypt≥4); HTMX
  vendorizado en `static/js`; sesión con `SessionMiddleware` (`APP_SECRET_KEY`).
- **Cobro tarjeta:** estrategia **Camino A** (credenciales TEST para simular) en la prueba.
- **Estructura:** `UserReq/` asimilado a `docs/` + `CLAUDE.md` a la raíz.
- **Code review (1er pase) aplicado:** venta total 0 se cierra sin `Pago`; parsing de
  devolución robusto ante campos malformados; `APP_SECRET_KEY` documentado;
  `session.query`→`select()`; `import or_` al tope; fix de `style` duplicado en COBRAR.
  Descartados (no-bugs): reimpresión cross-turno (intencional), XSS (Jinja autoescapa),
  timeout MP (hay salida por UI). Diferidos: N+1 en devolución/corte, centralizar helpers.

---

## 4. Pasos EXACTOS para retomar

1. **Arrancar entorno**
   ```bash
   cd /home/cleto/Documentos/maschinario-bazar
   docker compose up -d db
   source .venv/bin/activate     # o recrear: python -m venv .venv && pip install -r requirements.txt
   alembic upgrade head
   ```
2. **Estado de git** — `main` local está **adelante** de `origin/main` por commits aún
   **no publicados** (guía de hardware + fixes del review + este STATE). Para publicarlos:
   ```bash
   git switch -c chore/post-review-y-docs
   git push -u origin chore/post-review-y-docs
   gh pr create --base main --fill && gh pr merge --merge --delete-branch
   ```
   (o pídeme que lo haga). Verifica con `git log --oneline origin/main..main`.
3. **Cuando llegue la app de prueba MP (Camino A)** — completar `.env`:
   ```
   MP_ACCESS_TOKEN=TEST-...        # credenciales TEST
   MP_TERMINAL_ID=...              # del MISMO entorno (TEST) — ver HARDWARE_SETUP §3.3
   PRINTER_USB_VENDOR=0x????       # lsusb (HARDWARE_SETUP §1.2)
   PRINTER_USB_PRODUCT=0x????
   APP_SECRET_KEY=...              # python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
4. **Ejecutar la prueba de fuego** siguiendo `docs/HARDWARE_SETUP.md` (§1 impresora →
   §2 lector → §3 terminal [simulado y luego real+reembolso] → §4 checklist de 13 puntos).
5. **Anotar hallazgos** y pedirme los **ajustes de código** (p. ej. codepage RP850).
6. **Pedirme**: (a) el **acceso directo de escritorio** (P52s/Ubuntu) y (b) los **3 manuales**.

### Comandos útiles
```bash
pytest -q                      # 82 tests; MP siempre mockeado, sin cobros reales
ruff check app tests && black --check app tests
python -m app.seed --purge-demo   # quitar datos demo
docker compose exec db pg_dump -U pos maschinario > backup_$(date +%F).sql
```

### Referencias
`CLAUDE.md` (reglas) · `docs/HARDWARE_SETUP.md` (prueba de fuego) ·
`docs/ACCEPTANCE_TESTS.md` (criterios) · `docs/INTEGRATION_MP_POINT.md` (contrato MP).

---
*STATE · PRY-F-0001.1.8 Maschinario · Bazar · 2026-06-04.*
