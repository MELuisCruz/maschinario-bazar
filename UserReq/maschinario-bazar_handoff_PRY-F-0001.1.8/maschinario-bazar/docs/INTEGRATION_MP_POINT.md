# INTEGRATION_MP_POINT · POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 1.0 (para aprobación del titular)
**Fecha:** 01-jun-2026
**Consumidor:** Claude Code
**Fuente:** Documentación oficial de Mercado Pago — **API de Orders para Point** (`api.mercadopago.com/v1/orders`, `type:"point"`), verificada el 01-jun-2026. Referencia: `developers.mercadopago.com` → Pagos presenciales → Point → API Orders. **No** se usa la API Point legacy (Payment Intents / dispositivos), marcada como *deprecada* en la propia doc.

> Contrato de integración de cobro con tarjeta presencial. El efectivo **no** pasa por aquí (se registra local). Mapea contra `DATA_MODEL.md` (tablas `pagos`, `ventas`). Stack y resiliencia en `ARCHITECTURE.md` (ADR-003).

---

## 1. Modelo conceptual

- **Una venta del POS → una `order` de Point.** Para `type:"point"`, la order admite **una sola transacción** (un pago con tarjeta). Pagos mixtos (parte efectivo + parte tarjeta) se modelan con **varios `pagos`** en la venta, pero **solo el monto de tarjeta** va a la order.
- La terminal **carga la order automáticamente**; el cliente paga en el lector; el **estado de la order se actualiza con el resultado del pago**.
- Una terminal solo puede tener **una order en espera** a la vez. Hay que **finalizarla o cancelarla** antes de enviar otra.

---

## 2. Credenciales y entorno

- **Access Token** (header `Authorization: Bearer <token>`) obtenido del panel de desarrollador de Mercado Pago. Va en **toda** solicitud.
- **Nunca** se versiona el token en el repo: vive en `.env` (`MP_ACCESS_TOKEN`), ver `CLAUDE.md`.
- **Pruebas:** usar credenciales/entorno de test y el endpoint **Simular estado de la order** (`.../orders/simulate-order`) para validar sin cobrar de verdad. País: **México**; montos en **MXN** como string (`"50.00"`).

---

## 3. Vinculación de la terminal

1. **Listar terminales:** `GET .../point/terminals` para obtener el `terminal_id` (formato tipo `NEWLAND_N950__...`).
2. **Modo de operación:** la terminal debe estar en **modo integrado** para recibir orders desde el sistema. Se ajusta con `PATCH .../point/terminals/.../update-operation-mode`.
3. El `terminal_id` se guarda en configuración (`.env`: `MP_TERMINAL_ID`). `SUPUESTO`: una sola terminal (una caja).

---

## 4. Crear order (iniciar cobro con tarjeta)

`POST https://api.mercadopago.com/v1/orders`

**Headers:**
- `Authorization: Bearer <MP_ACCESS_TOKEN>` (requerido).
- `X-Idempotency-Key: <uuid>` (**requerido**). Uno **nuevo por intento de cobro**. Reusarlo con un cuerpo distinto en < 24 h devuelve error 409 (ver §8).
- `Content-Type: application/json`.

**Body (campos usados por el POS):**

```json
{
  "type": "point",
  "external_reference": "<folio de la venta>",
  "expiration_time": "PT5M",
  "transactions": {
    "payments": [ { "amount": "123.50" } ]
  },
  "config": {
    "point": {
      "terminal_id": "<MP_TERMINAL_ID>",
      "print_on_terminal": "no_ticket"
    },
    "payment_method": {
      "default_installments": 1,
      "installments_cost": "seller"
    }
  },
  "description": "Venta <folio>"
}
```

Notas de contrato:
- `external_reference` = **`ventas.folio`** (≤ 64 caracteres; letras, números, `-` y `_`). Es el puente venta↔order.
- `expiration_time` = duración ISO 8601 (p. ej. `PT5M` = 5 min). **Default de MP = 15 min** si se omite. `SUPUESTO`: 5 min para una caja de bazar.
- `print_on_terminal: "no_ticket"` — **no** imprimimos en la terminal; el ticket lo imprime nuestra impresora térmica (ver `THERMAL_TICKET_SPEC.md`).
- `installments`: `SUPUESTO` 1 (sin cuotas) para v1; confirmar con el titular si quiere meses sin intereses.

**Respuesta (201):** incluye `id` (formato `ORD...`), `status: "created"`, `status_detail`, y `transactions.payments[].id` (formato `PAY...`) con su `status`.

**Persistencia inmediata (`DATA_MODEL.md` → `pagos`):**
- `pagos.mp_order_id` ← `id` (ORD…).
- `pagos.mp_idempotency` ← el `X-Idempotency-Key` enviado.
- `pagos.estado` ← `pendiente`.

---

## 5. Consultar estado (resolución del cobro)

`GET https://api.mercadopago.com/v1/orders/{id}`

