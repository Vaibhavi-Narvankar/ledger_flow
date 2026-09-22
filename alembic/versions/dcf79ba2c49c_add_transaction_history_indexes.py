"""add transaction history indexes

Revision ID: dcf79ba2c49c
Revises: 5d19aa54b82d
Create Date: 2026-09-22
"""

from typing import Sequence, Union

from alembic import op


revision: str = "dcf79ba2c49c"
down_revision: Union[str, Sequence[str], None] = "5d19aa54b82d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_transactions_sender_wallet_created_at",
        "transactions",
        ["sender_wallet_id", "created_at"],
    )

    op.create_index(
        "ix_transactions_receiver_wallet_created_at",
        "transactions",
        ["receiver_wallet_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transactions_receiver_wallet_created_at",
        table_name="transactions",
    )

    op.drop_index(
        "ix_transactions_sender_wallet_created_at",
        table_name="transactions",
    )