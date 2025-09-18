#### 1. CONFIG
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

#### 2. DATASET

curl -X POST http://localhost:8000/v1/dataset/get-benchmark-dataset \
-H "Content-Type: application/json" \
-d '{
    "session_id":"86157809-6c0d-4df7-996c-3bbebc684c72",
    "user_id" : "minjichoi",
    "dataset_name": "response_merged_output.csv"
}'

#### 3. EVALUATE

curl -X POST http://localhost:8000/v1/evaluate/ \
-H "Content-Type: application/json" \
-d '{
    "session_id":"86157809-6c0d-4df7-996c-3bbebc684c72",
    "user_id": "minjichoi"
}'

#### 4. POST to Redis & Dashbord

curl -X POST http://localhost:8000/send-datapoint \
-H "Content-Type: application/json" \
-d '{"session_id":"86157809-6c0d-4df7-996c-3bbebc684c72",
    "endpoint":"http://localhost:8000/eval_result",
    "payload" : {"metric_name": "f1", 
                 "eval_result": {"f1": [[1,2,3,4,5,6], [1,2]]}
                            }
}'

### 0. Insert Data

curl -X POST \
    -F "file=@/home/minjichoi/RAG-Evaluation/RAG_Evaluation/data/response_merged_output.csv" \
    "http://localhost:8001/v1/insert?user_id=jjy714"


curl -X POST \
    -F "file=@/home/minjichoi/RAG-Evaluation/RAG_Evaluation/stress_test_locusts/bench_lotte_korag.csv" \
    "http://localhost:8001/v1/insert?user_id=minjichoi"


curl -X POST \
    -F "file=@/home/minjichoi/RAG-Evaluation/RAG_Evaluation/data/response_merged_output.csv" \
    "http://localhost:8001/v1/insert?user_id=minjichoi"
