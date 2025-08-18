from fastapi import Depends, FastAPI, HTTPException
from .services import crud
from . import schemas
from .database.database import db
from pydantic_mongo import PydanticObjectId

app = FastAPI()


# Dependency
def get_db():
    return db


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate):
    db_user = crud.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(user=user)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: PydanticObjectId):
    db_user = crud.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.patch("/users/{user_id}/role", response_model=schemas.User)
def update_user_role(user_id: PydanticObjectId, role_update: schemas.UserRoleUpdate):
    db_user = crud.update_user_role(user_id=user_id, role=role_update.role)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/sessions/", response_model=schemas.Session)
def create_session(session: schemas.SessionCreate):
    return crud.create_session(session=session)


@app.get("/sessions/{session_id}", response_model=schemas.Session)
def read_session(session_id: PydanticObjectId):
    db_session = crud.get_session(session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@app.get("/sessions/", response_model=list[schemas.Session])
def read_sessions(skip: int = 0, limit: int = 100):
    sessions = crud.get_sessions(skip=skip, limit=limit)
    return sessions
