"""Ticket térmico ESC/POS — nota de compra, no CFDI (THERMAL_TICKET_SPEC, AT-9.x).

`construir_ticket_texto` es puro (sirve para la vista previa y para enviar a la
impresora). `imprimir_ticket` es tolerante a fallos: si la impresora no está
disponible, NO rompe la venta (que ya está persistida) y deja el ticket para
reimpresión (AT-9.2). Sin cajón: no se emite `ESC p`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

WIDTH = 48  # columnas en Font A (~72 mm)

# Codepage de la impresora (Rongta RP850). CP850 cubre minúsculas y MAYÚSCULAS
# acentuadas (ÁÉÍÓÚ áéíóú), ñ/Ñ y $; el default CP437 no trae las mayúsculas
# acentuadas. Si en otra impresora salieran raras, probar "CP858" o "CP437"
# (HARDWARE_SETUP §1.5).
TICKET_CODEPAGE = "CP850"


def _sep() -> str:
    return "-" * WIDTH


def _lr(izq: str, der: str) -> str:
    """Etiqueta a la izquierda, cifra a la derecha, en `WIDTH` columnas."""
    espacio = WIDTH - len(izq) - len(der)
    if espacio < 1:
        izq = izq[: WIDTH - len(der) - 1]
        espacio = 1
    return f"{izq}{' ' * espacio}{der}"


def _center(txt: str) -> str:
    return txt.center(WIDTH)


def _money(value: Decimal) -> str:
    return f"${Decimal(value):,.2f}"


def construir_ticket_texto(
    venta,
    *,
    cajero_nombre: str,
    business_name: str,
    evento: str = "",
    domicilio: str = "",
    telefono: str = "",
    pie: str = "¡Gracias por su compra!",
    pagos=None,
    reimpresion: bool = False,
    fecha_reimpresion: datetime | None = None,
) -> str:
    """Arma el texto del ticket (nota de compra, no CFDI).

    `business_name` es el establecimiento; `evento`, `domicilio`, `telefono` y
    `pie` son editables por el admin (services/configuracion.py) y se omiten si
    vienen vacíos.
    """
    pagos = list(pagos if pagos is not None else getattr(venta, "pagos", []))
    fecha = venta.cerrado_en or venta.creado_en
    lineas: list[str] = []
    lineas.append(_center(business_name.upper()))
    if evento.strip():
        lineas.append(_center(evento.strip()))
    if domicilio.strip():
        lineas.append(_center(domicilio.strip()))
    if telefono.strip():
        lineas.append(_center(f"Tel: {telefono.strip()}"))
    lineas.append(_center("NOTA DE COMPRA  (no es CFDI)"))
    lineas.append(_sep())
    lineas.append(f"Folio: {venta.folio}")
    lineas.append(f"Fecha: {fecha.strftime('%Y-%m-%d %H:%M')}")
    lineas.append(f"Cajero: {cajero_nombre}")
    lineas.append(_sep())
    lineas.append(_lr("CANT DESCRIPCION", "IMPORTE"))
    for ln in venta.lineas:
        desc = ln.descripcion[:30]
        lineas.append(_lr(f"{Decimal(ln.cantidad):g} {desc}", _money(ln.importe)))
        if Decimal(ln.descuento) > 0:
            lineas.append(_lr("   (desc.)", f"-{_money(ln.descuento)}"))
    lineas.append(_sep())
    lineas.append(_lr("Subtotal:", _money(venta.subtotal)))
    if Decimal(venta.descuento_total) > 0:
        lineas.append(_lr("Descuento:", _money(venta.descuento_total)))
    lineas.append(_lr("IVA (16%):", _money(venta.iva_total)))
    lineas.append(_lr("TOTAL:", _money(venta.total)))
    lineas.append(_sep())
    for p in pagos:
        if p.medio == "efectivo":
            lineas.append(_lr("Pago: Efectivo", _money(p.recibido or p.monto)))
            if p.cambio is not None:
                lineas.append(_lr("Cambio:", _money(p.cambio)))
        else:
            ref = (p.mp_order_id or "")[-8:]
            lineas.append(_lr("Pago: Tarjeta Point", f"Aprob. {ref}"))
    lineas.append(_sep())
    lineas.append(_center(pie.strip() or "¡Gracias por su compra!"))
    if reimpresion:
        f = (fecha_reimpresion or fecha).strftime("%Y-%m-%d %H:%M")
        lineas.append(_center(f"*** REIMPRESIÓN {f} ***"))
    return "\n".join(lineas)


@dataclass
class PrintResult:
    ok: bool
    error: str | None = None


def get_printer(settings):
    """Construye la impresora USB ESC/POS desde la config. Lanza si no se puede."""
    from escpos.printer import Usb

    if not settings.printer_usb_vendor or not settings.printer_usb_product:
        raise RuntimeError("Impresora USB no configurada (PRINTER_USB_*).")
    vendor = int(settings.printer_usb_vendor, 16)
    product = int(settings.printer_usb_product, 16)
    return Usb(vendor, product)


def imprimir_ticket(
    venta,
    *,
    cajero_nombre: str,
    business_name: str,
    evento: str = "",
    domicilio: str = "",
    telefono: str = "",
    pie: str = "¡Gracias por su compra!",
    pagos=None,
    reimpresion: bool = False,
    fecha_reimpresion: datetime | None = None,
    printer_factory=None,
    settings=None,
) -> PrintResult:
    """Imprime el ticket; ante cualquier fallo devuelve ok=False sin romper (AT-9.2)."""
    texto = construir_ticket_texto(
        venta,
        cajero_nombre=cajero_nombre,
        business_name=business_name,
        evento=evento,
        domicilio=domicilio,
        telefono=telefono,
        pie=pie,
        pagos=pagos,
        reimpresion=reimpresion,
        fecha_reimpresion=fecha_reimpresion,
    )
    factory = printer_factory or get_printer
    try:
        printer = factory(settings)
        printer.charcode(TICKET_CODEPAGE)  # mayúsculas acentuadas (ÁÉÍÓÚ)
        printer.text(texto + "\n")
        printer.cut()  # GS V — corte; sin ESC p (no hay cajón)
        close = getattr(printer, "close", None)
        if callable(close):
            close()
        return PrintResult(ok=True)
    except Exception as exc:  # impresora no disponible / papel / device
        return PrintResult(ok=False, error=str(exc))
