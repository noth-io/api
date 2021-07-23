"""Initial migration

Revision ID: 75b5158dc721
Revises: 
Create Date: 2021-07-23 20:34:45.468302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75b5158dc721'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('firstname', sa.String(), nullable=False),
    sa.Column('lastname', sa.String(), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('fido2credential',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('attestation', sa.LargeBinary(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('attestation')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fido2credential')
    op.drop_table('user')
    # ### end Alembic commands ###
