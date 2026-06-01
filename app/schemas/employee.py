from typing import Optional

from pydantic import BaseModel, field_validator


class EmployeeCreateRequest(BaseModel):
    name: str
    department: str
    employee_number: str

    @field_validator("name", "department", "employee_number", mode="after")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다")
        return v.strip()


class EmployeeUpdateRequest(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None

    @field_validator("name", "department", mode="after")
    @classmethod
    def not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다")
        return v.strip() if v is not None else v


class EmployeeResponse(BaseModel):
    id: int
    name: str
    department: str
    employee_number: str

    model_config = {"from_attributes": True}
