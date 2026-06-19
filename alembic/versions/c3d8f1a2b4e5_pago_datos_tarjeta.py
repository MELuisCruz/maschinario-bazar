"""datos de tarjeta en pago (tipo, marca, ultimos 4)

Revision ID: c3d8f1a2b4e5
Revises: 7ede0ca0e2ba
Create Date: 2026-06-19 20:40:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c3d8f1a2b4e5"
down_revision: Union[str, None] = "7ede0ca0e2ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Datos de la tarjeta (de la order aprobada) para mostrar en el ticket.
    op.add_column("pagos", sa.Column("mp_payment_type", sa.Text(), nullable=True))
    op.add_column("pagos", sa.Column("mp_card_brand", sa.Text(), nullable=True))
    op.add_column("pagos", sa.Column("mp_card_last4", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("pagos", "mp_card_last4")
    op.drop_column("pagos", "mp_card_brand")
    op.drop_column("pagos", "mp_payment_type")
