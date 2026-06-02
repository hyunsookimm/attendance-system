import logging
from collections.abc import Sequence

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee
from app.models.attendance import AttendanceRecord

logger = logging.getLogger("app.service")


class EmployeeService:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> Sequence[Employee]:
        result = await self.session.exec(select(Employee).order_by(Employee.id))  # type: ignore[arg-type]
        return result.all()

    async def get_by_id(self, employee_id: int) -> Employee:
        employee = await self.session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="직원 없음")
        return employee

    async def _next_employee_number(self) -> str:
        result = await self.session.exec(select(Employee.employee_number))
        used = set()
        for num in result.all():
            if num.isdigit():
                used.add(int(num))
        n = 1
        while n in used:
            n += 1
        return str(n)

    async def create(self, name: str, department: str, employee_number: str | None) -> Employee:
        if employee_number is None:
            employee_number = await self._next_employee_number()
        else:
            existing = await self.session.exec(
                select(Employee).where(Employee.employee_number == employee_number)
            )
            if existing.first():
                raise HTTPException(status_code=409, detail=f"사번 [{employee_number}] 이미 존재합니다")

        employee = Employee(name=name, department=department, employee_number=employee_number)
        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        logger.info("직원 등록: id=%d, name=%s, employee_number=%s", employee.id, name, employee_number)
        return employee

    async def update(self, employee_id: int, name: str | None, department: str | None, employee_number: str | None) -> Employee:
        if name is None and department is None and employee_number is None:
            raise HTTPException(status_code=400, detail="변경할 내용이 없습니다")

        employee = await self.get_by_id(employee_id)

        if name is not None:
            employee.name = name
        if department is not None:
            employee.department = department
        if employee_number is not None:
            existing = await self.session.exec(
                select(Employee).where(Employee.employee_number == employee_number)
            )
            if existing.first():
                raise HTTPException(status_code=409, detail=f"사번 [{employee_number}] 이미 존재합니다")
            employee.employee_number = employee_number

        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        logger.info("직원 수정: id=%d", employee_id)
        return employee

    async def delete(self, employee_id: int) -> None:
        employee = await self.get_by_id(employee_id)

        has_records = await self.session.exec(
            select(AttendanceRecord).where(AttendanceRecord.employee_id == employee_id).limit(1)
        )
        if has_records.first():
            raise HTTPException(status_code=409, detail="출퇴근 기록이 있는 직원은 삭제할 수 없습니다")

        await self.session.delete(employee)
        await self.session.commit()
        logger.info("직원 삭제: id=%d, name=%s", employee_id, employee.name)
