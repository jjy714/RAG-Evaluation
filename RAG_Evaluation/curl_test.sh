
SESSION_ID="fbe0a8d8-0e70-484c-801b-97877310c1e9"

#### 1. CONFIG
curl -X POST http://localhost:8000/v1/config \
-H "Content-Type: application/json" \
-d '{
    "user_id": "jjy714",
    "retrieve_metrics": ["precision", "map", "ndcg", "f1"],
    "generate_metrics": ["bleu"],
    "top_k": 10,
    "model": "None",
    "evaluation_mode": "full"
}'

#### 2. DATASET

curl -X POST http://localhost:8000/v1/dataset/get-benchmark-dataset \
-H "Content-Type: application/json" \
-d "{
    \"session_id\": \"${SESSION_ID}\",
    \"user_id\" : \"jjy714\",
    \"dataset_name\": \"response_merged_output.csv\"
}"

#### 3. EVALUATE

curl -X POST http://localhost:8000/v1/evaluate/ \
-H "Content-Type: application/json" \
-d "{
    \"session_id\": \"${SESSION_ID}\",
    \"user_id\": \"jjy714\"
}"



### 0. Insert Data

curl -X POST \
    -F "file=@/Users/jason/Claion/RAG/RAG_Evaluation/RAG_Evaluation/data/response_merged_output.csv" \
    "http://localhost:8001/v1/insert?user_id=jjy714"


    