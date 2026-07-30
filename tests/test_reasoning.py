from ai_engine.reasoning.reasoning_engine import ReasoningEngine


def main():
    engine = ReasoningEngine()

    context = """
Retrieval-Augmented Generation (RAG) retrieves relevant documents before generating a response.
It reduces hallucinations by grounding answers in retrieved information.
It improves factual accuracy by providing the language model with relevant context.
"""

    queries = [
        "What is Retrieval-Augmented Generation?",
        "Why is RAG better than using only an LLM?",
        "Explain Reinforcement Learning."
    ]

    for query in queries:
        print("=" * 60)
        print(f"Question: {query}\n")

        answer = engine.reason(query, context)

        print("Answer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()