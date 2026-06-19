"""divisa por linea de venta + tipo de cambio

Revision ID: 7ede0ca0e2ba
Revises: b2796a1863b0
Create Date: 2026-06-18 21:21:22.136165
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7ede0ca0e2ba"
down_revision: Union[str, None] = "b2796a1863b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Divisa por línea: precio capturado en MXN/USD/EUR; el total siempre en MXN.
    # `precio_unit` sigue siendo el valor en MXN (snapshot) usado para totales.
    op.add_column(
        "venta_lineas",
        sa.Column("divisa", sa.Text(), nullable=False, server_default=sa.text("'MXN'")),
    )
    op.add_column(
        "venta_lineas", sa.Column("precio_divisa", sa.Numeric(12, 2), nullable=True)
    )
    op.add_column(
        "venta_lineas", sa.Column("tipo_cambio", sa.Numeric(14, 6), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("venta_lineas", "tipo_cambio")
    op.drop_column("venta_lineas", "precio_divisa")
    op.drop_column("venta_lineas", "divisa")
