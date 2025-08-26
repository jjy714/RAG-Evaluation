# start mongodb server
brew services start mongodb-community


# start fastapi
uvicorn app.main:app --reload

#Swagger UI: http://127.0.0.1:8000/docs

docker run \
    -p 9017:27017 \
    --rm \
    --network mongo-net \
    --name mongo \
    -e MONGO_INITDB_ROOT_USERNAME=root \
    -e MONGO_INITDB_ROOT_PASSWORD=changeme \
    -v mongo-data:/data/db \
    -d mongo

docker run \
    --name mongo-express \
    --network mongo-net \
    -p 9018:8081 \
    --rm \
    -e ME_CONFIG_MONGODB_ADMINUSERNAME=root \
    -e ME_CONFIG_MONGODB_ADMINPASSWORD=changeme \
    -e ME_CONFIG_MONGODB_SERVER=mongo \
    -d mongo

