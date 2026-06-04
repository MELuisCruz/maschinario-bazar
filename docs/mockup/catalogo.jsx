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
