
# we are going to create a dataclass that subclasses `MetricWithLLM` and `SingleTurnMetric`
from dataclasses import dataclass, field

# import the base classes
from ragas.metrics.base import MetricWithLLM, SingleTurnMetric, MetricType
from ragas.metrics import Faithfulness

# import types
import typing as t
from ragas.callbacks import Callbacks
from ragas.dataset_schema import SingleTurnSample


@dataclass
class HallucinationsMetric(MetricWithLLM, SingleTurnMetric):
    # name of the metric
    name: str = "hallucinations_metric"
    # we need to define the required columns for the metric
    _required_columns: t.Dict[MetricType, t.Set[str]] = field(
        default_factory=lambda: {
            MetricType.SINGLE_TURN: {"user_input", "response", "retrieved_contexts"}
        }
    )

    def __post_init__(self):
        # init the faithfulness metric
        self.faithfulness_metric = Faithfulness(llm=self.llm)

    async def _single_turn_ascore(
        self, sample: SingleTurnSample, callbacks: Callbacks
    ) -> float:
        faithfulness_score = await self.faithfulness_metric.single_turn_ascore(
            sample, callbacks
        )
        return 1 - faithfulness_score