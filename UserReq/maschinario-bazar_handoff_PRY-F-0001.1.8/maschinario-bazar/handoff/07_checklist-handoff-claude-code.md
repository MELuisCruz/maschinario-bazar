# Checklist de handoff a Claude Code · PRY-F-0001.1.8 `Maschinario – Bazar`

**Versión:** 1.0 · **Fecha:** 01-jun-2026
**Propósito:** verificar que el residuo está completo y entregar a Claude Code en el orden correcto de lectura.

---

## 1. Residuo a consumir (9 documentos, todos v1.0 final)

Marca cada uno al colocarlo en el repo:

- [ ] **`CLAUDE.md`** — gobierna cómo Claude Code construye, versiona, prueba y publica. **Va en la raíz del repo** (Claude Code lo lee automáticamente). *Léelo primero.*
- [ ] **`PRD.md`** — qué hace el sistema y qué no (alcance v1, no-goals).
- [ ] **`ARCHITECTURE.md`** — stack, topología híbrida, estructura de carpetas, ADRs.
- [ ] **`DATA_MODEL.md`** — esquema PostgreSQL (DDL de referencia), invariantes, IVA 16%.
- [ ] **`INTEGRATION_MP_POINT.md`** — contrato con la API de Orders (crear/consultar/cancelar/reembolsar order, idempotencia, offline, errores).
- [ ] **`THERMAL_TICKET_SPEC.md`** — ticket ESC/POS 80 mm (RP850), layout, reimpresión.
- [ ] **`PERIPHERALS.md`** — lector NETUM C750 (HID wedge), foco, teclado/mouse.
- [ ] **`UI_SPEC.md`** — pantallas, componentes, design tokens, foco del lector, prompts de mockup.
- [ ] **`ACCEPTANCE_TESTS.md`** — criterios Dado/Cuando/Entonces, traducibles a pytest.

**Anexo (referencia visual, no contrato):**
- [ ] Mockup de referencia (prototipo React) — *opcional*; orienta el look & feel. La UI de producción se construye como **Jinja2 + HTMX** según `UI_SPEC`, no copiando el React.

---

## 2. Orden de lectura recomendado para Claude Code

1. `CLAUDE.md` (reglas de construcción) → 2. `PRD.md` (qué) → 3. `ARCHITECTURE.md` (cómo) → 4. `DATA_MODEL.md` → 5. `INTEGRATION_MP_POINT.md` → 6. `THERMAL_TICKET_SPEC.md` → 7. `PERIPHERALS.md` → 8. `UI_SPEC.md` → 9. `ACCEPTANCE_TESTS.md`.

---

## 3. Verificación de coherencia (debe cumplirse antes de construir)

- [ ] Stack: FastAPI + Uvicorn · Jinja2 + HTMX (no SPA) · PostgreSQL · SQLAlchemy + Alembic · python-escpos · pytest.
- [ ] Despliegue híbrido: DB en docker-compose + app nativa en el host (USB de impresora).
- [ ] IVA **16% único** (`APP_IVA_RATE=0.16`); redondeo **HALF_UP a 2 decimales**.
- [ ] Cobro tarjeta: API de Orders, idempotencia, **nunca `pagado` sin confirmación de MP**.
- [ ] Ticket = **nota de compra (no CFDI)**; la app **no timbra** (export a RFC genérico).
- [ ] Sin cajón; sin concurrencia; operación mouse + teclado.

---

## 4. Pendientes externos (no bloquean el código; se resuelven en la máquina/operación)

- [ ] Vincular **Point Smart 2** (sucursal + caja + modo PDV) → obtener `terminal_id`.
- [ ] Leer `idVendor/idProduct` USB de la **RP850** (`lsusb`) y validar codepage.
- [ ] Credenciales de producción de Mercado Pago (cuenta MX, MXN).
- [ ] Validación del tratamiento **CFDI** con el contador.
- [ ] Manual de marca propio de Maschinario (afinar tokens en `UI_SPEC`).

---

## 5. Definición de "listo para entregar"

El residuo está listo cuando los 9 documentos están en el repo, `CLAUDE.md` en la raíz, y este checklist (§1 y §3) completo. Los pendientes de §4 se atienden durante la implementación, no antes.

---

*Checklist de handoff · PRY-F-0001.1.8 Maschinario – Bazar · v1.0 · 01-jun-2026.*
