

# uv run uvicorn app:main --reload


# Run Evaluator Systems 
docker start -d -p 8000:8000 --name evaluator_server evaluator_server 

# Run Backend 

# Run DB

# Run Frontend













curl -X POST http://localhost:8000/v1/config \
-H "Content-Type: application/json" \
-d '{
    "user_id": "user-jason-123",
    "retrieval_metrics": {
        "precision": true,
        "recall": true
    },
    "generation_metrics": {
        "faithfulness": true
    },
    "top_k": 10,
    "evaluation_mode": "full"
}'