from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import NoiseSensitivity

async def noise_sensitivity():
    sample = SingleTurnSample(
        user_input="What is the Life Insurance Corporation of India (LIC) known for?",
        response="The Life Insurance Corporation of India (LIC) is the largest insurance company in India, known for its vast portfolio of investments. LIC contributes to the financial stability of the country.",
        reference="The Life Insurance Corporation of India (LIC) is the largest insurance company in India, established in 1956 through the nationalization of the insurance industry. It is known for managing a large portfolio of investments.",
        retrieved_contexts=[
            "The Life Insurance Corporation of India (LIC) was established in 1956 following the nationalization of the insurance industry in India.",
            "LIC is the largest insurance company in India, with a vast network of policyholders and huge investments.",
            "As the largest institutional investor in India, LIC manages substantial funds, contributing to the financial stability of the country.",
            "The Indian economy is one of the fastest-growing major economies in the world, thanks to sectors like finance, technology, manufacturing etc."
        ]
    )

    scorer = NoiseSensitivity(llm=evaluator_llm)
    await scorer.single_turn_ascore(sample)