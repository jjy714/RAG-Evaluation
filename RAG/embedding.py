from fastembed import LateInteractionTextEmbedding, SparseTextEmbedding
from FlagEmbedding import BGEM3FlagModel
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from kiwipiepy import Kiwi

DENSE_MODEL = "BAAI/bge-m3"
SPARSE_MODEL = "Qdrant/bm25"
LATE_INTERATCION_MODEL = "jinaai/jina-colbert-v2"


class DenseEmbedding:
    def __init__(self):
        self.embed_model = BGEM3FlagModel(DENSE_MODEL, use_fp16=False)

    def embed(self, text: str) -> list[float]:
        embedded_text = self.embed_model.encode(text).get("dense_vecs")
        return embedded_text

    def query_embed(self, text: str) -> list[float]:  # embed 함수와 동일
        return self.embed(text)

class LangChainDenseEmbedding:
    def __init__(self):
        self.embed_model = HuggingFaceBgeEmbeddings(DENSE_MODEL)

    def embed(self, text: str) -> list[float]:
        embedded_text = self.embed_model.encode(text).get("dense_vecs")
        return embedded_text

    def query_embed(self, text: str) -> list[float]:  # embed 함수와 동일
        return self.embed(text)



class SparseEmbedding:
    def __init__(self):
        self.tokenizer = Kiwi()
        self.embed_model = SparseTextEmbedding(SPARSE_MODEL)

    def _tokenize(self, text: str) -> str:
        tokens = self.tokenizer.tokenize(text)
        tokenized_text = " ".join(
            [token.form for token in tokens if token.tag in ("NNG", "NNP", "SN", "SL")]
        )
        return tokenized_text

    def embed(self, text: str) -> dict:
        tokenized_text = self._tokenize(text)
        embedded_text = next(self.embed_model.embed(tokenized_text))
        return embedded_text.as_object()

    def query_embed(self, text: str) -> dict:
        tokenized_text = self._tokenize(text)
        embedded_text = next(self.embed_model.query_embed(tokenized_text))
        return embedded_text.as_object()

class SparseEmbedding:
    def __init__(self):
        self.tokenizer = Kiwi()
        self.embed_model = SparseTextEmbedding(SPARSE_MODEL)

    def _tokenize(self, text: str) -> str:
        tokens = self.tokenizer.tokenize(text)
        tokenized_text = " ".join(
            [token.form for token in tokens if token.tag in ("NNG", "NNP", "SN", "SL")]
        )
        return tokenized_text

    def embed(self, text: str) -> dict:
        tokenized_text = self._tokenize(text)
        embedded_text = next(self.embed_model.embed(tokenized_text))
        return embedded_text.as_object()

    def query_embed(self, text: str) -> dict:
        tokenized_text = self._tokenize(text)
        embedded_text = next(self.embed_model.query_embed(tokenized_text))
        return embedded_text.as_object()


class LateInteractionEmbedding:
    def __init__(self):
        self.embed_model = LateInteractionTextEmbedding(LATE_INTERATCION_MODEL)

    def embed(self, text: str) -> list[list[float]]:
        embedded_text = next(self.embed_model.embed(text))
        return embedded_text

    def query_embed(self, text: str) -> list[list[float]]:
        embedded_text = next(self.embed_model.query_embed(text))
        return embedded_text
