# krag/evaluators.py

from typing import Union, List, Dict, Optional
from enum import Enum
import math
from functools import lru_cache
from krag.document import KragDocument as Document
from korouge_score import rouge_scorer
from kiwipiepy import Kiwi
import numpy as np
import matplotlib.pyplot as plt


from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from sklearn.metrics.pairwise import cosine_similarity


class AveragingMethod(Enum):
    MICRO = "micro"
    MACRO = "macro"
    BOTH = "both"

class MatchingCriteria(Enum):
    ALL = "all"
    PARTIAL = "partial"


class OfflineRetrievalEvaluators:
    def __init__(self, actual_docs: List[List[Document]], predicted_docs: List[List[Document]], 
                 match_method: str = "text", averaging_method: AveragingMethod = AveragingMethod.BOTH, 
                 matching_criteria: MatchingCriteria = MatchingCriteria.ALL) -> None:
        """
        OfflineRetrievalEvaluators 클래스를 초기화합니다.

        Args:
            actual_docs (List[List[Document]]): 실제 문서 리스트의 리스트
            predicted_docs (List[List[Document]]): 예측된 문서 리스트의 리스트
            match_method (str, optional): 문서 매칭 방법. 기본값은 "text"
            averaging_method (AveragingMethod, optional): 결과 평균 계산 방법. 기본값은 AveragingMethod.BOTH
            matching_criteria (MatchingCriteria, optional): 히트로 간주할 기준. 기본값은 MatchingCriteria.ALL

        Raises:
            ValueError: 입력 리스트가 비어있거나 길이가 다를 경우 발생
        """
        if not actual_docs or not predicted_docs:
            raise ValueError("입력 문서 리스트가 비어있을 수 없습니다.")
        if len(actual_docs) != len(predicted_docs):
            raise ValueError("실제 문서 리스트와 예측 문서 리스트의 길이가 같아야 합니다.")
        
        self.actual_docs = actual_docs 
        self.predicted_docs = predicted_docs  
        self.match_method = match_method
        self.averaging_method = averaging_method
        self.matching_criteria = matching_criteria
        self._cache = {}

    @lru_cache(maxsize=1000)
    def text_match(self, actual_text: str, predicted_text: Union[str, List[str]]) -> bool:
        """
        실제 텍스트가 예측 텍스트와 일치하는지 확인합니다.

        Args:
            actual_text (str): 실제 텍스트
            predicted_text (Union[str, List[str]]): 예측 텍스트 또는 텍스트 리스트

        Returns:
            bool: 일치하면 True, 그렇지 않으면 False
        """
        if isinstance(predicted_text, list):
            return any(actual_text in text for text in predicted_text)
        return actual_text in predicted_text


    def calculate_hit_rate(self, k: Optional[int] = None) -> Dict[str, float]:
        """
        검색된 문서의 적중률을 계산합니다.

        Args:
            k (Optional[int], optional): 고려할 상위 문서 수. 기본값은 None

        Returns:
            Dict[str, float]: 적중률 딕셔너리
        """
        hit_count = 0
        for actual_docs, predicted_docs in zip(self.actual_docs, self.predicted_docs):
            predicted_texts = [pred_doc.page_content for pred_doc in predicted_docs[:k]]
            if self.matching_criteria == MatchingCriteria.ALL:
                hit = all(any(self.text_match(actual_doc.page_content, pred_text) for pred_text in predicted_texts) for actual_doc in actual_docs)
            else:  # PARTIAL
                hit = any(any(self.text_match(actual_doc.page_content, pred_text) for pred_text in predicted_texts) for actual_doc in actual_docs)
            hit_count += hit

        hit_rate = hit_count / len(self.actual_docs)
        return {"hit_rate": hit_rate}
    


    def calculate_precision(self, k: Optional[int] = None) -> Dict[str, float]:
        """정밀도 계산"""
        result = {}
        micro_precision = 0
        macro_precisions = []

        for actual_docs, predicted_docs in zip(self.actual_docs, self.predicted_docs):
            k_effective = min(k or len(predicted_docs), len(predicted_docs))
            relevant_count = sum(
                1 for predicted_doc in predicted_docs[:k_effective]
                if any(self.text_match(actual_doc.page_content, predicted_doc.page_content) for actual_doc in actual_docs)
            )
            micro_precision += relevant_count
            macro_precisions.append(relevant_count / k_effective if k_effective > 0 else 0)

        total_predicted = sum(min(k or len(predicted_docs), len(predicted_docs)) for predicted_docs in self.predicted_docs)
        
        if self.averaging_method in [AveragingMethod.MICRO, AveragingMethod.BOTH]:
            result["micro_precision"] = micro_precision / total_predicted if total_predicted > 0 else 0.0
        
        if self.averaging_method in [AveragingMethod.MACRO, AveragingMethod.BOTH]:
            result["macro_precision"] = sum(macro_precisions) / len(macro_precisions) if macro_precisions else 0.0
            
        return result

    def calculate_recall(self, k: Optional[int] = None) -> Dict[str, float]:
        """재현율 계산"""
        result = {}
        micro_recall = 0
        macro_recalls = []

        for actual_docs, predicted_docs in zip(self.actual_docs, self.predicted_docs):
            relevant_count = sum(
                1 for actual_doc in actual_docs
                if any(self.text_match(actual_doc.page_content, pred_doc.page_content) for pred_doc in predicted_docs[:k])
            )
            micro_recall += relevant_count
            macro_recalls.append(relevant_count / len(actual_docs) if actual_docs else 0)

        total_actual = sum(len(actual_docs) for actual_docs in self.actual_docs)
        
        if self.averaging_method in [AveragingMethod.MICRO, AveragingMethod.BOTH]:
            result["micro_recall"] = micro_recall / total_actual if total_actual > 0 else 0.0
        
        if self.averaging_method in [AveragingMethod.MACRO, AveragingMethod.BOTH]:
            result["macro_recall"] = sum(macro_recalls) / len(macro_recalls) if macro_recalls else 0.0
            
        return result
    

    def calculate_f1_score(self, k: Optional[int] = None) -> Dict[str, float]:
        """F1 점수 계산
        
        Args:
            k: 상위 k개 문서 고려

        Returns:
            F1 점수 딕셔너리 
        """
        precision = self.calculate_precision(k)  
        recall = self.calculate_recall(k)

        result = {}
        
        if self.averaging_method in [AveragingMethod.MICRO, AveragingMethod.BOTH]:
            micro_p = precision.get('micro_precision', 0.0)
            micro_r = recall.get('micro_recall', 0.0)
            if micro_p + micro_r > 0:
                result['micro_f1'] = 2 * (micro_p * micro_r) / (micro_p + micro_r)
                
        if self.averaging_method in [AveragingMethod.MACRO, AveragingMethod.BOTH]:
            macro_p = precision.get('macro_precision', 0.0) 
            macro_r = recall.get('macro_recall', 0.0)
            if macro_p + macro_r > 0:
                result['macro_f1'] = 2 * (macro_p * macro_r) / (macro_p + macro_r)

        return result

    def calculate_mrr(self, k: Optional[int] = None) -> Dict[str, float]:
        """
        평균 역순위(Mean Reciprocal Rank, MRR)를 계산합니다.

        Args:
            k (Optional[int], optional): 고려할 상위 문서 수. 기본값은 None

        Returns:
            Dict[str, float]: MRR 점수 딕셔너리
        """
        reciprocal_ranks = []
        for actual_docs, predicted_docs in zip(self.actual_docs, self.predicted_docs):
            for rank, pred_doc in enumerate(predicted_docs[:k], start=1):
                if any(self.text_match(actual_doc.page_content, pred_doc.page_content) for actual_doc in actual_docs):
                    reciprocal_ranks.append(1 / rank)
                    break
            else:
                reciprocal_ranks.append(0)
        
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        return {"mrr": mrr}

    def calculate_map(self, k: Optional[int] = None) -> Dict[str, float]:
        """
        평균 정확도(Mean Average Precision, MAP)를 계산합니다.

        Args:
            k (Optional[int], optional): 고려할 상위 문서 수. 기본값은 None

        Returns:
            Dict[str, float]: MAP 점수 딕셔너리
        """

        average_precisions = []
        for actual_docs, predicted_docs in zip(self.actual_docs, self.predicted_docs):
            relevant_docs = 0
            precision_sum = 0
            for i, pred_doc in enumerate(predicted_docs[:k], start=1):
                if any(self.text_match(actual_doc.page_content, pred_doc.page_content) for actual_doc in actual_docs):
                    relevant_docs += 1
                    precision_sum += relevant_docs / i
            average_precision = precision_sum / len(actual_docs) if actual_docs else 0
            average_precisions.append(average_precision)
        
        map_score = sum(average_precisions) / len(average_precisions) if average_precisions else 0.0
        return {"map": map_score}


    def calculate_ndcg(self, k: Optional[int] = None) -> Dict[str, float]:
        """
        정규화된 할인 누적 이득(Normalized Discounted Cumulative Gain, NDCG)을 계산합니다.

        Args:
            k (Optional[int], optional): 고려할 상위 문서 수. 기본값은 None

        Returns:
            Dict[str, float]: NDCG 점수 딕셔너리
        """
        def dcg(relevances):
            return sum((2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(relevances[:k]))

        ndcg_scores = []
        for actual_docs, predicted_docs in zip(self.actual_docs, self.predicted_docs):
            relevances = [
                1 if any(self.text_match(actual_doc.page_content, pred_doc.page_content) for actual_doc in actual_docs) else 0
                for pred_doc in predicted_docs[:k]
            ]
            ideal_relevances = [1] * len(actual_docs) + [0] * (len(predicted_docs) - len(actual_docs)) # 이상적인 경우는 모든 실제 문서가 관련성이 높다고 가정
            ideal_relevances = ideal_relevances[:k] # k개 문서만 고려

            relevances = relevances[:k] # k개 문서만 고려
            
            dcg_score = dcg(relevances)
            idcg_score = dcg(ideal_relevances)
            
            ndcg_scores.append(dcg_score / idcg_score if idcg_score > 0 else 0)
        
        ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0
        return {"ndcg": ndcg}

    def get_metrics_by_averaging_method(self, k: Optional[int] = None) -> str:
        """
        AveragingMethod에 따라 메트릭을 계산하고 문자열로 반환합니다.

        Args:
            k (Optional[int]): 고려할 상위 문서 수

        Returns:
            str: 포맷팅된 메트릭 결과
        """
        metrics_order = [
            ("Hit Rate", self.calculate_hit_rate),
            ("MRR", self.calculate_mrr),
            ("Recall", self.calculate_recall),
            ("Precision", self.calculate_precision),
            ("F1 Score", self.calculate_f1_score),
            ("MAP", self.calculate_map),
            ("NDCG", self.calculate_ndcg)
        ]

        result_lines = []
        for metric_name, metric_func in metrics_order:
            metric_results = metric_func(k)
            
            if self.averaging_method == AveragingMethod.MICRO:
                filtered_results = {k: v for k, v in metric_results.items() if 'micro' in k or len(metric_results) == 1}
            elif self.averaging_method == AveragingMethod.MACRO:
                filtered_results = {k: v for k, v in metric_results.items() if 'macro' in k or len(metric_results) == 1}
            else:  # BOTH
                filtered_results = metric_results

            result_lines.append(f"{metric_name} @{k}: {filtered_results}")

        return "\n".join(result_lines)

    def visualize_results(self, k: Optional[int] = None):
        # 각 메트릭 결과를 개별적으로 가져오기
        metrics = {
            'Hit Rate': self.calculate_hit_rate(k),
            'MRR': self.calculate_mrr(k),
            'Recall': self.calculate_recall(k),
            'Precision': self.calculate_precision(k),
            'F1': self.calculate_f1_score(k),
            'MAP': self.calculate_map(k),
            'NDCG': self.calculate_ndcg(k)
        }
        
        plt.figure(figsize=(12, 6))
        x = range(len(metrics))
        
        for i, (metric_name, values) in enumerate(metrics.items()):
            if len(values) == 1:
                plt.bar(i, list(values.values())[0], 0.4, label=metric_name, alpha=0.6)
            else:
                if self.averaging_method in [AveragingMethod.BOTH, AveragingMethod.MICRO]:
                    micro_value = next((v for k, v in values.items() if 'micro' in k), None)
                    if micro_value:
                        plt.bar(i - 0.2, micro_value, 0.4, label=f'{metric_name} (Micro)', alpha=0.6)
                
                if self.averaging_method in [AveragingMethod.BOTH, AveragingMethod.MACRO]:
                    macro_value = next((v for k, v in values.items() if 'macro' in k), None)
                    if macro_value:
                        plt.bar(i + 0.2, macro_value, 0.4, label=f'{metric_name} (Macro)', alpha=0.6)

        plt.xlabel('Metrics')
        plt.ylabel('Score')
        plt.title(f'Evaluation Results (k={k if k else "all"})')
        plt.xticks(x, list(metrics.keys()), rotation=45, ha='right')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()




from enum import Enum
from typing import Union, List, Dict, Optional, Callable
from dataclasses import dataclass
from functools import lru_cache

class TokenizerType(Enum):
    WHITESPACE = "whitespace"
    KIWI = "kiwi"
    NLTK = "nltk"

@dataclass
class TokenizerConfig:
    type: TokenizerType
    tokenize_fn: Callable[[str], str]

class RougeOfflineRetrievalEvaluators(OfflineRetrievalEvaluators):
    def __init__(self, 
        actual_docs: List[List[Document]], 
        predicted_docs: List[List[Document]],
        match_method: str = "rouge1",
        averaging_method: AveragingMethod = AveragingMethod.BOTH,
        matching_criteria: MatchingCriteria = MatchingCriteria.ALL,
        threshold: float = 0.5,
        tokenizer: TokenizerType = TokenizerType.KIWI) -> None:        

        """
        RougeOfflineRetrievalEvaluators 클래스를 초기화합니다.

        Args:
            actual_docs (List[List[Document]]): 실제 문서 리스트의 리스트
            predicted_docs (List[List[Document]]): 예측된 문서 리스트의 리스트
            match_method (str, optional): 문서 매칭을 위한 ROUGE 방법. 기본값은 "rouge1"
            averaging_method (AveragingMethod, optional): 결과 평균 계산 방법. 기본값은 AveragingMethod.BOTH
            matching_criteria (MatchingCriteria, optional): 히트로 간주할 기준. 기본값은 MatchingCriteria.ALL
            threshold (float, optional): ROUGE 점수 임계값. 기본값은 0.5
            tokenizer (TokenizerType, optional): 토크나이저 타입. 기본값은 TokenizerType.KIWI
        """

        super().__init__(actual_docs, predicted_docs, match_method, averaging_method, matching_criteria)
        self.threshold = threshold
        self._init_tokenizer(tokenizer)  # TokenizerConfig 초기화
        self.scorer = rouge_scorer.RougeScorer([match_method], use_stemmer=True)


    def _init_tokenizer(self, tokenizer: TokenizerType) -> None:
        if tokenizer == TokenizerType.KIWI:
            self.kiwi = Kiwi()
            self.tokenizer = TokenizerConfig(
                type=TokenizerType.KIWI,
                tokenize_fn=lambda x: " ".join([t.form for t in self.kiwi.tokenize(x)])
            )
        elif tokenizer == TokenizerType.NLTK:
            import nltk
            nltk.download('punkt')
            self.tokenizer = TokenizerConfig(
                type=TokenizerType.NLTK,
                tokenize_fn=lambda x: " ".join(nltk.word_tokenize(x))
            )
        else:
            self.tokenizer = TokenizerConfig(
                type=TokenizerType.WHITESPACE,
                tokenize_fn=lambda x: " ".join(x.split())  # 공백 기준 분할
            )

    @lru_cache(maxsize=1000)
    def text_match(self, actual_text: str, predicted_text: Union[str, List[str]]) -> bool:
        if self.match_method not in ["rouge1", "rouge2", "rougeL"]:
            return super().text_match(actual_text, predicted_text)

        actual_text = self.tokenizer.tokenize_fn(actual_text)
        
        if isinstance(predicted_text, list):
            return any(
                self.scorer.score(actual_text, self.tokenizer.tokenize_fn(text))[self.match_method].fmeasure >= self.threshold 
                for text in predicted_text
            )

        predicted_text = self.tokenizer.tokenize_fn(predicted_text)
        return self.scorer.score(actual_text, predicted_text)[self.match_method].fmeasure >= self.threshold

    def calculate_ndcg(self, k: Optional[int] = None) -> Dict[str, float]:
        def dcg(relevances: List[float]) -> float:
            return sum((2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(relevances[:k]))

        ndcg_scores = []
        for actual_docs, predicted_docs in zip(self.actual_docs, self.predicted_docs):
            actual_contents = [self.tokenizer.tokenize_fn(doc.page_content) for doc in actual_docs]
            predicted_contents = [self.tokenizer.tokenize_fn(doc.page_content) for doc in predicted_docs[:k]]
            
            relevances = [
                max(self.scorer.score(actual_content, pred_content)[self.match_method].fmeasure 
                    for actual_content in actual_contents)
                for pred_content in predicted_contents
            ]
            
            ideal_relevances = sorted(relevances, reverse=True)
            dcg_score = dcg(relevances)
            idcg_score = dcg(ideal_relevances)
            ndcg_scores.append(dcg_score / idcg_score if idcg_score > 0 else 0)

        return {"ndcg": sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0}



class EmbeddingRougeOfflineRetrievalEvaluators(OfflineRetrievalEvaluators):
    def __init__(self, 
                actual_docs: List[List[Document]], 
                predicted_docs: List[List[Document]],
                match_method: str = "rouge1",
                averaging_method: AveragingMethod = AveragingMethod.BOTH,
                matching_criteria: MatchingCriteria = MatchingCriteria.ALL,
                rouge_threshold: float = 0.7,
                similarity_threshold: float = 0.7,
                embedding_type: str = "huggingface",
                embedding_config: dict = None,
                tokenizer: TokenizerType = TokenizerType.KIWI) -> None:
        
        """
        임베딩 기반 필터링이 추가된 ROUGE 평가기 초기화
        
        Args:
            embedding_type (str): 'huggingface', 'openai', 'ollama' 중 선택
            embedding_config (dict): 임베딩 모델 설정
        """
        super().__init__(actual_docs, predicted_docs, match_method, averaging_method, matching_criteria)
        self.rouge_threshold = rouge_threshold
        self.similarity_threshold = similarity_threshold
        self.scorer = rouge_scorer.RougeScorer([match_method], use_stemmer=True)
        self._init_tokenizer(tokenizer)
        
        embedding_config = embedding_config or {}
        if embedding_type == "huggingface":
            default_config = {
                "model_name": "jhgan/ko-sroberta-multitask",
                "model_kwargs": {'device': 'cpu'},
                "encode_kwargs": {'normalize_embeddings': False}
            }
            self.embeddings = HuggingFaceEmbeddings(**{**default_config, **embedding_config})
        elif embedding_type == "openai":
            default_config = {"model": "text-embedding-3-small"}
            self.embeddings = OpenAIEmbeddings(**{**default_config, **embedding_config})
        elif embedding_type == "ollama":
            default_config = {"model": "bge-m3"}
            self.embeddings = OllamaEmbeddings(**{**default_config, **embedding_config})
        else:
            raise ValueError(f"Unsupported embedding type: {embedding_type}")
            
        self._embedding_cache = {}

    def _init_tokenizer(self, tokenizer: TokenizerType) -> None:
        if tokenizer == TokenizerType.KIWI:
            self.kiwi = Kiwi()
            self.tokenizer = TokenizerConfig(
                type=TokenizerType.KIWI,
                tokenize_fn=lambda x: " ".join([t.form for t in self.kiwi.tokenize(x)])
            )
        elif tokenizer == TokenizerType.NLTK:
            import nltk
            nltk.download('punkt')
            self.tokenizer = TokenizerConfig(
                type=TokenizerType.NLTK,
                tokenize_fn=lambda x: " ".join(nltk.word_tokenize(x))
            )
        else:
            self.tokenizer = TokenizerConfig(
                type=TokenizerType.WHITESPACE,
                tokenize_fn=lambda x: " ".join(x.split())  # 공백 기준 분할
            )


    def _get_embedding(self, text: str) -> np.ndarray:
        if text not in self._embedding_cache:
            self._embedding_cache[text] = self.embeddings.embed_query(text)
        return self._embedding_cache[text]
    

    def text_match(self, actual_text: str, predicted_text: Union[str, List[str]]) -> bool:
        actual_text_normalized = self.tokenizer.tokenize_fn(actual_text)
        actual_embedding = self._get_embedding(actual_text)

        if isinstance(predicted_text, list):
            return any(self._compare_texts(actual_text_normalized, actual_embedding, text) for text in predicted_text)
        return self._compare_texts(actual_text_normalized, actual_embedding, predicted_text)

    def _compare_texts(self, actual_text_normalized: str, actual_embedding: np.ndarray, predicted_text: str) -> bool:
        pred_text_normalized = self.tokenizer.tokenize_fn(predicted_text)
        pred_embedding = self._get_embedding(predicted_text)
        
        similarity = cosine_similarity([actual_embedding], [pred_embedding])[0][0]
        if similarity >= self.similarity_threshold:
            rouge_score = self.scorer.score(actual_text_normalized, pred_text_normalized)[self.match_method].fmeasure
            return rouge_score >= self.rouge_threshold
        return False

    def calculate_ndcg(self, k: Optional[int] = None) -> Dict[str, float]:
        def dcg(relevances):
            return sum((2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(relevances[:k]))

        ndcg_scores = []
        for actual_docs, predicted_docs in zip(self.actual_docs, self.predicted_docs):
            actual_contents = [self.tokenizer.tokenize_fn(doc.page_content) for doc in actual_docs]
            predicted_contents = [self.tokenizer.tokenize_fn(doc.page_content) for doc in predicted_docs[:k]]
            
            relevances = []
            for i, pred_content in enumerate(predicted_contents):
                pred_embedding = self._get_embedding(predicted_docs[i].page_content)
                max_relevance = 0
                
                for j, actual_content in enumerate(actual_contents):
                    actual_embedding = self._get_embedding(actual_docs[j].page_content)
                    similarity = cosine_similarity([actual_embedding], [pred_embedding])[0][0]
                    
                    if similarity >= self.similarity_threshold:
                        rouge_score = self.scorer.score(actual_content, pred_content)[self.match_method].fmeasure
                        max_relevance = max(max_relevance, rouge_score)
                
                relevances.append(max_relevance)
            
            ideal_relevances = [1] * len(actual_docs) + [0] * (len(predicted_docs) - len(actual_docs)) # 이상적인 경우는 모든 실제 문서가 관련성이 높다고 가정
            ideal_relevances = ideal_relevances[:k] # k개 문서만 고려

            relevances = relevances[:k] # k개 문서만 고려
            
            dcg_score = dcg(relevances)
            idcg_score = dcg(ideal_relevances)
            ndcg_scores.append(dcg_score / idcg_score if idcg_score > 0 else 0)
        
        return {"ndcg": sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0}