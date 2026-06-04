import logging
from datetime import datetime, time, timezone
from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy.orm import attributes
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.attendance import AttendanceRecord, AttendanceLog
from app.models.employee import Employee
from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType
from app.timezone import KST

logger = logging.getLogger("app.service")


class AttendanceService:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _get_today_range(self) -> tuple[datetime, datetime]:
        today = datetime.now(KST).date()
        start_kst = datetime.combine(today, time.min).replace(tzinfo=KST)
        end_kst = datetime.combine(today, time.max).replace(tzinfo=KST)
        start_utc = start_kst.astimezone(timezone.utc).replace(tzinfo=None)
        end_utc = end_kst.astimezone(timezone.utc).replace(tzinfo=None)
        return start_utc, end_utc

    def _to_utc_naive(self, dt: datetime) -> datetime:
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt.replace(tzinfo=KST).astimezone(timezone.utc).replace(tzinfo=None)

    async def get_today_records(self, employee_id: int) -> Sequence[AttendanceRecord]:
        start, end = self._get_today_range()
        statement = (
            select(AttendanceRecord)
            .where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.recorded_at >= start,
                AttendanceRecord.recorded_at <= end,
            )
            .order_by(AttendanceRecord.recorded_at)  # type: ignore[arg-type]
        )
        result = await self.session.exec(statement)
        return result.all()

    async def get_latest_today_record(self, employee_id: int) -> AttendanceRecord | None:
        # 오늘 기록 중 가장 최근
        start, end = self._get_today_range()
        statement = (
            select(AttendanceRecord)
            .where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.recorded_at >= start,
                AttendanceRecord.recorded_at <= end,
            )
            .order_by(AttendanceRecord.recorded_at.desc())  # type: ignore[attr-defined]
            .limit(1)
        )
        result = await self.session.exec(statement)
        return result.first()

    async def get_latest_record(self, employee_id: int) -> AttendanceRecord | None:
        # 가장 최근 기록 (관리자 수정/삭제용)
        statement = (
            select(AttendanceRecord)
            .where(AttendanceRecord.employee_id == employee_id)
            .order_by(AttendanceRecord.recorded_at.desc())  # type: ignore[attr-defined]
            .limit(1)
        )
        result = await self.session.exec(statement)
        return result.first()

    async def _create_record(
        self,
        employee_id: int,
        action_type: ActionType,
        status: AttendanceStatus,
        recorded_at: datetime | None = None,
    ) -> AttendanceRecord:
        if recorded_at is None:
            stored_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            stored_at = self._to_utc_naive(recorded_at)

        record = AttendanceRecord(
            employee_id=employee_id,
            action_type=action_type,
            status=status,
            recorded_at=stored_at,
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def tap(self, employee_id: int) -> AttendanceRecord:
        employee = await self.session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="등록되지 않은 직원입니다")

        latest = await self.get_latest_today_record(employee_id)

        if latest and latest.status == AttendanceStatus.WORKING:
            record = await self._create_record(employee_id, ActionType.EXIT, AttendanceStatus.OUT)
            logger.info("퇴근 tap: employee_id=%d, recorded_at=%s", employee_id, record.recorded_at)
            return record

        record = await self._create_record(employee_id, ActionType.ENTER, AttendanceStatus.WORKING)
        logger.info("출근 tap: employee_id=%d, recorded_at=%s", employee_id, record.recorded_at)
        return record

    async def calculate_work_hours(self, employee_id: int) -> tuple[int, bool, Sequence[AttendanceRecord]]:
        records = await self.get_today_records(employee_id)
        total_minutes = 0
        is_currently_in = False
        pending_enter: datetime | None = None

        for record in records:
            if record.status == AttendanceStatus.WORKING:
                pending_enter = record.recorded_at
            elif record.status == AttendanceStatus.OUT and pending_enter:
                total_minutes += int((record.recorded_at - pending_enter).total_seconds() / 60)
                pending_enter = None

        if pending_enter:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            total_minutes += int((now - pending_enter).total_seconds() / 60)
            is_currently_in = True

        return total_minutes, is_currently_in, records

    async def add_record(self, employee_id: int, action_type: ActionType, recorded_at: datetime) -> AttendanceRecord:
        status = AttendanceStatus.WORKING if action_type == ActionType.ENTER else AttendanceStatus.OUT
        record = await self._create_record(employee_id, action_type, status, recorded_at)
        logger.info("기록 추가: employee_id=%d, action=%s, recorded_at=%s", employee_id, action_type.value, record.recorded_at)
        return record

    async def update_record(self, employee_id: int, action_type: ActionType | None, recorded_at: datetime | None) -> AttendanceRecord:
        if action_type is None and recorded_at is None:
            raise HTTPException(status_code=400, detail="변경할 내용이 없습니다")

        record = await self.get_latest_record(employee_id)
        if not record:
            raise HTTPException(status_code=404, detail="출퇴근 기록 없음")

        if action_type is not None and action_type == record.action_type:
            raise HTTPException(status_code=400, detail=f"이미 [{action_type.label}] 상태입니다")

        stored_recorded_at = None
        if recorded_at is not None:
            stored_recorded_at = self._to_utc_naive(recorded_at)
            if stored_recorded_at == record.recorded_at:
                raise HTTPException(status_code=400, detail="변경된 시간이 없습니다")

        before_action_type = record.action_type
        before_status = record.status
        before_recorded_at = record.recorded_at

        if action_type is not None:
            record.action_type = action_type
            record.status = AttendanceStatus.WORKING if action_type == ActionType.ENTER else AttendanceStatus.OUT
            attributes.flag_modified(record, "action_type")
            attributes.flag_modified(record, "status")

        if stored_recorded_at is not None:
            record.recorded_at = stored_recorded_at
            attributes.flag_modified(record, "recorded_at")

        log = AttendanceLog(
            attendance_id=record.id,
            before_action_type=before_action_type,
            after_action_type=record.action_type,
            before_status=before_status,
            after_status=record.status,
            before_recorded_at=before_recorded_at,
            after_recorded_at=record.recorded_at,
        )

        self.session.add(record)
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(record)
        logger.info(
            "기록 수정: employee_id=%d, action=%s→%s, recorded_at=%s→%s",
            employee_id,
            before_action_type.value, record.action_type.value,
            before_recorded_at, record.recorded_at,
        )
        return record

    async def delete_record(self, employee_id: int) -> None:
        record = await self.get_latest_record(employee_id)
        if not record:
            raise HTTPException(status_code=404, detail="출퇴근 기록 없음")
        await self.session.delete(record)
        await self.session.commit()
        logger.info("기록 삭제: employee_id=%d, record_id=%s", employee_id, record.id)
