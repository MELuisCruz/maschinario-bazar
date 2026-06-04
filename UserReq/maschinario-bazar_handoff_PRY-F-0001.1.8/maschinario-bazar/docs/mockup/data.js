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
