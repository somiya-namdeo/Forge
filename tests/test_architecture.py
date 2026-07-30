from ai_engine.reasoning.architecture_generator import ArchitectureGenerator


def main():
    generator = ArchitectureGenerator()

    context = """
Qwen3 32B is an open-weight reasoning model suitable for production AI systems.
BAAI/bge-base-en-v1.5 provides high-quality embeddings.
Qdrant is a high-performance vector database optimized for semantic search.
Recursive Character Chunking preserves context while creating meaningful chunks.
Hybrid retrieval combines dense vector search with keyword search.
LangChain simplifies the development of Retrieval-Augmented Generation applications.
FastAPI is suitable for deploying AI inference APIs.
Docker provides portable and scalable deployment.
"""

    requirements = """
Design an AI-powered document question answering system for a legal firm.
"""

    architecture = generator.generate(requirements, context)

    print(architecture)


if __name__ == "__main__":
    main()