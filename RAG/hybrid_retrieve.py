from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from CONSTANTS import HOST, PORT, COLLECTION_NAME, DENSE_VECTOR, DENSE_MODEL, SPARSE_VECTOR
from pathlib import Path
from datetime import datetime
import pandas as pd




sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
dense_model = HuggingFaceEmbeddings(
    model_name=DENSE_MODEL,
    model_kwargs = {'device': 'cpu'},
    encode_kwargs = {'normalize_embeddings': False}
)
qdrant = QdrantVectorStore.from_existing_collection(
    embedding=dense_model,
    sparse_embedding=sparse_embeddings,
    collection_name=COLLECTION_NAME,
    host=HOST,
    port=PORT,
    retrieval_mode=RetrievalMode.HYBRID,
    vector_name=DENSE_VECTOR,
    sparse_vector_name=SPARSE_VECTOR
)


dataset_name = "data/new_rag-eval-ko-dataset-public.csv"
path = Path('.').parent 
dataset_path = path / dataset_name
dataset = pd.read_csv(dataset_path)
query = "model loading"

for idx, query in enumerate(dataset.question):
    start_time = datetime.now()
    # VectorDB 검색
    print(f"QUERY {idx+1} : {query}")
    docs = qdrant.search(
        query=query,
        search_type="similarity",
        k=5
    )
    print(f"TOP 1 RETRIEVED PAGE: {docs[0].metadata.get("file_name")}")

    # 검색결과저장
    for p_idx, point in enumerate(docs):
        _payload: Document = point
    end_time = datetime.now()
    latency_secs = float(f"{(end_time - start_time).total_seconds():.4f}")
    # print(f">> Complete Question {idx + 1:02} / Latency: {latency_secs