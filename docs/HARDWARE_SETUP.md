# Guía de preparación de hardware — primer uso ("prueba de fuego")

**Proyecto:** PRY-F-0001.1.8 `Maschinario · Bazar` · **SO objetivo:** Ubuntu (ThinkPad P52s)
**Aplica a:** primer estreno de los 3 dispositivos — impresora térmica 80 mm,
lector de código de barras NETUM y terminal **Mercado Pago Point Smart 2**.

> Sigue las secciones **en orden** (0 → 4). Cada paso indica cómo **verificar** que
> quedó bien antes de avanzar. Lo marcado `SUPUESTO` debe confirmarse contra el
> equipo/documentación reales (modelo de impresora, endpoints MP vigentes).
> Referencias del diseño: `docs/THERMAL_TICKET_SPEC.md`, `docs/PERIPHERALS.md`,
> `docs/INTEGRATION_MP_POINT.md`.

---

## 0. Antes de empezar (host Ubuntu)

1. **Paquetes del sistema** (lector USB de impresora y utilidades):
   ```bash
   sudo apt update
   sudo apt install -y usbutils libusb-1.0-0
   ```
   - `usbutils` aporta `lsusb`. `libusb-1.0-0` lo usa `python-escpos` para hablar
     con la impresora por USB crudo (sin driver de impresión).

2. **App lista** (en la carpeta del proyecto):
   ```bash
   docker compose up -d db
   source .venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head
   python -m app.seed            # admin + productos demo ([DEMO]/DEMO-####)
   ```
   Aún **no** levantes `uvicorn`: primero preparamos los dispositivos.

3. **Tu `.env`** (copia de `.env.example`). Lo iremos completando en cada sección:
   ```bash
   cp .env.example .env   # si no existe
   ```
   Variables relevantes para hardware/pago:
   ```
   MP_ACCESS_TOKEN=        # §3
   MP_TERMINAL_ID=         # §3
   PRINTER_USB_VENDOR=     # §1  (hex, p. ej. 0x0416)
   PRINTER_USB_PRODUCT=    # §1  (hex, p. ej. 0x5011)
   APP_SECRET_KEY=         # define uno propio (cadena larga aleatoria)
   ```

4. **Tu usuario y grupos** (para permisos USB sin `sudo`):
   ```bash
   whoami; groups
   ```
   Guarda tu usuario; lo usaremos en la regla udev de la impresora (§1.4).

---

## 1. Impresora térmica 80 mm (ESC/POS por USB)

> Equipo confirmado: **Rongta RP850** (POS térmica 80 mm, ESC/POS por USB). El
> procedimiento aplica tal cual; el único punto a afinar suele ser el *codepage* de
> acentos/`$` (ver §1.5).

### 1.1 Conexión física y papel
1. Conecta el cable USB de la impresora al P52s y enciéndela.
2. Carga el **rollo térmico de 80 mm**: levanta la tapa, coloca el rollo de modo que
   el papel salga **por encima** (el lado térmico va hacia el cabezal). Cierra la tapa
   dejando salir un tramo de papel.
3. **Cómo saber cuál es el lado térmico:** raya el papel con la uña; el lado que se
   marca (oscurece) es el térmico y debe quedar hacia el cabezal. Si imprime en blanco,
   el rollo está al revés.

### 1.2 Identificar el dispositivo USB (idVendor:idProduct)
1. Con la impresora **apagada o desconectada**, ejecuta:
   ```bash
   lsusb > /tmp/usb_antes.txt
   ```
2. **Conéctala/enciéndela** y ejecuta:
   ```bash
   lsusb > /tmp/usb_despues.txt
   diff /tmp/usb_antes.txt /tmp/usb_despues.txt
   ```
   La línea **nueva** es tu impresora. Ejemplo:
   ```
   > Bus 001 Device 007: ID 0416:5011 Winbond Electronics Corp. Virtual Com Port
   ```
   Aquí `idVendor=0416` y `idProduct=5011` (en **hex**).
3. Confírmalo también con el kernel:
   ```bash
   dmesg | tail -n 20      # debe mostrar el dispositivo USB recién conectado
   ```

