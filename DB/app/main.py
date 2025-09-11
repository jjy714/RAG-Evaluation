from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="RAG Evaluation MongoDB API",
    description="An API to CRUD DB.",
    version="1.0.0",
)
app.include_router(api_router, prefix="/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}

