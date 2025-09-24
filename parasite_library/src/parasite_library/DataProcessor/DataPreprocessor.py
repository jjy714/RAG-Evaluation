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
            # TODO: temporary_vector_store_copy에 buffer 공간만큼 비우고 train data 넣어 활용하는 기능 
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

    
    def _create_document(self, page_content: str, file_name: str | None, page_num: int | None) -> Document | None:
        if not page_content:
            return None
        
        metadata = {
            'file_name': file_name,
            'page': page_num
        }
        clean_metadata = {k: v for k, v in metadata.items() if v is not None}
        return Document(page_content=page_content, metadata=clean_metadata)


    def chunker(self, docs: List[Document]):

        chunk_overlap = self.kwargs.get("chunk_overlap", 5)
        chunk_size = self.kwargs.get("chunk_size", 100)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        splits = text_splitter.split_documents(docs)
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
        pass
        # if not docs:
        #     return []
        # result = []
        # for d in docs:
        #     if isinstance(d, Document):
        #         result.append({
        #             "text": d.page_content,
        #             "file_name": d.metadata
        #         })
        #     else:
        #         result.append(d)  # 이미 dict일 수도 있으니까 그대로 append
        # return result

    async def _generate_synthetic_data(self, query: str, context: str):
        buffer_k = self.kwargs.get("buffer_k", 5)
        synthetic_docs = []

        script_dir = Path(__file__).parent.resolve()
        prompt_path = script_dir / ".." / "Prompts" / "KOR_PROMPT.txt"
        template_string = prompt_path.read_text(encoding="utf-8")
        formatted_prompt = template_string.format(query=query, context=context, previous_hard_negatives=synthetic_docs)

        for _ in range(buffer_k):
            synthetic_doc = await self.llm_model.ainvoke(
                [
                    SystemMessage(content=formatted_prompt),
                    HumanMessage(content="합성 문서를 작성해줘.")
                ]
            )
            try:
                synthetic_doc = synthetic_doc.content
                synthetic_doc = self.cleaning(synthetic_doc, "hard_negative")
            except Exception:
                pass
            synthetic_docs.append(synthetic_doc)

        return synthetic_docs

    async def create_retrieval_bench_data(self, raw_data: List):
        benchmark_data = []
        for idx, row in tqdm(enumerate(raw_data), total=len(raw_data), desc="create_retrieval_bench_data"):
            per_data = {}
            per_data["idx"] = idx + 1
            per_data["question"] = row.get("question", row.get("query"))
            per_data["target_answer"] = row.get("target_answer", row.get("answer"))
            per_data["target_file_name"] = row.get("target_file_name", f"temp_docs{idx+1}.pdf")
            per_data["target_page_no"] = int(row.get("target_page_no", random.randint(1,100)))
            
            context = self._create_document(page_content=per_data["target_answer"], file_name=per_data["target_file_name"], page_num=per_data["target_page_no"])

            synth_documents = await self._generate_synthetic_data(per_data["question"], context)  # List of Synth Docs
            
            row_docs_docu = [ 
                self._create_document(page_content=synth_doc, file_name=f"temp_docs{i+1}.pdf", page_num=random.randint(1,100)) for i, synth_doc in enumerate(synth_documents)
                ]
            row_docs_docu.append(context)
            # print(f"--- AT {idx + 1}, document length : {len(context)} ---")
            # print("Adding Docs to the Vector Store")
            # copied_context = per_data["ground_truth_documents"].copy()
            # print("Chunking")
            docs = self.chunker(row_docs_docu) # 합성 문서와 실제 문서 합치는 과정
            self.add_documents(docs) # 형식화된 document self.vectorstore에 저장
            benchmark_data.append(per_data)

        search_kwargs= self.kwargs.get('k', 5)
        # print("----- Retrieving Documents -----")
        for row in benchmark_data:
            search_out = self.search(row["question"]) # 실제로 검색된 문서 k개 만큼임 (defalut 5개)
            row["search_out"] = search_out
            for i, retrieved_doc in enumerate(search_out):
                row[f"retrieved_doc{i+1}"] = retrieved_doc.metadata["file_name"]
                row[f"retrieved_cont{i+1}"] = retrieved_doc.page_content
                row[f"retrieved_page{i+1}"] = retrieved_doc.metadata["page"]
        
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
        doc_cols = ["retrieved가 포함되어있는 cols"]
        
        for row in tqdm(benchmark_data, desc="create_generation_bench_data"):

            retrieved_contexts = row["search_out"] # [Document]
            retrieved_contexts = [context.page_content for context in retrieved_contexts]
            retrieved_contexts = '\n'.join(retrieved_contexts)
            result = await chain.ainvoke(
                {
                    "context": retrieved_contexts,
                    "query": str(row.get("question")),
                }
            )
            try:
                result = self.cleaning(result, 'result')
            except Exception:
                pass
            row["response"] = result
            del row["search_out"]
        
        bench_df = pd.DataFrame(benchmark_data)
        save_path = Path('.').resolve().parent.parent
        save_csv_path = save_path /  "RAG_Evaluation" / "data" / f"bench_{save_benchmark_name}.csv"
        bench_df.to_csv(save_csv_path, index=False)
        
        import json
        save_json_path = save_path / "RAG_Evaluation" / "data" / f"bench_{save_benchmark_name}.json"
        with open(save_json_path, "w", encoding="utf-8") as f:
            json.dump(benchmark_data, f, ensure_ascii=False)
        
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
    sample_raw_data = sample_raw_data[:500]

    benchmark_data_result_path = await solver.create_generation_bench_data(sample_raw_data, save_benchmark_name="lotte_korag")

    print('benchmark_data_result_path: ', benchmark_data_result_path)



if __name__ == "__main__":

    asyncio.run(data_process())