### 1.3 Anotar en `.env`
Escribe los valores en **hex con prefijo `0x`**:
```
PRINTER_USB_VENDOR=0x0416
PRINTER_USB_PRODUCT=0x5011
```
(sustituye por los tuyos).

### 1.4 Permisos USB sin root (regla udev)
Por defecto Ubuntu no deja a tu usuario abrir el USB crudo. Crea una regla:

```bash
sudo tee /etc/udev/rules.d/99-escpos-maschinario.rules >/dev/null <<'EOF'
# Impresora térmica ESC/POS — acceso sin root para Maschinario · Bazar
SUBSYSTEM=="usb", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="5011", MODE="0660", GROUP="plugdev", TAG+="uaccess"
EOF
```
- **Reemplaza** `0416`/`5011` por los tuyos (aquí van **sin** `0x`, en minúsculas).
- Asegúrate de pertenecer al grupo `plugdev`:
  ```bash
  sudo usermod -aG plugdev "$USER"      # si no aparecía en 'groups'
  ```
- Recarga reglas y reconecta la impresora:
  ```bash
  sudo udevadm control --reload-rules && sudo udevadm trigger
  ```
  Desconecta y reconecta la impresora (o reinicia sesión si te agregaste a `plugdev`).

### 1.5 Prueba directa (sin la app)
Con el venv activo y los IDs correctos:
```bash
python - <<'PY'
from escpos.printer import Usb
p = Usb(0x0416, 0x5011)          # usa TUS ids
p.text("Maschinario · Bazar\nPRUEBA DE IMPRESORA\nAcentos: áéíóú ñ  Símbolo: $123.45\n")
p.cut()
print("Enviado a la impresora.")
PY
```
**Resultado esperado:** sale un tiquete con el texto y **corta** el papel.

**Acentos / `$` (codepage RP850):** si salen caracteres raros, la RP850 funciona bien
fijando el *codepage* a **CP850** (o **CP858** si quieres el símbolo `€`). Prueba:
```bash
python - <<'PY'
from escpos.printer import Usb
p = Usb(0x0416, 0x5011)          # usa TUS ids
p.charcode("CP850")              # RP850: CP850 (o "CP858")
p.text("Acentos: áéíóú ñ Ñ  ·  Símbolo: $1,234.50\n")
p.cut()
PY
```
- Si con **CP850** se ven bien, ese es el valor: lo dejamos fijo en
  `app/services/printing.py` (línea de `charcode`) durante el **paso 2 (ajustes)**.
- Si aún fallan, prueba `"CP858"` o `"CP437"` y anota cuál funcionó.
- Errores comunes:
  | Síntoma | Causa / solución |
  |---|---|
  | `USBError: Access denied` / `Permission denied` | Falta la regla udev (§1.4) o no estás en `plugdev`. Reconecta / reinicia sesión. |
  | `Device not found` | idVendor/idProduct equivocados (revisa `lsusb`). |
  | `Resource busy` | El kernel cargó `usblp`/CUPS sobre el equipo. Quítalo temporalmente: `sudo modprobe -r usblp` y reintenta. |
  | Imprime en blanco | Rollo al revés (§1.1, prueba de la uña). |

### 1.6 Verificación con la app
Tras `uvicorn` (ver §4), una venta cobrada debe imprimir el tiquete; si la impresora
está apagada, **la venta no se rompe** y el tiquete queda para **reimpresión**
(pantalla Reimpresión, por folio). Esto valida `THERMAL_TICKET_SPEC §6` y AT-9.2.

---

## 2. Lector de código de barras NETUM (HID keyboard-wedge)

> Equipo confirmado: **NETUM C750** (lector 1D/2D inalámbrico). Opera como **teclado**
> (HID keyboard-wedge): no requiere driver. La app solo necesita que escriba en el campo
> enfocado y termine en **Enter** (`docs/PERIPHERALS.md §1`).

### 2.1 Conexión (C750)
- **Dongle 2.4 GHz** (lo más común en el C750): inserta el receptor USB en el P52s; el
  lector se vincula solo (enciende el gatillo, beep de listo).
- **Cable USB**: también funciona como lector con cable (modo HID).
- El C750 trae **batería**: cárgalo si el LED lo indica.
- Espera unos segundos tras conectar; un beep/LED indica que está listo.

