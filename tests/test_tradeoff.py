from ai_engine.reasoning.tradeoff_analyzer import TradeoffAnalyzer


def main():
    analyzer = TradeoffAnalyzer()

    context = """
Qdrant is an open-source vector database optimized for semantic search and self-hosted deployments.
Pinecone is a managed vector database service with automatic scaling and minimal infrastructure management.
"""

    question = "Compare Qdrant and Pinecone for a production RAG system."

    result = analyzer.analyze(question, context)

    print(result)


if __name__ == "__main__":
    main()