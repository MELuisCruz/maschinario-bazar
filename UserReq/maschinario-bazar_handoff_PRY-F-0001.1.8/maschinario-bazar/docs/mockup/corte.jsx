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
