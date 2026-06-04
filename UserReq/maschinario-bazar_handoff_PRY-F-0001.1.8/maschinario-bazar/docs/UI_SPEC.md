# UI_SPEC · POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 2.0 — **reconstruido desde el mockup v2** y las referencias cruzadas del residuo (para aprobación del titular)
**Fecha:** 01-jun-2026
**Consumidor:** Claude Code

> Especifica **pantallas, componentes, design tokens, foco del lector y parciales** de la UI. La UI de producción se construye con **Jinja2 + HTMX (no SPA)** según `ARCHITECTURE.md` ADR-005; el prototipo React (`docs/mockup/`) es **referencia visual**, no se copia como código.
>
> **Nota de origen (honestidad epistémica):** este documento se reconstruyó desde el mockup v2 validado y las referencias cruzadas del residuo (PRD, ACCEPTANCE_TESTS, THERMAL_TICKET_SPEC, PERIPHERALS, ARCHITECTURE). La numeración de secciones honra las anclas ya citadas por otros documentos (§1 identidad, §5.4 Devolución, §5.6 Reportes, §5.8 Reimpresión, §7 parciales HTMX, §8 foco). Pendiente de validación del titular.

---

## 1. Identidad y sistema visual

- **Marca:** `MASCHINARIO · BAZAR`. Lockup en Orbitron (mayúsculas, `MASCHINARIO` con `BAZAR` en tamaño menor + acento teal). `SUPUESTO` Identidad gráfica base **ME Luis Cruz** hasta que exista manual de marca propio de Maschinario (entonces se hace swap de tokens).
- **Nombre del negocio operativo** (encabezado de ticket y barra de sesión): proviene de config `APP_BUSINESS_NAME` (`CLAUDE.md` §3), **no** se hardcodea.
- **Tipografía:** `Orbitron` (marca/títulos), `IBM Plex Sans` (UI), `IBM Plex Mono` (cifras, códigos, metadatos). Cifras monetarias siempre monoespaciadas con `tabular-nums`.
- **Dos zonas cromáticas:**
  - **Chrome oscuro** (tinta/petróleo): topbar, login, Corte de caja. Transmite "sistema".
  - **Operación clara** (neutros fríos): Venta, Cobro, Devolución, Catálogo, Reportes, Reimpresión. Prioriza legibilidad sostenida.
- **Geometría:** radios pequeños (3–5 px), líneas finas, estética técnica.

### 1.1 Design tokens (valores canónicos)

| Grupo | Token | Valor |
|---|---|---|
| Marca (chrome) | petróleo / tinta | `#19424C` / `#09191E` |
| Marca (líneas chrome) | petróleo-2 / tinta-line | `#1F525E` / `#12313A` |
| Acentos marca | rojo / menta / teal / teal-deep | `#B60C0C` / `#A9DFC2` / `#209B9B` / `#1B8484` |
| **Semántico** (separado de marca) | éxito / éxito-soft | `#1E9E5A` / `#E6F4EC` |
| | error / error-soft | `#C62828` / `#FBEAEA` |
| | aviso / aviso-soft | `#C77700` / `#FBF2E3` |
| Superficies claras | bg / surface / surface-2 | `#EBEEEE` / `#FFFFFF` / `#F4F6F6` |
| Texto | ink / ink-2 / muted / faint | `#0C1E23` / `#3C4E53` / `#6B7B7F` / `#9AA8AB` |
| Bordes | line / line-strong | `#D7DDDD` / `#C2C9C9` |

> **Regla dura:** el color **semántico** (éxito/error/aviso) es independiente de los **acentos de marca** (teal/menta/rojo). El rojo de marca **no** comunica error; el error usa `#C62828`. Mantener esa separación en todas las plantillas.

---

## 2. Principios de layout

1. **Total dominante:** en Venta/Cobro el total es el elemento de mayor jerarquía (cifra mono grande sobre tarjeta tinta con borde teal).
2. **Una caja, un flujo lineal:** sin multi-ventana ni concurrencia; cada pantalla resuelve una tarea.
3. **Teclado primero:** el flujo de caja es 100 % operable por teclado (escaneo, cantidades, cobrar, confirmar). Mouse como apoyo.
4. **Foco perpetuo en el lector:** ver §8. El `scan-input` recupera el foco salvo que el cursor esté en otro campo editable legítimo.
5. **Feedback inmediato y no bloqueante:** avisos con color semántico, toasts para confirmaciones.

---

## 3. Componentes compartidos

