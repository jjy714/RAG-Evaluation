from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Any, List

class SessionBase(BaseModel):
    rag_config: dict[str, Any] | None = None

class SessionCreate(SessionBase):
    user_id: int

class Session(SessionBase):
    session_id: UUID
    user_id: int
    start_time: datetime
    end_time: datetime | None = None

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str
    time_created: datetime
    time_updated: datetime | None = None
    sessions: list[Session] = []

    class Config:
        orm_mode = True

class UserRoleUpdate(BaseModel):
    role: str
