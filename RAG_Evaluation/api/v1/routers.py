from fastapi import APIRouter
from api.v1.endpoints import evaluate, systems


api_router = APIRouter()

# tags=["users"]: Swagger UI 문서화 시 “users”라는 구분 섹션을 생성
api_router.include_router(evaluate.router, prefix="/evaluate", tags=["evaluate"])
api_router.include_router(systems.router, prefix="/systems", tags=["systems"])
