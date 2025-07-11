from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph

from qdrant_client import QdrantClient

from typing_extensions import List, TypedDict
from dotenv import load_dotenv
import os 

load_dotenv()

LLM_URL = os.getenv("LLM_URL")
LLM_NAME = os.getenv("LLM_NAME")
LLM_API_KEY = os.getenv("LLM_API_KEY")

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class Generator:

    def __init__(
        self, 
        model: str,
        base_url: str,
        azure_deployment_name: str,
        azure_api_name: str
        ):
        
        if "azure" in model:
            self.client = AzureChatOpenAI(
                azure_deployment=azure_deployment_name,  # or your deployment
                api_version=azure_api_name,  # or your api version
                temperature=0.01,
                )
        else: 
            self.client = ChatOpenAI(
                model=LLM_NAME,
                base_url=LLM_URL,
                api_key=LLM_API_KEY
            )

    async def generate(self, state: State):
        docs_content = state.get("data")
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        response = self.client.ainvoke(docs_content)
        return {"answer": response.content}








