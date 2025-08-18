# start mongodb server
brew services start mongodb-community


# start fastapi
uvicorn app.main:app --reload

#Swagger UI: http://127.0.0.1:8000/docs