"""add fields to FIDO2Credential

Revision ID: c951223c9812
Revises: 7ed3e3c85119
Create Date: 2021-08-04 19:49:24.693057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c951223c9812'
down_revision = '7ed3e3c85119'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fido2credential', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enabled', sa.Boolean(), nullable=True))
    op.execute("UPDATE fido2credential SET enabled = true")
    with op.batch_alter_table('fido2credential', schema=None) as batch_op:
        batch_op.alter_column('enabled', nullable=False)

    with op.batch_alter_table('fido2credential', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE fido2credential SET created_at = NOW()")
    with op.batch_alter_table('fido2credential', schema=None) as batch_op:
        batch_op.alter_column('created_at', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fido2credential', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('enabled')

    # ### end Alembic commands ###
