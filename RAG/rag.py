import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langgraph.graph import START, StateGraph, END
from typing_extensions import List, TypedDict
from RAG.Retrieval.DenseRetriever import DenseRetriever
from RAG.Retrieval.SparseRetriever import SparseRetriever
from Generation import Generator
import os
from time import sleep
from RAG.utils.CONSTANTS import (
    HOST, 
    PORT, 
    COLLECTION_NAME, 
    DENSE_MODEL, 
    SPARSE_MODEL, 
    LLM_NAME, 
    LLM_URL, 
    LLM_API_KEY
    )

"""
QUERY 1 : 국세수입 담당부서와 담당자는 누구인가요?
TOP 1 RETRIEVED PAGE: (240411보도자료) 재정동향 4월호.pdf
QUERY 2 : 2024년 1월, 2월, 3월 각각의 평균 조달금리와 응찰률이 어떻게 되나요?
TOP 1 RETRIEVED PAGE: (240411보도자료) 재정동향 4월호.pdf
QUERY 3 : 2023년에 비해 2027년에 의무지출의 비중이 얼마나 늘어난 것인가?
TOP 1 RETRIEVED PAGE: 2023_2027 국가재정운용계획 주요내용.pdf
QUERY 4 : 불요불급한 자산을 처분하여 회수하는 자금은 어떻게 활용되는지, 그리고 공공기관의 재무건전성 관리 강화를 위해 '22~'26년 재정건전화계획 수정계획을 수립하는 것 외에 어떤 방법이 적용되는지 설명해주세요.
TOP 1 RETRIEVED PAGE: 2023_2027 국가재정운용계획 주요내용.pdf
QUERY 5 : 2023년 국가재정운용계획 수립 절차 중, 분야별·지역별 예산협의회 및 간담회 개최 시기와 국회 제출 시기는 언제인가요?
TOP 1 RETRIEVED PAGE: 2023_2027 국가재정운용계획 주요내용.pdf

"""
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# @TODO Create Subgraph for iteration.



# initialize Retriever / Generator 
dense_retriver = DenseRetriever(
    model= DENSE_MODEL,
    collection_name=COLLECTION_NAME,
    host=HOST,
    port=PORT
    )
sparse_retriever = SparseRetriever(
    model=SPARSE_MODEL,
    collection_name=COLLECTION_NAME,
    host=HOST,
    port=PORT
)
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_VERSION=os.getenv("AZURE_API_VERSION")



class RAGState(TypedDict):
    iteration: int
    question: str
    context: List[Document]
    rerank: bool
    answer: str

    output: List

from datasets import load_dataset

ds = load_dataset("allganize/RAG-Evaluation-Dataset-KO")

# Define application steps
def retrieve(state: RAGState):
    print(f"---------Node: Retrieve-----------")
    retrieved_docs = dense_retriver.retrieve(state["question"], k=5)
    with open("data/RAG_retrieved_file.csv") as f:
        f.write()
    sleep(5)
    print("Retrieval Complete")
    return {"context": retrieved_docs}

def rerank(state: RAGState):
    pass

def do_rerank(state: RAGState):
    """
    Condition: 
        Human Input: if human decides the document is not accurate, return true
        AI Input: If LLM model decides the document is not accurate enough, return true
        else:
            return False
    """
    return False

def generate(state: RAGState):
    print(f"---------Node: Generate-----------")
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    input_string = f"""
    ###Question
    {state['question']}
    ###Context
    {docs_content}
    ###Answer

    """
    response = llm.invoke(input_string)
    sleep(5)
    print("Generation Complete")
    return {"answer": response.content}


# Compile application and test
def create_rag_graph():
    graph_builder = StateGraph(RAGState).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    # graph_builder.add_conditional_edges(
    #     "source_node",
    #     "do_rerank",
    #     {
    #         "ndition1": "rerank",
    #         "default": "generate"
    #     }
    # )
    graph_builder.add_edge("retrieve", END)
    return graph_builder.compile()


async def run():
    graph = create_rag_graph()
    response = await graph.ainvoke()




# Define state for application

    
    # while True:
    #     try:
    #         user_query = input("Question? : ")
    #         if "quit" in user_query:
    #             break
    #         response = graph.invoke({"question": user_query})
    #         print(f"LLM Response: {response["answer"]}")
    #     except Exception as e:
    #         assert(e)


# if __name__ == '__main__':
#     run()