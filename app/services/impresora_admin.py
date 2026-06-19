"""Estado y re-conexión de la impresora USB desde Configuración (solo admin).

La impresora llega a WSL por usbipd (puente USB de Windows). A veces el attach
queda colgado contra una instancia de WSL vieja o un monitor de auto-attach
duplicado, y la app no puede abrirla. Aquí se ofrece un "Reconectar" que: mata
auto-attach colgados, hace detach+attach del busid de la impresora y reverifica.

Las herramientas son de Windows y se invocan por interop (rutas completas).
"""

from __future__ import annotations

import logging
import subprocess
import time

from app.config import get_settings
from app.services import printing

log = logging.getLogger("pos.impresora")

USBIPD = "/mnt/c/Program Files/usbipd-win/usbipd.exe"
POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

# Mata SOLO los monitores de auto-attach colgados (por línea de comando); no toca
# el servicio de usbipd.
_KILL_AUTOATTACH = (
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'usbipd.exe' "
    "-and $_.CommandLine -like '*auto-attach*' } | ForEach-Object "
    "{ Stop-Process -Id $_.ProcessId -Force }"
)


def estado(settings=None) -> dict:
    """¿La impresora está disponible? Intenta abrirla por USB (sin imprimir)."""
    settings = settings or get_settings()
    if not settings.printer_usb_vendor or not settings.printer_usb_product:
        return {"online": False, "mensaje": "Impresora no configurada (PRINTER_USB_*)."}
    try:
        printer = printing.get_printer(settings)
        cerrar = getattr(printer, "close", None)
        if callable(cerrar):
            cerrar()
        return {"online": True, "mensaje": "Impresora disponible."}
    except Exception as exc:  # device no encontrado / ocupado / permisos
        log.info("Impresora no disponible: %s", exc)
        return {
            "online": False,
            "mensaje": "No disponible. Pulsa «Reconectar».",
        }


def _vendor_product() -> str:
    s = get_settings()
    v = (s.printer_usb_vendor or "").lower().replace("0x", "").zfill(4)
    p = (s.printer_usb_product or "").lower().replace("0x", "").zfill(4)
    return f"{v}:{p}"


def _busid() -> str | None:
    """Busca el busid de la impresora en `usbipd list` por vendor:product."""
    vp = _vendor_product()
    out = subprocess.run(
        [USBIPD, "list"], capture_output=True, text=True, timeout=20
    ).stdout
    for line in out.splitlines():
        if vp and vp in line.lower():
            return line.split()[0]
    return None


def reconectar() -> dict:
    """Reset del puente USB de la impresora y reverificación de estado."""
    try:
        subprocess.run(
            [POWERSHELL, "-NoProfile", "-Command", _KILL_AUTOATTACH],
            capture_output=True,
            text=True,
            timeout=25,
        )
        busid = _busid()
        if not busid:
            return {
                "online": False,
                "mensaje": "No se encontró la impresora en usbipd "
                "(revisa cable/encendido).",
            }
        subprocess.run(
            [USBIPD, "detach", "--busid", busid],
            capture_output=True,
            text=True,
            timeout=25,
        )
        time.sleep(2)
        subprocess.run(
            [USBIPD, "attach", "--wsl", "--busid", busid],
            capture_output=True,
            text=True,
            timeout=30,
        )
        time.sleep(3)
    except (subprocess.SubprocessError, OSError) as exc:
        log.warning("Re-attach de impresora falló: %s", exc)
        return {"online": False, "mensaje": "No se pudo reconectar la impresora."}
    return estado()
