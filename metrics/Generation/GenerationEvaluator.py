from typing import Dict, List
from .BLEU import bleu
from .ROUGE import rouge
from .faithfulness import faithfulness
from string_similarity import string_similarity
from BertScore import bert_score
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from pathlib import Path
from dotenv import load_dotenv          
import os


# SingleTurnSample(user_input=q, response=a, retrieved_contexts=r)
# response: List, retrieved_documents:List
env_path = Path('.').resolve().parent.parent
load_dotenv(env_path)

AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")


class GenerationEvaluator:

    def __init__(
            self,
            user_input: List[str],
            reference: List[List[Document]],
            retrieved_contexts: List[List[Document]],
            response: List[str],
            model: str
            ):
        self.user_input = user_input
        self.reference = reference
        self.retrieved_contexts = retrieved_contexts
        self.response = response
        if "azure" in model: # LLM-as-Judge Evaluator
            self.model = AzureChatOpenAI(
                azure_deployment=AZURE_DEPLOYMENT_NAME,  # or your deployment
                api_version=AZURE_API_VERSION,  # or your api version
                temperature=0,
                )
        else:
            self.model = ChatOpenAI(model="Qwen3-30B-A3B",base_url="http://localhost:8000/v1", api_key="token-123")


    def bleu(self) -> Dict[str, float]:
        return bleu(self.response, self.reference)

    def rouge(self) -> Dict[str, float]:
        return rouge(self.response, self.reference)

    def faithfulness(self) -> Dict[str, float]:
        return faithfulness(
            llm=self.model, 
            user_input=self.user_input, 
            response=self.response, 
            retrieved_contexts=self.retrieved_contexts
            )

    def string_similarity(self):
        pass

    def bert_score(self):
        pass