- **Estrategia recomendada (`SUPUESTO` defendible): polling.** La app corre en una caja local (sin URL pública garantizada), por lo que **los webhooks de MP pueden no alcanzarla** sin un túnel. El POS hace **polling** del estado cada ~2 s mientras el cobro está en curso (alineado con `UI_SPEC.md` §5.3), hasta estado terminal o expiración.
- **Webhook (opcional):** si más adelante hay URL pública/túnel, se puede registrar `notification_url` y reaccionar a la notificación, **siempre confirmando con un `GET`** antes de marcar pagado.
- **Mapeo de estado → `pagos.estado`:**
  - order/pago **aprobado/finalizado** → `aprobado` → la venta puede pasar a `pagada` (regla en `DATA_MODEL.md`).
  - **rechazado** → `rechazado` → ofrecer reintento o cambio a efectivo.
  - **cancelado / expirado** → `cancelado`.
  - cualquier estado intermedio → permanece `pendiente`.

> **Invariante crítico (de `DATA_MODEL.md`):** un pago con tarjeta **nunca** se marca `aprobado` sin confirmación explícita de Mercado Pago vía `GET`. Ante respuesta ambigua o timeout, se consulta; nunca se asume aprobado.
> `SUPUESTO` — El enum exacto de estados/`status_detail` de la order debe confirmarse contra la doc vigente al implementar; aquí se fija el **comportamiento** (terminal-aprobado vs no), no los literales.

---

## 6. Cancelar order

`POST https://api.mercadopago.com/v1/orders/{id}/cancel`

- Se usa cuando el cliente no paga, hay timeout, o el cajero aborta el cobro.
- **Obligatorio** antes de crear una nueva order si la terminal quedó con una **en espera** (error 409 `already_queued_order_for_terminal`, §8).
- Tras cancelar: `pagos.estado` ← `cancelado`; la venta vuelve a estado cobrable (efectivo u otro intento).

---

## 7. Reembolso (devolución con tarjeta)

`POST https://api.mercadopago.com/v1/orders/{id}/refund`

- Alimenta el flujo de **devolución** (`UI_SPEC.md` §5.4, `DATA_MODEL.md` `devoluciones`).
- `SUPUESTO` v1: devolución **total** del pago con tarjeta. Reembolso parcial: confirmar si entra en v1 o se difiere.
- El efectivo se devuelve de caja, sin API.

---

## 8. Manejo de errores (documentados por MP)

| HTTP | Código | Significado | Acción del POS |
|---|---|---|---|
| 400 | `empty_required_header` | Falta `X-Idempotency-Key`. | Bug de cliente; generar key y reintentar. |
| 400 | `required_properties` / `property_*` / `json_*` | Cuerpo inválido. | Bug de cliente; loguear y corregir payload. |
| 401 | `unauthorized` | Access Token incorrecto. | Revisar `.env`; no reintentar en bucle. |
| 403 | `forbidden_checking_terminal_owner` | La terminal no pertenece a la cuenta. | Revisar `MP_TERMINAL_ID`/vinculación. |
| 409 | `idempotency_key_already_used` | Key reusada con cuerpo distinto (< 24 h). | Generar **nueva** key por intento. |
| 409 | `already_queued_order_for_terminal` | La terminal ya tiene una order en espera. | **Cancelar** la previa (§6) y reintentar. |
| 500 | `idempotency_validation_failed` / genérico | Error transitorio de MP. | Reintentar con **backoff**; conciliar por `GET` antes de recrear. |

**Sin conexión (offline):** el cobro con tarjeta **se bloquea** con aviso claro (`UI_SPEC.md` indicador de conexión). El **efectivo opera normal**. No se crea order sin conexión.

---

## 9. Reconciliación (a prueba de doble cobro)

- La **idempotencia** (`X-Idempotency-Key` por intento) evita crear dos orders idénticas ante reintentos de red.
- Si la app **pierde la respuesta** de creación, consulta por `external_reference` (= folio) o por el `id` persistido antes de recrear; nunca recrea a ciegas.
- `mp_order_id` es **único** en `pagos` cuando existe (índice único en `DATA_MODEL.md`).

---

## 10. SUPUESTOS y pendientes

- `SUPUESTO` Una caja / una terminal; modelo exacto de terminal **pendiente** (dato del titular). El contrato no depende del modelo, pero el `terminal_id` sí.
- `SUPUESTO` Polling como mecanismo principal de estado (caja local sin URL pública).
- `SUPUESTO` `installments = 1` (sin meses sin intereses) en v1.
- `SUPUESTO` Reembolso total en v1; parcial a confirmar.
- Pendiente: confirmar el **enum de estados** de la order contra la doc vigente al implementar.
- Pendiente: confirmar país/moneda y credenciales de producción (MXN, cuenta MX).

---

*INTEGRATION_MP_POINT · PRY-F-0001.1.8 Maschinario – Bazar · v1.0 · 01-jun-2026 · Residuo para Claude Code. Fundamentado en doc oficial MP verificada 01-jun-2026.*
