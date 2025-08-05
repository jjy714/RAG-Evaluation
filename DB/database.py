# database.py
from pymongo import MongoClient

MONGO_DATABASE_URL = "mongodb://localhost:27017/"
client = MongoClient(MONGO_DATABASE_URL)
db = client["myFastAPIDB"] # 데이터베이스 이름 설정