
# CONFIG
curl -X POST http://localhost:8000/v1/config \
-H "Content-Type: application/json" \
-d '{
    "user_id": "jjy714",
    "retrieval_metrics": ["precision", "map", "ndcg"],
    "generation_metrics": ["faithfulness"],
    "top_k": 10,
    "model": "None",
    "evaluation_mode": "full"
}'

## DATASET

curl -X POST http://localhost:8000/v1/dataset/get-benchmark-dataset \
-H "Content-Type: application/json" \
-d '{
    "session_id": "a521e338-6998-4b0f-ac06-9afa32f19095",
    "user_id" : "jjy714",
    "dataset_name": "response_merged_output.csv"
}'

## EVALUATE

curl -X POST http://localhost:8000/v1/evaluate/ \
-H "Content-Type: application/json" \
-d '{
    "session_id": "a521e338-6998-4b0f-ac06-9afa32f19095",
    "user_id": "jjy714"
}'