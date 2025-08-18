from ..models import models
from .. import schemas
from ..database.database import db
from pydantic_mongo import PydanticObjectId
from typing import List
import csv

def get_user(user_id: PydanticObjectId):
    user_data = db.users.find_one({"_id": user_id})
    if user_data:
        return models.User(**user_data)
    return None

def get_user_by_email(email: str):
    user_data = db.users.find_one({"email": email})
    if user_data:
        return models.User(**user_data)
    return None

def get_user_by_username(username: str):
    user_data = db.users.find_one({"username": username})
    if user_data:
        return models.User(**user_data)
    return None

def read_csv():
    csv_file = "해당csv파일명.csv"
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        csvReader = csv.DictReader(file)
        # You might want to process the CSV data here, e.g., insert into MongoDB

def create_user(user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    user_data = {
        "email": user.email,
        "username": user.username,
        "hashed_password": fake_hashed_password,
        "role": "user",
        "time_created": models.User.time_created.default_factory(),
        "time_updated": None
    }
    result = db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return models.User(**user_data)

def update_user_role(user_id: PydanticObjectId, role: str):
    result = db.users.update_one({"_id": user_id}, {"$set": {"role": role, "time_updated": models.User.time_updated.default_factory()}})
    if result.modified_count:
        return get_user(user_id)
    return None

def get_session(session_id: PydanticObjectId):
    session_data = db.sessions.find_one({"_id": session_id})
    if session_data:
        return models.Session(**session_data)
    return None

def create_session(session: schemas.SessionCreate):
    session_data = {
        "user_id": session.user_id,
        "rag_config": session.rag_config,
        "start_time": models.Session.start_time.default_factory(),
        "end_time": None
    }
    result = db.sessions.insert_one(session_data)
    session_data["_id"] = result.inserted_id
    return models.Session(**session_data)

def get_sessions(skip: int = 0, limit: int = 100) -> List[models.Session]:
    sessions_data = db.sessions.find().skip(skip).limit(limit)
    return [models.Session(**session) for session in sessions_data]
