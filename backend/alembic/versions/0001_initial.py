"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# create_type=False: we create these types explicitly (once) in upgrade()
# below, since each is reused across multiple tables' columns and letting
# create_table() auto-create them would try to CREATE TYPE a second time.
ats_type = postgresql.ENUM("greenhouse", "lever", "workday", "other", name="ats_type", create_type=False)
job_level = postgresql.ENUM(
    "intern", "junior", "mid", "senior", "staff", "unknown", name="job_level", create_type=False
)
degree_requirement = postgresql.ENUM(
    "none", "bachelor", "master", "phd", name="degree_requirement", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    ats_type.create(bind, checkfirst=True)
    job_level.create(bind, checkfirst=True)
    degree_requirement.create(bind, checkfirst=True)

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("ats_type", ats_type, nullable=False, server_default="other"),
        sa.Column("careers_url", sa.String(1024), nullable=True),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("level", job_level, nullable=False, server_default="unknown"),
        sa.Column("min_years_experience", sa.Integer, nullable=True),
        sa.Column("degree_requirement", degree_requirement, nullable=False, server_default="none"),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("company_id", "external_id", name="uq_job_company_external_id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title_keyword", sa.String(255), nullable=True),
        sa.Column("level", job_level, nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("min_years", sa.Integer, nullable=True),
        sa.Column("degree", degree_requirement, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("users")
    op.drop_table("jobs")
    op.drop_table("companies")

    bind = op.get_bind()
    degree_requirement.drop(bind, checkfirst=True)
    job_level.drop(bind, checkfirst=True)
    ats_type.drop(bind, checkfirst=True)
