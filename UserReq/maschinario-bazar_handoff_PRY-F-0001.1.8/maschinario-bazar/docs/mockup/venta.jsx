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
