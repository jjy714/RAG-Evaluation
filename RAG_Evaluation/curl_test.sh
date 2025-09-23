
#### 1. CONFIG  (** insert data before config)####
curl -X POST http://localhost:8000/v1/config \
-H "Content-Type: application/json" \
-d '{
    "user_id": "minjichoi",
    "retrieve_metrics": ["precision", "map", "ndcg"],
    "generate_metrics": ["bleu"],
    "top_k": 10,
    "model": "None",
    "evaluation_mode": "full"
}'


#### 2. DATASET  ####
# (1) response_merged_output test
curl -X POST http://localhost:8000/v1/dataset/get-benchmark-dataset \
-H "Content-Type: application/json" \
-d '{
    "session_id": "8eef32ab-f2d0-4f49-9031-01426edc5311",
    "user_id" : "minjichoi",
    "dataset_name": "response_merged_output.csv"
}'
# (2) bench_lotte_korag test
curl -X POST http://localhost:8000/v1/dataset/get-benchmark-dataset \
-H "Content-Type: application/json" \
-d '{
    "session_id":"14dce911-6018-47bf-b28b-20fd4a85d700",
    "user_id" : "minjichoi",
    "dataset_name": "bench_lotte_korag.csv"
}'


#### 3. EVALUATE  ####
curl -X POST http://localhost:8000/v1/evaluate/ \
-H "Content-Type: application/json" \
-d '{
    "session_id":"14dce911-6018-47bf-b28b-20fd4a85d700",
    "user_id": "minjichoi"
}'

### 4. GenerateReport  ####

curl -X POST http://localhost:8005/get-evaluate-report \
-H "Content-Type: application/json" \
-d '{
    "session_id":"14dce911-6018-47bf-b28b-20fd4a85d700"
}'

# ---------------------------------------------------------------------------------------------------------------------------
### 0. Insert Data  ####

curl -X POST \
    -F "file=@/home/minjichoi/RAG-Evaluation/RAG_Evaluation/data/response_merged_output.csv" \
    "http://localhost:8001/v1/insert?user_id=minjichoi"

curl -X POST \
    -F "file=@/home/minjichoi/RAG-Evaluation/RAG_Evaluation/data/bench_lotte_korag.csv" \
    "http://localhost:8001/v1/insert?user_id=minjichoi"
