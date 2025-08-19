from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: PydanticObjectId = Field(alias="_id")

class UserResponse(UserBase):
    id: str # Return id as string to the client