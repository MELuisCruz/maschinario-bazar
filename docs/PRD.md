# PRD · POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 0.1 (borrador)
**Fecha:** 01-jun-2026
**Consumidor:** Claude Code (este documento es autocontenido)

---

## 1. Propósito

Aplicación de punto de venta (POS) para un **negocio pequeño de bazar** en México (MXN). Web app en Python que **corre en local**, opera con **una sola caja** y permite cobrar en efectivo y con tarjeta (Mercado Pago Point), imprimir un **ticket térmico** como nota de compra y operar el catálogo con un **lector de código de barras**.

No es un sistema de facturación ni un e-commerce. No se sincroniza con MercadoLibre.

---

## 2. Usuarios

- **Cajero/operador:** opera la venta, el cobro, devoluciones y el corte de su turno. Se autentica con usuario y PIN/contraseña.
- **Administrador:** además gestiona catálogo, importa CSV, consulta reportes y configura la caja. (Mismo binario; rol determina permisos.)

Una sola caja física; varios cajeros pueden turnarse (relevo de turno), **nunca de forma concurrente sobre la misma instancia**.

---

## 3. Alcance v1 (funcional)

### 3.1 Venta
- Agregar productos por **escaneo de código de barras** (1D/2D) o búsqueda manual.
- Editar cantidades, eliminar líneas, aplicar **descuento** por línea y por venta (monto o %).
- Mostrar subtotal, IVA (si aplica) y total. Precios en MXN.
- Cerrar venta seleccionando medio de pago.

### 3.2 Cobro
- **Efectivo:** captura de monto recibido y cálculo de cambio. Opera **offline**.
- **Tarjeta (Mercado Pago Point):** se delega a la terminal vía la **API de Orders**; el POS crea la orden, recibe el estado (aprobado/rechazado/cancelado) y concilia. **Requiere conexión**.
- Corte de caja por turno/cajero (apertura con fondo, cierre con arqueo y totales por medio de pago).

### 3.3 Devolución simple
- Devolución total o parcial de una venta existente (búsqueda por folio).
- Reintegra stock; registra el movimiento; reimprime comprobante de devolución.

### 3.4 Catálogo e inventario
- Alta/edición manual de productos (SKU, código de barras, nombre, precio, IVA aplicable, existencia).
- **Importación por CSV** (alta y actualización masiva).
- **Control de stock básico:** descuento de existencias en venta, reintegro en devolución, ajuste manual.

### 3.5 Ticket / nota de compra
- Impresión térmica ESC/POS al cerrar la venta.
- **Reimpresión** de cualquier venta por folio.
- El ticket es **nota de compra, no CFDI**.

### 3.6 CFDI (acotado)
- Casilla "requiere factura" sobre la venta. **La app no timbra.**
- Las ventas marcadas y/o las del periodo se **exportan** (CSV/JSON) con los datos para que el contador/facturador emita la **factura global a RFC genérico** (`XAXX010101000`) fuera de la app.
- No se capturan datos fiscales del cliente ni se emiten facturas nominativas en v1.

### 3.7 Reportes
- Reporte de ventas por rango de fechas, por cajero/turno y por medio de pago.
- Export del periodo para facturación externa y para conciliación.

### 3.8 Multiusuario / turnos
- Autenticación de cajeros; apertura y cierre de turno por cajero; el corte de caja se asocia al turno.

---

## 4. Requisitos no funcionales

- **Local-first:** toda la operación core funciona sin internet salvo el cobro con tarjeta.
- **Arranque:** `docker compose up -d` (PostgreSQL) + `uvicorn` (app) en el host. Acceso a `http://localhost:<puerto>` desde el navegador de la caja.
- **Rendimiento:** una venta típica (≤30 líneas) responde de forma instantánea en hardware modesto; el escaneo no introduce latencia perceptible.
- **Persistencia/respaldo:** datos en PostgreSQL con volumen de docker-compose; respaldo por `pg_dump` documentado en `CLAUDE.md`.
- **Trazabilidad:** toda venta, devolución, ajuste de stock y corte queda registrado con timestamp y cajero.
- **Idempotencia de cobro:** la creación de orden en Point debe ser idempotente para evitar dobles cargos ante reintentos (detalle en `INTEGRATION_MP_POINT.md`).

---

## 5. Restricciones (fijas)

1. Web app en Python, ejecución local.
2. Cobro presencial con Mercado Pago Point (API de Orders).
3. Ticket térmico ESC/POS, 80 mm, USB.
4. Input por lector de código de barras (HID keyboard-wedge) + periféricos estándar.
5. Dominio: bazar pequeño, México, MXN.

---

## 6. Fuera de alcance v1 (no-goals)

- **Timbrado CFDI dentro de la app** (sin PAC/CSD). Solo export para timbrado externo.
- **Facturación nominativa** (a RFC del cliente con datos fiscales).
- **Registro de clientes / CRM** (diferido a v1.1+).
- **Sincronización con MercadoLibre** u otros marketplaces.
- **Multi-terminal concurrente** / operación cliente-servidor entre varias cajas.
- **Cobro con tarjeta offline** (la tarjeta exige conexión).

---

## 7. Supuestos abiertos

- `SUPUESTO` Modelo exacto de impresora 80 mm sin confirmar; se asume ESC/POS estándar por USB.
- `SUPUESTO` El lector se entrega configurado con sufijo Enter y layout de teclado consistente con el SO.
- `SUPUESTO` El tratamiento fiscal (factura global a RFC genérico) será validado con el contador del titular.

---

## 8. Criterios de aceptación

Los criterios verificables por feature viven en `ACCEPTANCE_TESTS.md` (traducibles a pruebas pytest).
