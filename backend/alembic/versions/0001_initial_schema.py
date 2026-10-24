"""initial schema

M0에서 create_tables.py(create_all)로 만들던 두 테이블을 그대로 옮긴 기준점(baseline).

- 빈 DB: `alembic upgrade head`로 테이블이 생긴다
- M0 방식으로 이미 테이블을 만든 DB: 구조가 같으므로 다시 만들지 않고
  `alembic stamp 0001`로 "여기까지 적용됨" 표시만 한 뒤 `alembic upgrade head`

Revision ID: 0001
Revises:
Create Date: 2026-10-24 21:43:14.558668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('bid_announcements',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bid_ntce_no', sa.String(length=40), nullable=False),
    sa.Column('bid_ntce_ord', sa.String(length=3), nullable=False),
    sa.Column('bid_ntce_nm', sa.String(length=1000), nullable=False),
    sa.Column('ntce_instt_nm', sa.String(length=400), nullable=True),
    sa.Column('dminstt_nm', sa.String(length=400), nullable=True),
    sa.Column('cnstrtsite_rgn_nm', sa.String(length=200), nullable=True),
    sa.Column('main_cnstty_nm', sa.String(length=300), nullable=True),
    sa.Column('cntrct_ccncls_mthd_nm', sa.String(length=500), nullable=True),
    sa.Column('bdgt_amt', sa.BigInteger(), nullable=True),
    sa.Column('presmpt_prce', sa.BigInteger(), nullable=True),
    sa.Column('bid_ntce_dt', sa.DateTime(), nullable=True),
    sa.Column('openg_dt', sa.DateTime(), nullable=True),
    sa.Column('fetched_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('bid_ntce_no', 'bid_ntce_ord', name='uq_bid_announcement')
    )
    op.create_index('ix_bid_ntce_dt', 'bid_announcements', ['bid_ntce_dt'], unique=False)
    op.create_index('ix_cnstrtsite_rgn_nm', 'bid_announcements', ['cnstrtsite_rgn_nm'], unique=False)

    op.create_table('bid_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('announcement_id', sa.Integer(), nullable=False),
    sa.Column('bid_ntce_no', sa.String(length=40), nullable=False),
    sa.Column('bid_ntce_ord', sa.String(length=3), nullable=False),
    sa.Column('bidwinnr_nm', sa.String(length=200), nullable=True),
    sa.Column('sucsfbid_amt', sa.BigInteger(), nullable=True),
    sa.Column('sucsfbid_rate', sa.Numeric(precision=6, scale=3), nullable=True),
    sa.Column('prtcpt_cnum', sa.Integer(), nullable=True),
    sa.Column('rl_openg_dt', sa.DateTime(), nullable=True),
    sa.Column('fnl_sucsf_date', sa.Date(), nullable=True),
    sa.Column('fetched_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['announcement_id'], ['bid_announcements.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('announcement_id')
    )


def downgrade() -> None:
    op.drop_table('bid_results')
    op.drop_index('ix_cnstrtsite_rgn_nm', table_name='bid_announcements')
    op.drop_index('ix_bid_ntce_dt', table_name='bid_announcements')
    op.drop_table('bid_announcements')
