from fastapi import FastAPI
from app.api import users, items

app = FastAPI(title="My MongoDB Backend")

app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(items.router, prefix="/api/v1", tags=["Items"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}