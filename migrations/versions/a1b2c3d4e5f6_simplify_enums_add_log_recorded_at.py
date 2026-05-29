"""simplify action_type and status enums, add log recorded_at fields

Revision ID: a1b2c3d4e5f6
Revises: db721b60340a
Create Date: 2026-05-29

"""
from typing import Union, Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'db721b60340a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 컬럼을 VARCHAR로 먼저 풀기 (ENUM은 정의된 값 외 UPDATE 불가)
    op.alter_column('attendance_records', 'action_type',
        existing_type=mysql.ENUM('CHECK_IN', 'OUTING', 'RETURN', 'LUNCH', 'EARLY_LEAVE', 'CHECK_OUT'),
        type_=sa.String(20), existing_nullable=False)
    op.alter_column('attendance_records', 'status',
        existing_type=mysql.ENUM('WORKING', 'OUTING', 'LUNCH', 'EARLY_LEAVE', 'OFF_WORK'),
        type_=sa.String(20), existing_nullable=False)
    op.alter_column('attendance_logs', 'before_status',
        existing_type=mysql.ENUM('WORKING', 'OUTING', 'LUNCH', 'EARLY_LEAVE', 'OFF_WORK'),
        type_=sa.String(20), existing_nullable=False)
    op.alter_column('attendance_logs', 'after_status',
        existing_type=mysql.ENUM('WORKING', 'OUTING', 'LUNCH', 'EARLY_LEAVE', 'OFF_WORK'),
        type_=sa.String(20), existing_nullable=False)

    # 2. 데이터 값 변환
    op.execute("UPDATE attendance_records SET action_type = 'ENTER' WHERE action_type = 'CHECK_IN'")
    op.execute("UPDATE attendance_records SET action_type = 'EXIT' WHERE action_type IN ('CHECK_OUT', 'OUTING', 'RETURN', 'LUNCH', 'EARLY_LEAVE')")
    op.execute("UPDATE attendance_records SET status = 'WORKING' WHERE status IN ('OUTING', 'LUNCH', 'EARLY_LEAVE')")
    op.execute("UPDATE attendance_records SET status = 'OUT' WHERE status = 'OFF_WORK'")
    op.execute("UPDATE attendance_logs SET before_status = 'WORKING' WHERE before_status IN ('OUTING', 'LUNCH', 'EARLY_LEAVE')")
    op.execute("UPDATE attendance_logs SET before_status = 'OUT' WHERE before_status = 'OFF_WORK'")
    op.execute("UPDATE attendance_logs SET after_status = 'WORKING' WHERE after_status IN ('OUTING', 'LUNCH', 'EARLY_LEAVE')")
    op.execute("UPDATE attendance_logs SET after_status = 'OUT' WHERE after_status = 'OFF_WORK'")

    # 3. 최종 ENUM 타입으로 변경
    op.alter_column('attendance_records', 'action_type',
        existing_type=sa.String(20),
        type_=sa.Enum('ENTER', 'EXIT', name='actiontype'), existing_nullable=False)
    op.alter_column('attendance_records', 'status',
        existing_type=sa.String(20),
        type_=sa.Enum('WORKING', 'OUT', name='attendancestatus'), existing_nullable=False)
    op.alter_column('attendance_logs', 'before_status',
        existing_type=sa.String(20),
        type_=sa.Enum('WORKING', 'OUT', name='attendancestatus'), existing_nullable=False)
    op.alter_column('attendance_logs', 'after_status',
        existing_type=sa.String(20),
        type_=sa.Enum('WORKING', 'OUT', name='attendancestatus'), existing_nullable=False)

    # 4. attendance_logs: before/after_recorded_at 컬럼 추가
    op.add_column('attendance_logs', sa.Column('before_recorded_at', sa.DateTime(), nullable=True))
    op.add_column('attendance_logs', sa.Column('after_recorded_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('attendance_logs', 'after_recorded_at')
    op.drop_column('attendance_logs', 'before_recorded_at')

    op.alter_column(
        'attendance_logs', 'after_status',
        existing_type=sa.Enum('WORKING', 'OUT', name='attendancestatus'),
        type_=mysql.ENUM('WORKING', 'OUTING', 'LUNCH', 'EARLY_LEAVE', 'OFF_WORK'),
        existing_nullable=False,
    )
    op.alter_column(
        'attendance_logs', 'before_status',
        existing_type=sa.Enum('WORKING', 'OUT', name='attendancestatus'),
        type_=mysql.ENUM('WORKING', 'OUTING', 'LUNCH', 'EARLY_LEAVE', 'OFF_WORK'),
        existing_nullable=False,
    )
    op.alter_column(
        'attendance_records', 'status',
        existing_type=sa.Enum('WORKING', 'OUT', name='attendancestatus'),
        type_=mysql.ENUM('WORKING', 'OUTING', 'LUNCH', 'EARLY_LEAVE', 'OFF_WORK'),
        existing_nullable=False,
    )
    op.alter_column(
        'attendance_records', 'action_type',
        existing_type=sa.Enum('ENTER', 'EXIT', name='actiontype'),
        type_=mysql.ENUM('CHECK_IN', 'OUTING', 'RETURN', 'LUNCH', 'EARLY_LEAVE', 'CHECK_OUT'),
        existing_nullable=False,
    )