### 2.2 Verificar que "teclea" (sin la app)
1. Abre un editor de texto (gedit, o una terminal con un `cat`).
2. Escanea **cualquier** código de barras (de un producto a la mano).
3. **Esperado:** aparecen los dígitos del código **y** un salto de línea (el sufijo
   **Enter**). Si los dígitos aparecen pero **no** salta de línea → falta el sufijo
   Enter (ver §2.3).

### 2.3 Configurar sufijo Enter (solo si falta)
El **NETUM C750** trae **Enter (CR/LF)** de fábrica; normalmente no hay que tocar nada.
Si por alguna razón no salta de línea:
- En el **manual del C750**, escanea **"Add CR suffix"** (o **"Enter/CR Suffix On"**).
- Si quedó en un estado raro, escanea primero **"Restore Factory Defaults"** del manual y
  vuelve a probar (el default ya incluye Enter).
- `SUPUESTO` sin **prefijo** (la app no lo requiere en v1).
- Vuelve a probar §2.2.

### 2.4 Layout de teclado (acentos/símbolos)
- Para códigos **numéricos** (EAN-13, etc.) no suele haber problema.
- Si un código alfanumérico sale con símbolos cambiados, el lector está en otro layout.
  Ponlo en **US** (o el que coincida con tu teclado de Ubuntu) con los códigos del manual.

### 2.5 Prueba con la app (foco automático del `scan-input`)
1. Levanta la app (§4) y entra a **Venta**: el cursor queda en el campo de escaneo.
2. Para que un escaneo **agregue** una línea, el código debe existir en el catálogo.
   Opciones para la prueba:
   - **Da de alta** (como admin, en **Catálogo**) un producto usando el **código del
     artículo físico** que vas a escanear, o
   - genera un código de barras de prueba para uno de los **EAN demo** (p. ej.
     `7501031311309` = «[DEMO] Cuaderno…») en un generador online y escanéalo desde la
     pantalla del teléfono.
3. **Esperado:** al escanear, se agrega/incrementa la línea sin tocar el ratón.
   - Código inexistente → aviso ámbar y el foco vuelve al campo (AT-2.2).
   - Doble disparo accidental → la app ignora lecturas idénticas < ~150 ms (AT-10.2).

---

## 3. Terminal Mercado Pago Point Smart 2 (API de Orders)

> Cobro con tarjeta presencial. El efectivo **no** pasa por aquí. Detalle del contrato
> en `docs/INTEGRATION_MP_POINT.md`.
>
> **Importante (tu caso): solo tienes credenciales de PRODUCCIÓN, no TEST.** La
> simulación sin dinero requiere un **entorno/credenciales de prueba**. Tienes dos
> caminos seguros (elige uno en §3.2):
> - **A (recomendado):** crea una **aplicación de prueba** gratis en el panel de
>   desarrollador de MP para obtener credenciales TEST y poder **simular** (§3.5).
> - **B:** ve directo a un **cobro real de monto mínimo** y **reembólsalo** enseguida
>   (§3.6). Implica una transacción real (y su comisión).

### 3.1 Preparar la terminal
1. Enciende la Point Smart 2, conéctala a **Internet** (WiFi de la caja o datos) y
   verifica batería.
2. En la **app de Mercado Pago / panel de cobros**, **vincula** la terminal a tu cuenta
   (sucursal + caja + punto de venta). Debe aparecer **en línea**.
3. Ponla en **modo integrado / PDV** para que reciba órdenes desde el sistema (no modo
   autónomo). Se ajusta desde el **menú de la terminal** (Ajustes → Modo de operación →
   *Punto de venta integrado*) o por API (§3.4). `SUPUESTO`: nombre exacto del menú.

### 3.2 Credenciales (Access Token)
Tienes credenciales de **producción**. Elige el camino de prueba:

- **Camino A — obtener credenciales TEST (recomendado, sin dinero):**
  1. En **developers.mercadopago.com → Tus integraciones**, crea (o abre) una
     **aplicación**; en **Credenciales** verás un juego **TEST** y otro **Producción**.
  2. Copia el **Access Token de TEST** a `.env` para la fase simulada (§3.5):
     ```
     MP_ACCESS_TOKEN=TEST-...        # credenciales de prueba
     ```
  3. Tras validar en simulado, cámbialo al de **producción** para el cobro real (§3.6).

