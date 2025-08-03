"""add mcp tables

Revision ID: 20250801182305
Revises: d31026856c01
Create Date: 2025-08-01 18:23:05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite, postgresql

# revision identifiers, used by Alembic.
revision: str = '20250801182305'
down_revision: Union[str, None] = 'd31026856c01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create MCP tables for Model Context Protocol support"""
    
    # Create mcp_servers table
    op.create_table(
        'mcp_servers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('transport_type', sa.String(), nullable=False),
        sa.Column('command', sa.Text(), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('args', sa.JSON(), nullable=True),
        sa.Column('env', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on user_id for better query performance
    op.create_index(
        'ix_mcp_servers_user_id',
        'mcp_servers',
        ['user_id'],
        unique=False
    )
    
    # Create mcp_tools table
    op.create_table(
        'mcp_tools',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('server_id', sa.String(), nullable=False),
        sa.Column('tool_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['server_id'], ['mcp_servers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on server_id for better query performance
    op.create_index(
        'ix_mcp_tools_server_id',
        'mcp_tools',
        ['server_id'],
        unique=False
    )


def downgrade() -> None:
    """Drop MCP tables"""
    
    # Drop indexes
    op.drop_index('ix_mcp_tools_server_id', table_name='mcp_tools')
    op.drop_index('ix_mcp_servers_user_id', table_name='mcp_servers')
    
    # Drop tables
    op.drop_table('mcp_tools')
    op.drop_table('mcp_servers')