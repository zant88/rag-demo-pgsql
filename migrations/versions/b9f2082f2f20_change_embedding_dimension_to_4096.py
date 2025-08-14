"""Change embedding dimension to 4096

Revision ID: b9f2082f2f20
Revises: da0d605f5f35
Create Date: 2025-07-28 23:23:37.297430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'b9f2082f2f20'
down_revision: Union[str, Sequence[str], None] = 'da0d605f5f35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('chunks', 'embedding',
               type_=Vector(1536),
               existing_type=Vector(4096),
               existing_nullable=True)

def downgrade():
    op.alter_column('chunks', 'embedding',
               type_=Vector(4096),
               existing_type=Vector(1536),
               existing_nullable=True)
