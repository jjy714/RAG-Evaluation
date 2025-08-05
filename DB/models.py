# models.py
from pydantic import BaseModel, Field, EmailStr

# 사용자 생성을 위한 모델 (회원가입 시)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 데이터베이스에 저장될 사용자 모델 (비밀번호 해시 포함)
class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str

# JWT 토큰을 위한 모델
class Token(BaseModel):
    access_token: str
    token_type: str