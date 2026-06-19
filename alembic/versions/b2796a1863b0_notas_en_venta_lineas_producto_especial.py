"""notas en venta_lineas (producto especial)

Revision ID: b2796a1863b0
Revises: 9619c251868b
Create Date: 2026-06-18 20:40:44.751873
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b2796a1863b0"
down_revision: Union[str, None] = "9619c251868b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Notas internas de línea (trazabilidad del "producto especial"). Nullable.
    op.add_column("venta_lineas", sa.Column("notas", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("venta_lineas", "notas")
