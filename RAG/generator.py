from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph

from qdrant_client import QdrantClient

from typing_extensions import List, TypedDict
from dotenv import load_dotenv
import os 

load_dotenv

LLM_URL = os.getenv("LLM_URL")
LLM_NAME = os.getenv("LLM_NAME")
LLM_API_KEY = os.getenv("LLM_API_KEY")


class Generator:

    def __init__(self, model:str, base_url: str, api_key: str):
        self.client = ChatOpenAI(
            model=LLM_NAME,
            base_url=LLM_URL,
            api_key=LLM_API_KEY
        )

# client = 

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str





def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = client.invoke(messages)
    return {"answer": response.content}



