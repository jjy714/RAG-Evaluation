

from typing_extensions import TypedDict, List, Dict
from datasets import Dataset





class GeneratorEvaluationState(TypedDict):
    dataset: Dataset | List
    evaluation_result = Dict

