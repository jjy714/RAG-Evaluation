from langchain_core.documents import Document
from fastapi import File
from datasets import load_dataset
from pathlib import Path
import pandas as pd
import asyncio
from . import datatype_checker



def dataprocess_retrieve(dataset):
    actual_docs = []
    predicted_docs = []
    # datatype_checker()
    df = pd.read_csv(dataset)
    questions = df.loc[:, ["question"]]
    target_docs_names = df.loc[:, "target_file_name"]
    target_docs_names = target_docs_names.values.tolist()
    retrieved_docs = df.loc[
        :,
        [
            "retrieved_doc1",
            "retrieved_doc2",
            "retrieved_doc3",
            "retrieved_doc4",
            "retrieved_doc5",
        ],
    ]
    retrieved_docs = retrieved_docs.values.tolist()

    for content in target_docs_names:
        actual_docs.append([Document(metadata={}, page_content=content)])
    for id, content in enumerate(retrieved_docs):
        temp = []
        for i in content:
            temp.append(Document(metadata={}, page_content=i))
        predicted_docs.append(temp)

    return actual_docs, predicted_docs


def dataprocess_generate(dataset):
    # df = pd.read_csv(dataset)
    # datatype_checker()
    df = pd.read_csv(dataset)
    retrieved_docs = df.loc[
        :,
        [
            "retrieved_doc1",
            "retrieved_doc2",
            "retrieved_doc3",
            "retrieved_doc4",
            "retrieved_doc5",
        ],
    ]
    query = df["question"].to_list()
    reference = df["target_answer"].to_list()
    retrieved_contexts = retrieved_docs
    response = df["response"].to_list()

    return query, reference, retrieved_contexts, response
