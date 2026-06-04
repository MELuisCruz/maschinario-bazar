# PERIPHERALS · POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 1.0 (para aprobación del titular)
**Fecha:** 01-jun-2026
**Consumidor:** Claude Code

> Captura de periféricos del POS. La impresora térmica vive en `THERMAL_TICKET_SPEC.md`; aquí: **lector de código de barras**, **teclado/mouse** y manejo de **foco**. Operación principal **mouse + teclado** (decisión 01-jun-2026).

---

## 1. Lector de código de barras

- **Modelo:** NETUM 1D/2D (USB / dongle 2.4G / Bluetooth).
- **Modo:** **HID keyboard-wedge** — el lector se comporta como un **teclado**; **no requiere driver** ni SDK. Escribe los caracteres del código en el campo enfocado del navegador, terminados en **Enter**.
- **Implicación clave:** la app **no “habla” con el lector**; solo necesita **garantizar el foco** en el campo correcto y reaccionar al Enter.

### 1.1 Captura
- **Longitud variable:** no asumir longitud fija (EAN-13, Code128, QR, etc. difieren). El **Enter (sufijo)** delimita el fin del código.
- **Velocidad:** el lector "teclea" muy rápido; un humano, lento. Se puede distinguir un escaneo de tecleo manual por la cadencia, pero **no es necesario** para v1: basta con tratar el contenido del `scan-input` al recibir Enter.
- **Anti-doble lectura:** ignorar lecturas idénticas dentro de ~150 ms (debounce) para evitar duplicados por rebote del gatillo.

### 1.2 Configuración del lector (una vez, fuera de la app)
- Asegurar **sufijo Enter (CR/LF)** activado (default de fábrica en la mayoría de NETUM; si no, se programa con los códigos del manual del lector).
- `SUPUESTO` Sin prefijo. Si se configurara un prefijo identificador, la app puede usarlo para distinguir escaneo de tecleo (mejora opcional, no v1).

---

## 2. Manejo de foco (crítico)

El lector solo funciona si el `scan-input` tiene el foco. Reglas (alineadas con `UI_SPEC.md` §8):

1. **Auto-foco** al `scan-input` en la pantalla de venta al cargar.
2. **Recuperar foco** cuando: se cierra un modal, termina un swap HTMX que reemplaza la tabla, o el usuario hace clic en zona no editable.
3. **No robar foco** si el cursor está en otro campo editable legítimo (p. ej. monto recibido en cobro, búsqueda de catálogo).
4. **Enter en `scan-input`** dispara el alta del producto (lookup por `codigo_barras` en `productos`).
5. **Código no encontrado** → aviso (`--warn`) + opción de búsqueda manual; el foco vuelve al `scan-input`.

> Implementación: JS mínimo (compatible con el enfoque Jinja2+HTMX, no SPA). El foco se re-aplica tras cada intercambio HTMX con un pequeño hook (`htmx:afterSwap`).

---

## 3. Teclado y mouse

- **Operación principal: teclado + mouse** (sin pantalla táctil en v1).
- **Teclado:** el flujo de caja debe ser **100% operable por teclado** (escaneo, cantidades, cobrar, confirmar). Atajos sugeridos (`SUPUESTO`, confirmar con el titular):
  - `F2` cobrar · `F3` descuento · `Supr` quitar línea · `Esc` cerrar modal/cancelar · `Enter` confirmar.
- **Mouse:** soporte estándar para botones y tablas; no indispensable para el flujo rápido.
- **Numpad en pantalla:** apoyo para PIN y montos (clic), **secundario** frente al teclado físico.

---

## 4. Otros periféricos

- **Cajón de dinero:** **no hay** (decisión 01-jun-2026). Sin integración ni comando de apertura.
- **Báscula / otros:** fuera de alcance v1.

---

## 5. SUPUESTOS y pendientes

- `SUPUESTO` NETUM ya configurado con sufijo Enter y sin prefijo.
- `SUPUESTO` Atajos de teclado propuestos; confirmar con el titular.
- `SUPUESTO` Operación con teclado+mouse (no touch); si cambiara a touch, revisar `UI_SPEC.md` (`--tap-min`, numpad).
- Pendiente: pruebas con el lector y la máquina reales (cadencia, codificación de caracteres del código).

---

*PERIPHERALS · PRY-F-0001.1.8 Maschinario – Bazar · v1.0 · 01-jun-2026 · Residuo para Claude Code.*
