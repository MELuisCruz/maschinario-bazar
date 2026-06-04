# ACCEPTANCE_TESTS · POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 1.0 (para aprobación del titular)
**Fecha:** 01-jun-2026
**Consumidor:** Claude Code

> Criterios de aceptación por feature, redactados en estilo **Dado/Cuando/Entonces** para que Claude Code los traduzca a **pytest**. Cubren el alcance v1 congelado. Referencias: `DATA_MODEL.md`, `INTEGRATION_MP_POINT.md`, `THERMAL_TICKET_SPEC.md`, `PERIPHERALS.md`.

---

## 1. Autenticación y turno

- **AT-1.1** Dado un cajero activo con PIN correcto, cuando inicia sesión, entonces se crea un `turno` con `fondo_inicial` y queda abierto.
- **AT-1.2** Dado un PIN incorrecto, cuando intenta entrar, entonces se rechaza y no se crea turno.
- **AT-1.3** Dado un cajero con turno abierto, cuando vuelve a entrar, entonces se le ofrece **reanudar** el turno, no abrir otro.
- **AT-1.4** Dado un cajero inactivo (`activo=false`), cuando intenta entrar, entonces se rechaza.

## 2. Venta

- **AT-2.1** Dado un `codigo_barras` existente, cuando se escanea (Enter), entonces se agrega una `venta_linea` con `descripcion`, `precio_unit` e `iva_tasa` **snapshot** del producto.
- **AT-2.2** Dado un código inexistente, cuando se escanea, entonces se avisa y **no** se agrega línea.
- **AT-2.3** Dado el mismo producto escaneado dos veces, cuando se agrega, entonces la cantidad **incrementa** (o se crea segunda línea, según regla elegida) — comportamiento definido y consistente.
- **AT-2.4** Dado el IVA único 16%, cuando se calcula la venta, entonces `iva_total` corresponde al 16% de la base y `total` = subtotal − descuento + IVA, con redondeo a 2 decimales.
- **AT-2.5** Dado un descuento de línea o de venta, cuando se aplica, entonces `descuento_total` y `total` se recalculan correctamente.
- **AT-2.6** Dado un producto con `controla_stock=true` y existencia 0, cuando se agrega, entonces se **avisa** (regla de bloqueo/duro definida) sin romper la venta.
- **AT-2.7** Dado anular venta, cuando se confirma, entonces la venta queda `cancelada` y no afecta stock ni caja.

## 3. Cobro — efectivo

- **AT-3.1** Dado un total y un `recibido ≥ total`, cuando se cobra en efectivo, entonces `cambio = recibido − total` y la venta pasa a `pagada`.
- **AT-3.2** Dado `recibido < total`, cuando se intenta cerrar, entonces no se permite (o se registra pago parcial), según regla; nunca `pagada` por debajo del total.
- **AT-3.3** Dado **sin conexión**, cuando se cobra en efectivo, entonces **funciona normal** (efectivo es offline).

## 4. Cobro — tarjeta (Point / API de Orders)

- **AT-4.1** Dado un cobro con tarjeta, cuando se inicia, entonces se crea una `order` (`type:"point"`) con `external_reference = folio` y `X-Idempotency-Key` único; se persiste `mp_order_id` y `pagos.estado='pendiente'`.
- **AT-4.2** Dado que MP devuelve **aprobado** (vía `GET` order), cuando se concilia, entonces `pagos.estado='aprobado'` y la venta pasa a `pagada`.
- **AT-4.3** Dado que MP devuelve **rechazado**, cuando se concilia, entonces `pagos.estado='rechazado'` y la venta **no** queda pagada; se ofrece reintento o efectivo.
- **AT-4.4** Dado una respuesta ambigua/timeout, cuando ocurre, entonces el pago **permanece pendiente** y se concilia por `GET`; **nunca** se marca aprobado sin confirmación.
- **AT-4.5** Dado que la terminal ya tiene una order en espera (409 `already_queued`), cuando se intenta otra, entonces se **cancela** la previa y se reintenta.
- **AT-4.6** Dado el mismo `X-Idempotency-Key` reusado con cuerpo distinto, cuando se envía, entonces se maneja el 409 generando una **key nueva**.
- **AT-4.7** Dado **sin conexión**, cuando se intenta cobrar con tarjeta, entonces se **bloquea** con aviso; el efectivo sigue disponible.