| Componente | Uso | Notas |
|---|---|---|
| **Topbar / shell** | Marca + navegación + sesión (negocio, terminal, turno, cajero, salir) | Chrome oscuro. Nav resaltada con petróleo + subrayado teal. |
| **`scan-input`** | Campo de captura del lector (Venta, Devolución, Reimpresión, alta de Catálogo) | Mono, grande, autofoco; Enter dispara la acción. Reglas en §8. |
| **Sugerencias** | Dropdown de búsqueda bajo `scan-input` | Navegable con ↑/↓ + Enter. |
| **Tabla de líneas** | Líneas de venta/devolución | Columnas: #, descripción (+código), cantidad (stepper), precio, importe. |
| **Stepper de cantidad** | `−  [n]  +` | Mono; en Devolución el `+` topa en lo vendido. |
| **Total-card** | Total a cobrar / a reembolsar | Tarjeta tinta, cifra mono ~46px, borde de acento (teal cobro / rojo devolución). |
| **Botón primario** | Cobrar / Confirmar | teal; estados disabled claros. |
| **Botón peligro** | Cancelar venta / Devolución | error-soft / rojo. |
| **Tag/chip** | Estado de stock | `ok` (menta/éxito), `low` (aviso), `out` (error). |
| **Toast** | Confirmación de operación | Tinta, esquina inferior, autodescarta ~3 s. |
| **Terminal (cobro tarjeta)** | Visual del estado de la Point | Estados en vivo §5.3. |
| **Ticket-paper** | Vista previa térmica 80 mm | Mono, layout de `THERMAL_TICKET_SPEC.md`; §5.8. |

---

## 4. Shell y navegación

- **Topbar** (chrome): marca a la izquierda; nav al centro; sesión a la derecha (negocio · terminal/turno, avatar de cajero, "Salir").
- **Navegación (6 destinos):** Venta · Devolución · Reimpresión · Catálogo · Reportes · Corte de caja.
- **Teclas de navegación:** `SUPUESTO` F1–F6 como acceso a cada destino (visual en el mockup). Ver §9 para el mapa canónico y su distinción de los atajos de acción dentro de pantalla.

---

## 5. Pantallas

### 5.1 Login (PIN)
Chrome oscuro a pantalla completa, logo de marca, **numpad** y PIN de 4 dígitos. Autenticación por PIN abre **turno** con fondo inicial (`PRD` §4). Error de PIN: shake + mensaje semántico. `SUPUESTO` Etiqueta de versión de build es placeholder.

### 5.2 Venta
Dos columnas. **Izquierda:** `scan-input` (con sugerencias) + tabla de líneas (stepper, quitar línea, estado vacío). **Derecha:** panel fijo con artículos, subtotal, **IVA (16%)**, **total dominante** y botón **COBRAR**.
- Snapshot de descripción/precio/IVA por línea al vender (`PRD` invariante 2).
- Código inexistente → aviso (`--warn`) + búsqueda manual; foco vuelve al `scan-input`.
- **Descuento:** acción que aplica descuento **por línea** y/o **global** (campo de monto/%); recalcula totales. `SUPUESTO` Forma exacta (monto vs %) y permisos por rol a confirmar.
- Cancelar venta limpia el ticket (con confirmación).

### 5.3 Cobro (modal)
Segmento **Efectivo | Tarjeta**.
- **Efectivo:** monto recibido (mono grande), sugerencias de redondeo, **cambio** = recibido − total con color semántico (ok/short). Nunca `pagada` por debajo del total. Opera **offline**.
- **Tarjeta (Point Smart 2):** envía a terminal; estados en vivo **`idle → waiting → approved → done`**. Texto de referencia: **"Mercado Pago Point Smart 2 · contactless habilitado"**.
- **Invariante crítico:** el estado `approved`/venta `pagada` **solo** se alcanza con **confirmación explícita de Mercado Pago** (`INTEGRATION_MP_POINT.md`). La animación del mockup es simulación; en producción el estado se concilia por webhook/polling. Bloqueado sin conexión.

### 5.4 Devolución
Layout espejo de Venta. **Izquierda:** busca por **folio** (escaneable del ticket / QR) → muestra cabecera de la venta (folio, fecha, cajero, medio) y líneas con stepper **topado a lo vendido**. **Derecha:** nota de crédito con subtotal/IVA, **reembolso según el medio original** (efectivo desde caja / reembolso a tarjeta vía Point) y aviso de **reintegro de stock**. Bloqueo si se excede lo vendido (`PRD` módulo Devolución; `ACCEPTANCE_TESTS` §? devolución).

### 5.5 Catálogo / alta + stock
Tabla buscable (código, nombre, categoría, precio, existencia, estado) + formulario lateral de **alta** con **campo de código escaneable**. Import CSV con reporte de errores por fila (`PRD`). Control de stock básico por producto (`controla_stock`).

### 5.6 Reportes / export fiscal
Barra de filtros (**periodo**: hoy/7 días/mes; **cajero**) + **KPIs** (ventas, tickets, ticket promedio, IVA 16%) + desglose **por medio de pago** y **por cajero** (barras) + **tabla de folios** (folio, fecha, cajero, subtotal, IVA, total, medio).
- **Export fiscal:** entrega las ventas del periodo y marca `exportada_fiscal=true`; destino **RFC genérico `XAXX010101000`**; **la app no timbra** (`ACCEPTANCE_TESTS` AT-8.2, ADR-004).

