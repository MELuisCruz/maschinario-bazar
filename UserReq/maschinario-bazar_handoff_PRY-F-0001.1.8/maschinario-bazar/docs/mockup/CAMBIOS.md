# Mockup de referencia · MASCHINARIO · BAZAR — v2

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar` · **Anexo visual** (referencia de *look & feel*)
**Fecha:** 01-jun-2026 · **Naturaleza:** prototipo React (Babel en navegador). **No es la UI de producción** (producción = Jinja2 + HTMX, ADR-005).

## Cómo verlo
Abrir `index.html` en un navegador. PIN demo de acceso: **2 4 6 8**.

## Cambios respecto a v1 (prototipo anterior)
- **Marca:** `VECTOR POS` → **`MASCHINARIO · BAZAR`** en chrome, login, footer y título.
- **Terminal de cobro:** referencia `Terminal BBVA` → **`Mercado Pago Point Smart 2`** en el flujo de tarjeta.
- **Pantallas nuevas** (antes faltaban):
  - **Devolución** (`UI_SPEC` §5.4): busca folio, devolución total/parcial con tope a lo vendido, reembolso según medio original (efectivo / tarjeta vía Point), reintegro de stock.
  - **Reportes** (`UI_SPEC` §5.6): totales por periodo / medio de pago / cajero, detalle de folios y **export fiscal** a RFC genérico `XAXX010101000` (marca `exportada_fiscal`; **la app no timbra**).
  - **Reimpresión** (`UI_SPEC` §5.8): busca folio, previsualiza el ticket 80 mm y reimprime **idéntico** + leyenda `*** REIMPRESIÓN <fecha/hora> ***`; no altera la venta.
- **Navegación** ampliada a 6 destinos (Venta · Devolución · Reimpresión · Catálogo · Reportes · Corte) con *fallback* responsivo.

## Conservado de v1 (sin cambios)
- Tokens de marca (petróleo/tinta/rojo/menta/teal) y semánticos (éxito/error/aviso) **separados**.
- Tipografía Orbitron + IBM Plex Sans + IBM Plex Mono; dos zonas (chrome oscuro / operación clara).
- Foco del `scan-input`, total dominante y flujo de cobro con estado en vivo (efectivo y tarjeta).

## Notas de honestidad epistémica
- `SUPUESTO` Identidad gráfica basada en **ME Luis Cruz** (pendiente: manual de marca propio de Maschinario; al existir, se hace swap de tokens en `UI_SPEC`).
- `SUPUESTO` Datos semilla (productos, folios, cajeros, montos) son **ficticios** para demostración.
- `SUPUESTO` Teclas de navegación F1–F6 visuales; los atajos operativos finos viven en `PERIPHERALS`/`UI_SPEC`.
- **Nota de sesión:** el `UI_SPEC.md` v1.0 no estuvo adjunto en esta sesión; las pantallas nuevas se construyeron alineadas a las referencias cruzadas del residuo (PRD, ACCEPTANCE_TESTS, THERMAL_TICKET_SPEC, PERIPHERALS) y al relevo §4. Conviene revisarlas contra el `UI_SPEC` íntegro al archivar.

## Estructura
`index.html` · `styles.css` (tokens + chrome) · `screens.css` · `data.js` (semilla) · `icons.jsx` · `app.jsx` (shell/nav) · pantallas: `login` `venta` `cobro` `catalogo` `corte` `devolucion` `reportes` `reimpresion`.
