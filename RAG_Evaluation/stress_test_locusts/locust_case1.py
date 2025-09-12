from locust import HttpUser, task, between
import random
import uuid

class RAGEvaluationUser(HttpUser):
    wait_time = between(1,2)  # 각 task 실행 간격 (1~2초)

    @task
    def run_evaluation_flow(self):
        """
        1) /v1/config
        2) /v1/dataset/get-benchmark-dataset-without-mongo
        3) /v1/evaluate/
        """

        user_id = f"user-{uuid.uuid4()}"

        # ---------- STEP 1. config ----------
        config_payload = {
            "user_id": user_id,
            "retrieval_metrics": {
                "retrieval_metrics": ["mrr", "map", "f1", "precision"]
            },
            "generation_metrics": {
                "generation_metrics": ["bleu", "rouge"]
            },
            "top_k": 5,
            "model": "openai",
            "evaluation_mode": "full"
        }

        with self.client.post("/v1/config", json=config_payload, catch_response=True) as response:
            if response.status_code == 200:
                session_id = response.json().get("session_id")
            else:
                response.failure(f"Config failed: {response.text}")
                return

        # ---------- STEP 2. dataset ----------
        dataset_payload = {
            "session_id": session_id,
            "user_id": user_id,
            "dataset_name": "temp_rag_data"
        }

        with self.client.post("/v1/dataset/get-benchmark-dataset-without-mongo",
                              json=dataset_payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Dataset failed: {response.text}")
                return

        # ---------- STEP 3. evaluate ----------
        eval_payload = {
            "session_id": session_id,
            "user_id": user_id
        }

        with self.client.post("/v1/evaluate/", json=eval_payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Evaluate failed: {response.text}")
            else:
                response.success()
