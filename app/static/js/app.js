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

  // Auto-foco al cargar (§8.1).
  document.addEventListener("DOMContentLoaded", focusScan);

  // Recuperar foco tras swaps HTMX que reemplazan la tabla / cierran modal (§8.2).
  document.body.addEventListener("htmx:afterSwap", function () {
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
