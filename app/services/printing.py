"""Ticket térmico ESC/POS — nota de compra, no CFDI (THERMAL_TICKET_SPEC, AT-9.x).

`construir_ticket_texto` es puro (sirve para la vista previa y para enviar a la
impresora). `imprimir_ticket` es tolerante a fallos: si la impresora no está
disponible, NO rompe la venta (que ya está persistida) y deja el ticket para
reimpresión (AT-9.2). Sin cajón: no se emite `ESC p`.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

WIDTH = 48  # columnas en Font A (~72 mm)

# Formato y zona horaria por defecto del timestamp (editables en Configuración).
FECHA_FORMATO_DEFAULT = "%d-%m-%Y %H:%M"
TZ_OFFSET_DEFAULT = -6  # UTC-6


def _fmt_fecha(dt: datetime, fecha_formato: str, tz_offset: int) -> str:
    """Convierte un datetime (UTC) a la zona local y lo formatea, con etiqueta TZ."""
    if dt.tzinfo is None:  # asume UTC si viene naive
        dt = dt.replace(tzinfo=timezone.utc)
    local = dt.astimezone(timezone(timedelta(hours=tz_offset)))
    formato = fecha_formato or FECHA_FORMATO_DEFAULT
    try:
        base = local.strftime(formato)
    except (ValueError, TypeError):
        base = local.strftime(FECHA_FORMATO_DEFAULT)
    return f"{base} UTC{tz_offset:+d}"


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
    fecha_formato: str = FECHA_FORMATO_DEFAULT,
    tz_offset: int = TZ_OFFSET_DEFAULT,
    pagos=None,
    reimpresion: bool = False,
    fecha_reimpresion: datetime | None = None,
) -> str:
    """Arma el texto del ticket (nota de compra, no CFDI).

    `business_name` es el establecimiento; `evento`, `domicilio`, `telefono`,
    `pie`, `fecha_formato` (strftime) y `tz_offset` (horas UTC) son editables por
    el admin (services/configuracion.py); los textos vacíos se omiten.
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
    lineas.append(f"Fecha: {_fmt_fecha(fecha, fecha_formato, tz_offset)}")
    lineas.append(f"Cajero: {cajero_nombre}")
    lineas.append(_sep())
    lineas.append(_lr("CANT DESCRIPCION", "IMPORTE"))
    for ln in venta.lineas:
        cant = f"{Decimal(ln.cantidad):g}"
        desc = ln.descripcion
        if len(desc) <= 30:
            lineas.append(_lr(f"{cant} {desc}", _money(ln.importe)))
        else:
            # Descripción larga (p. ej. producto especial): en sus propias líneas
            # para que se vea completa, y luego la cantidad × importe.
            for chunk in textwrap.wrap(desc, WIDTH):
                lineas.append(chunk)
            lineas.append(_lr(f"  {cant} x", _money(ln.importe)))
        if Decimal(ln.descuento) > 0:
            lineas.append(_lr("   (desc.)", f"-{_money(ln.descuento)}"))
        # Si la línea se capturó en divisa, mostrar moneda original y tipo de cambio.
        divisa = getattr(ln, "divisa", "MXN") or "MXN"
        if (
            divisa != "MXN"
            and getattr(ln, "precio_divisa", None) is not None
            and getattr(ln, "tipo_cambio", None) is not None
        ):
            lineas.append(
                f"  {divisa} {Decimal(ln.precio_divisa):,.2f} @ "
                f"{Decimal(ln.tipo_cambio):.4f} = {_money(ln.precio_unit)}"
            )
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
        f = _fmt_fecha(fecha_reimpresion or fecha, fecha_formato, tz_offset)
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
    fecha_formato: str = FECHA_FORMATO_DEFAULT,
    tz_offset: int = TZ_OFFSET_DEFAULT,
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
        fecha_formato=fecha_formato,
        tz_offset=tz_offset,
        pagos=pagos,
        reimpresion=reimpresion,
        fecha_reimpresion=fecha_reimpresion,
    )
    return imprimir_texto(texto, settings=settings, printer_factory=printer_factory)


def imprimir_texto(texto, *, settings=None, printer_factory=None) -> PrintResult:
    """Envía texto crudo a la impresora ESC/POS. Tolerante a fallos (AT-9.2)."""
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


def construir_ticket_devolucion(
    dev,
    venta,
    *,
    cajero_nombre: str,
    business_name: str,
    evento: str = "",
    domicilio: str = "",
    telefono: str = "",
    medio: str = "",
    fecha_formato: str = FECHA_FORMATO_DEFAULT,
    tz_offset: int = TZ_OFFSET_DEFAULT,
) -> str:
    """Comprobante de devolución (no es CFDI). Importes en MXN."""
    desc_por_linea = {ln.id: ln.descripcion for ln in venta.lineas}
    lineas: list[str] = []
    lineas.append(_center(business_name.upper()))
    if evento.strip():
        lineas.append(_center(evento.strip()))
    if domicilio.strip():
        lineas.append(_center(domicilio.strip()))
    if telefono.strip():
        lineas.append(_center(f"Tel: {telefono.strip()}"))
    lineas.append(_center("COMPROBANTE DE DEVOLUCIÓN"))
    lineas.append(_center("(no es CFDI)"))
    lineas.append(_sep())
    lineas.append(f"Devolución: {dev.id}")
    lineas.append(f"Venta orig.: {venta.folio}")
    lineas.append(f"Fecha: {_fmt_fecha(dev.creado_en, fecha_formato, tz_offset)}")
    lineas.append(f"Cajero: {cajero_nombre}")
    lineas.append(_sep())
    lineas.append(_lr("CANT DESCRIPCION", "IMPORTE"))
    for dl in dev.lineas:
        desc = desc_por_linea.get(dl.venta_linea_id, "Artículo")
        cant = f"{Decimal(dl.cantidad):g}"
        if len(desc) <= 30:
            lineas.append(_lr(f"{cant} {desc}", _money(dl.importe)))
        else:
            for chunk in textwrap.wrap(desc, WIDTH):
                lineas.append(chunk)
            lineas.append(_lr(f"  {cant} x", _money(dl.importe)))
    lineas.append(_sep())
    lineas.append(_lr("TOTAL DEVUELTO:", _money(dev.monto)))
    if medio:
        lineas.append(_lr("Reembolso:", medio))
    lineas.append(_sep())
    lineas.append(_center("Comprobante de devolución"))
    return "\n".join(lineas)
