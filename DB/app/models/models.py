from datetime import datetime
from typing import Optional, List, Any
from pydantic import Field
from pydantic_mongo import PydanticObjectId
from pydantic import BaseModel

class User(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    username: str
    email: str
    hashed_password: str
    role: str = "user"
    time_created: datetime = Field(default_factory=datetime.utcnow)
    time_updated: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PydanticObjectId: str
        }

class Session(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    user_id: PydanticObjectId  # Reference to User's _id
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    rag_config: Optional[dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PydanticObjectId: str
        }

