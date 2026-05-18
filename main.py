from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "출퇴근 시스템"}
