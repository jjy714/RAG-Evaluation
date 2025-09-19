import redis
import json
import asyncio
import os
from operator import itemgetter
from pathlib import Path
from typing import Any, List, Dict, Optional
from tqdm import tqdm

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

    def load_eval_result(self):
        stored_session_json = self.r.get(self.session_id)
        session_data = json.loads(stored_session_json)
        metric_result = session_data["metric_result"] # {"mrr": {"score": [], "error_index": []}, "map": {"score": [], "error_index": []}}
        for metric, score_dict in metric_result.items():
            score_dict["score"] = score_dict["score"].mean()

        return metric_result
    def _get_error_query_docs(self, data, error_index):
        error_data = data.iloc[error_index, :]
        return error_data[["qeury", "predicted_documents", 'ground_truth_documents', 'generated_answer' 'ground_truth_answer']]
    
    async def create_report(self, metric_result: str, false_value: dict):
        script_dir = Path(__file__).parent.parent.resolve()
        prompt_path = script_dir / "Prompts" / "REPORT_PROMPT.txt"
        template_string = prompt_path.read_text(encoding="utf-8")
        # error_list = _get_error_query_docs(data, error_index)

        formatted_prompt = template_string.format(score_result=metric_result["metric_result"], 
                                                  error_list=error_list)

        eval_report = await self.llm_model.ainvoke(
            [
                SystemMessage(content=formatted_prompt),
            ]
        )
        eval_report = eval_report.content

        return eval_report


## main
async def main(data):
    session_id = "abc"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=api_key)
    # embeddings = None
    # llm = ChatOpenAI(
    #     model="gemma-3-4b-it",
    #     api_key='token-123',
    #     base_url="http://localhost:8000/v1",
    # )

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

    solver = GenerateReport(llm_model=llm, embedding_model=embeddings, session_id=session_id)
    ## for test

    eval_report = await solver.load_eval_result()
    return {"eval_repot": eval_report}


if __name__ == "__main__":

    asyncio.run(main())
