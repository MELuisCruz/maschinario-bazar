"""configuracion ticket editable

Revision ID: af6ea9fa7814
Revises: 9e479b911218
Create Date: 2026-06-18 17:41:52.474584
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "af6ea9fa7814"
down_revision: Union[str, None] = "9e479b911218"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Configuración clave-valor de la app (editable por admin). Los valores por
    # defecto los provee la capa de servicio; aquí solo se crea la tabla.
    op.create_table(
        "configuracion",
        sa.Column("clave", sa.Text(), primary_key=True),
        sa.Column("valor", sa.Text(), nullable=False, server_default=sa.text("''")),
    )


def downgrade() -> None:
    op.drop_table("configuracion")
