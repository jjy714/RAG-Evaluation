import httpx 
import os
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

from wrapper_library.DataProcessor.RecieveData import DataReceiver
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


    def create_chain(self):
        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)

        try:
            retriever = self.vector_store.as_retriever(
                search_type='similarity',
                search_kwargs={'k': self.kwargs.get('k', 5)}
            )

            script_dir = Path(__file__).parent.resolve()
            prompt_path = script_dir / "KOR_PROMPT.txt"
            template_string = prompt_path.read_text(encoding="utf-8")
            prompt = ChatPromptTemplate.from_template(template_string)

            rag_chain = (

                {
                    'context': itemgetter('context'),
                    'question': itemgetter('question'),
                    'n': itemgetter('n'),
                }
                # {
                #     "context": retriever | format_docs,
                #     "question": RunnablePassthrough(),
                # }
                | prompt
                | self.llm_model
                | StrOutputParser()
            )

            return rag_chain

        except FileNotFoundError:
            script_dir = Path(__file__).parent.resolve()
            prompt_path = script_dir / "KOR_PROMPT.txt"
            print(f"ERROR: Prompt file not found at {prompt_path}. Please create it.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while creating the chain: {e}")
            raise
        
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
    
        
    def add_documents(self, documents: List[Document]):

        if not documents:
            return None
        return self.vector_store.add_documents(documents=documents)

    def search(self, query: str) -> List[Document]:
        k=self.kwargs.get('k', 5)
        return self.vector_store.similarity_search(query, k=k)

    async def _generate_synthetic_data(self, context: str):
        buffer_k = self.kwargs.get("buffer_k", 5)
        self.chain = self.create_chain()
        if not self.chain:
            print("Synthesis chain is not initialized. Cannot generate data.")
            return []
        synthetic_docs = []

        script_dir = Path(__file__).parent.resolve()
        prompt_path = script_dir / "KOR_PROMPT.txt"
        template_string = prompt_path.read_text(encoding="utf-8")
        for _ in range(buffer_k):
            formatted_prompt = template_string.format(context=context, n=_)

            synthetic_doc = await self.llm_model.ainvoke(
                [
                    {"role": "system", "content": formatted_prompt},
                    {"role": "user", "content": "합성 문서를 작성해줘."}
                ]
            )
            synthetic_docs.append(synthetic_doc.content)

        return synthetic_docs

    async def create_retrieval_bench_data(self, raw_data: List):
        benchmark_data = []
        buffer_k = self.kwargs.get("buffer_k", 5)
        
        for idx, row in tqdm(enumerate(raw_data)):
            per_data = {}
            
            query = row.get("query", "")
            docs = row.get("document", [])
            context = "\n\n".join([d.page_content for d in docs])
            
            per_data["query"] = query
            per_data["idx"] = idx
            per_data["ans_doc"] = context
            per_data["synth_documents"] = await self._generate_synthetic_data(context) # List of Synth Docs
            
            print("Adding Docs to the Vector Store")
            docs = per_data["synth_documents"].copy()
            print("Chunking")
            docs.append(context) # 합성 문서와 실제 문서 합치는 과정
            docs = self.chunker(docs)
            self.add_documents(docs) # 형식화된 document self.vectorstore에 저장
            
            benchmark_data.append(per_data)
            
        print("----- Retrieving Documents -----")
        for row in benchmark_data:
            row["retrieved_docs"] = self.search(row["query"]) # 실제로 검색된 문서
            
        print('benchmark_data: ', benchmark_data)
        return benchmark_data


    async def create_generation_bench_data(self, raw_data: List):
        chain = self.create_chain()
        if chain is None:
            raise ValueError("RAG chain 생성 실패")
        self.chain = chain
        
        benchmark_data = await self.create_retrieval_bench_data(raw_data) # query, idx, 정답텍스트(ans_doc), 정답(으로 간주되는) 임의 문서(synth_documents), 
                                                                          # 예측된 검색 문서(retrieved_docs), 예측 정답 생성(pred_answer)
        print("----- Generating Answers -----")
        print(type(benchmark_data))
        for row in tqdm(benchmark_data):
            result = await chain.ainvoke(

                {
                    "context": str(row.get("ans_doc")),
                    "question": str(row.get("query")),
                    "n": row.get("idx")
                }
            )
            row["pred_answer"] = result

        bench_df = pd.DataFrame(benchmark_data)
        bench_df.to_csv('bench_preprocessed.csv', index=False)
        return benchmark_data
    
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

#############################
    async def send_benchdata(self, eval_api: str, benchdata):
        try:
            for row in benchdata:
                if "retrieved_docs" in row:
                    row["retrieved_docs"] = self._serialize_docs(row["retrieved_docs"])
                if "document" in row:
                    row["document"] = self._serialize_docs(row["document"])

            async with httpx.AsyncClient(timeout=60) as client:
                print('eval_api: ', eval_api)
                response = await client.post(eval_api, json=benchdata) # httpx.post(benchdata)
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
    sample_raw_data = sample_raw_data['samples']
    ## for test
    sample_raw_data = sample_raw_data[:3]
    sample_raw_data[0].keys()

    print("Generating synthetic data...")
    benchmark_data_result = await solver.create_generation_bench_data(sample_raw_data)
    print("Generation complete.")
    print(f'### result \n{benchmark_data_result} ')
    return await solver.send_benchdata(eval_api='http://localhost:8001/evaluate', benchdata=benchmark_data_result)

    # 문서-쿼리 쌍에 대해, 사용자가 사용하고 있는 임베딩 모델 기반의 실제 검색된 문서, 생성된 결과가 짝 지어져야 함

if __name__ == "__main__":
    
    asyncio.run(data_process())