from typing import List, Dict, Optional
from langchain_core.documents import Document
from abc import ABC, abstractmethod


class Retriever(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def retrieve(self, query: str) -> List[Document]:
        return

    @abstractmethod
    def load_document(self):
        return


