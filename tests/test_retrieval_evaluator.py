from ai_engine.retrieval.query_encoder import QueryEncoder
from ai_engine.retrieval.retriever import Retriever
from ai_engine.retrieval.retrieval_evaluator import RetrievalEvaluator


def main():
    encoder = QueryEncoder()
    retriever = Retriever()
    evaluator = RetrievalEvaluator()

    try:
        query = "Best open source vector database for RAG"

        print("=" * 60)
        print("Testing Retrieval Evaluator")
        print("=" * 60)

        embedding = encoder.encode(query)
        results = retriever.search(embedding)

        evaluation = evaluator.evaluate(results)

        print("\nEvaluation Results")
        print("-" * 60)
        print(evaluation)

        print("\n✓ Retrieval evaluation completed successfully.")

    finally:
        retriever.close()


if __name__ == "__main__":
    main()