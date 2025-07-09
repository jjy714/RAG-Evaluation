from typing_extensions import TypedDict, List, Dict
from datasets import Dataset


class OverallEvaluationState():
    dataset: Dataset | List
    evaluation_result = Dict