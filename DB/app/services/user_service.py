from pymongo import AsyncMongoClient
from app.models.user_model import UserCreate, UserInDB
from bson import ObjectId
import csv

async def create_user(db: AsyncMongoClient, user: UserCreate) -> UserInDB:
    user_dict = user.model_dump()
    # In a real app, you would hash the password here
    user_dict["hashed_password"] = user.password + "_hashed" 
    result = await db["users"].insert_one(user_dict)
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    return UserInDB(**created_user)

async def get_user_by_id(db: AsyncMongoClient, user_id: str) -> UserInDB | None:
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user:
        return UserInDB(**user)
    return None

def read_csv():
    csv_file = "해당csv파일명.csv"
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        csvReader = csv.DictReader(file)
        # You might want to process the CSV data here, e.g., insert into MongoDB