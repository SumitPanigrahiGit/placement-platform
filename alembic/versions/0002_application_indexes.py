"""index the foreign keys on applications

PostgreSQL does not index foreign keys automatically. GET /applications/me filters by
user_id, so without this index it scans the whole table as it grows.

Revision ID: 0002
Revises: 0001
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_posting_id", "applications", ["posting_id"])


def downgrade() -> None:
    op.drop_index("ix_applications_posting_id", table_name="applications")
    op.drop_index("ix_applications_user_id", table_name="applications")
