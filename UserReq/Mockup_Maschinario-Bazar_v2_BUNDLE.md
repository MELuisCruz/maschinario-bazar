# Mockup de referencia · MASCHINARIO · BAZAR — v2 (bundle)

> Anexo visual del proyecto **PRY-F-0001.1.8 `Maschinario – Bazar`**. Referencia de *look & feel*, **no** la UI de producción (producción = Jinja2 + HTMX, ADR-005). Prototipo React (Babel en navegador).

> Este archivo único reúne todas las fuentes del mockup para archivarlo en la base de conocimiento del proyecto. Para ejecutarlo, reconstruir los archivos individuales y abrir `index.html` (PIN demo: 2 4 6 8).

## Manifiesto de archivos

- `CAMBIOS.md`
- `index.html`
- `data.js`
- `icons.jsx`
- `app.jsx`
- `login.jsx`
- `venta.jsx`
- `cobro.jsx`
- `catalogo.jsx`
- `corte.jsx`
- `devolucion.jsx`
- `reportes.jsx`
- `reimpresion.jsx`
- `styles.css`
- `screens.css`

---

## `CAMBIOS.md`

````markdown
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
````

## `index.html`

````html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MASCHINARIO · BAZAR — Punto de Venta</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800;900&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
  <link rel="stylesheet" href="screens.css" />
</head>
<body>
  <div id="root"></div>

  <script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>

  <script src="data.js"></script>
  <script type="text/babel" src="icons.jsx"></script>
  <script type="text/babel" src="login.jsx"></script>
  <script type="text/babel" src="venta.jsx"></script>
  <script type="text/babel" src="cobro.jsx"></script>
  <script type="text/babel" src="catalogo.jsx"></script>
  <script type="text/babel" src="corte.jsx"></script>
  <script type="text/babel" src="devolucion.jsx"></script>
  <script type="text/babel" src="reportes.jsx"></script>
  <script type="text/babel" src="reimpresion.jsx"></script>
  <script type="text/babel" src="app.jsx"></script>
</body>
</html>
````

## `data.js`

````js
/* Product catalog seed data — bazar / variety store (MXN, IVA 16%) */
window.IVA_RATE = 0.16;

window.SEED_PRODUCTS = [
  { code: "7501031311309", name: "Cuaderno profesional 100 hojas", price: 32.50, stock: 48, cat: "Papelería" },
  { code: "7501234567890", name: "Pluma tinta negra (pza)", price: 8.00, stock: 230, cat: "Papelería" },
  { code: "7502211000017", name: "Lápiz HB no.2", price: 5.50, stock: 184, cat: "Papelería" },
  { code: "7501045401123", name: "Pilas AA alcalinas 2 pzas", price: 38.90, stock: 26, cat: "Eléctrico" },
  { code: "7501045409877", name: "Pilas AAA alcalinas 2 pzas", price: 36.00, stock: 9, cat: "Eléctrico" },
  { code: "7503007654321", name: "Foco LED 9W luz cálida", price: 45.00, stock: 31, cat: "Eléctrico" },
  { code: "7501008123456", name: "Cinta adhesiva transparente 18mm", price: 14.50, stock: 72, cat: "Ferretería" },
  { code: "7501008998877", name: "Cinta canela empaque 48mm", price: 26.00, stock: 40, cat: "Ferretería" },
  { code: "7506306412345", name: "Vasos desechables 12oz 25pz", price: 28.00, stock: 53, cat: "Desechables" },
  { code: "7506306498765", name: "Platos desechables no.10 20pz", price: 24.50, stock: 0, cat: "Desechables" },
  { code: "7501999000123", name: "Vela parafina blanca (pza)", price: 6.50, stock: 120, cat: "Hogar" },
  { code: "7501999000444", name: "Encendedor recargable", price: 12.00, stock: 64, cat: "Hogar" },
  { code: "7501020304055", name: "Jabón tocador 150g", price: 13.50, stock: 88, cat: "Limpieza" },
  { code: "7501020309988", name: "Cloro 950ml", price: 21.00, stock: 7, cat: "Limpieza" },
  { code: "7501020311220", name: "Fibra esponja doble uso", price: 9.00, stock: 110, cat: "Limpieza" },
  { code: "7501777001234", name: "Cargador USB-C 1m", price: 59.00, stock: 18, cat: "Eléctrico" },
  { code: "7501777005678", name: "Audífonos alámbricos 3.5mm", price: 79.00, stock: 12, cat: "Eléctrico" },
  { code: "7501555000990", name: "Cinta métrica 3m", price: 34.00, stock: 22, cat: "Ferretería" },
  { code: "7501555002211", name: "Juego destornilladores 6pz", price: 89.00, stock: 5, cat: "Ferretería" },
  { code: "7501333008812", name: "Bolsa basura jumbo 10pz", price: 27.50, stock: 44, cat: "Limpieza" },
  { code: "7501888112233", name: "Marcador permanente negro", price: 16.00, stock: 67, cat: "Papelería" },
  { code: "7501888556677", name: "Resistol blanco 250g", price: 33.00, stock: 29, cat: "Papelería" },
  { code: "7501444667788", name: "Guantes latex talla M 5pz", price: 19.50, stock: 8, cat: "Limpieza" },
  { code: "7501222334455", name: "Extensión eléctrica 3m", price: 65.00, stock: 14, cat: "Eléctrico" },
];

/* Historical sales seed — folios cerrados del turno (para Devolución, Reportes, Reimpresión).
   total = precio público con IVA incluido (16%). subtotal/iva derivados. */
window.SEED_SALES = [
  { folio: "B-001038", fecha: "2026-06-01T09:14:00", cajero: "M. Ruiz", medio: "Efectivo",
    ref: null, lines: [
      { code: "7501031311309", name: "Cuaderno profesional 100 hojas", qty: 2, price: 32.50 },
      { code: "7501234567890", name: "Pluma tinta negra (pza)", qty: 5, price: 8.00 },
    ] },
  { folio: "B-001039", fecha: "2026-06-01T09:41:00", cajero: "M. Ruiz", medio: "Tarjeta",
    ref: "MP 4QK9-2207 · VISA ****4021", lines: [
      { code: "7501777001234", name: "Cargador USB-C 1m", qty: 1, price: 59.00 },
      { code: "7501777005678", name: "Audífonos alámbricos 3.5mm", qty: 1, price: 79.00 },
    ] },
  { folio: "B-001040", fecha: "2026-06-01T10:05:00", cajero: "M. Ruiz", medio: "Efectivo",
    ref: null, lines: [
      { code: "7503007654321", name: "Foco LED 9W luz cálida", qty: 3, price: 45.00 },
      { code: "7501045401123", name: "Pilas AA alcalinas 2 pzas", qty: 2, price: 38.90 },
    ] },
  { folio: "B-001041", fecha: "2026-06-01T10:32:00", cajero: "L. Cruz", medio: "Tarjeta",
    ref: "MP 7HT2-9981 · MC ****8870", lines: [
      { code: "7501555002211", name: "Juego destornilladores 6pz", qty: 1, price: 89.00 },
      { code: "7501222334455", name: "Extensión eléctrica 3m", qty: 1, price: 65.00 },
      { code: "7501555000990", name: "Cinta métrica 3m", qty: 1, price: 34.00 },
    ] },
  { folio: "B-001042", fecha: "2026-06-01T11:08:00", cajero: "L. Cruz", medio: "Efectivo",
    ref: null, lines: [
      { code: "7506306412345", name: "Vasos desechables 12oz 25pz", qty: 4, price: 28.00 },
      { code: "7501999000123", name: "Vela parafina blanca (pza)", qty: 6, price: 6.50 },
      { code: "7501020304055", name: "Jabón tocador 150g", qty: 3, price: 13.50 },
    ] },
  { folio: "B-001043", fecha: "2026-06-01T11:47:00", cajero: "M. Ruiz", medio: "Tarjeta",
    ref: "MP 1ZP5-3340 · VISA ****1180", lines: [
      { code: "7501008998877", name: "Cinta canela empaque 48mm", qty: 2, price: 26.00 },
      { code: "7501333008812", name: "Bolsa basura jumbo 10pz", qty: 3, price: 27.50 },
    ] },
];

/* helpers */
window.money = function (n) {
  return n.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};
/* Totales de una venta: total con IVA incluido → subtotal + IVA 16% */
window.saleTotals = function (lines) {
  const total = lines.reduce((s, l) => s + l.price * l.qty, 0);
  const subtotal = total / (1 + window.IVA_RATE);
  return { total, subtotal, iva: total - subtotal };
};
window.fmtFecha = function (iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("es-MX", { day: "2-digit", month: "short", year: "numeric" }) +
    " · " + d.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" });
};
window.stockState = function (s) {
  if (s <= 0) return { cls: "tag--out", label: "Agotado" };
  if (s <= 10) return { cls: "tag--low", label: "Bajo" };
  return { cls: "tag--ok", label: "En piso" };
};
````

## `icons.jsx`

````jsx
// Shared geometric line icons (1.6px stroke, currentColor)
const Icon = {
  scan: (p) => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M3 7V4h3M21 7V4h-3M3 17v3h3M21 17v3h-3" />
      <path d="M6 8v8M9 8v8M12 8v8M15 8v8M18 8v8" strokeWidth="1.3" />
    </svg>
  ),
  cart: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M3 4h2l2.2 11h10l2-7H6" /><circle cx="9" cy="20" r="1.4" /><circle cx="17" cy="20" r="1.4" />
    </svg>
  ),
  box: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M3 7l9-4 9 4v10l-9 4-9-4V7z" /><path d="M3 7l9 4 9-4M12 11v10" />
    </svg>
  ),
  cut: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <rect x="3" y="5" width="18" height="14" rx="1.5" /><path d="M3 10h18M8 5v14" />
    </svg>
  ),
  search: (p) => (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...p}>
      <circle cx="11" cy="11" r="7" /><path d="m20 20-3.2-3.2" />
    </svg>
  ),
  trash: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13" />
    </svg>
  ),
  cash: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <rect x="2" y="6" width="20" height="12" rx="1.5" /><circle cx="12" cy="12" r="2.6" /><path d="M5 9v6M19 9v6" strokeWidth="1.2" />
    </svg>
  ),
  card: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <rect x="2" y="5" width="20" height="14" rx="2" /><path d="M2 9h20M5 15h5" />
    </svg>
  ),
  check: (p) => (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
  ),
  checkSm: (p) => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
  ),
  plus: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
      <path d="M12 5v14M5 12h14" />
    </svg>
  ),
  alert: (p) => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...p}>
      <path d="M12 3 2 20h20L12 3z" /><path d="M12 10v4M12 17v.5" />
    </svg>
  ),
  ret: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M9 14 4 9l5-5" /><path d="M4 9h11a5 5 0 0 1 5 5v0a5 5 0 0 1-5 5H8" />
    </svg>
  ),
  report: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M4 20V4" /><path d="M4 20h16" /><path d="M8 20v-6M13 20V8M18 20v-9" />
    </svg>
  ),
  printer: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M6 9V3h12v6" /><path d="M6 18H4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2" />
      <rect x="6" y="14" width="12" height="7" rx="1" /><path d="M9 17h6" strokeWidth="1.2" />
    </svg>
  ),
  cal: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <rect x="3" y="5" width="18" height="16" rx="1.5" /><path d="M3 9h18M8 3v4M16 3v4" />
    </svg>
  ),
  user: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <circle cx="12" cy="8" r="3.4" /><path d="M5 20a7 7 0 0 1 14 0" />
    </svg>
  ),
  export: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M12 15V3m0 0 4 4m-4-4-4 4" /><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
    </svg>
  ),
};
window.Icon = Icon;
````

## `app.jsx`

