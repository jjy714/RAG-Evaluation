# krag/retrievers.py

from langchain_core.runnables import Runnable
from langchain_community.retrievers import BM25Retriever
from typing import List
from krag.tokenizers import KiwiTokenizer   
from krag.document import KragDocument as Document

class KiWiBM25RetrieverWithScore(Runnable):
    def __init__(self, documents, kiwi_tokenizer: KiwiTokenizer = None, k: int = None, threshold: float = 0.0):
        self.documents = documents
        self.kiwi_tokenizer = kiwi_tokenizer
        self.k = k if k is not None else 4
        self.threshold = threshold

        if self.kiwi_tokenizer is None:
            self.bm25_retriever = BM25Retriever.from_documents(documents=self.documents)
        else:
            self.bm25_retriever = BM25Retriever.from_documents(
                documents=self.documents,
                preprocess_func=self._tokenize
            )

    def _tokenize(self, text: str) -> List[str]:
        if self.kiwi_tokenizer is None:
            return text.split()
        else:
            return [t.form for t in self.kiwi_tokenizer.tokenize(text)]

    def _retireve_bm25_with_score(self, query: str) -> List[dict]:
        self.bm25_retriever.k = self.k
        retrieved_docs = self.bm25_retriever.invoke(query)

        tokenized_query = self._tokenize(query)
        
        doc_scores = self.bm25_retriever.vectorizer.get_scores(tokenized_query)
        doc_scores_sorted = sorted(enumerate(doc_scores), key=lambda x: x[1], reverse=True)

        new_docs = []
        for i, doc in enumerate(retrieved_docs):
            new_doc = Document(page_content=doc.page_content, metadata=doc.metadata)
            new_doc.metadata["bm25_score"] = doc_scores_sorted[i][1]
            new_docs.append(new_doc)
        
        return [doc for doc in new_docs if doc.metadata["bm25_score"] > self.threshold]

    def invoke(self, query: str, config=None) -> List[dict]:
        return self._retireve_bm25_with_score(query)
