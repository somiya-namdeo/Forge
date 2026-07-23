# Knowledge Sources

Defining a curated, high-quality knowledge corpus is a critical prerequisite for building an effective Retrieval-Augmented Generation (RAG) pipeline. In an AI Engineering Decision Support Platform like Forge, the quality of the generated system architectures is directly bound to the accuracy, relevance, and authority of the underlying data. Relying on verified and structured sources minimizes hallucination, ensures architectural recommendations are grounded in current best practices, and prevents the reasoning engine from ingesting contradictory or outdated information.

## 1. Official Documentation

Official documentation is considered the highest-confidence source for implementation details, API surfaces, and framework capabilities.

*   **LangChain**
*   **LlamaIndex**
*   **Qdrant**
*   **FastAPI**
*   **Ollama**
*   **Hugging Face**
*   **Sentence Transformers**

## 2. Model Cards

Model cards provide essential metadata regarding model capabilities, limitations, licensing, benchmarks, and recommended use cases. They are vital for the reasoning engine to select appropriate models for specific architectural requirements.

*   **Hugging Face Model Cards**
*   **Embedding Models**
*   **Large Language Models (LLMs)**
*   **Rerankers**

## 3. Research Papers

Research papers provide deep algorithmic insights, state-of-the-art methodologies, and recent advancements in the field.

*   **arXiv**
*   **Papers With Code**

## 4. Benchmarks

Benchmark data is critical for supporting objective model comparisons and ensuring that architectural decisions are backed by empirical performance metrics rather than assumptions.

*   **MTEB (Massive Text Embedding Benchmark)**
*   **Open LLM Leaderboard**

## 5. GitHub Repositories

Curated open-source repositories provide the platform with practical implementation patterns, usage examples, and established best practices.

*   **LangChain**
*   **LlamaIndex**
*   **Qdrant**
*   **Ollama**
*   **Reference RAG implementations**

## 6. Evaluation Frameworks

Evaluation frameworks establish the criteria by which the AI system's outputs are measured. While primarily used for testing, their documentation is ingested to ensure the system understands how to design testable and observable architectures.

*   **RAGAS**
*   **DeepEval**

## Out of Scope (Version 1)

To maintain a high signal-to-noise ratio and ensure the reliability of generated architectures, Forge will **NOT** use the following unstructured or unverified sources in Version 1:

*   Random blogs
*   Reddit
*   Stack Overflow
*   YouTube transcripts
*   Medium articles

These sources may be considered for future versions, provided they pass through a rigorous manual curation and verification process.

## Version 1 Goals

The following checklist represents the approved knowledge sources that will form the initial corpus for the Forge Version 1 RAG pipeline:

*   [ ] Ingest LangChain, LlamaIndex, Qdrant, FastAPI, Ollama, Hugging Face, and Sentence Transformers official documentation.
*   [ ] Ingest Model Cards for key Embedding Models, LLMs, and Rerankers from Hugging Face.
*   [ ] Ingest foundational RAG and LLM research papers from arXiv and Papers With Code.
*   [ ] Ingest current benchmark data from MTEB and Open LLM Leaderboard.
*   [ ] Ingest repository structures and patterns from curated LangChain, LlamaIndex, Qdrant, and Ollama GitHub repositories.
*   [ ] Ingest documentation for RAGAS and DeepEval evaluation frameworks.