````jsx
// App — shell, navigation, shared POS session state
const { useState, useCallback } = React;

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [screen, setScreen] = useState("venta");
  const [products, setProducts] = useState(() => window.SEED_PRODUCTS.map(p => ({ ...p })));
  const [cart, setCart] = useState([]);
  const [ticketNo, setTicketNo] = useState(1042);
  const [cobroOpen, setCobroOpen] = useState(false);
  const [toast, setToast] = useState(null);

  // session sales accumulator for corte de caja (seeded with prior turn activity)
  const [sales, setSales] = useState({
    efectivo: { amount: 3184.50, count: 37 },
    tarjeta: { amount: 5421.00, count: 21 },
  });
  const openingFund = 1500;

  const notify = useCallback((msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3200);
  }, []);

  const total = cart.reduce((s, l) => {
    const p = products.find(x => x.code === l.code);
    return p ? s + p.price * l.qty : s;
  }, 0);

  const completeSale = useCallback((res) => {
    setSales(prev => {
      const k = res.method === "Efectivo" ? "efectivo" : "tarjeta";
      return { ...prev, [k]: { amount: prev[k].amount + res.total, count: prev[k].count + 1 } };
    });
    // decrement stock
    setProducts(prev => prev.map(p => {
      const line = cart.find(l => l.code === p.code);
      return line ? { ...p, stock: Math.max(0, p.stock - line.qty) } : p;
    }));
    setCart([]);
    setCobroOpen(false);
    setTicketNo(n => n + 1);
    notify(`Ticket #${ticketNo} cobrado · ${res.method} · $ ${window.money(res.total)}`);
  }, [cart, ticketNo, notify]);

  function addProduct(p) {
    setProducts(prev => {
      if (prev.some(x => x.code === p.code)) return prev.map(x => x.code === p.code ? p : x);
      return [p, ...prev];
    });
  }

  if (!loggedIn) return <LoginScreen onLogin={() => setLoggedIn(true)} />;

  const nav = [
    { id: "venta", label: "Venta", icon: Icon.cart, key: "F1" },
    { id: "devolucion", label: "Devolución", icon: Icon.ret, key: "F2" },
    { id: "reimpresion", label: "Reimpresión", icon: Icon.printer, key: "F3" },
    { id: "catalogo", label: "Catálogo", icon: Icon.box, key: "F4" },
    { id: "reportes", label: "Reportes", icon: Icon.report, key: "F5" },
    { id: "corte", label: "Corte de caja", icon: Icon.cut, key: "F6" },
  ];

  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar__brand">
          <span className="brand-mark" />
          <span className="brand">MASCHINARIO<small>BAZAR</small></span>
        </div>
        <nav className="nav">
          {nav.map(n => (
            <button key={n.id} className={"nav__item" + (screen === n.id ? " is-active" : "")} onClick={() => setScreen(n.id)}>
              {n.icon()} {n.label}
              <span className="nav__key">{n.key}</span>
            </button>
          ))}
        </nav>
        <div className="topbar__right">
          <div className="session">
            <span className="session__store">Bazar Lupita · Centro</span>
            <span className="session__meta">TERMINAL 01 · TURNO MATUTINO</span>
          </div>
          <div className="session__user">
            <span className="avatar">MR</span>
          </div>
          <button className="btn-logout" onClick={() => { setLoggedIn(false); setScreen("venta"); }}>Salir</button>
        </div>
      </header>

      <main className="workspace">
        {screen === "venta" && (
          <VentaScreen
            products={products}
            cart={cart}
            setCart={setCart}
            ticketNo={ticketNo}
            onCobrar={() => setCobroOpen(true)}
          />
        )}
        {screen === "catalogo" && <CatalogoScreen products={products} onAdd={addProduct} />}
        {screen === "devolucion" && <DevolucionScreen notify={notify} />}
        {screen === "reportes" && <ReportesScreen notify={notify} />}
        {screen === "reimpresion" && <ReimpresionScreen notify={notify} />}
        {screen === "corte" && <CorteScreen sales={sales} openingFund={openingFund} />}

        {cobroOpen && (
          <CobroModal
            total={total}
            ticketNo={ticketNo}
            onClose={() => setCobroOpen(false)}
            onComplete={completeSale}
          />
        )}
      </main>

      {toast && (
        <div className="toast">{Icon.checkSm()} {toast}</div>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
````

## `login.jsx`

````jsx
// LoginScreen — full-screen dark brand chrome, Orbitron logo, numeric PIN pad
const { useState, useEffect, useCallback } = React;

function LoginScreen({ onLogin }) {
  const PIN = "2468";
  const [pin, setPin] = useState("");
  const [err, setErr] = useState(false);

  const submit = useCallback((value) => {
    if (value === PIN) {
      setErr(false);
      setTimeout(() => onLogin(), 220);
    } else {
      setErr(true);
      setTimeout(() => { setPin(""); setErr(false); }, 600);
    }
  }, [onLogin]);

  const press = useCallback((d) => {
    setErr(false);
    setPin((p) => {
      if (p.length >= 4) return p;
      const next = p + d;
      if (next.length === 4) setTimeout(() => submit(next), 120);
      return next;
    });
  }, [submit]);

  const del = useCallback(() => { setErr(false); setPin((p) => p.slice(0, -1)); }, []);
  const clear = useCallback(() => { setErr(false); setPin(""); }, []);

  useEffect(() => {
    const h = (e) => {
      if (e.key >= "0" && e.key <= "9") press(e.key);
      else if (e.key === "Backspace") del();
      else if (e.key === "Escape") clear();
      else if (e.key === "Enter" && pin.length === 4) submit(pin);
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [press, del, clear, submit, pin]);

  const keys = ["1","2","3","4","5","6","7","8","9"];

  return (
    <div className="login">
      <div className="login__grid" />
      <div className="login__brandbar">
        <span className="brand-mark" />
        <span className="brand">MASCHINARIO<small>BAZAR</small></span>
      </div>
      <div className="login__store">
        BAZAR LUPITA · SUC. CENTRO<br />
        TERMINAL 01 · v3.2.0
      </div>

      <div className="login-card">
        <div className="login-card__top">
          <div className="login-logo">
            <span className="brand-mark" />
            <span className="brand">MASCHINARIO<small>BAZAR</small></span>
          </div>
          <div className="eyebrow">Acceso de cajero · Ingresa tu PIN</div>
        </div>

        <div className="pin-display">
          {[0,1,2,3].map((i) => (
            <span key={i} className={"pin-dot" + (i < pin.length ? " filled" : "") + (err ? " err" : "")} />
          ))}
        </div>
        <div className={"pin-msg " + (err ? "err" : "hint")}>
          {err ? "PIN incorrecto, intenta de nuevo" : "Demo: 2 4 6 8"}
        </div>

        <div className="numpad">
          {keys.map((k) => <button key={k} onClick={() => press(k)}>{k}</button>)}
          <button className="action" onClick={clear}>C</button>
          <button onClick={() => press("0")}>0</button>
          <button className="action enter" onClick={() => pin.length === 4 ? submit(pin) : del()}>
            {pin.length === 4 ? "ENTRAR" : "◀"}
          </button>
        </div>
      </div>

      <div className="login__foot">MASCHINARIO · BAZAR · SISTEMA DE PUNTO DE VENTA</div>
    </div>
  );
}

window.LoginScreen = LoginScreen;
````

## `venta.jsx`

````jsx
// VentaScreen — left: scan + lines table; right: fixed totals panel + COBRAR
const { useState, useRef, useEffect, useMemo } = React;

function VentaScreen({ products, cart, setCart, ticketNo, onCobrar }) {
  const [query, setQuery] = useState("");
  const [activeIdx, setActiveIdx] = useState(0);
  const [flashId, setFlashId] = useState(null);
  const inputRef = useRef(null);

  const byCode = useMemo(() => Object.fromEntries(products.map(p => [p.code, p])), [products]);

  const suggestions = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return products.filter(p =>
      p.name.toLowerCase().includes(q) || p.code.includes(q) || p.cat.toLowerCase().includes(q)
    ).slice(0, 7);
  }, [query, products]);

  useEffect(() => { setActiveIdx(0); }, [query]);
  useEffect(() => { inputRef.current && inputRef.current.focus(); }, []);

  function addProduct(p) {
    if (!p) return;
    setCart(prev => {
      const found = prev.find(l => l.code === p.code);
      if (found) return prev.map(l => l.code === p.code ? { ...l, qty: l.qty + 1 } : l);
      return [...prev, { code: p.code, qty: 1 }];
    });
    setFlashId(p.code);
    setTimeout(() => setFlashId(null), 500);
    setQuery("");
    inputRef.current && inputRef.current.focus();
  }

  function onKeyDown(e) {
    if (e.key === "ArrowDown") { e.preventDefault(); setActiveIdx(i => Math.min(i + 1, suggestions.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActiveIdx(i => Math.max(i - 1, 0)); }
    else if (e.key === "Enter") {
      e.preventDefault();
      if (suggestions.length) addProduct(suggestions[activeIdx]);
      else if (byCode[query.trim()]) addProduct(byCode[query.trim()]);
    } else if (e.key === "Escape") setQuery("");
  }

  function setQty(code, qty) {
    if (qty <= 0) { setCart(prev => prev.filter(l => l.code !== code)); return; }
    setCart(prev => prev.map(l => l.code === code ? { ...l, qty } : l));
  }
  function removeLine(code) { setCart(prev => prev.filter(l => l.code !== code)); }

  const lines = cart.map(l => ({ ...l, p: byCode[l.code] })).filter(l => l.p);
  const itemCount = lines.reduce((s, l) => s + l.qty, 0);
  const total = lines.reduce((s, l) => s + l.p.price * l.qty, 0);
  const subtotal = total / (1 + window.IVA_RATE);
  const iva = total - subtotal;

  return (
    <div className="venta">
      {/* LEFT */}
      <div className="venta__main">
        <div className="scanbar">
          <div className="scanbar__icon">{Icon.scan()}</div>
          <div className="scan-input-wrap">
            <input
              ref={inputRef}
              className="scan-input"
              placeholder="Escanea un código de barras o escribe para buscar…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={onKeyDown}
            />
            {suggestions.length > 0 && (
              <div className="suggest">
                {suggestions.map((p, i) => (
                  <div
                    key={p.code}
                    className={"suggest__row" + (i === activeIdx ? " is-active" : "")}
                    onMouseEnter={() => setActiveIdx(i)}
                    onClick={() => addProduct(p)}
                  >
                    <span className="suggest__code">{p.code}</span>
                    <span className="suggest__name">{p.name}</span>
                    <span className="suggest__price">$ {window.money(p.price)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="scan-hint"><kbd>Enter</kbd> agrega</div>
        </div>

        <div className="lines">
          <div className="lines__head">
            <span>#</span>
            <span>Descripción</span>
            <span className="r">Cantidad</span>
            <span className="r">Precio</span>
            <span className="r">Importe</span>
            <span />
          </div>

          {lines.length === 0 ? (
            <div className="lines__empty">
              <div className="ring">{Icon.cart({ width: 30, height: 30 })}</div>
              <div>
                <div style={{ fontWeight: 600, color: "var(--ink-2)" }}>Ticket vacío</div>
                <div className="mono" style={{ fontSize: 12, marginTop: 4 }}>Escanea un producto para comenzar</div>
              </div>
            </div>
          ) : (
            <div className="lines__body scroll">
              {lines.map((l, i) => (
                <div key={l.code} className={"line" + (flashId === l.code ? " is-flash" : "")}>
                  <span className="line__idx">{String(i + 1).padStart(2, "0")}</span>
                  <div className="line__name">
                    <b>{l.p.name}</b>
                    <span>{l.p.code}</span>
                  </div>
                  <div className="qty">
                    <button onClick={() => setQty(l.code, l.qty - 1)}>−</button>
                    <input
                      value={l.qty}
                      onChange={e => { const v = parseInt(e.target.value.replace(/\D/g, "")) || 0; setQty(l.code, v); }}
                    />
                    <button onClick={() => setQty(l.code, l.qty + 1)}>+</button>
                  </div>
                  <span className="line__price">{window.money(l.p.price)}</span>
                  <span className="line__amount">{window.money(l.p.price * l.qty)}</span>
                  <button className="line__del" onClick={() => removeLine(l.code)} title="Quitar">{Icon.trash()}</button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT PANEL */}
      <aside className="cobro-panel">
        <div className="cobro-panel__head">
          <span className="eyebrow">Venta en curso</span>
          <span className="ticket">TICKET #{ticketNo}</span>
        </div>
        <div className="cobro-panel__body">
          <div className="sumrow sumrow--items">
            <span className="sumrow__label">Artículos <small>{lines.length} líneas</small></span>
            <span className="sumrow__val">{itemCount}</span>
          </div>
          <div className="sum-divider" />
          <div className="sumrow">
            <span className="sumrow__label">Subtotal</span>
            <span className="sumrow__val">$ {window.money(subtotal)}</span>
          </div>
          <div className="sumrow">
            <span className="sumrow__label">IVA <small>16%</small></span>
            <span className="sumrow__val">$ {window.money(iva)}</span>
          </div>

          <div className="total-block">
            <div className="total-card">
              <div className="total-card__label">Total a cobrar</div>
              <div className="total-card__amount"><span className="cur">$</span>{window.money(total)}</div>
            </div>
          </div>
        </div>
        <div className="panel-actions">
          <button className="btn-cobrar" disabled={lines.length === 0} onClick={onCobrar}>
            <span>COBRAR</span>
            <span className="k">F12</span>
          </button>
          <div className="sec-actions">
            <button className="btn btn--ghost" disabled={lines.length === 0}>Descuento</button>
            <button className="btn btn--danger" disabled={lines.length === 0} onClick={() => setCart([])}>
              Cancelar venta
            </button>
          </div>
        </div>
      </aside>
    </div>
  );
}

window.VentaScreen = VentaScreen;
````

## `cobro.jsx`

````jsx
// CobroModal — segment Efectivo | Tarjeta. Cash change + live terminal status.
const { useState, useEffect, useRef } = React;

function CobroModal({ total, ticketNo, onClose, onComplete }) {
  const [tab, setTab] = useState("efectivo");
  const [received, setReceived] = useState("");
  const [phase, setPhase] = useState("idle"); // idle | waiting | approved | done
  const inputRef = useRef(null);

  useEffect(() => { if (tab === "efectivo" && inputRef.current) inputRef.current.focus(); }, [tab]);

  const recvNum = parseFloat(received) || 0;
  const change = recvNum - total;
  const enough = recvNum >= total && recvNum > 0;

  // round-up cash suggestions
  const quick = [];
  const denoms = [50, 100, 200, 500];
  denoms.forEach(d => { const v = Math.ceil(total / d) * d; if (v >= total && !quick.includes(v)) quick.push(v); });
  const suggestions = Array.from(new Set([Math.ceil(total), ...quick])).filter(v => v >= total).slice(0, 3);

  function payCash() {
    if (!enough) return;
    setPhase("done");
    setTimeout(() => onComplete({ method: "Efectivo", received: recvNum, change, total }), 1400);
  }

  function startCard() {
    setPhase("waiting");
    setTimeout(() => {
      setPhase("approved");
      setTimeout(() => {
        setPhase("done");
        setTimeout(() => onComplete({ method: "Tarjeta", received: total, change: 0, total }), 1100);
      }, 900);
    }, 2400);
  }

  useEffect(() => {
    const h = (e) => {
      if (e.key === "Escape" && phase === "idle") onClose();
      if (e.key === "Enter" && tab === "efectivo" && enough && phase === "idle") payCash();
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  });

  const isDone = phase === "done";

  return (
    <div className="overlay" onMouseDown={(e) => { if (e.target === e.currentTarget && phase === "idle") onClose(); }}>
      <div className="modal">
        <div className="modal__head">
          <h3>Cobro · Ticket #{ticketNo}</h3>
          <span className="due">$ {window.money(total)}</span>
          {phase === "idle" && <button className="modal__close" onClick={onClose}>×</button>}
        </div>

        {isDone ? (
          <div className="modal__body">
            <div className="paydone">
              <div className="tick">{Icon.check()}</div>
              <h3>Pago aprobado</h3>
              <p>{tab === "efectivo" ? `Cambio $ ${window.money(change)}` : "Transacción con tarjeta aprobada"}</p>
            </div>
          </div>
        ) : (
          <React.Fragment>
            <div className="seg">
              <button className={tab === "efectivo" ? "is-active" : ""} disabled={phase !== "idle"} onClick={() => setTab("efectivo")}>
                {Icon.cash()} Efectivo
              </button>
              <button className={tab === "tarjeta" ? "is-active" : ""} disabled={phase !== "idle"} onClick={() => setTab("tarjeta")}>
                {Icon.card()} Tarjeta
              </button>
            </div>

            <div className="modal__body">
              {tab === "efectivo" ? (
                <div className="efectivo">
                  <div>
                    <div className="field" style={{ marginBottom: 4 }}>
                      <label>Monto recibido</label>
                      <input
                        ref={inputRef}
                        className="cash-recv-input"
                        inputMode="decimal"
                        placeholder="0.00"
                        value={received}
                        onChange={e => setReceived(e.target.value.replace(/[^\d.]/g, ""))}
                      />
                    </div>
                    <div className="quick-cash">
                      <button className="exact" onClick={() => setReceived(total.toFixed(2))}>Importe exacto</button>
                      {suggestions.map(v => (
                        <button key={v} onClick={() => setReceived(v.toFixed(2))}>$ {window.money(v)}</button>
                      ))}
                    </div>
                  </div>
                  <div className={"change-card " + (recvNum === 0 ? "" : enough ? "is-ok" : "is-short")}>
                    <div className="change-card__label">{!enough && recvNum > 0 ? "Faltan" : "Cambio"}</div>
                    <div className="change-card__amt">
                      $ {window.money(recvNum === 0 ? 0 : Math.abs(change))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="tarjeta">
                  <div className={"terminal " + (phase === "waiting" ? "is-waiting" : "")}>
                    <span className="pulse-ring" />
                    <div className="terminal__screen">
                      {phase === "idle" && "LISTO"}
                      {phase === "waiting" && "$ " + window.money(total)}
                      {phase === "approved" && "APROBADO"}
                    </div>
                    <div className="terminal__slot" />
                  </div>
                  {phase === "idle" && <div className="term-status" style={{ color: "var(--ink-2)" }}>Inserta o acerca la tarjeta</div>}
                  {phase === "waiting" && <div className="term-status waiting"><span className="spinner" /> Esperando terminal…</div>}
                  {phase === "approved" && <div className="term-status approved">{Icon.checkSm()} Aprobado</div>}
                  <div className="term-sub">
                    {phase === "idle" && "Mercado Pago Point Smart 2 · contactless habilitado"}
                    {phase === "waiting" && "No retires la tarjeta"}
                    {phase === "approved" && "AUTH 014592 · VISA ****4021"}
                  </div>
                </div>
              )}
            </div>

            <div className="modal__foot">
              {tab === "efectivo" ? (
                <React.Fragment>
                  <button className="btn" onClick={onClose}>Cancelar</button>
                  <button className="btn btn--primary" disabled={!enough} onClick={payCash}>
                    Confirmar cobro
                  </button>
                </React.Fragment>
              ) : (
                <React.Fragment>
                  <button className="btn" disabled={phase !== "idle"} onClick={onClose}>Cancelar</button>
                  <button className="btn btn--primary" disabled={phase !== "idle"} onClick={startCard}>
                    Enviar a terminal
                  </button>
                </React.Fragment>
              )}
            </div>
          </React.Fragment>
        )}
      </div>
    </div>
  );
}

window.CobroModal = CobroModal;
````

## `catalogo.jsx`

````jsx
// CatalogoScreen — searchable product table + side "alta" form with scannable barcode field
const { useState, useMemo, useRef, useEffect } = React;

function CatalogoScreen({ products, onAdd }) {
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ code: "", name: "", price: "", stock: "", cat: "Papelería" });
  const [scanning, setScanning] = useState(false);
  const [justAdded, setJustAdded] = useState(false);
  const codeRef = useRef(null);

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return products;
    return products.filter(p =>
      p.name.toLowerCase().includes(s) || p.code.includes(s) || p.cat.toLowerCase().includes(s)
    );
  }, [q, products]);

  // simulate a barcode gun populating the field
  function simulateScan() {
    setScanning(true);
    const fake = "75" + Math.floor(10000000000 + Math.random() * 89999999999);
    let i = 0;
    const iv = setInterval(() => {
      i++;
      setForm(f => ({ ...f, code: fake.slice(0, i) }));
      if (i >= fake.length) { clearInterval(iv); setScanning(false); }
    }, 28);
  }

  const valid = form.code.trim() && form.name.trim() && parseFloat(form.price) > 0;

  function submit() {
    if (!valid) return;
    onAdd({
      code: form.code.trim(),
      name: form.name.trim(),
      price: parseFloat(form.price),
      stock: parseInt(form.stock) || 0,
      cat: form.cat,
    });
    setForm({ code: "", name: "", price: "", stock: "", cat: form.cat });
    setJustAdded(true);
    setTimeout(() => setJustAdded(false), 1800);
  }

  const cats = ["Papelería", "Eléctrico", "Ferretería", "Desechables", "Hogar", "Limpieza"];
  const totalStock = products.reduce((s, p) => s + p.stock, 0);

  return (
    <div className="catalogo">
      <div className="cat__main">
        <div className="cat__bar">
          <div className="search">
            {Icon.search()}
            <input placeholder="Buscar por nombre, código o categoría…" value={q} onChange={e => setQ(e.target.value)} />
          </div>
          <span className="cat__count">{filtered.length} de {products.length} productos · {totalStock} pzas</span>
        </div>

        <div className="cat-table-wrap scroll">
          <table className="cat-table">
            <thead>
              <tr>
                <th style={{ width: 160 }}>Código de barras</th>
                <th>Nombre</th>
                <th style={{ width: 120 }}>Categoría</th>
                <th className="r" style={{ width: 110 }}>Precio</th>
                <th className="r" style={{ width: 100 }}>Existencia</th>
                <th style={{ width: 110 }}>Estado</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(p => {
                const st = window.stockState(p.stock);
                return (
                  <tr
                    key={p.code}
                    className={selected === p.code ? "is-selected" : ""}
                    onClick={() => setSelected(p.code)}
                  >
                    <td className="c-code">{p.code}</td>
                    <td className="c-name">{p.name}</td>
                    <td className="c-cat">{p.cat}</td>
                    <td className="r c-price">$ {window.money(p.price)}</td>
                    <td className="r c-stock">{p.stock}</td>
                    <td><span className={"tag " + st.cls}>{st.label}</span></td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr><td colSpan="6" style={{ textAlign: "center", padding: 40, color: "var(--faint)" }}>
                  Sin resultados para “{q}”
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* SIDE FORM */}
      <aside className="cat__form">
        <div className="cat__form-head">
          <h3>Alta de producto</h3>
          <p>Escanea el código para iniciar</p>
        </div>
        <div className="cat__form-body scroll">
          <div className="field">
            <label>Código de barras</label>
            <div className="scan-field-wrap">
              <input
                ref={codeRef}
                className="input input--mono"
                placeholder="Escanea o teclea…"
                value={form.code}
                onChange={e => setForm({ ...form, code: e.target.value.replace(/\D/g, "") })}
              />
              <button
                className={"scan-badge" + (scanning ? " live" : "")}
                onClick={simulateScan}
                style={{ border: "none", cursor: "pointer" }}
                title="Simular lectura de pistola"
              >
                {Icon.scan({ width: 12, height: 12 })} {scanning ? "Leyendo" : "Escanear"}
              </button>
            </div>
          </div>

          <div className="field">
            <label>Nombre del producto</label>
            <input className="input" placeholder="Ej. Cuaderno profesional 100h" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
          </div>

          <div className="two-col">
            <div className="field">
              <label>Precio (con IVA)</label>
              <input className="input input--mono" inputMode="decimal" placeholder="0.00" value={form.price} onChange={e => setForm({ ...form, price: e.target.value.replace(/[^\d.]/g, "") })} />
            </div>
            <div className="field">
              <label>Existencia</label>
              <input className="input input--mono" inputMode="numeric" placeholder="0" value={form.stock} onChange={e => setForm({ ...form, stock: e.target.value.replace(/\D/g, "") })} />
            </div>
          </div>

          <div className="field">
            <label>Categoría</label>
            <select className="input" value={form.cat} onChange={e => setForm({ ...form, cat: e.target.value })} style={{ appearance: "auto" }}>
              {cats.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>

          {justAdded && (
            <div className="tag tag--ok" style={{ alignSelf: "flex-start", display: "inline-flex", alignItems: "center", gap: 6 }}>
              {Icon.checkSm()} Producto agregado al catálogo
            </div>
          )}
        </div>
        <div className="cat__form-foot">
          <button className="btn btn--ghost" onClick={() => setForm({ code: "", name: "", price: "", stock: "", cat: form.cat })}>Limpiar</button>
          <button className="btn btn--primary" disabled={!valid} onClick={submit}>{Icon.plus()} Guardar</button>
        </div>
      </aside>
    </div>
  );
}

window.CatalogoScreen = CatalogoScreen;
````

## `corte.jsx`

````jsx
// CorteScreen — shift close in dark brand chrome. Sales by method, fondo, expected vs counted.
const { useState, useMemo } = React;

function CorteScreen({ sales, openingFund }) {
  // sales: { efectivo: {amount, count}, tarjeta: {amount, count} }
  const [contado, setContado] = useState("");
  const [fondo] = useState(openingFund);

  const efectivoVentas = sales.efectivo.amount;
  const tarjetaVentas = sales.tarjeta.amount;
  const totalVentas = efectivoVentas + tarjetaVentas;
  const totalTickets = sales.efectivo.count + sales.tarjeta.count;
  const esperado = fondo + efectivoVentas;
  const contadoNum = parseFloat(contado) || 0;
  const diff = contado === "" ? null : contadoNum - esperado;

  const diffClass = diff === null ? "" : Math.abs(diff) < 0.005 ? "zero" : diff < 0 ? "neg" : "pos";
  const diffLabel = diff === null ? "Captura el efectivo contado" :
    Math.abs(diff) < 0.005 ? "Caja cuadrada" : diff < 0 ? "Faltante de caja" : "Sobrante de caja";

  const now = new Date();
  const fdate = now.toLocaleDateString("es-MX", { day: "2-digit", month: "short", year: "numeric" });
  const ftime = now.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="corte scroll scroll--dark">
      <div className="corte__inner">
        <div className="corte__top">
          <div>
            <div className="eyebrow">Cierre de turno</div>
            <h2>Corte de caja</h2>
          </div>
          <div className="meta">
            TERMINAL 01 · CAJERO M. RUIZ<br />
            {fdate} · {ftime}<br />
            TURNO MATUTINO 08:00–15:00
          </div>
        </div>

        <div className="summary-strip">
          <div className="cell">
            <div className="eyebrow">Ventas del turno</div>
            <div className="v accent">$ {window.money(totalVentas)}</div>
          </div>
          <div className="cell">
            <div className="eyebrow">Tickets</div>
            <div className="v">{totalTickets}</div>
          </div>
          <div className="cell">
            <div className="eyebrow">Ticket promedio</div>
            <div className="v">$ {window.money(totalTickets ? totalVentas / totalTickets : 0)}</div>
          </div>
          <div className="cell">
            <div className="eyebrow">Fondo inicial</div>
            <div className="v">$ {window.money(fondo)}</div>
          </div>
        </div>

        <div className="corte__grid">
          {/* LEFT: ventas por medio de pago */}
          <div className="dpanel">
            <div className="dpanel__head">
              <h4>Ventas por medio de pago</h4>
              <span className="eyebrow" style={{ color: "#6E8488" }}>{totalTickets} operaciones</span>
            </div>
            <div className="dpanel__body">
              <div className="drow">
                <div className="drow__l">
                  <span className="drow__icon">{Icon.cash()}</span>
                  <div>
                    <div>Efectivo</div>
                    <div className="drow__sub">{sales.efectivo.count} tickets</div>
                  </div>
                </div>
                <span className="drow__v">$ {window.money(efectivoVentas)}</span>
              </div>
              <div className="drow">
                <div className="drow__l">
                  <span className="drow__icon">{Icon.card()}</span>
                  <div>
                    <div>Tarjeta</div>
                    <div className="drow__sub">{sales.tarjeta.count} tickets · débito/crédito</div>
                  </div>
                </div>
                <span className="drow__v">$ {window.money(tarjetaVentas)}</span>
              </div>
              <div className="drow" style={{ borderTop: "1px solid var(--tinta-line)" }}>
                <div className="drow__l">
                  <span className="drow__icon" style={{ background: "transparent", border: "none", color: "var(--menta)" }}>Σ</span>
                  <div><div style={{ fontWeight: 600 }}>Total vendido</div></div>
                </div>
                <span className="drow__v" style={{ color: "var(--menta)" }}>$ {window.money(totalVentas)}</span>
              </div>
            </div>
          </div>

          {/* RIGHT: arqueo de efectivo */}
          <div className="expected-card">
            <div className="eyebrow" style={{ color: "var(--menta)", marginBottom: 10 }}>Arqueo de efectivo</div>
            <div className="bigrow muted">
              <span className="bigrow__label">Fondo inicial</span>
              <span className="bigrow__val">$ {window.money(fondo)}</span>
            </div>
            <div className="bigrow muted">
              <span className="bigrow__label">+ Ventas en efectivo</span>
              <span className="bigrow__val">$ {window.money(efectivoVentas)}</span>
            </div>
            <div style={{ height: 1, background: "var(--tinta-line)", margin: "6px 0" }} />
            <div className="bigrow">
              <span className="bigrow__label" style={{ color: "#fff" }}>Efectivo esperado</span>
              <span className="bigrow__val">$ {window.money(esperado)}</span>
            </div>

            <div className="bigrow" style={{ alignItems: "center", marginTop: 6 }}>
              <span className="bigrow__label" style={{ color: "#fff" }}>Efectivo contado</span>
              <input
                className="corte-input"
                inputMode="decimal"
                placeholder="0.00"
                value={contado}
                onChange={e => setContado(e.target.value.replace(/[^\d.]/g, ""))}
              />
            </div>

            <div className={"diff-card " + diffClass}>
              <div className="diff-card__label">
                {diffClass === "zero" ? Icon.checkSm() : Icon.alert()} {diffLabel}
              </div>
              <div className="diff-card__amt">
                {diff === null ? "—" : (diff > 0 ? "+" : diff < 0 ? "−" : "") + "$ " + window.money(Math.abs(diff))}
              </div>
            </div>
          </div>
        </div>

        <div className="corte__actions">
          <button className="btn-dark">Imprimir reporte X</button>
          <button className="btn-cierre" disabled={diff === null}>Cerrar turno y caja</button>
        </div>
      </div>
    </div>
  );
}

window.CorteScreen = CorteScreen;
````

## `devolucion.jsx`

````jsx
// DevolucionScreen — busca folio, devuelve total/parcial (tope = vendido),
// reembolso según medio original, reintegra stock. Layout espejo de Venta.
const { useState, useRef, useEffect } = React;

function DevolucionScreen({ notify }) {
  const [folio, setFolio] = useState("");
  const [sale, setSale] = useState(null);
  const [qtys, setQtys] = useState({});   // code -> cantidad a devolver
  const [notFound, setNotFound] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => { inputRef.current && inputRef.current.focus(); }, []);

  function lookup(value) {
    const f = (value || folio).trim().toUpperCase();
    const found = window.SEED_SALES.find(s => s.folio.toUpperCase() === f);
    if (found) {
      setSale(found);
      setQtys(Object.fromEntries(found.lines.map(l => [l.code, 0])));
      setNotFound(false);
    } else {
      setSale(null);
      setNotFound(true);
    }
  }

  function onKeyDown(e) {
    if (e.key === "Enter") { e.preventDefault(); lookup(); }
    else if (e.key === "Escape") { setFolio(""); setSale(null); setNotFound(false); }
  }

  function setQty(code, max, v) {
    const n = Math.max(0, Math.min(max, v)); // tope: no excede lo vendido
    setQtys(prev => ({ ...prev, [code]: n }));
  }

  function reset() {
    setFolio(""); setSale(null); setQtys({}); setNotFound(false);
    inputRef.current && inputRef.current.focus();
  }

  const selLines = sale ? sale.lines.map(l => ({ ...l, ret: qtys[l.code] || 0 })) : [];
  const refundLines = selLines.filter(l => l.ret > 0);
  const refundTotal = refundLines.reduce((s, l) => s + l.price * l.ret, 0);
  const { subtotal, iva } = window.saleTotals(refundLines.length ? refundLines.map(l => ({ price: l.price, qty: l.ret })) : []);
  const canRefund = refundTotal > 0;
  const esTarjeta = sale && sale.medio === "Tarjeta";

  function confirmar() {
    if (!canRefund) return;
    const piezas = refundLines.reduce((s, l) => s + l.ret, 0);
    notify(`Devolución ${sale.folio} · ${piezas} pza(s) · ${esTarjeta ? "reembolso a tarjeta" : "reintegro efectivo"} · $ ${window.money(refundTotal)}`);
    reset();
  }

  return (
    <div className="venta">
      {/* LEFT */}
      <div className="venta__main">
        <div className="scanbar">
          <div className="scanbar__icon">{Icon.ret()}</div>
          <div className="scan-input-wrap">
            <input
              ref={inputRef}
              className="scan-input"
              placeholder="Escanea el QR del ticket o teclea el folio (ej. B-001039)…"
              value={folio}
              onChange={e => { setFolio(e.target.value); setNotFound(false); }}
              onKeyDown={onKeyDown}
            />
          </div>
          <div className="scan-hint"><kbd>Enter</kbd> busca</div>
        </div>

        <div className="lines">
          {!sale ? (
            <div className="lines__empty">
              <div className="ring">{Icon.ret({ width: 28, height: 28 })}</div>
              <div>
                <div style={{ fontWeight: 600, color: "var(--ink-2)" }}>
                  {notFound ? "Folio no encontrado" : "Busca una venta para devolver"}
                </div>
                <div className="mono" style={{ fontSize: 12, marginTop: 4 }}>
                  {notFound ? "Verifica el folio impreso en el ticket" : "Escanea el ticket o teclea el folio"}
                </div>
                <div className="folio-chips">
                  {window.SEED_SALES.slice(0, 4).map(s => (
                    <button key={s.folio} className="folio-chip" onClick={() => { setFolio(s.folio); lookup(s.folio); }}>
                      {s.folio}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <React.Fragment>
              <div className="found-bar">
                <div>
                  <span className="found-bar__folio mono">{sale.folio}</span>
                  <span className="found-bar__meta">{window.fmtFecha(sale.fecha)} · {sale.cajero}</span>
                </div>
                <span className={"tag " + (esTarjeta ? "tag--low" : "tag--ok")}>
                  Pagó con {sale.medio}
                </span>
              </div>

              <div className="devo-head">
                <span>Descripción</span>
                <span className="r">Vendidas</span>
                <span className="c">Devolver</span>
                <span className="r">Importe</span>
              </div>
              <div className="lines__body scroll">
                {selLines.map(l => (
                  <div key={l.code} className="devo-line">
                    <div className="line__name">
                      <b>{l.name}</b>
                      <span>{l.code} · $ {window.money(l.price)} c/u</span>
                    </div>
                    <span className="num devo-sold">{l.qty}</span>
                    <div className="qty">
                      <button onClick={() => setQty(l.code, l.qty, l.ret - 1)}>−</button>
                      <input value={l.ret}
                        onChange={e => setQty(l.code, l.qty, parseInt(e.target.value.replace(/\D/g, "")) || 0)} />
                      <button onClick={() => setQty(l.code, l.qty, l.ret + 1)}>+</button>
                    </div>
                    <span className="num devo-amt">{l.ret > 0 ? "$ " + window.money(l.price * l.ret) : "—"}</span>
                  </div>
                ))}
              </div>
            </React.Fragment>
          )}
        </div>
      </div>

      {/* RIGHT PANEL */}
      <aside className="cobro-panel">
        <div className="cobro-panel__head">
          <span className="eyebrow">Nota de crédito</span>
          <span className="ticket">{sale ? sale.folio : "—"}</span>
        </div>
        <div className="cobro-panel__body">
          <div className="sumrow sumrow--items">
            <span className="sumrow__label">Piezas a devolver</span>
            <span className="sumrow__val">{refundLines.reduce((s, l) => s + l.ret, 0)}</span>
          </div>
          <div className="sum-divider" />
          <div className="sumrow">
            <span className="sumrow__label">Subtotal</span>
            <span className="sumrow__val">$ {window.money(subtotal)}</span>
          </div>
          <div className="sumrow">
            <span className="sumrow__label">IVA <small>16%</small></span>
            <span className="sumrow__val">$ {window.money(iva)}</span>
          </div>

          <div className="refund-note">
            {esTarjeta
              ? <span>{Icon.card({ width: 14, height: 14 })} Reembolso a la <b>tarjeta original</b> vía Point Smart 2.</span>
              : <span>{Icon.cash({ width: 14, height: 14 })} Reintegro en <b>efectivo</b> desde caja.</span>}
            <span className="refund-note__stock">Reintegra el stock de las piezas devueltas.</span>
          </div>

          <div className="total-block">
            <div className="total-card total-card--refund">
              <div className="total-card__label">Total a reembolsar</div>
              <div className="total-card__amount"><span className="cur">$</span>{window.money(refundTotal)}</div>
            </div>
          </div>
        </div>
        <div className="panel-actions">
          <button className="btn-cobrar btn-cobrar--refund" disabled={!canRefund} onClick={confirmar}>
            <span>PROCESAR DEVOLUCIÓN</span>
            {Icon.ret({ width: 16, height: 16 })}
          </button>
          <div className="sec-actions">
            <button className="btn btn--ghost" disabled={!sale} onClick={reset}>Cancelar</button>
          </div>
        </div>
      </aside>
    </div>
  );
}

window.DevolucionScreen = DevolucionScreen;
````

## `reportes.jsx`

````jsx
// ReportesScreen — totales por periodo/medio/cajero + export fiscal (RFC genérico, sin timbrar).
const { useState, useMemo } = React;

function ReportesScreen({ notify }) {
  const [periodo, setPeriodo] = useState("hoy");
  const [cajero, setCajero] = useState("todos");

  const sales = window.SEED_SALES;
  const cajeros = useMemo(() => ["todos", ...Array.from(new Set(sales.map(s => s.cajero)))], [sales]);

  // (mockup: el periodo es visual; el filtro real es por cajero)
  const filtered = useMemo(
    () => sales.filter(s => cajero === "todos" || s.cajero === cajero),
    [sales, cajero]
  );

  const rows = filtered.map(s => {
    const t = window.saleTotals(s.lines);
    return { ...s, ...t };
  });

  const totalVentas = rows.reduce((s, r) => s + r.total, 0);
  const totalIva = rows.reduce((s, r) => s + r.iva, 0);
  const tickets = rows.length;
  const prom = tickets ? totalVentas / tickets : 0;

  const porMedio = ["Efectivo", "Tarjeta"].map(m => {
    const g = rows.filter(r => r.medio === m);
    return { medio: m, monto: g.reduce((s, r) => s + r.total, 0), n: g.length };
  });
  const porCajero = Array.from(new Set(rows.map(r => r.cajero))).map(c => {
    const g = rows.filter(r => r.cajero === c);
    return { cajero: c, monto: g.reduce((s, r) => s + r.total, 0), n: g.length };
  });

  const periodos = [
    { id: "hoy", label: "Hoy" },
    { id: "7d", label: "7 días" },
    { id: "mes", label: "Mes" },
  ];

  function exportar() {
    notify(`Export fiscal · ${tickets} ventas · RFC genérico XAXX010101000 · marcadas exportada_fiscal (la app no timbra)`);
  }

  const pLabel = periodos.find(p => p.id === periodo).label;

  return (
    <div className="reportes scroll">
      <div className="rep__inner">
        <div className="rep-bar">
          <div className="rep-bar__filters">
            <div className="seg-pills">
              {periodos.map(p => (
                <button key={p.id} className={periodo === p.id ? "is-active" : ""} onClick={() => setPeriodo(p.id)}>
                  {Icon.cal({ width: 14, height: 14 })} {p.label}
                </button>
              ))}
            </div>
            <div className="rep-select">
              {Icon.user({ width: 14, height: 14 })}
              <select value={cajero} onChange={e => setCajero(e.target.value)}>
                {cajeros.map(c => <option key={c} value={c}>{c === "todos" ? "Todos los cajeros" : c}</option>)}
              </select>
            </div>
          </div>
          <button className="btn btn--primary" onClick={exportar}>{Icon.export()} Exportar fiscal</button>
        </div>

        <div className="kpi-strip">
          <div className="kpi"><div className="eyebrow">Ventas · {pLabel}</div><div className="kpi__v accent">$ {window.money(totalVentas)}</div></div>
          <div className="kpi"><div className="eyebrow">Tickets</div><div className="kpi__v">{tickets}</div></div>
          <div className="kpi"><div className="eyebrow">Ticket promedio</div><div className="kpi__v">$ {window.money(prom)}</div></div>
          <div className="kpi"><div className="eyebrow">IVA (16%)</div><div className="kpi__v">$ {window.money(totalIva)}</div></div>
        </div>

        <div className="rep-grid">
          <div className="rep-panel">
            <div className="rep-panel__head"><h4>Por medio de pago</h4></div>
            <div className="rep-panel__body">
              {porMedio.map(m => {
                const pct = totalVentas ? (m.monto / totalVentas) * 100 : 0;
                return (
                  <div key={m.medio} className="bar-row">
                    <div className="bar-row__top">
                      <span>{m.medio === "Efectivo" ? Icon.cash({ width: 15, height: 15 }) : Icon.card({ width: 15, height: 15 })} {m.medio} <small className="mono">· {m.n}</small></span>
                      <span className="num">$ {window.money(m.monto)}</span>
                    </div>
                    <div className="bar"><span className={"bar__fill " + (m.medio === "Efectivo" ? "fill-teal" : "fill-petro")} style={{ width: pct + "%" }} /></div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="rep-panel">
            <div className="rep-panel__head"><h4>Por cajero</h4></div>
            <div className="rep-panel__body">
              {porCajero.map(c => {
                const pct = totalVentas ? (c.monto / totalVentas) * 100 : 0;
                return (
                  <div key={c.cajero} className="bar-row">
                    <div className="bar-row__top">
                      <span>{Icon.user({ width: 15, height: 15 })} {c.cajero} <small className="mono">· {c.n}</small></span>
                      <span className="num">$ {window.money(c.monto)}</span>
                    </div>
                    <div className="bar"><span className="bar__fill fill-teal" style={{ width: pct + "%" }} /></div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="rep-panel">
          <div className="rep-panel__head">
            <h4>Detalle de ventas</h4>
            <span className="eyebrow">{tickets} folios · destino export RFC XAXX010101000</span>
          </div>
          <div className="rep-table-wrap">
            <table className="cat-table rep-table">
              <thead>
                <tr>
                  <th style={{ width: 120 }}>Folio</th>
                  <th>Fecha</th>
                  <th style={{ width: 110 }}>Cajero</th>
                  <th className="r" style={{ width: 110 }}>Subtotal</th>
                  <th className="r" style={{ width: 100 }}>IVA</th>
                  <th className="r" style={{ width: 110 }}>Total</th>
                  <th style={{ width: 100 }}>Medio</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.folio}>
                    <td className="c-code">{r.folio}</td>
                    <td style={{ fontSize: 12.5 }}>{window.fmtFecha(r.fecha)}</td>
                    <td className="c-cat" style={{ textTransform: "none" }}>{r.cajero}</td>
                    <td className="r c-stock">$ {window.money(r.subtotal)}</td>
                    <td className="r c-stock">$ {window.money(r.iva)}</td>
                    <td className="r c-price">$ {window.money(r.total)}</td>
                    <td><span className={"tag " + (r.medio === "Efectivo" ? "tag--ok" : "tag--low")}>{r.medio}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="rep-foot">
            <span className="mono">El export entrega los datos para timbrado externo a RFC genérico. <b>La app no timbra (no CFDI).</b></span>
          </div>
        </div>
      </div>
    </div>
  );
}

window.ReportesScreen = ReportesScreen;
````

## `reimpresion.jsx`

````jsx
// ReimpresionScreen — busca folio, muestra el ticket (80 mm) y reimprime
// idéntico + leyenda "*** REIMPRESIÓN <fecha/hora> ***". No altera la venta.
const { useState, useRef, useEffect } = React;

function ReimpresionScreen({ notify }) {
  const [folio, setFolio] = useState("");
  const [sale, setSale] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [reprint, setReprint] = useState(null); // fecha/hora de reimpresión
  const inputRef = useRef(null);

  useEffect(() => { inputRef.current && inputRef.current.focus(); }, []);

  function lookup(value) {
    const f = (value || folio).trim().toUpperCase();
    const found = window.SEED_SALES.find(s => s.folio.toUpperCase() === f);
    setReprint(null);
    if (found) { setSale(found); setNotFound(false); }
    else { setSale(null); setNotFound(true); }
  }

  function onKeyDown(e) {
    if (e.key === "Enter") { e.preventDefault(); lookup(); }
    else if (e.key === "Escape") { setFolio(""); setSale(null); setNotFound(false); setReprint(null); }
  }

  function reimprimir() {
    const now = new Date();
    setReprint(now.toLocaleDateString("es-MX", { day: "2-digit", month: "2-digit", year: "numeric" }) +
      " " + now.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" }));
    notify(`Reimpresión enviada a RP850 · ${sale.folio} (ticket idéntico, no altera la venta)`);
  }

  const totals = sale ? window.saleTotals(sale.lines) : null;

  return (
    <div className="reimp">
      {/* LEFT: lookup */}
      <aside className="reimp__side">
        <div className="reimp__side-head">
          <h3>Reimprimir ticket</h3>
          <p>Escanea el folio del ticket o tecléalo</p>
        </div>
        <div className="reimp__side-body">
          <div className="scanbar scanbar--inset">
            <div className="scanbar__icon">{Icon.scan()}</div>
            <div className="scan-input-wrap">
              <input
                ref={inputRef}
                className="scan-input"
                placeholder="Folio…"
                value={folio}
                onChange={e => { setFolio(e.target.value); setNotFound(false); }}
                onKeyDown={onKeyDown}
              />
            </div>
          </div>
          {notFound && <div className="reimp__err">{Icon.alert()} Folio no encontrado</div>}
          <div className="eyebrow" style={{ marginTop: 18, marginBottom: 8 }}>Folios recientes</div>
          <div className="reimp__list">
            {window.SEED_SALES.slice().reverse().map(s => {
              const t = window.saleTotals(s.lines);
              return (
                <button key={s.folio}
                  className={"reimp__item" + (sale && sale.folio === s.folio ? " is-active" : "")}
                  onClick={() => { setFolio(s.folio); lookup(s.folio); }}>
                  <span className="reimp__item-folio mono">{s.folio}</span>
                  <span className="reimp__item-meta">{window.fmtFecha(s.fecha)}</span>
                  <span className="reimp__item-total num">$ {window.money(t.total)}</span>
                </button>
              );
            })}
          </div>
        </div>
      </aside>

      {/* RIGHT: ticket preview */}
      <div className="reimp__stage scroll">
        {!sale ? (
          <div className="reimp__placeholder">
            <div className="ring">{Icon.printer({ width: 30, height: 30 })}</div>
            <div style={{ fontWeight: 600, color: "var(--ink-2)" }}>Selecciona un folio para previsualizar</div>
            <div className="mono" style={{ fontSize: 12, marginTop: 4, color: "var(--faint)" }}>El ticket reimpreso es idéntico al original</div>
          </div>
        ) : (
          <React.Fragment>
            <div className={"ticket-paper" + (reprint ? " is-reprint" : "")}>
              <div className="tp-center tp-brand">MASCHINARIO · BAZAR</div>
              <div className="tp-center tp-sub">Bazar Lupita · Suc. Centro</div>
              <div className="tp-center tp-sub">NOTA DE COMPRA (NO CFDI)</div>
              <div className="tp-rule" />
              <div className="tp-kv"><span>Folio</span><span>{sale.folio}</span></div>
              <div className="tp-kv"><span>Fecha</span><span>{window.fmtFecha(sale.fecha)}</span></div>
              <div className="tp-kv"><span>Cajero</span><span>{sale.cajero}</span></div>
              <div className="tp-rule" />
              {sale.lines.map(l => (
                <div className="tp-line" key={l.code}>
                  <div className="tp-line__desc">{l.qty} x {l.name}</div>
                  <div className="tp-line__row">
                    <span className="tp-line__unit">@ {window.money(l.price)}</span>
                    <span>{window.money(l.price * l.qty)}</span>
                  </div>
                </div>
              ))}
              <div className="tp-rule" />
              <div className="tp-kv"><span>Subtotal</span><span>{window.money(totals.subtotal)}</span></div>
              <div className="tp-kv"><span>IVA (16%)</span><span>{window.money(totals.iva)}</span></div>
              <div className="tp-total"><span>TOTAL</span><span>$ {window.money(totals.total)}</span></div>
              <div className="tp-rule" />
              <div className="tp-kv"><span>Pago</span><span>{sale.medio}</span></div>
              {sale.ref && <div className="tp-kv"><span>Ref.</span><span>{sale.ref}</span></div>}
              <div className="tp-rule" />
              <div className="tp-center tp-thanks">¡Gracias por su compra!</div>
              <div className="tp-center tp-qr">[ QR folio {sale.folio} ]</div>
              {reprint && <div className="tp-center tp-reprint">*** REIMPRESIÓN {reprint} ***</div>}
            </div>

            <div className="reimp__actions">
              <button className="btn btn--primary" onClick={reimprimir}>{Icon.printer()} Reimprimir ticket</button>
              {reprint && <span className="reimp__done">{Icon.checkSm()} Enviado a la RP850 · no altera la venta</span>}
            </div>
          </React.Fragment>
        )}
      </div>
    </div>
  );
}

window.ReimpresionScreen = ReimpresionScreen;
````

## `styles.css`

````css
/* ============================================================
   MASCHINARIO · BAZAR — design tokens & base styles
   Brand chrome dark / operational light. Technical, geometric.
   ============================================================ */

:root {
  /* Brand chrome */
  --petroleo: #19424C;
  --tinta: #09191E;
  --petroleo-2: #1F525E;   /* lifted petroleo for hover/lines */
  --tinta-line: #12313A;   /* hairlines on dark */

  /* Brand accents */
  --rojo: #B60C0C;
  --menta: #A9DFC2;
  --teal: #209B9B;
  --teal-deep: #1B8484;

  /* Semantic (separate from brand) */
  --exito: #1E9E5A;
  --exito-soft: #E6F4EC;
  --error: #C62828;
  --error-soft: #FBEAEA;
  --aviso: #C77700;
  --aviso-soft: #FBF2E3;

  /* Operational light surfaces (cool neutrals) */
  --bg: #EBEEEE;
  --surface: #FFFFFF;
  --surface-2: #F4F6F6;
  --ink: #0C1E23;
  --ink-2: #3C4E53;
  --muted: #6B7B7F;
  --faint: #9AA8AB;
  --line: #D7DDDD;
  --line-strong: #C2C9C9;

  /* Type */
  --brand-font: 'Orbitron', sans-serif;
  --ui: 'IBM Plex Sans', system-ui, sans-serif;
  --mono: 'IBM Plex Mono', 'SF Mono', monospace;

  --r: 3px;            /* base radius — geometric, tight */
  --r-lg: 5px;
  --shadow: 0 1px 0 rgba(9,25,30,0.04), 0 6px 24px -12px rgba(9,25,30,0.25);
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  height: 100%;
  font-family: var(--ui);
  color: var(--ink);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

#root { height: 100%; }

button { font-family: inherit; cursor: pointer; }
input { font-family: inherit; }

/* ---------- type helpers ---------- */
.brand {
  font-family: var(--brand-font);
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.10em;
}
.mono { font-family: var(--mono); font-variant-numeric: tabular-nums; }
.num { font-family: var(--mono); font-variant-numeric: tabular-nums; text-align: right; }
.eyebrow {
  font-family: var(--mono);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 11px;
  font-weight: 500;
  color: var(--muted);
}

/* ============================================================
   APP SHELL
   ============================================================ */
.app {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
}

.topbar {
  flex: 0 0 auto;
  height: 56px;
  background: var(--tinta);
  color: #DCE6E6;
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid var(--tinta-line);
  user-select: none;
}
.topbar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 22px 0 20px;
  border-right: 1px solid var(--tinta-line);
}
.brand-mark {
  width: 22px; height: 22px;
  border: 2px solid var(--teal);
  transform: rotate(45deg);
  position: relative;
  flex: 0 0 auto;
}
.brand-mark::after {
  content: "";
  position: absolute; inset: 4px;
  background: var(--teal);
}
.topbar__brand .brand {
  font-size: 17px;
  color: #fff;
}
.topbar__brand .brand small {
  font-size: 10px;
  color: var(--teal);
  letter-spacing: 0.22em;
  margin-left: 2px;
  vertical-align: 2px;
}

.nav {
  display: flex;
  align-items: stretch;
}
.nav__item {
  background: none;
  border: none;
  border-right: 1px solid var(--tinta-line);
  color: #7E9296;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
  display: flex;
  align-items: center;
  gap: 9px;
  position: relative;
  transition: color .12s;
}
.nav__item:hover { color: #CFE0E0; background: rgba(255,255,255,0.03); }
.nav__item.is-active { color: #fff; background: var(--petroleo); }
.nav__item.is-active::after {
  content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 2px;
  background: var(--teal);
}
.nav__key {
  font-family: var(--mono);
  font-size: 10px;
  color: #5E777C;
  border: 1px solid var(--tinta-line);
  border-radius: 2px;
  padding: 1px 4px;
}
.nav__item.is-active .nav__key { color: var(--menta); border-color: #2C5560; }

.topbar__right {
  margin-left: auto;
  display: flex;
  align-items: stretch;
}
.session {
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: right;
  padding: 0 18px;
  border-left: 1px solid var(--tinta-line);
}
.session__store { font-size: 12.5px; color: #DCE6E6; font-weight: 600; }
.session__meta { font-family: var(--mono); font-size: 10.5px; color: #6E8488; letter-spacing: .04em; }
.session__user {
  display: flex; align-items: center; gap: 10px;
  padding: 0 18px; border-left: 1px solid var(--tinta-line);
}
.avatar {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--petroleo); color: var(--menta);
  display: grid; place-items: center;
  font-weight: 700; font-size: 12px;
  border: 1px solid #2C5560;
}
.btn-logout {
  background: none; border: none; color: #6E8488; padding: 0 16px;
  border-left: 1px solid var(--tinta-line);
  font-size: 11px; font-family: var(--mono); letter-spacing: .1em; text-transform: uppercase;
}
.btn-logout:hover { color: var(--error); background: rgba(198,40,40,.08); }

.workspace { flex: 1 1 auto; min-height: 0; overflow: hidden; position: relative; }

/* ============================================================
   GENERIC CONTROLS
   ============================================================ */
.btn {
  appearance: none;
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--ink);
  font-size: 13px;
  font-weight: 600;
  padding: 9px 14px;
  border-radius: var(--r);
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  transition: background .12s, border-color .12s, color .12s, transform .04s;
}
.btn:hover { background: var(--surface-2); border-color: var(--muted); }
.btn:active { transform: translateY(1px); }
.btn--primary {
  background: var(--teal); border-color: var(--teal-deep); color: #fff;
}
.btn--primary:hover { background: var(--teal-deep); border-color: var(--teal-deep); }
.btn--danger { color: var(--error); border-color: #E2BEBE; background: var(--error-soft); }
.btn--danger:hover { background: #F5DCDC; border-color: var(--error); }
.btn--ghost { background: transparent; border-color: transparent; color: var(--ink-2); }
.btn--ghost:hover { background: var(--surface-2); border-color: var(--line); }
.btn:disabled { opacity: .45; cursor: not-allowed; transform: none; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field > label { font-family: var(--mono); font-size: 10.5px; text-transform: uppercase; letter-spacing: .12em; color: var(--muted); }
.input {
  border: 1px solid var(--line-strong);
  background: var(--surface);
  border-radius: var(--r);
  padding: 9px 11px;
  font-size: 14px;
  color: var(--ink);
  width: 100%;
  outline: none;
  transition: border-color .12s, box-shadow .12s;
}
.input:focus { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(32,155,155,.16); }
.input--mono { font-family: var(--mono); font-variant-numeric: tabular-nums; }

/* tag / chip */
.tag {
  font-family: var(--mono); font-size: 10.5px; letter-spacing: .06em;
  text-transform: uppercase; padding: 3px 7px; border-radius: 2px;
  border: 1px solid var(--line); color: var(--muted); background: var(--surface);
}
.tag--ok { color: var(--exito); border-color: #B7E0C7; background: var(--exito-soft); }
.tag--low { color: var(--aviso); border-color: #EAD5AE; background: var(--aviso-soft); }
.tag--out { color: var(--error); border-color: #E2BEBE; background: var(--error-soft); }

/* utility scrollbars */
.scroll { overflow-y: auto; }
.scroll::-webkit-scrollbar { width: 10px; }
.scroll::-webkit-scrollbar-thumb { background: #C9D2D2; border: 3px solid var(--surface); border-radius: 6px; }
.scroll::-webkit-scrollbar-thumb:hover { background: #AEB9B9; }
.scroll--dark::-webkit-scrollbar-thumb { background: #1E4751; border-color: var(--tinta); }

/* toast */
.toast {
  position: absolute; bottom: 22px; left: 50%; transform: translateX(-50%);
  background: var(--tinta); color: #fff; padding: 12px 18px; border-radius: var(--r);
  display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 600;
  box-shadow: 0 16px 40px -16px rgba(9,25,30,.6); z-index: 80;
  border: 1px solid var(--tinta-line); animation: toastIn .25s ease both;
}
.toast svg { color: var(--exito); }
@keyframes toastIn { from { opacity: 0; transform: translate(-50%, 12px); } }
````

## `screens.css`

````css
/* ============================================================
   SCREEN STYLES — venta, cobro, catálogo, corte, login
   ============================================================ */

/* ---------------- VENTA ---------------- */
.venta {
  display: grid;
  grid-template-columns: 1fr 360px;
  height: 100%;
}
.venta__main {
  display: flex; flex-direction: column; min-width: 0;
  background: var(--bg);
}

.scanbar {
  flex: 0 0 auto;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  padding: 16px 22px;
  display: flex; align-items: center; gap: 16px;
  position: relative;
}
.scanbar__icon {
  width: 40px; height: 40px; flex: 0 0 auto;
  border: 1px solid var(--line-strong); border-radius: var(--r);
  display: grid; place-items: center; color: var(--teal); background: var(--surface-2);
}
.scan-input-wrap { flex: 1 1 auto; position: relative; }
.scan-input {
  width: 100%;
  border: 1px solid var(--line-strong);
  border-radius: var(--r);
  padding: 13px 14px;
  font-family: var(--mono);
  font-size: 16px;
  letter-spacing: .02em;
  outline: none;
  background: var(--surface);
  transition: border-color .12s, box-shadow .12s;
}
.scan-input:focus { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(32,155,155,.16); }
.scan-input::placeholder { color: var(--faint); font-family: var(--ui); letter-spacing: 0; }

.suggest {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0; z-index: 30;
  background: var(--surface); border: 1px solid var(--line-strong); border-radius: var(--r);
  box-shadow: var(--shadow); max-height: 320px; overflow-y: auto; overflow-x: hidden;
}
.suggest__row {
  display: grid; grid-template-columns: 132px 1fr auto; gap: 14px; align-items: center;
  padding: 10px 14px; border-bottom: 1px solid var(--line); cursor: pointer;
}
.suggest__row:last-child { border-bottom: none; }
.suggest__row:hover, .suggest__row.is-active { background: var(--surface-2); }
.suggest__code { font-family: var(--mono); font-size: 11.5px; color: var(--muted); }
.suggest__name { font-size: 13.5px; }
.suggest__price { font-family: var(--mono); font-variant-numeric: tabular-nums; font-weight: 600; }

.scan-hint {
  flex: 0 0 auto; font-family: var(--mono); font-size: 11px; color: var(--faint);
  display: flex; align-items: center; gap: 6px;
}
kbd {
  font-family: var(--mono); font-size: 10.5px; background: var(--surface-2);
  border: 1px solid var(--line-strong); border-bottom-width: 2px; border-radius: 3px;
  padding: 1px 6px; color: var(--ink-2);
}

/* lines table */
.lines { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; }
.lines__head, .line {
  display: grid;
  grid-template-columns: 30px minmax(96px, 1fr) 106px 78px 94px 32px;
  align-items: center;
  gap: 10px;
}
.lines__head {
  flex: 0 0 auto;
  padding: 10px 18px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--line);
  font-family: var(--mono); font-size: 10px; text-transform: uppercase; letter-spacing: .14em;
  color: var(--muted);
}
.lines__head .r, .line .r { text-align: right; }
.lines__body { flex: 1 1 auto; min-height: 0; overflow-y: auto; }
.line {
  padding: 0 18px; height: 60px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
}
.line:hover { background: var(--surface-2); }
.line.is-flash { animation: flash .5s ease; }
@keyframes flash { 0% { background: var(--menta); } 100% { background: var(--surface); } }
.line__idx { font-family: var(--mono); font-size: 12px; color: var(--faint); }
.line__name { min-width: 0; }
.line__name b { font-weight: 600; font-size: 13.5px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.25; }
.line__name span { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.line__price, .line__amount { font-family: var(--mono); font-variant-numeric: tabular-nums; text-align: right; }
.line__amount { font-weight: 700; }
.line__price { color: var(--ink-2); }

.qty { display: inline-flex; align-items: center; justify-content: flex-end; gap: 0; }
.qty button {
  width: 28px; height: 28px; border: 1px solid var(--line-strong); background: var(--surface);
  color: var(--ink-2); font-size: 16px; line-height: 1; display: grid; place-items: center;
}
.qty button:first-child { border-radius: var(--r) 0 0 var(--r); }
.qty button:last-child { border-radius: 0 var(--r) var(--r) 0; }
.qty button:hover { background: var(--surface-2); color: var(--teal); border-color: var(--muted); }
.qty input {
  width: 46px; height: 28px; text-align: center; border: 1px solid var(--line-strong); border-left: 0; border-right: 0;
  font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 14px; outline: none; color: var(--ink);
}
.line__del {
  width: 30px; height: 30px; border: none; background: none; color: var(--faint);
  border-radius: var(--r); display: grid; place-items: center; justify-self: end;
}
.line__del:hover { background: var(--error-soft); color: var(--error); }

/* empty state */
.lines__empty {
  flex: 1 1 auto; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 14px; color: var(--faint); text-align: center;
}
.lines__empty .ring {
  width: 64px; height: 64px; border: 2px dashed var(--line-strong); border-radius: 50%;
  display: grid; place-items: center; color: var(--line-strong);
}

/* RIGHT PANEL */
.cobro-panel {
  background: var(--surface);
  border-left: 1px solid var(--line);
  display: flex; flex-direction: column;
}
.cobro-panel__head {
  padding: 16px 22px 14px; border-bottom: 1px solid var(--line);
  display: flex; justify-content: space-between; align-items: baseline;
}
.cobro-panel__head .ticket { font-family: var(--mono); font-size: 12px; color: var(--ink-2); }
.cobro-panel__body { flex: 1 1 auto; padding: 18px 22px; display: flex; flex-direction: column; gap: 2px; overflow-y: auto; }

.sumrow { display: flex; justify-content: space-between; align-items: baseline; padding: 9px 0; }
.sumrow__label { font-size: 13.5px; color: var(--ink-2); }
.sumrow__label small { font-family: var(--mono); color: var(--muted); font-size: 11px; margin-left: 6px; }
.sumrow__val { font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 15px; font-weight: 600; }
.sumrow--items .sumrow__val { color: var(--muted); font-weight: 500; }
.sum-divider { height: 1px; background: var(--line); margin: 6px 0; }

.total-block {
  margin-top: auto;
}
.total-card {
  background: var(--tinta);
  border-radius: var(--r-lg);
  padding: 18px 20px 20px;
  color: #fff;
  position: relative;
  overflow: hidden;
}
.total-card::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--teal);
}
.total-card__label {
  font-family: var(--mono); font-size: 11px; letter-spacing: .2em; text-transform: uppercase;
  color: var(--menta); margin-bottom: 4px;
}
.total-card__amount {
  font-family: var(--mono); font-variant-numeric: tabular-nums;
  font-weight: 600; font-size: 46px; line-height: 1; letter-spacing: -0.01em;
  display: flex; align-items: baseline; gap: 8px; justify-content: flex-end;
}
.total-card__amount .cur { font-size: 18px; color: #8FB6BC; font-weight: 500; }

.panel-actions { padding: 16px 22px 20px; border-top: 1px solid var(--line); display: flex; flex-direction: column; gap: 10px; }
.btn-cobrar {
  width: 100%; padding: 17px; font-size: 16px; font-weight: 700; letter-spacing: .04em;
  border-radius: var(--r); border: 1px solid var(--teal-deep); background: var(--teal); color: #fff;
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  transition: background .12s, transform .04s;
}
.btn-cobrar:hover:not(:disabled) { background: var(--teal-deep); }
.btn-cobrar:active:not(:disabled) { transform: translateY(1px); }
.btn-cobrar .k { font-family: var(--mono); font-size: 11px; opacity: .8; border: 1px solid rgba(255,255,255,.3); padding: 2px 6px; border-radius: 3px; }
.btn-cobrar:disabled { opacity: .4; cursor: not-allowed; }
.sec-actions { display: flex; gap: 10px; }
.sec-actions .btn { flex: 1; }

/* ---------------- COBRO MODAL ---------------- */
.overlay {
  position: absolute; inset: 0; background: rgba(9,25,30,0.55);
  backdrop-filter: blur(2px);
  display: grid; place-items: center; z-index: 60;
}
.modal {
  width: 560px; max-width: calc(100vw - 40px); background: var(--surface);
  border-radius: var(--r-lg); box-shadow: 0 30px 80px -20px rgba(9,25,30,.6);
  overflow: hidden; animation: pop .18s cubic-bezier(.2,.8,.3,1) both;
}
@keyframes pop { from { transform: scale(.97) translateY(8px); } }
.modal__head {
  background: var(--tinta); color: #fff; padding: 16px 22px;
  display: flex; align-items: center; justify-content: space-between;
}
.modal__head h3 { margin: 0; font-size: 15px; font-weight: 600; letter-spacing: .01em; }
.modal__head .due { font-family: var(--mono); color: var(--menta); font-size: 13px; }
.modal__close { background: none; border: none; color: #7E9296; font-size: 20px; width: 32px; height: 32px; border-radius: var(--r); }
.modal__close:hover { background: rgba(255,255,255,.08); color: #fff; }

.seg {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0;
  border-bottom: 1px solid var(--line); background: var(--surface-2);
}
.seg button {
  background: none; border: none; padding: 14px; font-size: 14px; font-weight: 600; color: var(--muted);
  display: flex; align-items: center; justify-content: center; gap: 9px; position: relative;
  border-bottom: 2px solid transparent;
}
.seg button:hover { color: var(--ink-2); }
.seg button.is-active { color: var(--teal); background: var(--surface); border-bottom-color: var(--teal); }

.modal__body { padding: 22px; }

/* efectivo */
.efectivo { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
.quick-cash { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }
.quick-cash button {
  border: 1px solid var(--line-strong); background: var(--surface); border-radius: var(--r);
  padding: 11px; font-family: var(--mono); font-size: 14px; font-weight: 600; color: var(--ink);
}
.quick-cash button:hover { border-color: var(--teal); color: var(--teal); background: var(--surface-2); }
.quick-cash button.exact { grid-column: 1 / -1; color: var(--teal); border-color: var(--teal); background: rgba(32,155,155,.06); }

.cash-recv-input {
  width: 100%; border: 1px solid var(--line-strong); border-radius: var(--r); padding: 14px 16px;
  font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 28px; font-weight: 600; text-align: right;
  outline: none; color: var(--ink);
}
.cash-recv-input:focus { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(32,155,155,.16); }

.change-card {
  border: 1px solid var(--line); border-radius: var(--r); padding: 16px 18px;
  display: flex; flex-direction: column; justify-content: center; min-height: 132px; background: var(--surface-2);
}
.change-card.is-ok { background: var(--exito-soft); border-color: #B7E0C7; }
.change-card.is-short { background: var(--error-soft); border-color: #E2BEBE; }
.change-card__label { font-family: var(--mono); text-transform: uppercase; letter-spacing: .16em; font-size: 11px; color: var(--muted); }
.change-card.is-ok .change-card__label { color: var(--exito); }
.change-card.is-short .change-card__label { color: var(--error); }
.change-card__amt {
  font-family: var(--mono); font-variant-numeric: tabular-nums; font-weight: 700; font-size: 40px; line-height: 1.1;
  text-align: right; color: var(--ink-2);
}
.change-card.is-ok .change-card__amt { color: var(--exito); }
.change-card.is-short .change-card__amt { color: var(--error); }

/* tarjeta */
.tarjeta { text-align: center; padding: 8px 0 4px; }
.terminal {
  margin: 0 auto 20px; width: 200px; height: 132px; border-radius: 10px;
  background: linear-gradient(160deg, #1F525E, #09191E); border: 1px solid #2C5560;
  position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
  box-shadow: 0 16px 40px -18px rgba(9,25,30,.7);
}
.terminal__screen {
  width: 150px; height: 44px; border-radius: 4px; background: #07151A; border: 1px solid #14333C;
  display: grid; place-items: center; font-family: var(--mono); font-size: 12px; color: var(--menta);
}
.terminal__slot { width: 120px; height: 6px; border-radius: 3px; background: #0B2026; }
.pulse-ring {
  position: absolute; inset: -6px; border: 2px solid var(--teal); border-radius: 14px; opacity: 0;
}
.is-waiting .pulse-ring { animation: ring 1.4s ease-out infinite; }
@keyframes ring { 0% { opacity: .7; transform: scale(1); } 100% { opacity: 0; transform: scale(1.12); } }
.term-status { font-size: 15px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 10px; min-height: 24px; }
.term-status.waiting { color: var(--aviso); }
.term-status.approved { color: var(--exito); }
.term-status.declined { color: var(--error); }
.spinner { width: 16px; height: 16px; border: 2px solid rgba(199,119,0,.3); border-top-color: var(--aviso); border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.term-sub { font-family: var(--mono); font-size: 11.5px; color: var(--muted); margin-top: 8px; }

.modal__foot { padding: 16px 22px; border-top: 1px solid var(--line); display: flex; gap: 10px; }
.modal__foot .btn { flex: 1; padding: 13px; }

/* success tick */
.tick { width: 56px; height: 56px; border-radius: 50%; background: var(--exito); display: grid; place-items: center; margin: 0 auto 14px; animation: pop .2s ease both; }
.paydone { text-align: center; padding: 16px 0; }
.paydone h3 { margin: 0 0 4px; font-size: 18px; }
.paydone p { margin: 0; color: var(--muted); font-family: var(--mono); font-size: 12.5px; }

/* ---------------- CATÁLOGO ---------------- */
.catalogo { display: grid; grid-template-columns: 1fr 360px; height: 100%; }
.cat__main { display: flex; flex-direction: column; min-width: 0; background: var(--bg); }
.cat__bar {
  padding: 16px 22px; background: var(--surface); border-bottom: 1px solid var(--line);
  display: flex; align-items: center; gap: 14px;
}
.search { position: relative; flex: 1 1 auto; max-width: 440px; }
.search input { width: 100%; padding: 10px 12px 10px 38px; border: 1px solid var(--line-strong); border-radius: var(--r); font-size: 14px; outline: none; }
.search input:focus { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(32,155,155,.16); }
.search svg { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--faint); }
.cat__count { margin-left: auto; font-family: var(--mono); font-size: 12px; color: var(--muted); }

.cat-table-wrap { flex: 1 1 auto; min-height: 0; overflow-y: auto; }
.cat-table { width: 100%; border-collapse: collapse; }
.cat-table thead th {
  position: sticky; top: 0; z-index: 2; background: var(--surface-2); text-align: left;
  font-family: var(--mono); font-size: 10px; text-transform: uppercase; letter-spacing: .14em; color: var(--muted);
  padding: 11px 18px; border-bottom: 1px solid var(--line); font-weight: 500;
}
.cat-table th.r, .cat-table td.r { text-align: right; }
.cat-table tbody td { padding: 12px 18px; border-bottom: 1px solid var(--line); font-size: 13.5px; background: var(--surface); }
.cat-table tbody tr:hover td { background: var(--surface-2); }
.cat-table tbody tr.is-selected td { background: rgba(32,155,155,.07); }
.cat-table .c-code { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.cat-table .c-name { font-weight: 600; }
.cat-table .c-cat { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.cat-table .c-price { font-family: var(--mono); font-variant-numeric: tabular-nums; font-weight: 600; }
.cat-table .c-stock { font-family: var(--mono); font-variant-numeric: tabular-nums; }

.cat__form { background: var(--surface); border-left: 1px solid var(--line); display: flex; flex-direction: column; }
.cat__form-head { padding: 16px 20px; border-bottom: 1px solid var(--line); }
.cat__form-head h3 { margin: 0; font-size: 14px; }
.cat__form-head p { margin: 3px 0 0; font-family: var(--mono); font-size: 11px; color: var(--muted); }
.cat__form-body { flex: 1 1 auto; padding: 18px 20px; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
.scan-field-wrap { position: relative; }
.scan-field-wrap .scan-badge {
  position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
  font-family: var(--mono); font-size: 9.5px; letter-spacing: .1em; text-transform: uppercase;
  color: var(--teal); border: 1px solid var(--menta); background: rgba(32,155,155,.06); padding: 3px 6px; border-radius: 2px;
  display: flex; align-items: center; gap: 5px;
}
.scan-badge.live { animation: blink 1.1s ease-in-out infinite; }
@keyframes blink { 50% { opacity: .35; } }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.cat__form-foot { padding: 16px 20px; border-top: 1px solid var(--line); display: flex; gap: 10px; }
.cat__form-foot .btn { flex: 1; }

/* ---------------- CORTE DE CAJA ---------------- */
.corte { height: 100%; background: var(--tinta); color: #DCE6E6; overflow-y: auto; }
.corte__inner { max-width: 1080px; margin: 0 auto; padding: 32px 28px 48px; }
.corte__top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 26px; }
.corte__top h2 { margin: 0; font-size: 24px; color: #fff; letter-spacing: -.01em; }
.corte__top .eyebrow { color: var(--menta); }
.corte__top .meta { text-align: right; font-family: var(--mono); font-size: 12px; color: #7E9296; line-height: 1.7; }
.corte__grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 22px; align-items: start; }

.dpanel { background: #0E2228; border: 1px solid var(--tinta-line); border-radius: var(--r-lg); overflow: hidden; }
.dpanel__head { padding: 14px 18px; border-bottom: 1px solid var(--tinta-line); display: flex; justify-content: space-between; align-items: center; }
.dpanel__head h4 { margin: 0; font-size: 13px; color: #fff; font-weight: 600; letter-spacing: .02em; }
.dpanel__body { padding: 6px 18px 14px; }

.drow { display: flex; justify-content: space-between; align-items: center; padding: 13px 0; border-bottom: 1px solid var(--tinta-line); }
.drow:last-child { border-bottom: none; }
.drow__l { display: flex; align-items: center; gap: 12px; font-size: 13.5px; }
.drow__icon { width: 32px; height: 32px; border-radius: var(--r); display: grid; place-items: center; background: #12313A; color: var(--menta); border: 1px solid var(--tinta-line); }
.drow__sub { font-family: var(--mono); font-size: 10.5px; color: #6E8488; }
.drow__v { font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 15px; font-weight: 600; color: #fff; }

.corte-input {
  width: 150px; background: #07151A; border: 1px solid #1E4751; border-radius: var(--r);
  padding: 9px 12px; font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 15px;
  color: #fff; text-align: right; outline: none;
}
.corte-input:focus { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(32,155,155,.2); }

.expected-card { background: linear-gradient(165deg, #12313A, #0B2026); border: 1px solid var(--tinta-line); border-radius: var(--r-lg); padding: 20px; }
.bigrow { display: flex; justify-content: space-between; align-items: baseline; padding: 12px 0; }
.bigrow__label { font-size: 13.5px; color: #9DB0B4; }
.bigrow__val { font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 22px; font-weight: 600; color: #fff; }
.bigrow.muted .bigrow__val { color: #9DB0B4; font-size: 18px; }

.diff-card { margin-top: 16px; border-radius: var(--r); padding: 18px 20px; border: 1px solid; }
.diff-card.zero { background: rgba(30,158,90,.12); border-color: rgba(30,158,90,.4); }
.diff-card.neg { background: rgba(198,40,40,.14); border-color: rgba(198,40,40,.5); }
.diff-card.pos { background: rgba(199,119,0,.14); border-color: rgba(199,119,0,.5); }
.diff-card__label { font-family: var(--mono); text-transform: uppercase; letter-spacing: .14em; font-size: 11px; display: flex; align-items: center; gap: 8px; }
.diff-card.zero .diff-card__label { color: var(--exito); }
.diff-card.neg .diff-card__label { color: #FF8A8A; }
.diff-card.pos .diff-card__label { color: #F0B860; }
.diff-card__amt { font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 36px; font-weight: 700; text-align: right; margin-top: 6px; }
.diff-card.zero .diff-card__amt { color: var(--exito); }
.diff-card.neg .diff-card__amt { color: #FF8A8A; }
.diff-card.pos .diff-card__amt { color: #F0B860; }

.corte__actions { margin-top: 24px; display: flex; gap: 12px; justify-content: flex-end; }
.btn-dark { background: #12313A; border: 1px solid #1E4751; color: #DCE6E6; padding: 13px 20px; border-radius: var(--r); font-weight: 600; font-size: 14px; }
.btn-dark:hover { background: #1A3F49; border-color: #2C5560; }
.btn-cierre { background: var(--teal); border: 1px solid var(--teal-deep); color: #fff; padding: 13px 26px; border-radius: var(--r); font-weight: 700; font-size: 14px; letter-spacing: .03em; }
.btn-cierre:hover { background: var(--teal-deep); }

.summary-strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--tinta-line); border: 1px solid var(--tinta-line); border-radius: var(--r-lg); overflow: hidden; margin-bottom: 22px; }
.summary-strip .cell { background: #0E2228; padding: 16px 18px; }
.summary-strip .cell .eyebrow { color: #6E8488; }
.summary-strip .cell .v { font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 22px; font-weight: 600; color: #fff; margin-top: 6px; }
.summary-strip .cell .v.accent { color: var(--menta); }

/* ---------------- LOGIN ---------------- */
.login {
  height: 100%; background:
    radial-gradient(1200px 600px at 70% -10%, #12313A 0%, transparent 60%),
    radial-gradient(900px 500px at 0% 120%, #103039 0%, transparent 55%),
    var(--tinta);
  display: grid; place-items: center; position: relative; overflow: hidden;
}
.login__grid {
  position: absolute; inset: 0;
  background-image: linear-gradient(var(--tinta-line) 1px, transparent 1px), linear-gradient(90deg, var(--tinta-line) 1px, transparent 1px);
  background-size: 44px 44px; opacity: .35; mask-image: radial-gradient(circle at 50% 40%, #000, transparent 80%);
}
.login__brandbar { position: absolute; top: 28px; left: 32px; display: flex; align-items: center; gap: 12px; color: #fff; }
.login__brandbar .brand { font-size: 16px; }
.login__brandbar .brand small { color: var(--teal); font-size: 9px; letter-spacing: .22em; margin-left: 2px; vertical-align: 2px; }
.login__store { position: absolute; top: 30px; right: 32px; font-family: var(--mono); font-size: 12px; color: #6E8488; text-align: right; line-height: 1.6; }

.login-card {
  position: relative; z-index: 2; width: 380px; background: #0E2228; border: 1px solid var(--tinta-line);
  border-radius: var(--r-lg); box-shadow: 0 40px 90px -30px rgba(0,0,0,.7); overflow: hidden;
}
.login-card__top { padding: 30px 32px 22px; text-align: center; border-bottom: 1px solid var(--tinta-line); }
.login-logo { display: inline-flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.login-logo .brand-mark { width: 30px; height: 30px; }
.login-logo .brand { font-size: 26px; color: #fff; }
.login-logo .brand small { color: var(--teal); font-size: 11px; letter-spacing: .24em; vertical-align: 4px; margin-left: 3px; }
.login-card__top .eyebrow { color: #6E8488; }

.pin-display { display: flex; justify-content: center; gap: 14px; padding: 24px 0 6px; }
.pin-dot { width: 14px; height: 14px; border-radius: 50%; border: 1.5px solid #2C5560; transition: all .15s; }
.pin-dot.filled { background: var(--teal); border-color: var(--teal); box-shadow: 0 0 12px rgba(32,155,155,.5); }
.pin-dot.err { border-color: var(--error); animation: shake .35s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-6px)} 75%{transform:translateX(6px)} }
.pin-msg { text-align: center; font-family: var(--mono); font-size: 11.5px; min-height: 18px; margin-bottom: 6px; }
.pin-msg.err { color: #FF8A8A; }
.pin-msg.hint { color: #6E8488; }

.numpad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--tinta-line); border-top: 1px solid var(--tinta-line); }
.numpad button {
  background: #0E2228; border: none; color: #DCE6E6; height: 64px; font-family: var(--mono);
  font-size: 22px; font-weight: 500; transition: background .1s;
}
.numpad button:hover { background: #163840; }
.numpad button:active { background: var(--petroleo); }
.numpad button.action { font-size: 13px; color: #6E8488; letter-spacing: .06em; }
.numpad button.enter { color: var(--teal); }
.numpad button.enter:hover { background: var(--teal); color: #fff; }

.login__foot { position: absolute; bottom: 24px; left: 0; right: 0; text-align: center; font-family: var(--mono); font-size: 10.5px; color: #46595E; letter-spacing: .08em; }

/* ============================================================
   CHROME TWEAKS — longer brand "MASCHINARIO", 6 nav items
   ============================================================ */
.topbar__brand { padding: 0 18px; }
.topbar__brand .brand { font-size: 15px; letter-spacing: .07em; }
.topbar__brand .brand small { font-size: 9px; letter-spacing: .18em; }
.nav__item { font-size: 12.5px; gap: 7px; }
.nav__item .nav__key { display: inline-block; }
.login-logo .brand { font-size: 21px; }
.login__brandbar .brand { font-size: 14px; }

/* ============================================================
   DEVOLUCIÓN  (reusa .venta / .scanbar / .lines / .cobro-panel)
   ============================================================ */
.folio-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; justify-content: center; }
.folio-chip {
  font-family: var(--mono); font-size: 12px; font-weight: 600; color: var(--teal);
  border: 1px solid var(--menta); background: rgba(32,155,155,.06); border-radius: var(--r);
  padding: 6px 11px;
}
.folio-chip:hover { background: rgba(32,155,155,.12); border-color: var(--teal); }

.found-bar {
  flex: 0 0 auto; display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px; background: var(--surface); border-bottom: 1px solid var(--line);
}
.found-bar__folio { font-size: 14px; font-weight: 700; color: var(--ink); }
.found-bar__meta { font-family: var(--mono); font-size: 11.5px; color: var(--muted); margin-left: 12px; }

.devo-head, .devo-line {
  display: grid; grid-template-columns: minmax(120px,1fr) 90px 132px 100px; align-items: center; gap: 12px;
}
.devo-head {
  flex: 0 0 auto; padding: 10px 18px; background: var(--surface-2); border-bottom: 1px solid var(--line);
  font-family: var(--mono); font-size: 10px; text-transform: uppercase; letter-spacing: .14em; color: var(--muted);
}
.devo-head .r, .devo-line .num.devo-sold, .devo-head .c { text-align: right; }
.devo-head .c { text-align: center; }
.devo-line { padding: 0 18px; height: 64px; border-bottom: 1px solid var(--line); background: var(--surface); }
.devo-line:hover { background: var(--surface-2); }
.devo-sold { font-size: 14px; color: var(--ink-2); }
.devo-line .qty { justify-content: center; }
.devo-amt { font-weight: 700; }
.devo-amt:not(:empty) { color: var(--ink); }

.refund-note {
  margin-top: 14px; border: 1px dashed var(--line-strong); border-radius: var(--r);
  background: var(--surface-2); padding: 12px 14px; font-size: 12.5px; color: var(--ink-2);
  display: flex; flex-direction: column; gap: 6px;
}
.refund-note span { display: flex; align-items: center; gap: 8px; }
.refund-note svg { color: var(--teal); flex: 0 0 auto; }
.refund-note__stock { font-family: var(--mono); font-size: 11px; color: var(--muted); }

.total-card--refund::before { background: var(--rojo); }
.total-card--refund .total-card__label { color: #F2B8B8; }
.btn-cobrar--refund { background: var(--rojo); border-color: #8E0909; }
.btn-cobrar--refund:hover:not(:disabled) { background: #8E0909; }

/* ============================================================
   REPORTES  (light operational)
   ============================================================ */
.reportes { height: 100%; background: var(--bg); overflow-y: auto; }
.rep__inner { max-width: 1120px; margin: 0 auto; padding: 24px 28px 44px; }

.rep-bar { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.rep-bar__filters { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.seg-pills { display: inline-flex; border: 1px solid var(--line-strong); border-radius: var(--r); overflow: hidden; background: var(--surface); }
.seg-pills button {
  background: none; border: none; border-right: 1px solid var(--line); padding: 9px 14px; font-size: 13px; font-weight: 600;
  color: var(--ink-2); display: inline-flex; align-items: center; gap: 7px;
}
.seg-pills button:last-child { border-right: none; }
.seg-pills button:hover { background: var(--surface-2); }
.seg-pills button.is-active { background: var(--teal); color: #fff; }
.rep-select { display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--line-strong); background: var(--surface); border-radius: var(--r); padding: 0 10px; color: var(--muted); }
.rep-select select { border: none; background: none; padding: 9px 4px; font-size: 13px; font-weight: 600; color: var(--ink); outline: none; appearance: auto; }

.kpi-strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: var(--r-lg); overflow: hidden; margin-bottom: 22px; }
.kpi { background: var(--surface); padding: 16px 18px; }
.kpi__v { font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 24px; font-weight: 600; color: var(--ink); margin-top: 6px; }
.kpi__v.accent { color: var(--teal); }

.rep-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }
.rep-panel { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); overflow: hidden; }
.rep-panel__head { padding: 14px 18px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; align-items: center; }
.rep-panel__head h4 { margin: 0; font-size: 13px; font-weight: 600; color: var(--ink); }
.rep-panel__body { padding: 16px 18px; display: flex; flex-direction: column; gap: 16px; }

.bar-row { display: flex; flex-direction: column; gap: 7px; }
.bar-row__top { display: flex; justify-content: space-between; align-items: center; font-size: 13.5px; color: var(--ink); }
.bar-row__top > span:first-child { display: inline-flex; align-items: center; gap: 8px; }
.bar-row__top small { color: var(--muted); }
.bar-row__top svg { color: var(--muted); }
.bar { height: 8px; background: var(--surface-2); border-radius: 4px; overflow: hidden; border: 1px solid var(--line); }
.bar__fill { display: block; height: 100%; border-radius: 4px; transition: width .3s; }
.fill-teal { background: var(--teal); }
.fill-petro { background: var(--petroleo); }

.rep-table-wrap { max-height: 320px; overflow-y: auto; }
.rep-table tbody td { font-size: 13px; }
.rep-foot { padding: 12px 18px; border-top: 1px solid var(--line); background: var(--surface-2); }
.rep-foot .mono { font-size: 11.5px; color: var(--muted); }
.rep-foot b { color: var(--aviso); }

/* ============================================================
   REIMPRESIÓN  (lookup + thermal ticket preview)
   ============================================================ */
.reimp { display: grid; grid-template-columns: 360px 1fr; height: 100%; }
.reimp__side { background: var(--surface); border-right: 1px solid var(--line); display: flex; flex-direction: column; min-height: 0; }
.reimp__side-head { padding: 16px 20px; border-bottom: 1px solid var(--line); }
.reimp__side-head h3 { margin: 0; font-size: 14px; }
.reimp__side-head p { margin: 3px 0 0; font-family: var(--mono); font-size: 11px; color: var(--muted); }
.reimp__side-body { flex: 1 1 auto; min-height: 0; padding: 16px 18px; display: flex; flex-direction: column; }
.scanbar--inset { padding: 0; border: none; background: none; gap: 10px; }
.scanbar--inset .scanbar__icon { width: 38px; height: 38px; }
.reimp__err { display: flex; align-items: center; gap: 8px; color: var(--error); font-size: 12.5px; font-weight: 600; margin-top: 12px; }
.reimp__err svg { color: var(--error); }
.reimp__list { display: flex; flex-direction: column; gap: 8px; overflow-y: auto; }
.reimp__item {
  display: grid; grid-template-columns: 1fr auto; grid-template-rows: auto auto; gap: 2px 10px;
  text-align: left; background: var(--surface); border: 1px solid var(--line-strong); border-radius: var(--r);
  padding: 10px 12px;
}
.reimp__item:hover { border-color: var(--teal); background: var(--surface-2); }
.reimp__item.is-active { border-color: var(--teal); background: rgba(32,155,155,.07); box-shadow: 0 0 0 2px rgba(32,155,155,.12); }
.reimp__item-folio { grid-column: 1; font-size: 13px; font-weight: 700; color: var(--ink); }
.reimp__item-total { grid-column: 2; grid-row: 1 / 3; align-self: center; font-size: 14px; font-weight: 700; color: var(--ink); }
.reimp__item-meta { grid-column: 1; font-size: 11px; color: var(--muted); }

.reimp__stage { background: var(--bg); display: flex; flex-direction: column; align-items: center; gap: 18px; padding: 32px 24px; overflow-y: auto; }
.reimp__placeholder { margin: auto; display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; color: var(--faint); }
.reimp__placeholder .ring { width: 64px; height: 64px; border: 2px dashed var(--line-strong); border-radius: 50%; display: grid; place-items: center; color: var(--line-strong); }

.ticket-paper {
  width: 320px; background: #fff; color: #1A1A1A; border: 1px solid var(--line);
  border-radius: 2px; padding: 22px 24px 18px;
  font-family: var(--mono); font-size: 12px; line-height: 1.55;
  box-shadow: 0 18px 50px -22px rgba(9,25,30,.45);
  position: relative;
}
.ticket-paper::before, .ticket-paper::after {
  content: ""; position: absolute; left: 0; right: 0; height: 8px;
  background: repeating-linear-gradient(-45deg, #fff 0 6px, var(--bg) 6px 12px);
}
.ticket-paper::before { top: -8px; }
.ticket-paper::after { bottom: -8px; transform: scaleY(-1); }
.tp-center { text-align: center; }
.tp-brand { font-family: var(--brand-font); font-weight: 800; letter-spacing: .06em; font-size: 13px; }
.tp-sub { font-size: 10.5px; color: #555; letter-spacing: .04em; }
.tp-rule { border-top: 1px dashed #B0B0B0; margin: 9px 0; }
.tp-kv { display: flex; justify-content: space-between; gap: 12px; }
.tp-kv span:first-child { color: #555; }
.tp-line { margin: 4px 0; }
.tp-line__desc { white-space: normal; }
.tp-line__row { display: flex; justify-content: space-between; }
.tp-line__unit { color: #777; }
.tp-total { display: flex; justify-content: space-between; align-items: baseline; font-weight: 700; font-size: 17px; margin: 4px 0; }
.tp-thanks { margin-top: 6px; font-size: 11.5px; }
.tp-qr { margin-top: 6px; color: #888; font-size: 10.5px; }
.tp-reprint { margin-top: 10px; padding-top: 8px; border-top: 1px dashed #B0B0B0; color: var(--error); font-weight: 700; font-size: 11px; }
.ticket-paper.is-reprint { box-shadow: 0 0 0 2px rgba(198,40,40,.25), 0 18px 50px -22px rgba(9,25,30,.45); }

.reimp__actions { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.reimp__actions .btn { padding: 12px 22px; }
.reimp__done { display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: var(--exito); font-weight: 600; }
.reimp__done svg { color: var(--exito); }

/* topbar: evitar desbordes con 6 ítems en anchos medianos */
@media (max-width: 1240px) {
  .nav__item { padding: 0 13px; font-size: 12px; }
  .nav__item .nav__key { display: none; }
  .session__store { font-size: 11.5px; }
  .topbar__brand .brand small { display: none; }
}
@media (max-width: 1024px) {
  .nav__item span:not(.nav__key) { } /* labels se mantienen; iconos + texto compactos */
  .nav__item { padding: 0 11px; gap: 6px; }
  .session__meta { display: none; }
}
````

