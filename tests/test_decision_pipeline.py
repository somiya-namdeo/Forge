from ai_engine.orchestration.DecisionPipeline import DecisionPipeline
from ai_engine.reasoning.decision_engine import DecisionEngine


def main():
    decision_engine = DecisionEngine()
    pipeline = DecisionPipeline(decision_engine)

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

    result = pipeline.run(requirements, context)

    print(result)


if __name__ == "__main__":
    main()