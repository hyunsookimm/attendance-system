from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.database import engine
from app.models.employee import Employee
from app.models.attendance import AttendanceRecord


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield 


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "attendance system"}