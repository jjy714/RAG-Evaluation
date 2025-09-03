import asyncio
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
from fastapi import FastAPI, APIRouter
import httpx 

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
        self.router = APIRouter()
        self.router.add_api_route("/get-raw", self.receieve_rawdata, methods=["GET"])
        self.kwargs = kwargs
        
        self.app = FastAPI()
        self.app.include_router(self.router)


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
                    "context": retriever | format_docs,
                    "question": RunnablePassthrough(),
                }
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
        return self.vector_store.add_documents(documents=self._to_documents(documents))

    def search(self, query: str) -> List[Document]:
        k=self.kwargs.get('k', 5)
        return self.vector_store.similarity_search(query, k=k)

    async def _generate_synthetic_data(self, context: str):
        buffer_k = self.kwargs.get("buffer_k", 5)
        if not self.chain:
            print("Synthesis chain is not initialized. Cannot generate data.")
            return []
        synthetic_docs = []
        with open(Path(__file__).parent.resolve(), "rb") as prompt:
            for _ in range(buffer_k):
                temp = []
                synthetic_doc = self.llm_model.chat.completions.create(
                    {
                        "role" : "system",
                        "context": prompt.format(context=context)
                        },
                    {
                        "role": "user",
                        "content" : "Create Data ... "
                    }
                    )
                temp.append(synthetic_doc)
                synthetic_docs.append(temp)
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
            per_data["synth_documents"] = self._generate_synthetic_data(raw_data=context, buffer_k=buffer_k) # List of Synth Docs
            
            print("Adding Docs to the Vector Store")
            docs = per_data["synth_documents"].copy()
            print("Chunking")
            docs.append(context)
            docs = self.chunker(docs)
            self.add_documents(docs)
            
            benchmark_data.append(per_data)
            
        print("----- Retrieving Documents -----")
        for row in benchmark_data:
            row["retrieved_docs"] = self.search(row["query"])
            
        
        return benchmark_data


    async def create_generation_bench_data(self, raw_data: List, buffer_k=5):
        
        if not self.create_chain:
            raise ValueError
        else:
            chain = self.create_chain()
        
        benchmark_data = self.create_retrieval_bench_data(raw_data, buffer_k=buffer_k)
        
        print("----- Generating Answers -----")
        
        for row in tqdm(benchmark_data):
            result = await chain.ainvoke(
                {
                    "context": row.get("ans_doc", ""),
                    "question": row.get("query", "")
                }
            )
            row["pred_answer"] = result
        return benchmark_data




########################################



    def receieve_rawdata(self):
        pass

    def send_benchdata(self, eval_api: str, benchdata):
        try:
            response = httpx.post(benchdata)
        except ConnectionError as ce: 
            yield {"status" : "fail", "error" :  ce}
        except TimeoutError as te: 
            yield {"status" : "fail", "error" :  te}
            
        return response



########################################
async def main():

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    llm = ChatOpenAI(
        model="gemma",
        api_key="token-123",
        base_url="http://localhost:8000/v1",
    )

    solver = DataPreprocessor(embedding_model=embeddings, llm_model=llm)

    sample_raw_data = [
        {
            "document": [Document(page_content="The sky is blue.")],
            "query": "What color is the sky?",
        },
        {
            "document": [
                Document(
                    page_content="Photosynthesis is the process used by plants to convert light energy into chemical energy."
                )
            ],
            "query": "What is photosynthesis?",
        },
    ]

    print("Generating synthetic data...")
    synthetic_results = await solver.generate_synthetic_data(sample_raw_data)
    print("Generation complete.")
    print(synthetic_results)


if __name__ == "__main__":
    asyncio.run(main())
