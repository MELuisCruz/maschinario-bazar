"""existencia no negativa (check)

Revision ID: 9619c251868b
Revises: af6ea9fa7814
Create Date: 2026-06-18 19:07:25.376019
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9619c251868b"
down_revision: Union[str, None] = "af6ea9fa7814"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Garantiza que la existencia nunca sea negativa (refuerza el bloqueo de
    # sobreventa en la capa de aplicación). Requiere datos ya saneados (>= 0).
    op.create_check_constraint(
        "ck_productos_existencia_no_negativa",
        "productos",
        "existencia >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_productos_existencia_no_negativa", "productos", type_="check"
    )
