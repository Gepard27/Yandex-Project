"""empty message

Revision ID: c3ea68cad0db
Revises: 1b4869c8c0c1
Create Date: 2023-04-30 14:59:57.852619

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3ea68cad0db"
down_revision = "1b4869c8c0c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("expence", sa.Column("name", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("expence", "name")
    # ### end Alembic commands ###
