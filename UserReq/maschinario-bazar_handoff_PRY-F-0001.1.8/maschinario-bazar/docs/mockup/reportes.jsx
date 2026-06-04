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
