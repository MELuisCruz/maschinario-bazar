# THERMAL_TICKET_SPEC · POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 1.0 (para aprobación del titular)
**Fecha:** 01-jun-2026
**Consumidor:** Claude Code

> Especificación del ticket térmico que funge como **nota de compra** (no CFDI). Implementación vía `python-escpos` por USB (ver `ARCHITECTURE.md`). Datos desde `DATA_MODEL.md` (`ventas`, `venta_lineas`, `pagos`).

---

## 1. Hardware y formato

- **Impresora:** térmica **80 mm**, comandos **ESC/POS**, conexión **USB**.
- **Área imprimible de trabajo:** ≈ 72 mm → **~48 columnas** en Font A (~32 en Font B). El layout se diseña a **48 columnas**.
- **Sin cajón de dinero** (decisión del titular, 01-jun-2026): **no** se emite el comando de apertura de cajón (`ESC p`). La impresora solo imprime y corta.
- `SUPUESTO` Marca/modelo exacto **pendiente**; el comando de **corte** (`GS V`) y la inicialización (`ESC @`) son estándar ESC/POS y se afinan al confirmar el modelo.

---

## 2. Estructura del ticket (nota de compra)

Ancho de referencia: 48 columnas. Cifras alineadas a la derecha.

```
        [LOGO / NOMBRE NEGOCIO]            <- centrado, doble alto
        MASCHINARIO · BAZAR
   [Dirección / RFC emisor opcional]       <- centrado, Font B
------------------------------------------------
NOTA DE COMPRA  (no es CFDI)               <- destacado
Folio: <ventas.folio>
Fecha: <YYYY-MM-DD HH:MM>   Cajero: <nombre>
------------------------------------------------
CANT  DESCRIPCION              IMPORTE
 1    Producto largo nombre…    $  120.00
 2    Otro producto             $   40.00
        (desc. -$5.00)                       <- línea de descuento si aplica
------------------------------------------------
                 Subtotal:      $  155.00
                 Descuento:     $    5.00
                 IVA (16%):     $   24.80
                 TOTAL:         $  179.80     <- doble alto/ancho
------------------------------------------------
Pago: Efectivo     $  200.00
Cambio:            $   20.20
   (o)  Pago: Tarjeta Point  Aprob. <PAY id corto>
------------------------------------------------
   ¡Gracias por su compra!
   [QR opcional con folio para devolución]
------------------------------------------------
        <fecha/hora reimpresión si aplica>
```

---

## 3. Campos (origen en `DATA_MODEL.md`)

| Sección | Campo | Origen |
|---|---|---|
| Encabezado | Nombre/negocio, leyenda "nota de compra" | constante de config |
| Identif. | Folio | `ventas.folio` |
| Identif. | Fecha/hora | `ventas.creado_en` (o `cerrado_en`) |
| Identif. | Cajero | `cajeros.nombre` vía `ventas.cajero_id` |
| Líneas | Cantidad, descripción, importe | `venta_lineas.cantidad`, `.descripcion` (snapshot), `.importe` |
| Líneas | Descuento por línea | `venta_lineas.descuento` (si > 0) |
| Totales | Subtotal, descuento, IVA, total | `ventas.subtotal`, `.descuento_total`, `.iva_total`, `.total` |
| Pago | Medio, recibido, cambio | `pagos.medio`, `.recibido`, `.cambio` |
| Pago | Ref. tarjeta | `pagos.mp_order_id` (mostrar fragmento legible) |

**IVA:** único al **16%** (decisión 01-jun-2026). Se imprime una sola línea `IVA (16%)`. El ticket muestra IVA incluido en el total (precios al público con IVA).

---

## 4. Comandos ESC/POS (referencia para `python-escpos`)

| Acción | Comando | Uso |
|---|---|---|
| Inicializar | `ESC @` | Al inicio de cada ticket. |
| Alineación | `ESC a {0/1/2}` | Izq/centro/der (encabezado centrado, cifras der). |
| Énfasis | `ESC E {1/0}` | Negrita on/off (TOTAL, "NOTA DE COMPRA"). |
| Tamaño | `GS ! {n}` | Doble alto/ancho para nombre y TOTAL. |
| Alimentar | `ESC d {n}` | Espaciado entre bloques. |
| Cortar | `GS V {m}` | Corte (parcial/total) al final. |
| ~~Cajón~~ | ~~`ESC p`~~ | **No se usa** (sin cajón). |

> `python-escpos` abstrae la mayoría (`p.set(...)`, `p.text(...)`, `p.cut()`); esta tabla documenta el equivalente ESC/POS por si se requiere control fino.

---

## 5. Reimpresión

- Disponible desde `UI_SPEC.md` §5.8, buscando por folio (escaneable del propio ticket).
- El ticket reimpreso es **idéntico** al original más una leyenda al pie: `*** REIMPRESIÓN <fecha/hora> ***`.
- La reimpresión **no** altera datos de la venta ni del pago.

---

## 6. Manejo de fallos

- **Impresora no disponible:** la venta **se persiste igual** (el cobro no depende de imprimir); el ticket queda disponible para reimpresión. La UI avisa (`--warn`) y ofrece reintentar.
- **Papel agotado / error de dispositivo:** capturar la excepción de `python-escpos`, no romper la venta, registrar y permitir reintento de impresión.

---

## 7. SUPUESTOS y pendientes

- `SUPUESTO` Modelo de impresora; afinar `GS V` (corte parcial vs total) y codificación de caracteres (acentos/`$`) al confirmar.
- `SUPUESTO` Codepage para caracteres latinos (típicamente CP850/CP858 o equivalente); validar acentos y símbolo `$` en el equipo real.
- `SUPUESTO` Inclusión de RFC emisor / dirección en encabezado: opcional, a definir con el titular.
- `SUPUESTO` QR de folio al pie: opcional (útil para devolución por escaneo); confirmar.

---

*THERMAL_TICKET_SPEC · PRY-F-0001.1.8 Maschinario – Bazar · v1.0 · 01-jun-2026 · Residuo para Claude Code.*
