from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import AsyncMongoClient
import uuid
from app.db.database import get_database
from app.models.user_model import UserCreate, UserResponse
from app.services import user_service
from starlette.responses import JSONResponse

router = APIRouter()

@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, db: AsyncMongoClient = Depends(get_database)):
    created_user = await user_service.create_user(db, user)
    return UserResponse(id=str(created_user.id), **created_user.model_dump())

@router.get("/users/{name}", status_code=status.HTTP_200_OK)
async def query_user(name: str, db: AsyncMongoClient = Depends(get_database)):
    return JSONResponse(
        {
            'id': str(uuid.uuid4()),
            'name': name
        }
    )