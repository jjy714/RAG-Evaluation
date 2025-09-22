from ipaddress import v6_int_to_packed
import redis
import json
import asyncio
import os
from operator import itemgetter
from pathlib import Path
from typing import Any, List, Dict, Optional
from tqdm import tqdm
import polars as pl

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv

from parasite_library.DataProcessor.RecieveData import DataReceiver

load_dotenv()
api_key = os.getenv("API_KEY")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_HOST = os.getenv("REDIS_HOST")
class GenerateReport:
    def __init__(self, embedding_model: Optional[Any | None], llm_model: Any, session_id:str, **kwargs):

        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.session_id = session_id
        self.kwargs = kwargs
        self.r = redis.Redis(
                host=REDIS_HOST,
                port=int(REDIS_PORT),
                decode_responses=True
                )
        try:
            self.r.ping()
        except redis.exceptions.ConnectionError as e:
            print(f"Could not connect to Redis: {e}")
# {"metric_result"
#      retrieval_evaluation_result = {
#     "mrr": {"score": mrr_score, "error_index": error_at_mrr_score},
#     "map": {"score": map_score, "error_index": error_at_map_score},
#     "f1": {"score": f1_score, "error_index": error_at_f1_score},
#     "ndcg": {"score": ndcg_score, "error_index": error_at_ndcg_score},
#     "context_relevance": {"score": context_relevance_score},
#     "precision": {"score": precision_score, "error_index": error_at_precision_score},
#     "recall": {"score": recall_score, "error_index": error_at_recall_score},
#     }
# }
    def _load_eval_result(self):
        stored_session_json = self.r.get(self.session_id)
        session_data = json.loads(stored_session_json)
        evaluate_result = session_data["metric_result"]
        dataset = session_data["benchmark_dataset"]
        return evaluate_result, dataset
        
    def _get_error_query_docs(self, data: Any, error_index: list[int]):
        data = pl.DataFrame(data)
        error_rows = data[error_index]
        return error_rows.select(
            ["query", "predicted_documents", "ground_truth_documents", "retrieved_contexts"]
        ).to_dicts()
        
    async def create_report(self): 
        # TODO:  data는 UI에 저장되어있다고 가정
        evaluate_result, dataset = self._load_eval_result()
        for metric, score_dict in evaluate_result.items():
            score_dict["error_index"] = self._get_error_query_docs(data=dataset, error_index=score_dict["error_index"])
        
        print("final_input result: ", evaluate_result)
        script_dir = Path(__file__).parent.parent.resolve()
        
        prompt = script_dir / "Prompts" / "REPORT_PROMPT.txt"
        prompt = prompt.read_text(encoding="utf-8")
        prompt = prompt.format(metric_result=evaluate_result)

        eval_report = await self.llm_model.ainvoke(
            [
                SystemMessage(content=prompt),
            ]
        )
        eval_report = eval_report.content
        print("final result ; ", eval_report)
        return eval_report

## main
async def main(session_id, model="gpt-4o-mini", embedding_model="text-embedding-3-large"):
    embeddings = OpenAIEmbeddings(model=embedding_model, api_key=api_key)
    # embeddings = None
    # llm = ChatOpenAI(
    #     model="gemma-3-4b-it",
    #     api_key='token-123',
    #     base_url="http://localhost:8000/v1",
    # )

    llm = ChatOpenAI(model=model, api_key=api_key)
    solver = GenerateReport(session_id=session_id, llm_model=llm, embedding_model=embeddings)
    eval_report = await solver.create_report()
    return eval_report


if __name__ == "__main__":

    asyncio.run(main())
