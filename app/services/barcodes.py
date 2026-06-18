"""Generación de códigos de barras para el catálogo imprimible.

Los SKU internos del bazar se codifican como **Code128** (admite alfanumérico y
longitud variable), que el lector NETUM lee sin configuración especial. El SVG se
devuelve como *data URI* listo para incrustar en una etiqueta <img> de la hoja
imprimible (vectorial: nítido al imprimir y escanear).

El lookup de venta resuelve por `codigo_barras` **o** `sku` (services/ventas.py),
así que basta con imprimir el SKU para que el escaneo encuentre el producto.
"""

from __future__ import annotations

import base64
from functools import lru_cache
from io import BytesIO

import barcode
from barcode.writer import SVGWriter

# Opciones de render pensadas para impresión en hoja (impresora normal) y lectura
# fiable: barra angosta de 0.4 mm y alto de 12 mm con zona muda y texto legible.
_SVG_OPTIONS = {
    "module_width": 0.4,
    "module_height": 12.0,
    "quiet_zone": 2.5,
    "font_size": 9,
    "text_distance": 3.0,
    "write_text": True,  # imprime el SKU bajo las barras (HRI)
}


@lru_cache(maxsize=2048)
def code128_data_uri(value: str) -> str:
    """Devuelve el Code128 de `value` como data URI de un SVG.

    Cacheado: el mismo SKU produce siempre el mismo SVG, y un catálogo grande
    puede repetir render entre recargas de la hoja.
    """
    buf = BytesIO()
    barcode.get("code128", value, writer=SVGWriter()).write(buf, options=_SVG_OPTIONS)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"
