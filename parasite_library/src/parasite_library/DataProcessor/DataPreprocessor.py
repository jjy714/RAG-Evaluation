import httpx 
import os
import re
import json
import ast
import asyncio
import pandas as pd
from operator import itemgetter
from pathlib import Path
from typing import Any, List, Dict
from tqdm import tqdm
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

class DataPreprocessor:
    def __init__(
        self, 
        embedding_model: Any, 
        llm_model: Any, 
        **kwargs
        ):
        
        # SHOULD BE INTIATED PER COLLECTION
        self.embedding_model = embedding_model
        self.vector_store = InMemoryVectorStore(embedding=self.embedding_model)
        self.llm_model = llm_model
        # self.app = FastAPI()
        # self.router = APIRouter()
        # self.app.include_router(self.router)

        self.kwargs = kwargs

        
    def _to_documents(self, texts: List[str]) -> List[Document]:
        return [Document(page_content=text) for text in texts if text and text != "null"]

    def chunker(self, docs: List[str]):
        
        chunk_overlap=self.kwargs.get('chunk_overlap', 50)
        chunk_size=self.kwargs.get('chunk_size', 1000)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
            )

        splits = text_splitter.split_documents(self._to_documents(docs))
        return splits
    
    def _serialize_docs(self, docs):
        if not docs:
            return []
        result = []
        for d in docs:
            if isinstance(d, Document):
                result.append({
                    "id": getattr(d, "id", None),
                    "page_content": d.page_content,
                    "metadata": d.metadata,
                })
            else:
                result.append(d)  # 이미 dict일 수도 있으니까 그대로 append
        return result
        
    def add_documents(self, documents: List[Document]):

        if not documents:
            return None
        return self.vector_store.add_documents(documents=documents)

    def search(self, query: str) -> List[Document]:
        k=self.kwargs.get('k', 5)
        return self.vector_store.similarity_search(query, k=k)
    
    def cleaning(self,raw_text, column_name): 
        cleaned = re.sub(r"^```json\n|\n```$", "", raw_text.strip(), flags=re.MULTILINE).replace("\n", "").strip()
        if '{' in cleaned and ':' in cleaned:
            parsed = json.loads(cleaned)
            result = parsed[column_name]
        else:
            result = cleaned.strip()
        return result


    async def _generate_synthetic_data(self, context: str):
        buffer_k = self.kwargs.get("buffer_k", 5)

        script_dir = Path(__file__).parent.resolve()
        prompt_path = script_dir / ".." / "Prompts" / "KOR_PROMPT.txt"
        template_string = prompt_path.read_text(encoding="utf-8")

        for _ in range(buffer_k):
            formatted_prompt = template_string.format(context=context, n=buffer_k)

            synthetic_doc = await self.llm_model.ainvoke(
                [
                    {"role": "system", "content": formatted_prompt},
                    {"role": "user", "content": "합성 문서를 작성해줘."}
                ]
            )
            synthetic_doc = synthetic_doc.content
            synthetic_doc = self.cleaning(synthetic_doc, 'hard_negatives')

        return synthetic_doc

    async def create_retrieval_bench_data(self, raw_data: List):
        benchmark_data = []

        for idx, row in tqdm(enumerate(raw_data)):
            per_data = {}
            docs = []
            question = row.get("question", "") #done
            doc = row.get("document", []) # done
            target_answer = row.get("target_answer", "")
            target_file_name = row.get("target_file_name", "")
            # context = "\n\n".join([d.page_content for d in docs])
            docs.append(str(doc))
            per_data["question"] = question
            per_data["target_file_name"] = target_file_name
            per_data["idx"] = idx
            per_data["target_answer"] = target_answer  #실제 정답
            print('input doc: \n', doc)
            per_data['synth_documents'] =  await self._generate_synthetic_data(doc) # List of Synth Docs
            
            print("Adding Docs to the Vector Store")
            doc_lst = per_data["synth_documents"]
            print("Chunking")
            for doc in doc_lst:
                docs.append(doc) # 합성 문서와 실제 문서 합치는 과정
            docs = self.chunker(docs)
            self.add_documents(docs) # 형식화된 document self.vectorstore에 저장
            benchmark_data.append(per_data)

        search_kwargs= self.kwargs.get('k', 5)
        print("----- Retrieving Documents -----")
        for row in benchmark_data:
            search_out = self.search(row["question"]) # 실제로 검색된 문서 k개 만큼임 (defalut 5개)
            for k in range(search_kwargs):
                row[f"retrieved_doc{k+1}"] = search_out[k]
            
        print('benchmark_data: ', benchmark_data)
        return benchmark_data



    def create_chain(self):
        try:
            script_dir = Path(__file__).parent.resolve()
            prompt_path = script_dir / ".." /  "Prompts" / "KOR_GENERATE_ANS_PROMPT.txt"
            template_string = prompt_path.read_text(encoding="utf-8")
            prompt = ChatPromptTemplate.from_template(template_string)

            rag_chain = (

                {
                    'context': itemgetter('context'),
                    'question': itemgetter('question'),
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
        

    async def create_generation_bench_data(self, benchmark_data: List):
        chain = self.create_chain()
        if chain is None:
            raise ValueError("RAG chain 생성 실패")
        self.chain = chain

        print("----- Generating Answers -----")
        print(type(benchmark_data))
        search_kwargs=self.kwargs.get('k', 5)
        for row in tqdm(benchmark_data):
            retrieved_contexts = []
            for k in range(search_kwargs):
                retrieved_context = row.get(f'retrieved_doc{k+1}')
                retrieved_context = retrieved_context.page_content
                retrieved_contexts.append(retrieved_context)
            retrieved_contexts = '\n'.join(retrieved_contexts)
            result = await chain.ainvoke(

                {
                    "context": retrieved_contexts, #str(row.get("document")), #done
                    "question": str(row.get("question")), # done
                }
            )
            result = self.cleaning(result, 'result')
            print('result, \n', result)
            row["response"] = result

        bench_df = pd.DataFrame(benchmark_data)
        for col in bench_df.columns:
            if "retrieved_doc" in col or 'document' in col:
                bench_df[col] = bench_df[col].apply(lambda x: self._serialize_docs(x))

        save_path = '/home/minjichoi/RAG-Evaluation/RAG_Evaluation/data/bench_preprocessed.csv'
        bench_df.to_csv(save_path, index=False)
        print(f'### result \n{bench_df} ')
        return save_path

#############################  

    async def send_benchdata(self, eval_api: str, benchdata):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                print('eval_api: ', eval_api)
                response = await client.post(eval_api, json={"file": benchdata}) # httpx.post(benchdata)
                response.raise_for_status()
                return {"response": response}
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
    sample_raw_data = sample_raw_data['samples'] # 리스트 형태임 [{"col1":~. "col2":~}, ...]
    ## for test
    sample_raw_data = sample_raw_data[:1 ]

    print("Generating synthetic data...")
    benchmark_data = await solver.create_retrieval_bench_data(sample_raw_data)
    benchmark_data_result_path = await solver.create_generation_bench_data(benchmark_data)
    print("Generation complete.")
    
    return await solver.send_benchdata(eval_api='http://localhost:8000/v1/evaluate/evaluate', benchdata=benchmark_data_result_path)

    # 문서-쿼리 쌍에 대해, 사용자가 사용하고 있는 임베딩 모델 기반의 실제 검색된 문서, 생성된 결과가 짝 지어져야 함

if __name__ == "__main__":
    
    asyncio.run(data_process())