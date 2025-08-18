from pymongo import MongoClient

MONGO_DATABASE_URL = "mongodb://localhost:27017/"  # You might want to move this to an environment variable
MONGO_DB_NAME = "rag_db"  # Your database name

client = MongoClient(MONGO_DATABASE_URL)
db = client[MONGO_DB_NAME]
