# krag/utils.py

from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
from langchain.retrievers import EnsembleRetriever
from krag.document import KragDocument as Document
from krag.evaluators import OfflineRetrievalEvaluators, RougeOfflineRetrievalEvaluators, AveragingMethod, MatchingCriteria
import matplotlib.pyplot as plt
import seaborn as sns
import math
from tqdm.auto import tqdm


def context_to_document(df_test: pd.DataFrame, idx: int) -> List[Document]:
    """
    테스트 데이터셋의 특정 행에 있는 컨텍스트 데이터를 Document 객체 리스트로 변환
    """

    context = eval(df_test['context'].iloc[idx])
    source = eval(df_test['source'].iloc[idx])
    doc_id = eval(df_test['doc_id'].iloc[idx])

    context_docs = []
    for c, s, d in zip(context, source, doc_id):
        doc = Document(page_content=c, metadata={'source': s, 'doc_id': d})
        context_docs.append(doc)

    return context_docs


def setup_retriever(retriever: Any, k: int) -> Any:
    """검색기를 설정하는 헬퍼 함수"""
    retriever_type = str(type(retriever)).lower()
    try:
        if "vectorstores" in retriever_type:
            retriever.search_kwargs['k'] = k
        elif "bm25" in retriever_type:
            retriever.k = k
        elif "multi_query" in retriever_type:
            retriever.retriever.search_kwargs['k'] = k
        elif "runnables" in retriever_type:
            return retriever.with_config({"configurable": {"search_kwargs": {"k": k}}})
        return retriever
    except Exception as e:
        print(f"Error setting up retriever: {e}")
        return retriever

def flatten_metrics(metrics: Dict[str, Any], k: int) -> Dict[str, float]:
    """메트릭 딕셔너리를 평탄화하는 함수"""
    flattened = {}
    for key, value in metrics.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flattened[f"{sub_key}@{k}"] = sub_value
        else:
            flattened[f"{key}@{k}"] = value
    return flattened





def evaluate_retrieval_at_K(
    df_qa_test: pd.DataFrame,
    k: int,
    retrievers: Dict[str, Any],
    ensemble: bool = False,
    rouge_method: Optional[str] = None,
    threshold: float = 0.5,
    ensemble_weights: Optional[List[float]] = None,
    averaging_method: AveragingMethod = AveragingMethod.BOTH,
    matching_criteria: MatchingCriteria = MatchingCriteria.PARTIAL
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    k 값에 따른 검색 성능 평가 지표를 계산합니다.

    Args:
        df_qa_test (pd.DataFrame): 테스트 데이터 프레임
        k (int): 상위 k개 문서
        retrievers (Dict[str, Any]): 검색기 딕셔너리
        ensemble (bool): 앙상블 검색 사용 여부
        rouge_method (Optional[str]): ROUGE 평가 방법 ("rouge1", "rouge2", "rougeL")
        threshold (float): ROUGE 임계값
        ensemble_weights (Optional[List[float]]): 앙상블 검색기 가중치
        averaging_method (AveragingMethod): 평균 계산 방법
        matching_criteria (MatchingCriteria): 매칭 기준

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (평균 평가지표 데이터프레임, 개별 평가지표 데이터프레임)
    """
    set_retrievers = {key: setup_retriever(retriever, k) for key, retriever in retrievers.items()}

    if ensemble:
        ensemble_retrievers = list(set_retrievers.values())
        weights = ensemble_weights or [1/len(ensemble_retrievers)] * len(ensemble_retrievers)
        set_retrievers["Ensemble"] = EnsembleRetriever(retrievers=ensemble_retrievers, weights=weights)

    print("Evaluating retrieval performance...")
    print(f"ROUGE method: {rouge_method}, threshold: {threshold}, averaging method: {averaging_method}, matching criteria: {matching_criteria}")
    print(f"Ensemble: {ensemble}, Ensemble weights: {ensemble_weights}")
    print(f"Number of questions: {len(df_qa_test)}")

    outputs = []
    for idx, row in tqdm(df_qa_test.iterrows(), total=len(df_qa_test), desc="Processing questions"):
        question = row['question']
        context_docs = context_to_document(df_qa_test, idx)

        for retriever_key, retriever in set_retrievers.items():
            try:
                retrieved_docs = retriever.invoke(question)

                evaluator_class = RougeOfflineRetrievalEvaluators if rouge_method and 'rouge' in rouge_method else OfflineRetrievalEvaluators
                evaluator = evaluator_class(
                    actual_docs=[context_docs],
                    predicted_docs=[retrieved_docs],
                    match_method=rouge_method or "text",
                    threshold=threshold,
                    averaging_method=averaging_method,
                    matching_criteria=matching_criteria
                )

                metrics = {
                    "hit_rate": evaluator.calculate_hit_rate(k),
                    "mrr": evaluator.calculate_mrr(k),
                    "recall": evaluator.calculate_recall(k),
                    "precision": evaluator.calculate_precision(k),
                    "f1": evaluator.calculate_f1_score(k),
                    "map": evaluator.calculate_map(k),
                    "ndcg": evaluator.calculate_ndcg(k)
                }

                flattened_metrics = flatten_metrics(metrics, k)

                outputs.append({
                    "question": question,
                    "retriever": retriever_key,
                    **flattened_metrics
                })
            except Exception as e:
                print(f"Error evaluating retriever {retriever_key} for question '{question}': {e}")

    df_output = pd.DataFrame(outputs)
    df_mean = df_output.groupby('retriever').mean(numeric_only=True)

    print("Evaluation complete.")
    
    return df_mean, df_output





def visualize_retrieval_at_K(df_mean: pd.DataFrame, k: int):
    """
    각 지표별로 검색기 성능을 비교하는 시각화를 생성합니다.
    
    Args:
        df_mean (pd.DataFrame): 평균 평가지표 데이터프레임
        k (int): 상위 k개 문서
    """
    metrics = [col for col in df_mean.columns if f'@{k}' in col]
    n_metrics = len(metrics)
    
    # 서브플롯 레이아웃 계산
    n_cols = 5  # 한 행에 표시할 그래프 수
    n_rows = math.ceil(n_metrics / n_cols)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
    fig.suptitle(f'Retrieval Performance Metrics @{k}', fontsize=16, y=1.02)
    
    for i, metric in enumerate(metrics):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col] if n_rows > 1 else axes[col]
        
        sns.barplot(x=df_mean.index, y=df_mean[metric], ax=ax)
        ax.set_title(metric.split('@')[0], pad=20)
        ax.set_xlabel('')
        ax.set_ylabel('Score')
        ax.tick_params(axis='x', rotation=45)
        
        # 바 위에 값 표시
        for j, v in enumerate(df_mean[metric]):
            ax.text(j, v, f'{v:.2f}', ha='center', va='bottom')
        
        # y축 범위 설정 (0부터 시작, 약간의 여유 추가)
        ax.set_ylim(0, min(1, df_mean[metric].max() * 1.1))
    
    # 사용하지 않는 서브플롯 제거
    for i in range(n_metrics, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        fig.delaxes(axes[row, col] if n_rows > 1 else axes[col])
    
    plt.tight_layout()
    plt.show()