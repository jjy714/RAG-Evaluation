from datasets import load_dataset
from langchain_openai import ChatOpenAI
from tqdm import tqdm
import json
import os
from dotenv import load_dotenv

LLM_NAME = os.getenv("LLM_NAME")
LLM_URL = os.getenv("LLM_URL")

eval_dataset = load_dataset("allganize/RAG-Evaluation-Dataset-KO",split="test")


client = ChatOpenAI(
        model=LLM_NAME,
        base_url=LLM_URL,
        api_key="token-123"
        )
temp_questions = eval_dataset['question']

with open("data/RAG-Evaluation-Dataset-KO_ans.jsonl", "a", encoding="utf-8") as f:
    for idx, que in enumerate(tqdm(temp_questions)):
        que = que + " /no_think"
        model_output=client.invoke(que)
        model_output = {idx + 1: model_output.content}
        json.dump(model_output, f, ensure_ascii=False)
        f.write("\n")