### 5.7 Corte de caja / turno
Chrome oscuro. KPIs del turno + **ventas por medio de pago** + **arqueo de efectivo**: esperado = fondo + ventas efectivo − devoluciones efectivo; captura de efectivo contado; **diferencia** resaltada (cuadrada/faltante/sobrante). Bloqueo de cierre si hay ventas abiertas (`ACCEPTANCE_TESTS` §7). Acciones: reporte X / cerrar turno y caja.

### 5.8 Reimpresión
Panel de búsqueda por **folio** (escaneable) + lista de folios recientes → **vista previa del ticket 80 mm** (todos los campos de `THERMAL_TICKET_SPEC.md`). **Reimprimir** emite un ticket **idéntico** al original más la leyenda al pie `*** REIMPRESIÓN <fecha/hora> ***`. **No altera** datos de la venta ni del pago (`THERMAL_TICKET_SPEC.md` §5).

---

## 6. Estados y feedback

- **Éxito:** verde semántico + toast.
- **Aviso (`--warn`):** ámbar (código inexistente, stock 0, impresora caída → la venta no se rompe).
- **Error:** rojo semántico (PIN incorrecto, cobro rechazado, faltante de caja).
- **Vacío:** ilustración tenue + instrucción ("Escanea un producto para comenzar").
- **Carga/espera:** spinner en cobro tarjeta (`waiting`).

---

## 7. Plantillas Jinja2 y parciales HTMX

- Cada pantalla es una **plantilla** Jinja2; las zonas que cambian sin recargar (tabla de líneas, panel de totales, estado de cobro, resultados de búsqueda, vista de ticket) son **parciales** servidos por endpoints y montados con **swaps HTMX** (`hx-get`/`hx-post`/`hx-target`).
- Sin lógica de negocio en plantillas (`CLAUDE.md` §7): `routers` → `services` → `models`.
- Estructura: `app/templates/` (plantillas + parciales) y `app/static/` (CSS de marca con los tokens de §1, JS mínimo para foco/atajos). Routers correspondientes: `venta, cobro, devolucion, catalogo, corte, reportes, auth` (`ARCHITECTURE.md` §4).
- Tras cada swap que reemplace la tabla o cierre un modal, re-aplicar foco al `scan-input` (§8) con un hook `htmx:afterSwap` (JS mínimo).

---

## 8. Foco del lector (`scan-input`) — crítico

Alineado con `PERIPHERALS.md` §2. El lector NETUM C750 opera como **HID keyboard-wedge**: escribe en el campo enfocado y termina en **Enter**. Reglas:

1. **Auto-foco** al `scan-input` al cargar la pantalla que lo use (Venta, Devolución, Reimpresión, alta de Catálogo).
2. **Recuperar foco** cuando: se cierra un modal, termina un swap HTMX que reemplaza la tabla, o se hace clic en zona no editable.
3. **No robar foco** si el cursor está en otro campo editable legítimo (monto recibido en cobro, búsqueda de catálogo).
4. **Enter en `scan-input`** dispara la acción del contexto: alta de producto (Venta), lookup de folio (Devolución/Reimpresión).
5. **Código/folio no encontrado** → aviso (`--warn`) + búsqueda manual; el foco vuelve al `scan-input`.
6. **Anti-doble lectura:** ignorar lecturas idénticas dentro de ~150 ms (debounce).

---

## 9. Teclado y accesibilidad

- Flujo de caja **100 % operable por teclado**.
- **Dos namespaces de atajos** (a reconciliar; el mockup los muestra mezclados):
  - **Navegación:** `SUPUESTO` F1–F6 → Venta / Devolución / Reimpresión / Catálogo / Reportes / Corte.
  - **Acción dentro de pantalla:** `SUPUESTO` (de `PERIPHERALS.md` §3) `F2` cobrar · `F3` descuento · `Supr` quitar línea · `Esc` cerrar/cancelar · `Enter` confirmar.
  - **Conflicto detectado:** F2/F3 colisionan entre navegación y acción. **A confirmar con el titular** un mapa único (p. ej. navegación con `Alt`+Fn, acciones con Fn; o cobrar=`F12` como en el panel de Venta). No congelado.
- Numpad en pantalla como apoyo para PIN/montos (clic), secundario al teclado físico.

---

## 10. SUPUESTOS y pendientes

- `SUPUESTO` Identidad gráfica base ME Luis Cruz; swap de tokens al existir manual propio de Maschinario.
- `SUPUESTO` Mapa de atajos de teclado (ver §9) — **conflicto F2/F3 a resolver**.
- `SUPUESTO` Forma del descuento (monto vs %, por línea/global, permiso por rol) — §5.2.
- `SUPUESTO` Datos de marca del negocio en el ticket vía `APP_BUSINESS_NAME`.
- Pendiente: validar legibilidad de la vista de ticket contra el ancho real de 80 mm / ~48 columnas (`THERMAL_TICKET_SPEC.md`).
- El mockup (`docs/mockup/`) es referencia visual; ante divergencia, este `UI_SPEC` prevalece para la construcción.

---

*UI_SPEC · PRY-F-0001.1.8 Maschinario – Bazar · v2.0 (reconstruido) · 01-jun-2026 · Residuo para Claude Code.*
