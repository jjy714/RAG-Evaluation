from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import AspectCritic
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from datasets import load_dataset, Dataset
from tqdm import tqdm
from openai import OpenAI
import asyncio

from dotenv import load_dotenv
import json
import os

load_dotenv()

LLM_URL = os.getenv("LLM_URL")
LLM_NAME = os.getenv("LLM_NAME")



eval_dataset = load_dataset("allganize/RAG-Evaluation-Dataset-KO",split="test")


client = ChatOpenAI(
        model=LLM_NAME,
        base_url=LLM_URL,
        api_key="token-123"
        )

model_output = []
with open("data/RAG-Evaluation-Dataset-KO_ans.jsonl", "r") as f:
    model_output = [json.loads(line) for line in f]


def format_data(example, model_ans):
    # domain = example.get("domain")
    # question= example.get("question")
    target_answer=example["target_answer"]
    model_answer = model_ans[0]
    model_answer = model_answer.replace("<think>\n\n</think>\n\n", "")

    return {"model_answer" : model_answer, "target_answer": target_answer}


eval_data = eval_dataset.map(format_data, fn_kwargs={"model_ans": model_output} )
eval_dataset = EvaluationDataset.from_hf_dataset(eval_data)



print("Features in dataset:", eval_dataset.features())
print("Total samples in dataset:", len(eval_dataset))



evaluator_llm = LangchainLLMWrapper(
    ChatOpenAI(
        model=LLM_NAME,
        base_url=LLM_URL,
        api_key="token-123"
        )
    )
evaluator_embeddings = LangchainEmbeddingsWrapper(
    OpenAIEmbeddings(
            model=LLM_NAME,
            base_url=LLM_URL,
            api_key="token-123"
    )
)


async def run_metrics():

    metric_1 = AspectCritic(name="answer_similarity",llm=evaluator_llm, definition="Verify if the answer is similar.")
    metric_2 = AspectCritic(name="answer_correctness",llm=evaluator_llm, definition="Verify if the answer is correct.")
    # test_data = SingleTurnSample(**test_data)
    # result = await metric.single_turn_ascore(test_data)
    
    print(f"Evaluation Result for '{eval_dataset}':")
    results = evaluate(eval_dataset, metrics=[metric_1, metric_2])
    print(results)
    with open("results/eval_result.txt", "w") as w:
        w.write(results.scores)
asyncio.run(run_metrics())


