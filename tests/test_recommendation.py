from ai_engine.reasoning.recommendation_engine import RecommendationEngine


def main():
    engine = RecommendationEngine()

    context = """
Qwen3 32B is an open-weight reasoning model suitable for production AI systems.
BAAI/bge-base-en-v1.5 provides high-quality embeddings.
Qdrant is a high-performance vector database optimized for semantic search.
Pinecone is a managed vector database service with automatic scaling.
Recursive Character Chunking preserves context while creating meaningful chunks.
Hybrid retrieval combines dense vector search with keyword search.
LangChain simplifies Retrieval-Augmented Generation development.
FastAPI is suitable for deploying AI inference APIs.
Docker provides portable deployment.
"""

    requirements = """
Design an AI-powered legal document question answering system.
"""

    comparison_question = """
Compare Qdrant and Pinecone for this system.
"""

    recommendation = engine.recommend(
        requirements,
        context,
        comparison_question,
    )

    print(recommendation)


if __name__ == "__main__":
    main()