# crud.py
from pymongo.database import Database
from . import models, auth

def get_user(db: Database, email: str):
    """이메일로 사용자를 조회합니다."""
    user = db.users.find_one({"email": email})
    return user

def create_user(db: Database, user: models.UserCreate):
    """새로운 사용자를 생성합니다."""
    hashed_password = auth.get_password_hash(user.password)
    db_user = {"email": user.email, "hashed_password": hashed_password}
    db.users.insert_one(db_user)
    return db_user