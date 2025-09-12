import httpx
import os
import re
import json
import ast
import asyncio
import random
import pandas as pd
from operator import itemgetter
from pathlib import Path
from typing import Any, List, Dict, Optional
from tqdm import tqdm
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv

from parasite_library.DataProcessor.RecieveData import DataReceiver

load_dotenv()
api_key = os.getenv("API_KEY")
'''
query : str

'''

class DataPreprocessor:
    def __init__(self, embedding_model: Optional[Any | None], llm_model: Any, **kwargs):

        # SHOULD BE INTIATED PER COLLECTION
        self.embedding_model = embedding_model
        self.vector_store = InMemoryVectorStore(embedding=self.embedding_model)
        self.llm_model = llm_model
        # self.app = FastAPI()
        # self.router = APIRouter()
        # self.app.include_router(self.router)

        self.kwargs = kwargs

    def create_chain(self):
        try:
            script_dir = Path(__file__).parent.resolve()
            prompt_path = script_dir / ".." /  "Prompts" / "KOR_GENERATE_ANS_PROMPT.txt"
            template_string = prompt_path.read_text(encoding="utf-8")
            prompt = ChatPromptTemplate.from_template(template_string)

            rag_chain = (

                {
                    'context': itemgetter('context'),
                    'query': itemgetter('query'),
                }
                | prompt
                | self.llm_model
                | StrOutputParser()
            )

            return rag_chain

        except FileNotFoundError:
            script_dir = Path(__file__).parent.resolve()
            prompt_path = script_dir / "KOR_GENERATE_ANS_PROMPT.txt"
            print(f"ERROR: Prompt file not found at {prompt_path}. Please create it.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while creating the chain: {e}")
            raise
        
    def _to_documents(self, document_list: List[Dict]) -> List[Document]:
        return [
            Document(page_content=docu_dict["text"], metadata={"file_name": docu_dict["file_name"]}) for docu_dict in document_list if docu_dict and docu_dict != "null"
        ]
        
    def chunker(self, docs: List[str]):

        chunk_overlap = self.kwargs.get("chunk_overlap", 5)
        chunk_size = self.kwargs.get("chunk_size", 100)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        splits = text_splitter.split_documents(self._to_documents(docs))
        return splits

    def add_documents(self, documents: List[Document]):

        if not documents:
            return None
        return self.vector_store.add_documents(documents=documents)

    def search(self, query: str) -> List[Document]:
        k = self.kwargs.get("k", 5)
        return self.vector_store.similarity_search(query, k=k)
    
    def cleaning(self,raw_text, column_name): 
        cleaned = re.sub(r"^```json\n|\n```$", "", raw_text.strip(), flags=re.MULTILINE).replace("\n", "").strip()
        if '{' in cleaned and ':' in cleaned:
            parsed = json.loads(cleaned)
            result = parsed[column_name]
        else:
            result = cleaned.strip()
        return result
    
    def _serialize_docs(self, docs: List):
        if not docs:
            return []
        result = []
        for d in docs:
            if isinstance(d, Document):
                result.append({
                    "text": d.page_content,
                    "file_name": d.metadata
                })
            else:
                result.append(d)  # 이미 dict일 수도 있으니까 그대로 append
        return result

    async def _generate_synthetic_data(self, context: str):
        buffer_k = self.kwargs.get("buffer_k", 5)

        script_dir = Path(__file__).parent.resolve()
        prompt_path = script_dir / ".." / "Prompts" / "KOR_PROMPT.txt"
        template_string = prompt_path.read_text(encoding="utf-8")

        # for _ in range(buffer_k):
        formatted_prompt = template_string.format(context=context, n=buffer_k)

        synthetic_doc = await self.llm_model.ainvoke(
            [
                SystemMessage(content=formatted_prompt),
                HumanMessage(content="합성 문서를 작성해줘.")
            ]
        )
        synthetic_doc = synthetic_doc.content
        synthetic_doc = self.cleaning(synthetic_doc, 'hard_negatives')
        synthetic_doc = [{"text": doc, "file_name": f"temp_doc{i}.pdf"} for i, doc in enumerate(synthetic_doc)]
        return synthetic_doc

    async def create_retrieval_bench_data(self, raw_data: List):
        benchmark_data = []
        for idx, row in tqdm(enumerate(raw_data), total=len(raw_data), desc="create_retrieval_bench_data"):
            row_q = row["query"]
            row_docs = ast.literal_eval(row["ground_truth_documents"]) if type(row["ground_truth_documents"])==str else row["ground_truth_documents"]
            ground_truth_answer = ast.literal_eval(row["ground_truth_answer"]) if type(row["ground_truth_answer"])==str else row["ground_truth_answer"]

            per_data = {}
            per_data["idx"] = idx + 1
            per_data["query"] = row_q
            context = "\n\n".join([str(doc) for doc in row_docs])
            context = context if len(context) < 10000 else context[:10000]
            per_data["ground_truth_answer"] = ground_truth_answer
            synth_documents = await self._generate_synthetic_data(context)  # List of Synth Docs
            per_data["ground_truth_documents"] = row_docs
            row_docs.extend(synth_documents)
            # print(f"--- AT {idx + 1}, document length : {len(context)} ---")
            # print("Adding Docs to the Vector Store")
            # copied_context = per_data["ground_truth_documents"].copy()
            # print("Chunking")
            docs = self.chunker(row_docs) # 합성 문서와 실제 문서 합치는 과정
            self.add_documents(docs) # 형식화된 document self.vectorstore에 저장
            benchmark_data.append(per_data)

        search_kwargs= self.kwargs.get('k', 5)
        # print("----- Retrieving Documents -----")
        for row in benchmark_data:
            search_out = self.search(row["query"]) # 실제로 검색된 문서 k개 만큼임 (defalut 5개+1개개)
            row["predicted_documents"] = search_out # 가장 유사하다고 판단한 문서들 순서서
            row["retrieved_contexts"] = search_out # 일단 실제 검색된 문장이 없으므로 동일하게 문서로 넣음
        
        return benchmark_data



    async def create_generation_bench_data(self, raw_data: List, save_benchmark_name: str):
        chain = self.create_chain()
        if chain is None:
            raise ValueError("RAG chain 생성 실패")
        self.chain = chain
        
        benchmark_data = await self.create_retrieval_bench_data(raw_data) # query, idx, 정답텍스트(ans_doc), 정답(으로 간주되는) 임의 문서(synth_documents), 
                                                                          # 예측된 검색 문서(retrieved_docs), 예측 정답 생성(pred_answer)
        # print("----- Generating Answers -----")
        search_kwargs=self.kwargs.get('k', 5)
        doc_cols = ["predicted_documents", "ground_truth_documents", "retrieved_contexts"]
        
        for row in tqdm(benchmark_data, desc="create_generation_bench_data"):

            retrieved_contexts = row["retrieved_contexts"] # [Document]
            retrieved_contexts = [context.page_content for context in retrieved_contexts]
            retrieved_contexts = '\n'.join(retrieved_contexts)
            result = await chain.ainvoke(
                {
                    "context": retrieved_contexts,
                    "query": str(row.get("query")),
                }
            )
            result = self.cleaning(result, 'result')
            row["generated_answer"] = result
            for col in doc_cols:
                row[col] = self._serialize_docs(row[col])
        
        bench_df = pd.DataFrame(benchmark_data)
        save_path = Path('.').resolve().parent.parent
        save_csv_path = save_path /  "RAG_Evaluation" / "test" / f"bench_{save_benchmark_name}.csv"
        bench_df.to_csv(save_csv_path, index=False)
        
        import json
        save_json_path = save_path / "RAG_Evaluation" / "test" / f"bench_{save_benchmark_name}.json"
        with open(save_json_path, "w", encoding="utf-8") as f:
            json.dump(benchmark_data[0], f, ensure_ascii=False)
        
        response = f'{save_benchmark_name}.csv'
        return response

#############################  

    async def send_benchdata(self, eval_api: str):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(eval_api)
                response.raise_for_status()
                return {
                    "status": "success",
                    "status_code": response.status_code,
                    "content": response.json() if response.headers.get("content-type") == "application/json" else response.text
                }
        except httpx.ConnectError as ce:
            return {"status": "fail", "error": str(ce)}
        except httpx.TimeoutException as te:
            return {"status": "fail", "error": str(te)}


################main#######################
async def data_process(data):

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=api_key)
    # llm = ChatOpenAI(
    #     model="gemma",
    #     api_key='token-123',
    #     base_url="http://localhost:8000/v1",
    # )

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

    solver = DataPreprocessor(embedding_model=embeddings, llm_model=llm)
    receiver = DataReceiver()
    sample_raw_data = await receiver.receive_rawdata_csv(content=data)
    sample_raw_data = sample_raw_data['samples'] 
    ## for test
    sample_raw_data = sample_raw_data[:1]

    benchmark_data_result_path = await solver.create_generation_bench_data(sample_raw_data, save_benchmark_name="lotte_korag")

    print('benchmark_data_result_path: ', benchmark_data_result_path)



if __name__ == "__main__":

    asyncio.run(data_process())
