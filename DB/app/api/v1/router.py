
from fastapi import APIRouter
from app.api.v1.endpoints import insert, read

api_router = APIRouter()

api_router.include_router(insert.router, prefix="/insert", tags=["insert"])
api_router.include_router(read.router, prefix="/read", tags=["read"])