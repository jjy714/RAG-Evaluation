from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Optional
from pydantic_mongo import PydanticObjectId

class SessionBase(BaseModel):
    rag_config: Optional[dict[str, Any]] = None

class SessionCreate(SessionBase):
    user_id: PydanticObjectId

class Session(SessionBase):
    id: PydanticObjectId = Field(alias="_id")
    user_id: PydanticObjectId
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PydanticObjectId: str
        }

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: PydanticObjectId = Field(alias="_id")
    role: str
    time_created: datetime
    time_updated: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PydanticObjectId: str
        }

class UserRoleUpdate(BaseModel):
    role: str
