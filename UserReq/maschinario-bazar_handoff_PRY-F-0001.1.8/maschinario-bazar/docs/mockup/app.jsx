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