- **Camino B — solo producción (cobro real mínimo + reembolso):**
  ```
  MP_ACCESS_TOKEN=APP_USR-...        # producción
  ```
  Sáltate §3.5 y ve a §3.6.

> El token es secreto: vive en `.env` (no se versiona). Para listar terminales y cobrar,
> el token y el `terminal_id` deben ser del **mismo entorno** (TEST con TEST, prod con prod).

### 3.3 Obtener el `terminal_id`
Con el token cargado, lista las terminales de la cuenta:
```bash
source .venv/bin/activate
python - <<'PY'
import os, httpx
from dotenv import load_dotenv  # si no está: pip install python-dotenv
load_dotenv()
tok = os.environ["MP_ACCESS_TOKEN"]
r = httpx.get("https://api.mercadopago.com/v1/point/terminals",
              headers={"Authorization": f"Bearer {tok}"}, timeout=15)
print(r.status_code)
print(r.text)
PY
```
Copia el `id` de tu terminal (formato tipo `NEWLAND_N950__...`) a `.env`:
```
MP_TERMINAL_ID=NEWLAND_N950__XXXXXXXX
```

### 3.4 (Si hiciera falta) forzar modo integrado por API
Si la terminal no quedó en modo integrado desde el menú:
```bash
# `SUPUESTO`: confirma endpoint/campo contra la doc vigente (INTEGRATION §3).
curl -X PATCH "https://api.mercadopago.com/v1/point/terminals/operating-mode" \
  -H "Authorization: Bearer $MP_ACCESS_TOKEN" -H "Content-Type: application/json" \
  -d '{"terminals":[{"id":"'"$MP_TERMINAL_ID"'","operating_mode":"PDV"}]}'
```

### 3.5 Prueba SIMULADA (sin dinero real) — solo Camino A (credenciales TEST)
> Requiere el **Access Token de TEST** de §3.2. Si vas por el Camino B (solo
> producción), **omite esta sección** y pasa a §3.6.

1. Levanta la app (§4), haz una venta y elige **Cobrar → Tarjeta → Enviar cobro a la
   terminal**. La app crea la *order* y queda **"Esperando pago…"** (hace *polling*).
2. En otra terminal, **simula** la aprobación de esa order (`docs/INTEGRATION_MP_POINT.md §2`):
   ```bash
   # Toma el ORDER_ID que la app guardó (o el último de GET /v1/orders).
   # `SUPUESTO`: ruta/método de simulación según doc vigente.
   curl -X POST "https://api.mercadopago.com/v1/orders/{ORDER_ID}/simulate" \
     -H "Authorization: Bearer $MP_ACCESS_TOKEN" -H "Content-Type: application/json" \
     -d '{"status":"processed"}'
   ```
3. **Esperado:** en ≤ 2 s la app concilia por `GET` y la venta pasa a **pagada**; se
   imprime el tiquete. Valida AT-4.1/4.2 con cero riesgo de cobro.

### 3.6 Prueba REAL (cobro mínimo + reembolso) — Camino B (o cierre del A)
> Como **no tienes credenciales TEST**, esta es la validación de cobro real. Usa un
> **monto mínimo** y **reembólsalo** enseguida. Ten presente que es una transacción real
> y puede causar una **comisión** de MP aunque reembolses.

1. Con `MP_ACCESS_TOKEN` de **producción** y `MP_TERMINAL_ID` de producción, reinicia
   `uvicorn`.
2. Haz una venta de **monto mínimo** (p. ej. $5) y cobra con tarjeta; **acerca/inserta**
   una tarjeta real en la Point.
3. **Esperado:** la terminal procesa, la app recibe **aprobado** (vía `GET`, nunca antes)
   y la venta queda **pagada**; imprime tiquete.
4. **Reembolsa de inmediato:** en la app, **Devolución** por el folio de esa venta →
   dispara el `refund` de la order (recupera el monto). Valida AT-5.3 de paso.

