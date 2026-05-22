from typing import Optional

from sqlmodel import SQLModel, Field


class Employee(SQLModel, table=True):
    __tablename__ = "employees"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str

    department: str

    employee_number: str = Field(unique=True)