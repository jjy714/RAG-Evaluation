docker run -d \
    --name test-qdrant \
    -p 63331:6333 \
    -p 63332:6334 \
    -v ./qdrant_storage:/qdrant/storage  \
    qdrant/qdrant