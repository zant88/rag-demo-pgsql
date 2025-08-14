"""
Add knowledge_entry_id to chunk table, make document_id nullable
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250729addknowledgechunk'
down_revision = 'b9f2082f2f20'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('chunks', sa.Column('knowledge_entry_id', sa.Integer(), nullable=True))
    op.alter_column('chunks', 'document_id', existing_type=sa.Integer(), nullable=True)
    op.create_foreign_key('fk_chunks_knowledge_entry_id', 'chunks', 'knowledge_entries', ['knowledge_entry_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_chunks_knowledge_entry_id', 'chunks', type_='foreignkey')
    op.drop_column('chunks', 'knowledge_entry_id')
    op.alter_column('chunks', 'document_id', existing_type=sa.Integer(), nullable=False)
