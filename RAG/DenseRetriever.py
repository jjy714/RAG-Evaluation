from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph, state
from langchain_huggingface import HuggingFaceEmbeddings

from embedding import DenseEmbedding, SparseEmbedding
from qdrant_client import QdrantClient, models

import pandas as pd
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
from CONSTANTS import HOST, PORT, COLLECTION_NAME, DENSE_MODEL,DENSE_VECTOR
import uuid
load_dotenv() #환경변수 로드




# dense_model = DenseEmbedding()

class DenseRetriever:
    def __init__(
            self, 
            model: str, 
            collection_name:str, 
            host: Optional[int] = None,
            port: Optional[int] = None,
            ):
        super().__init__()
        self.model = HuggingFaceEmbeddings(model_name=model)
        self.vector_store = QdrantVectorStore.from_existing_collection(
            embedding=self.model,
            collection_name=collection_name,
            host=host,
            port=port,
            retrieval_mode=RetrievalMode.DENSE,
            vector_name=DENSE_VECTOR
        )

    def retrieve(self, query: str, search_type: str="similarity" , k: int=5) -> List[Document]:
        docs = self.vector_store.search(
            query=query,
            search_type=search_type,
            k=k
        )
        return docs

    def load_document(self, document: any):
        try:
            input_doc = Document(page_content = document.content, metadata={"file_name": document.filename, "page": document.page})
            id = str(uuid.uuid4())
            self.vector_store.add_documents(documents=input_doc, ids=id)
        except Exception as e:
            print(f"Error occured while loading file : {document} \n Error: {e}")
    
    def load_documents(self, documents: any):
        docs=[]
        for item in documents:
            try:
                docs.append(
                    Document(page_content = item.content, metadata={"file_name": item.file_name, "page": item.page})
                )
            except Exception as e1:
                print(f"Error occured while loading file : {documents} \n Error: {e1}")
        uuids = [str(uuid.uuid4()) for _ in range(len(documents))]
        try:
            self.vector_store.add_documents(documents=documents, ids=uuids)
        except Exception as e2:
            print(f"Error while adding documents to the Vector DB {e2}")