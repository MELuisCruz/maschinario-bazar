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
