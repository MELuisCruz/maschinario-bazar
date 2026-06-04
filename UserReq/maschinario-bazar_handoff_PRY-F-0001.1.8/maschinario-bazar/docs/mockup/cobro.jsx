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
