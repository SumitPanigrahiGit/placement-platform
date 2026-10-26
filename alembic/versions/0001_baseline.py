"""baseline: users, job_postings, applications (the tables create_all used to make)

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(100), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("skills", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_table(
        "job_postings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_name", sa.String(150), nullable=False),
        sa.Column("role_title", sa.String(150), nullable=False),
        sa.Column("required_skills", sa.String(), nullable=True),
        sa.Column("source_url", sa.String(300), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_job_postings_id", "job_postings", ["id"])
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("posting_id", sa.Integer(), sa.ForeignKey("job_postings.id"), nullable=False),
        sa.Column("status", sa.String(50)),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_applications_id", "applications", ["id"])


def downgrade() -> None:
    op.drop_table("applications")
    op.drop_table("job_postings")
    op.drop_table("users")