### 3.7 Problemas frecuentes (de `INTEGRATION_MP_POINT.md §8`)
| HTTP / estado | Significado | Acción |
|---|---|---|
| 401 `unauthorized` | Access Token incorrecto | Revisa `.env`; no reintentar en bucle. |
| 403 `forbidden_checking_terminal_owner` | La terminal no es de la cuenta | Revisa vinculación / `MP_TERMINAL_ID`. |
| 409 `already_queued_order_for_terminal` | Ya hay una order en espera | La app cancela la previa y reintenta (AT-4.5). |
| Sin Internet | — | Tarjeta **se bloquea** con aviso; el **efectivo opera** (AT-4.7). |
| Terminal en modo autónomo | No recibe órdenes | Ponla en **modo integrado/PDV** (§3.1/§3.4). |

---

## 4. Arranque y prueba end-to-end

1. **Levanta todo:**
   ```bash
   docker compose up -d db
   source .venv/bin/activate
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. Abre `http://127.0.0.1:8000` y **entra**: usuario `admin`, PIN `2468`
   (cámbialo después). Abre turno con un fondo inicial.
3. **Recorre todos los módulos** (checklist de la prueba de fuego):

   | # | Módulo | Acción | OK |
   |---|---|---|----|
   | 1 | Login / turno | Entrar como admin, abrir turno | ☐ |
   | 2 | Lector | Escanear y que agregue línea en Venta | ☐ |
   | 3 | Venta | Cantidades, descuento, total con IVA 16% | ☐ |
   | 4 | Cobro efectivo | Cambio correcto; venta pagada | ☐ |
   | 5 | Impresora | Tiquete impreso y cortado | ☐ |
   | 6 | Cobro tarjeta (SIMULADO) | Solo Camino A (TEST, §3.5); si no, omitir | ☐ |
   | 7 | Cobro tarjeta (REAL) | Cobro mínimo aprobado **+ reembolso** (§3.6) | ☐ |
   | 8 | Reimpresión | Reimprimir por folio (idéntico + leyenda) | ☐ |
   | 9 | Devolución | Por folio, reintegra stock / refund tarjeta | ☐ |
   | 10 | Catálogo | Alta + import CSV (como admin) | ☐ |
   | 11 | Reportes / export | KPIs + export fiscal CSV (RFC genérico) | ☐ |
   | 12 | Corte de caja | Arqueo, diferencia, cierre de turno | ☐ |
   | 13 | Roles | Cajero no-admin: 403 en catálogo/usuarios | ☐ |

4. **Apunta cada hallazgo** (lo que falle o se vea raro): será la entrada para el
   **paso 2 del cierre del proyecto** (ajustes de código).

---

## 5. Valores a tener listos (resumen del `.env`)

```
DATABASE_URL=postgresql+psycopg://pos:pos@localhost:5432/maschinario
DB_HOST_PORT=5433            # si el 5432 del host está ocupado (ver nota)
MP_ACCESS_TOKEN=             # §3.2 (producción; TEST opcional para simular)
MP_TERMINAL_ID=              # §3.3 (del mismo entorno que el token)
PRINTER_USB_VENDOR=0x????    # §1.2/1.3 (Rongta RP850)
PRINTER_USB_PRODUCT=0x????   # §1.2/1.3 (Rongta RP850)
APP_BUSINESS_NAME=Maschinario · Bazar
APP_IVA_RATE=0.16
APP_SECRET_KEY=<cadena-larga-aleatoria>
```
> Si usas `DB_HOST_PORT=5433`, el `DATABASE_URL` debe terminar en `:5433/maschinario`.

---

## 6. Hallazgos pendientes a confirmar en la prueba
- **Impresora Rongta RP850** (confirmada): falta validar el **codepage** correcto de
  acentos/`$` (probar CP850 → CP858 → CP437) y fijarlo en `app/services/printing.py`.
- **Lector NETUM C750** (confirmado): confirmar que el sufijo **Enter** viene activo de
  fábrica (lo normal) y el layout de teclado.
- **MP**: endpoints/campos exactos para **modo de operación** y **simulación** (doc
  vigente). **No hay credenciales TEST**: la prueba de tarjeta es real + reembolso (§3.6),
  salvo que crees una app de prueba (§3.2 Camino A).

---
*HARDWARE_SETUP · PRY-F-0001.1.8 Maschinario · Bazar · guía de primer uso · Ubuntu (P52s).*
