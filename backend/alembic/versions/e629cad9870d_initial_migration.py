"""Initial migration

Revision ID: e629cad9870d
Revises:
Create Date: 2026-03-05 02:56:55.228754

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e629cad9870d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    dialect_name = conn.engine.dialect.name

    if dialect_name == "postgresql":
        timestamp_type = sa.TIMESTAMP(timezone=True)
        json_type = JSONB
    else:
        timestamp_type = sa.String()
        json_type = sa.Text()

    # Create trades table
    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", timestamp_type, nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("side", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("expected_price", sa.Float(), nullable=True),
        sa.Column("slippage", sa.Float(), nullable=True),
        sa.Column("size", sa.Float(), nullable=False),
        sa.Column("notional", sa.Float(), nullable=False),
        sa.Column("fee", sa.Float(), nullable=True),
        sa.Column("fee_currency", sa.String(), nullable=True),
        sa.Column("pnl", sa.Float(), nullable=True),
        sa.Column("pnl_pct", sa.Float(), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("stop_loss", sa.Float(), nullable=True),
        sa.Column("take_profit", sa.Float(), nullable=True),
    )
    op.create_index("idx_trades_timestamp", "trades", ["timestamp"])
    op.create_index("idx_trades_symbol", "trades", ["symbol"])

    # Create daily_summary table
    if dialect_name == "postgresql":
        date_type = sa.Date()
    else:
        date_type = sa.String()

    op.create_table(
        "daily_summary",
        sa.Column("date", date_type, primary_key=True),
        sa.Column("starting_balance", sa.Float(), nullable=False),
        sa.Column("ending_balance", sa.Float(), nullable=False),
        sa.Column("pnl", sa.Float(), nullable=False),
        sa.Column("pnl_pct", sa.Float(), nullable=False),
        sa.Column("trades_count", sa.Integer(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column("losses", sa.Integer(), nullable=False),
    )

    # Create equity_snapshots table
    op.create_table(
        "equity_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", timestamp_type, nullable=False),
        sa.Column("balance", sa.Float(), nullable=False),
    )
    op.create_index("idx_equity_timestamp", "equity_snapshots", ["timestamp"])

    # Create signals_log table
    op.create_table(
        "signals_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", timestamp_type, nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("signal", sa.String(), nullable=False),
        sa.Column("regime", sa.String(), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("indicators", json_type, nullable=True),
    )
    op.create_index("idx_signals_timestamp", "signals_log", ["timestamp"])

    # Create funding_payments table
    op.create_table(
        "funding_payments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", timestamp_type, nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("payment", sa.Float(), nullable=False),
        sa.Column("position_size", sa.Float(), nullable=False),
    )
    op.create_index("idx_funding_timestamp", "funding_payments", ["timestamp"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("funding_payments")
    op.drop_table("signals_log")
    op.drop_table("equity_snapshots")
    op.drop_table("daily_summary")
    op.drop_table("trades")
