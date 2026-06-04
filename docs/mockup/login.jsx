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
