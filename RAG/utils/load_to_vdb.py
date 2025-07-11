import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List
import pandas as pd
from qdrant_client.models import PointStruct
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_huggingface import HuggingFaceEmbeddings
from RAG.utils.embedding import DenseEmbedding, LateInteractionEmbedding, SparseEmbedding

dense_model = DenseEmbedding()
sparse_model = SparseEmbedding()
late_interaction_model = LateInteractionEmbedding()

from qdrant_client import QdrantClient, models

HOST = "localhost"
PORT = 6333
COLLECTION_NAME = "RAG_evaluation_test"

DENSE_VECTOR = "dense"
DENSE_MODEL = "BAAI/bge-m3"
SPARSE_VECTOR = "sparse"
LATE_INTERACTION_VECTOR = "late_interaction"


dense_model = HuggingFaceEmbeddings(
    model_name=DENSE_MODEL,
    model_kwargs = {'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

client = QdrantClient(host=HOST, port=PORT)
first = False 

# 콜렉션 생성(한 번만)
if first: 
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            DENSE_VECTOR: models.VectorParams(
                size=1024,  # size of each vector produced by ColBERT
                distance=models.Distance.COSINE,  # similarity metric between each vector
            ),
            LATE_INTERACTION_VECTOR: models.VectorParams(
                size=128,  # size of each vector produced by ColBERT
                distance=models.Distance.COSINE,  # similarity metric between each vector
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM  # similarity metric between multivectors (matrices)
                ),
            ),
        },
        sparse_vectors_config={
            SPARSE_VECTOR: models.SparseVectorParams(),
        },
    )

dense_qdrant = QdrantVectorStore.from_existing_collection(
    embedding=dense_model,
    collection_name=COLLECTION_NAME,
    host=HOST,
    port=PORT,
    vector_name=DENSE_VECTOR
)

sparse_qdrant = QdrantVectorStore.from_existing_collection(
    collection_name=COLLECTION_NAME,
    host=HOST,
    port=PORT,
    sparse_vector_name="sparse",
    sparse_embedding=sparse_embeddings,
    retrieval_mode=RetrievalMode.SPARSE,
)

def langchain_load_vectordb(data, vector_store) -> List:
    documents = []
    file_name = data.file_name[0]
    for idx, (page,content) in enumerate(zip(data.page, data.content)):
        documents.append(
            Document(page_content = content, metadata={"file_name": file_name, "page": page})
        )
    uuids = [str(uuid.uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    return documents

def embed_and_load_to_vectordb(data: pd.DataFrame):
    file_name = data.file_name[0]
    for idx, (page,content,) in enumerate(zip(data.page,data.content,)):
        start_time = datetime.now()
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector={
                DENSE_VECTOR: dense_model.embed(content),
                SPARSE_VECTOR: sparse_model.embed(content),
                LATE_INTERACTION_VECTOR: late_interaction_model.embed(content),
            },
            payload={"file_name": file_name, "page": page, "content": content},
        )

        client.upsert(collection_name=COLLECTION_NAME, points=[point])
        print(f">> {file_name}_{idx}: {datetime.now() - start_time}")


base_file_path = Path.joinpath(Path('.').parent, "data/outputs")
input_files = [file_name for file_name in os.listdir(base_file_path) if file_name.endswith((".csv"))]

total_start_time = datetime.now()
for file_name in input_files:
    try:
        file_path = os.path.join(base_file_path, file_name)
        data = pd.read_csv(file_path)
        langchain_load_vectordb(data, sparse_qdrant)
        print(f"::::::::: Complete: {file_name} :::::::::", end="\n\n")
    except Exception as e:
        print(f"::::::::: Error: {file_name} :::::::::", end="\n\n")
        print(e)
print(f"Total Running Time: {datetime.now() - total_start_time}")