## 5. Devolución

- **AT-5.1** Dada una venta `pagada`, cuando se devuelven líneas/cantidades válidas, entonces se crea `devolucion` + `devolucion_lineas` y el estado de la venta refleja parcial/total.
- **AT-5.2** Dado intentar devolver más de lo vendido, cuando se valida, entonces se **bloquea**.
- **AT-5.3** Dada devolución de un pago con tarjeta, cuando se procesa, entonces se invoca **refund** de la order (`INTEGRATION_MP_POINT.md` §7).
- **AT-5.4** Dada una devolución, cuando se confirma, entonces el stock se **reintegra** (`movimientos_stock` tipo `devolucion`).

## 6. Catálogo y stock

- **AT-6.1** Dado un alta de producto, cuando se guarda con `codigo_barras` único, entonces se crea; si el código existe, se **rechaza**.
- **AT-6.2** Dado un import CSV, cuando hay filas inválidas, entonces se reporta **por fila** y se importan solo las válidas (o se rechaza el lote, según regla definida).
- **AT-6.3** Dada una venta confirmada, cuando descuenta stock, entonces se registra `movimientos_stock` negativo y `existencia` queda consistente con la bitácora.
- **AT-6.4** Dado un producto `controla_stock=false`, cuando se vende, entonces **no** descuenta existencia.

## 7. Corte de caja / turno

- **AT-7.1** Dado un turno con ventas, cuando se hace corte, entonces el efectivo esperado = fondo + ventas efectivo − devoluciones efectivo, desglosado por `medio_pago`.
- **AT-7.2** Dado `efectivo_contado ≠ esperado`, cuando se cierra, entonces se calcula y resalta la **diferencia** y se pide nota.
- **AT-7.3** Dado un turno con ventas abiertas, cuando se intenta cerrar, entonces se **bloquea** hasta resolverlas.

## 8. Reportes y export fiscal

- **AT-8.1** Dado un rango de fechas, cuando se genera el reporte, entonces totaliza ventas por periodo/medio/cajero correctamente.
- **AT-8.2** Dado el export fiscal, cuando se ejecuta, entonces entrega las ventas del periodo con folio, fecha, subtotal, IVA (16%), total y medio; marca `exportada_fiscal=true`; destino **RFC genérico `XAXX010101000`**; **la app no timbra**.

## 9. Ticket e impresión

- **AT-9.1** Dada una venta pagada, cuando se imprime, entonces el ticket muestra folio, líneas, subtotal, IVA (16%), total, medio de pago y la leyenda **"nota de compra (no CFDI)"**.
- **AT-9.2** Dada la impresora no disponible, cuando se cobra, entonces la venta **se persiste** y el ticket queda para reimpresión.
- **AT-9.3** Dada una reimpresión, cuando se ejecuta, entonces el ticket es idéntico más la leyenda de reimpresión; no altera datos.

## 10. Periféricos / foco

- **AT-10.1** Dada la pantalla de venta, cuando se carga o se cierra un modal, entonces el `scan-input` recupera el foco.
- **AT-10.2** Dado un escaneo (longitud variable + Enter), cuando llega, entonces se procesa una sola vez (debounce anti-doble lectura).

---

## 11. Notas para la traducción a pytest

- Tests de **lógica** (totales, IVA, stock, estados) → unitarios puros sobre servicios/modelos.
- Tests de **integración MP** → contra el endpoint **simulate-order** / mocks; nunca cobros reales en CI.
- Tests de **impresión** → mock de `python-escpos` (verificar comandos emitidos, no hardware).
- Tests de **foco/HID** → fuera de pytest (UI); documentar como prueba manual o e2e ligera.
- Redondeo monetario: fijar política (HALF_UP a 2 decimales) y probarla explícitamente.

---

*ACCEPTANCE_TESTS · PRY-F-0001.1.8 Maschinario – Bazar · v1.0 · 01-jun-2026 · Residuo para Claude Code.*
