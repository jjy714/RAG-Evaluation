from .RetrieverEvaluationGraph import create_retrieval_subgraph
from .main_graph import create_main_graph

__any__ = [
    "create_main_graph",
    "create_retrieval_subgraph"
    ]


# krag/__init__.py

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions
    from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("graphs")
except PackageNotFoundError:
    __version__ = "unknown"

