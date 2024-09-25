"""create tracking tables

Revision ID: a3d8a1e6a447
Revises:
Create Date: 2024-09-14 21:52:46.606892

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a3d8a1e6a447"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "days",
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("updated", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="day_uix_email_date"),
    )
    op.create_index(op.f("ix_days_date"), "days", ["date"], unique=False)
    op.create_index(op.f("ix_days_id"), "days", ["id"], unique=False)
    op.create_table(
        "sleeps",
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column(
            "quality",
            sa.Enum("BAD", "MODERATE", "GOOD", name="sleepquality"),
            nullable=False,
        ),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("updated", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="sleep_uix_email_date"),
    )
    op.create_index(op.f("ix_sleeps_date"), "sleeps", ["date"], unique=False)
    op.create_index(op.f("ix_sleeps_id"), "sleeps", ["id"], unique=False)
    op.create_table(
        "symptoms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_symptoms_id"), "symptoms", ["id"], unique=False)
    op.create_table(
        "triggers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "FOOD",
                "ENVIRONMENT",
                "LIFESTYLE",
                "EMOTION",
                "OTHER",
                name="triggercategory",
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_triggers_id"), "triggers", ["id"], unique=False)
    op.create_table(
        "afternoon_symptom_association",
        sa.Column("day_id", sa.Integer(), nullable=True),
        sa.Column("symptom_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["day_id"], ["days.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["symptom_id"],
            ["symptoms.id"],
        ),
    )
    op.create_table(
        "day_trigger_association",
        sa.Column("day_id", sa.Integer(), nullable=True),
        sa.Column("trigger_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["day_id"], ["days.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["trigger_id"],
            ["triggers.id"],
        ),
    )
    op.create_table(
        "late_morning_symptom_association",
        sa.Column("day_id", sa.Integer(), nullable=True),
        sa.Column("symptom_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["day_id"], ["days.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["symptom_id"],
            ["symptoms.id"],
        ),
    )
    op.create_table(
        "sleep_symptom_association",
        sa.Column("sleep_id", sa.Integer(), nullable=True),
        sa.Column("symptom_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["sleep_id"], ["sleeps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["symptom_id"],
            ["symptoms.id"],
        ),
    )
    try:
        op.execute("INSERT INTO symptoms (name) VALUES ('Pain')")
        op.execute("INSERT INTO symptoms (name) VALUES ('Squibble')")
        op.execute("INSERT INTO symptoms (name) VALUES ('Headache')")
        op.execute("INSERT INTO symptoms (name) VALUES ('Nausea')")

        op.execute("INSERT INTO triggers (name, category) VALUES ('sugar', 'FOOD')")
        op.execute("INSERT INTO triggers (name, category) VALUES ('nikotin', 'FOOD')")
        op.execute(
            "INSERT INTO triggers (name, category) VALUES ('sport', 'LIFESTYLE')"
        )
    except Exception as e:
        print("Error inserting data", e)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sleep_symptom_association")
    op.drop_table("late_morning_symptom_association")
    op.drop_table("day_trigger_association")
    op.drop_table("afternoon_symptom_association")
    op.drop_index(op.f("ix_triggers_id"), table_name="triggers")
    op.drop_table("triggers")
    op.drop_index(op.f("ix_symptoms_id"), table_name="symptoms")
    op.drop_table("symptoms")
    op.drop_index(op.f("ix_sleeps_id"), table_name="sleeps")
    op.drop_index(op.f("ix_sleeps_date"), table_name="sleeps")
    op.drop_table("sleeps")
    op.drop_index(op.f("ix_days_id"), table_name="days")
    op.drop_index(op.f("ix_days_date"), table_name="days")
    op.drop_table("days")
    # ### end Alembic commands ###
