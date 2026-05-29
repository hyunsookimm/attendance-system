from datetime import datetime, time

from fastapi import HTTPException
from sqlalchemy.orm import attributes
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.attendance import AttendanceRecord, AttendanceLog
from app.models.employee import Employee
from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType
from app.timezone import KST


class AttendanceService:

    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_today_range(self) -> tuple[datetime, datetime]:
        today = datetime.now(KST).date()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        return start, end

    async def get_today_records(self, employee_id: int):
        start, end = self._get_today_range()
        statement = (
            select(AttendanceRecord)
            .where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.recorded_at >= start,
                AttendanceRecord.recorded_at <= end,
            )
            .order_by(AttendanceRecord.recorded_at)
        )
        result = await self.session.exec(statement)
        return result.all()

    async def get_latest_record(self, employee_id: int):
        start, end = self._get_today_range()
        statement = (
            select(AttendanceRecord)
            .where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.recorded_at >= start,
                AttendanceRecord.recorded_at <= end,
            )
            .order_by(AttendanceRecord.recorded_at.desc())
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
    ):
        record = AttendanceRecord(
            employee_id=employee_id,
            action_type=action_type,
            status=status,
            recorded_at=recorded_at or datetime.now(KST).replace(tzinfo=None),
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def tap(self, employee_id: int):
        employee = await self.session.get(Employee, employee_id)
        if not employee:
            employee = Employee(
                id=employee_id,
                name=f"직원_{employee_id}",
                department="미지정",
                employee_number=str(employee_id),
            )
            self.session.add(employee)
            await self.session.commit()

        latest = await self.get_latest_record(employee_id)

        if latest and latest.status == AttendanceStatus.WORKING:
            return await self._create_record(employee_id, ActionType.EXIT, AttendanceStatus.OUT)

        return await self._create_record(employee_id, ActionType.ENTER, AttendanceStatus.WORKING)

    async def calculate_work_hours(self, employee_id: int):
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
            now = datetime.now(KST).replace(tzinfo=None)
            total_minutes += int((now - pending_enter).total_seconds() / 60)
            is_currently_in = True

        return total_minutes, is_currently_in, records

    async def add_record(self, employee_id: int, action_type: ActionType, recorded_at: datetime):
        status = AttendanceStatus.WORKING if action_type == ActionType.ENTER else AttendanceStatus.OUT
        return await self._create_record(employee_id, action_type, status, recorded_at)

    async def update_record(self, employee_id: int, action_type: ActionType | None, recorded_at: datetime | None):
        record = await self.get_latest_record(employee_id)
        if not record:
            raise HTTPException(status_code=404, detail="출퇴근 기록 없음")

        if action_type is not None and action_type == record.action_type:
            raise HTTPException(status_code=400, detail=f"이미 [{action_type.label}] 상태입니다")

        if recorded_at is not None and recorded_at == record.recorded_at:
            raise HTTPException(status_code=400, detail="변경된 시간이 없습니다")

        before_status = record.status
        before_recorded_at = record.recorded_at

        if action_type is not None:
            record.action_type = action_type
            record.status = AttendanceStatus.WORKING if action_type == ActionType.ENTER else AttendanceStatus.OUT
            attributes.flag_modified(record, "action_type")
            attributes.flag_modified(record, "status")

        if recorded_at is not None:
            record.recorded_at = recorded_at
            attributes.flag_modified(record, "recorded_at")

        log = AttendanceLog(
            attendance_id=record.id,
            before_status=before_status,
            after_status=record.status,
            before_recorded_at=before_recorded_at,
            after_recorded_at=record.recorded_at,
        )

        self.session.add(record)
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def delete_record(self, employee_id: int):
        record = await self.get_latest_record(employee_id)
        if not record:
            raise HTTPException(status_code=404, detail="출퇴근 기록 없음")
        await self.session.delete(record)
        await self.session.commit()
