// JS mínimo para foco del scan-input y atajos (PERIPHERALS §2, UI_SPEC §8).
// Compatible con Jinja2+HTMX (no SPA): solo gestión de foco y navegación por teclas.
(function () {
  "use strict";

  function scanInput() {
    return document.getElementById("scan-input");
  }

  // Regla §8.3: no robar foco si el cursor está en otro campo editable legítimo.
  function focusScan() {
    var el = scanInput();
    if (!el) return;
    var active = document.activeElement;
    var editing =
      active &&
      active !== el &&
      (active.tagName === "INPUT" || active.tagName === "SELECT" || active.isContentEditable);
    if (!editing) el.focus();
  }

  function clearScan() {
    var el = scanInput();
    if (el) el.value = "";
  }

  // Auto-foco al cargar (§8.1).
  document.addEventListener("DOMContentLoaded", focusScan);

  // Recuperar foco tras swaps HTMX que reemplazan la tabla / cierran modal (§8.2).
  // En la pantalla de venta (existe #venta-main), además limpia el código ya
  // procesado para preparar la siguiente lectura del escáner.
  document.body.addEventListener("htmx:afterSwap", function () {
    if (document.getElementById("venta-main")) clearScan();
    focusScan();
  });

  // Tras un POST (HTMX), limpia los formularios marcados con
  // `data-reset-on-success` (p. ej. el de producto especial). Sustituye a los
  // `hx-on::after-request` inline, que la CSP bloquea (HTMX los evalúa con eval).
  document.body.addEventListener("htmx:afterRequest", function (evt) {
    var d = evt.detail || {};
    if (d.failed) return;
    var elt = d.elt;
    var form = elt && elt.closest ? elt.closest("form[data-reset-on-success]") : null;
    if (form && typeof form.reset === "function") form.reset();
    focusScan();
  });

  // Navegación por F1–F6 (UI_SPEC §9): solo navega; las acciones usan Enter/Esc.
  var NAV = {
    F1: "/venta",
    F2: "/devolucion",
    F3: "/reimpresion",
    F4: "/catalogo",
    F5: "/reportes",
    F6: "/corte",
  };
  document.addEventListener("keydown", function (e) {
    if (NAV[e.key]) {
      e.preventDefault();
      window.location.href = NAV[e.key];
    }
  });
})();
