"""Carga inicial (seed) del POS Maschinario · Bazar.

Crea un cajero administrador inicial y un set de **productos de demostración**.

Los productos demo están MUY claramente identificados para poder distinguirlos
y eliminarlos sin tocar datos reales:
  - `nombre`  con prefijo  «[DEMO] »
  - `sku`     con prefijo  «DEMO-»  (DEMO-0001, DEMO-0002, …)

Uso:
    python -m app.seed                 # crea admin + productos demo (idempotente)
    python -m app.seed --no-demo       # solo el admin
    python -m app.seed --purge-demo    # ELIMINA todos los productos demo (sku DEMO-%)
    SEED_ADMIN_PIN=1234 python -m app.seed   # define el PIN del admin

Corre contra la base apuntada por DATABASE_URL (.env). En producción el esquema
se crea con Alembic (`alembic upgrade head`) antes de sembrar.
"""

from __future__ import annotations

import argparse
import os
from decimal import Decimal

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Cajero, Producto
from app.services import catalogo as cat
from app.services.security import hash_pin

DEMO_NOMBRE_PREFIJO = "[DEMO] "
DEMO_SKU_PREFIJO = "DEMO-"

# (codigo_barras, nombre, precio_con_iva, existencia, iva_tasa)
DEMO_PRODUCTOS = [
    ("7501031311309", "Cuaderno profesional 100 hojas", "32.50", "48", "0.160"),
    ("7501234567890", "Pluma tinta negra", "8.00", "230", "0.160"),
    ("7502211000017", "Lápiz HB no.2", "5.50", "184", "0.160"),
    ("7501045401123", "Pilas AA alcalinas 2 pzas", "38.90", "26", "0.160"),
    ("7501045409877", "Pilas AAA alcalinas 2 pzas", "36.00", "9", "0.160"),
    ("7503007654321", "Foco LED 9W luz cálida", "45.00", "31", "0.160"),
    ("7501008123456", "Cinta adhesiva transparente 18mm", "14.50", "72", "0.160"),
    ("7501008998877", "Cinta canela empaque 48mm", "26.00", "40", "0.160"),
    ("7506306412345", "Vasos desechables 12oz 25pz", "28.00", "53", "0.160"),
    ("7506306498765", "Platos desechables no.10 20pz", "24.50", "0", "0.160"),
    ("7501999000123", "Vela parafina blanca", "6.50", "120", "0.160"),
    ("7501999000444", "Encendedor recargable", "12.00", "64", "0.160"),
    ("7501020304055", "Jabón tocador 150g", "13.50", "88", "0.160"),
    ("7501020309988", "Cloro 950ml", "21.00", "7", "0.160"),
]


def crear_admin(session, usuario: str, nombre: str, pin: str) -> tuple[Cajero, bool]:
    existente = session.scalar(select(Cajero).where(Cajero.usuario == usuario))
    if existente is not None:
        return existente, False
    admin = Cajero(
        usuario=usuario,
        nombre=nombre,
        pin_hash=hash_pin(pin),
        rol="administrador",
        activo=True,
    )
    session.add(admin)
    session.flush()
    return admin, True


def sembrar_demo(session) -> int:
    creados = 0
    for i, (codigo, nombre, precio, existencia, iva) in enumerate(
        DEMO_PRODUCTOS, start=1
    ):
        sku = f"{DEMO_SKU_PREFIJO}{i:04d}"
        ya = session.scalar(
            select(Producto).where(
                (Producto.codigo_barras == codigo) | (Producto.sku == sku)
            )
        )
        if ya is not None:
            continue
        cat.crear_producto(
            session,
            nombre=f"{DEMO_NOMBRE_PREFIJO}{nombre}",
            precio=Decimal(precio),
            codigo_barras=codigo,
            sku=sku,
            iva_tasa=Decimal(iva),
            existencia_inicial=Decimal(existencia),
            controla_stock=True,
        )
        creados += 1
    return creados


def purgar_demo(session) -> int:
    demo = session.scalars(
        select(Producto).where(Producto.sku.like(f"{DEMO_SKU_PREFIJO}%"))
    ).all()
    for p in demo:
        session.delete(p)
    return len(demo)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed del POS Maschinario · Bazar")
    parser.add_argument("--admin-user", default="admin")
    parser.add_argument("--admin-name", default="Administrador")
    parser.add_argument(
        "--no-demo", action="store_true", help="No crear productos demo"
    )
    parser.add_argument(
        "--purge-demo",
        action="store_true",
        help="Eliminar productos demo (sku DEMO-%%)",
    )
    args = parser.parse_args()
    pin = os.environ.get("SEED_ADMIN_PIN", "2468")

    session = SessionLocal()
    try:
        if args.purge_demo:
            n = purgar_demo(session)
            session.commit()
            print(f"🗑️  Productos demo eliminados: {n}")
            return

        admin, creado = crear_admin(session, args.admin_user, args.admin_name, pin)
        demo_creados = 0 if args.no_demo else sembrar_demo(session)
        session.commit()

        print("✅ Seed completado.")
        if creado:
            print(f"   Admin creado: usuario='{admin.usuario}' · PIN='{pin}'")
            print("   ⚠️  Cambia este PIN antes de operar en producción.")
        else:
            print(f"   Admin ya existía: usuario='{admin.usuario}' (sin cambios).")
        if not args.no_demo:
            print(
                f"   Productos demo nuevos: {demo_creados} "
                f"(identificados por nombre '[DEMO] ' y sku 'DEMO-####')."
            )
            print("   Para borrarlos: python -m app.seed --purge-demo")
    finally:
        session.close()


if __name__ == "__main__":
    main()
