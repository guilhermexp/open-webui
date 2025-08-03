"""Add note folders support

Revision ID: 20250802223804
Revises: 20250801182305
Create Date: 2025-08-02 22:38:04

"""
from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision = '20250802223804'
down_revision = '20250801182305'
branch_labels = None
depends_on = None


def upgrade():
    # Create note_folder table
    op.create_table(
        'note_folder',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('parent_id', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('items', sa.JSON(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('is_expanded', sa.Boolean(), default=False),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
    )
    
    # Add folder_id column to note table
    op.add_column('note', sa.Column('folder_id', sa.Text(), nullable=True))
    
    # Create index on folder_id for better query performance
    op.create_index('idx_note_folder_id', 'note', ['folder_id'])
    
    # Create index on note_folder for better query performance
    op.create_index('idx_note_folder_user_id', 'note_folder', ['user_id'])
    op.create_index('idx_note_folder_parent_id', 'note_folder', ['parent_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_note_folder_parent_id', 'note_folder')
    op.drop_index('idx_note_folder_user_id', 'note_folder')
    op.drop_index('idx_note_folder_id', 'note')
    
    # Remove folder_id column from note table
    op.drop_column('note', 'folder_id')
    
    # Drop note_folder table
    op.drop_table('note_folder')