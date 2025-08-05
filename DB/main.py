# main.py
from fastapi import FastAPI
from .routers import users

app = FastAPI()

# /routers/users.py에서 정의한 라우터 포함
app.include_router(users.router, tags=["users"])

@app.get("/")
def read_root():
    return {"message": "FastAPI 로그인 예제에 오신 것을 환영합니다!"}