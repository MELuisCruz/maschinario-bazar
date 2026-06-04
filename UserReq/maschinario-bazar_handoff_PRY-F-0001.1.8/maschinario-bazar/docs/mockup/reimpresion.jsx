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
