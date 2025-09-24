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
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv
from collections import defaultdict

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


    def _create_document(self, page_content: str, file_name: str | None, page_num: int | None) -> Document | None:
        if not page_content:
            return None
        
        metadata = {
            'file_name': file_name,
            'page': page_num
        }
        clean_metadata = {k: v for k, v in metadata.items() if v is not None}
        return  {"page_content": page_content, "metadata": clean_metadata}

    def _cleanse_data(self, data: List[Dict[str, Any]], max_retrieved_docs: int = 5) -> Dict[str, List]:
        queries = []
        predicted_documents_batch = []
        ground_truth_documents_batch = []
        ground_truth_answers = []
        generated_answers = []
        for row in data:

            if isinstance(row, str):
                row = json.loads(row)

            queries.append(row.get("question"))
            ground_truth_answers.append(row.get("target_answer"))
            generated_answers.append(row.get("response"))

            current_ground_truth_docs = []
            gt_doc = self._create_document(
                page_content=row.get("target_answer"),
                file_name=row.get("target_file_name"),
                page_num=row.get("target_page_no")
            )
            if gt_doc:
                current_ground_truth_docs.append(gt_doc)
            ground_truth_documents_batch.append(current_ground_truth_docs)

            current_predicted_docs = []
            for i in range(1, max_retrieved_docs + 1):
                doc_key = f'retrieved_doc{i}'
                cont_key = f'retrieved_cont{i}'
                page_key = f'retrieved_page{i}'

                pred_doc = self._create_document(
                    page_content=row.get(cont_key),
                    file_name=row.get(doc_key),
                    page_num=row.get(page_key)
                )
                if pred_doc:
                    current_predicted_docs.append(pred_doc)
            
            predicted_documents_batch.append(current_predicted_docs)

        return {
            "query": queries,
            "predicted_documents": predicted_documents_batch,
            "ground_truth_documents": ground_truth_documents_batch,
            "ground_truth_answer": ground_truth_answers,
            "generated_answer": generated_answers
        }

    def _load_eval_result(self):
        stored_session_json = self.r.get(self.session_id)
        session_data = json.loads(stored_session_json)
        evaluate_result = session_data["metric_result"]
        dataset = session_data["benchmark_dataset"]
        return evaluate_result, dataset
        
    def _get_error_query_docs(self, data: Any, error_index: list[int], n: int):
        if isinstance(data, dict) and "records" in data:
            data = data["records"]
            data = self._cleanse_data(data)
        data = pl.DataFrame(data)
        error_rows = data[error_index]
        return error_rows.select(
            ["query", "predicted_documents", "ground_truth_documents", "generated_answer", "ground_truth_answer"]
        ).sample(n).to_dicts() # error example 3개씩만


    async def summarize_evaluation(self, prompt_name, **kwargs):
        script_dir = Path(__file__).parent.parent.resolve()
        prompt = script_dir / "Prompts" / f"{prompt_name}.txt"
        prompt = prompt.read_text(encoding="utf-8")
        safe_kwargs = defaultdict(str, kwargs)
        prompt = prompt.format_map(safe_kwargs)
        print("## prompt: \n", prompt)
        result = await self.llm_model.ainvoke(
            [
                SystemMessage(content=prompt),
            ]
        )
        result = result.content
        return result


    async def create_individual_report(self, n): 
        evaluate_result, dataset = self._load_eval_result()
        final_report_dict = {}

        for metric, score_dict in evaluate_result.items():
            score_dict["error_index"] = self._get_error_query_docs(data=dataset, error_index=score_dict["error_index"], n=n)
            eval_report = await self.summarize_evaluation(prompt_name="ERROR_CASE_ANALYSIS_PROMPT", metric=metric, score=score_dict["score"], error=score_dict["error_index"])
            final_report_dict[metric] = {"score": score_dict["score"], "anaysis_text": eval_report}

        return final_report_dict


    def merge_report(self, reports_dict):
        FORMAT = '[성능 지표 {idx}]\n* **지표명:** {metric_name}\n* **성능 점수:** {metric_score}\n* **LLM 분석 의견:**\n"""{llm_analysis}"""\n---'
        result = ''
        for idx, (metric, score_dict) in enumerate(reports_dict.items()):
            output = FORMAT.format(idx=idx+1, metric_name=metric, metric_score=score_dict["score"], llm_analysis=score_dict["anaysis_text"])
            result += f"\n{output}"
        return result
   

    async def create_final_report(self, num_use_errorcase):
        final_report_dict = await self.create_individual_report(n=num_use_errorcase)
        all_summarized_result = self.merge_report(final_report_dict)
        eval_report = await self.summarize_evaluation(prompt_name="FINAL_REPORT_PROMPT", all_summarized_result=all_summarized_result)
        return eval_report





## main
async def generate_report(session_id, model="gpt-4o-mini", embedding_model="text-embedding-3-large", num_use_errorcase=3):
    embeddings = OpenAIEmbeddings(model=embedding_model, api_key=api_key)
    # embeddings = None
    # llm = ChatOpenAI(
    #     model="gemma-3-4b-it",
    #     api_key='token-123',
    #     base_url="http://localhost:8000/v1",
    # )

    llm = ChatOpenAI(model=model, api_key=api_key, temperature=0)
    solver = GenerateReport(session_id=session_id, llm_model=llm, embedding_model=embeddings)
    eval_report = await solver.create_final_report(num_use_errorcase=num_use_errorcase)
    return eval_report


if __name__ == "__main__":

    asyncio.run(generate_report())
