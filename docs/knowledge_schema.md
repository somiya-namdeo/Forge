# Knowledge Schema

## Introduction

A standardized knowledge schema is the foundational blueprint of any robust Retrieval-Augmented Generation (RAG) system. In Forge, defining this schema before data collection begins ensures:

- **Consistent Ingestion**: Uniform processing pipelines regardless of whether the source is a PDF, a GitHub repository, or a web-scraped model card.
- **Metadata Filtering**: Enabling precise, faceted search (e.g., filtering only for MIT-licensed embedding models).
- **Hybrid Retrieval**: Combining dense vector search with exact-match metadata and keyword search for superior context relevance.
- **Vector Search**: Providing structured text fields (like summaries) alongside raw content to optimize embedding quality.
- **Evaluation**: Tracking provenance and source quality for debugging RAG outputs and improving evaluation metrics.
- **Future Scalability**: Allowing seamless addition of new data types and sources without breaking existing pipelines.

Every document collected and ingested into the Forge knowledge base **must** adhere to this canonical schema.

---

## Core Schema

The following table defines the canonical schema for top-level documents in the knowledge base.

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | String (UUID) | Yes | Unique identifier for the document. |
| `title` | String | Yes | Human-readable title of the document or resource. |
| `source` | String | Yes | Name of the original source (e.g., "LangChain", "Hugging Face"). |
| `source_type` | String (Enum) | Yes | Type of source (e.g., "Official Documentation", "Research Paper"). |
| `url` | String | Yes | The canonical URL or URI where the document was retrieved. |
| `category` | String | Yes | Primary domain category (e.g., "Retrieval", "LLM"). |
| `sub_category` | String | No | Secondary or granular classification. |
| `content` | String | Yes | The raw, unstructured text content of the document. |
| `summary` | String | No | A condensed summary of the content to assist in rapid retrieval. |
| `tags` | Array[String] | No | A list of keywords associated with the document. |
| `language` | String | Yes | ISO 639-1 language code (e.g., "en" for English). |
| `license` | String | Yes | Licensing information (e.g., "MIT", "Apache-2.0", "Proprietary"). |
| `author` | String | No | Name of the individual or entity who authored the document. |
| `organization` | String | No | The organization responsible for publishing the resource. |
| `publication_date`| Date/String | No | The original publication or release date of the material. |
| `last_updated` | Date/String | Yes | Timestamp of the last time this document was modified or scraped. |
| `version` | String | No | Version number (for software, frameworks, or model iterations). |
| `embedding_model` | String | Yes | Identifier for the model used to embed this document. |
| `chunk_count` | Integer | Yes | The total number of vectorized chunks derived from this document. |
| `metadata` | Object (JSON) | Yes | A nested object containing domain-specific metadata. |

---

## Metadata Object

The `metadata` field is a nested JSON object designed to hold dynamic, domain-specific attributes that do not universally apply to all document types.

- **`framework`**: Identifies specific software frameworks discussed (e.g., "FastAPI", "React").
- **`model_family`**: The lineage of an AI model (e.g., "Llama 3", "Mistral").
- **`programming_language`**: Relevant coding languages (e.g., "Python", "TypeScript").
- **`task`**: The specific AI task the document addresses (e.g., "Text Generation", "Semantic Search").
- **`document_type`**: Finer classification (e.g., "Tutorial", "API Reference", "Whitepaper").
- **`difficulty`**: Target audience technical level (e.g., "Beginner", "Advanced").
- **`domain`**: Industry or architectural domain (e.g., "Cloud Architecture", "NLP").
- **`retrieval_priority`**: An integer score used to artificially boost the importance of highly authoritative sources during search.

---

## Source Types

The `source_type` field restricts documents to a set of approved knowledge classes. 

- **Official Documentation**: Direct, authoritative documentation from framework or tool creators. Highest trust tier.
- **Research Paper**: Academic or industry research papers (e.g., from arXiv) providing theoretical and algorithmic context.
- **Model Card**: Standardized model documentation detailing capabilities, biases, parameters, and benchmarks.
- **Benchmark**: Empirical performance data and datasets used to objectively compare models and architectures.
- **GitHub Repository**: Curated open-source codebases serving as reference implementations and architecture patterns.
- **Evaluation Framework**: Documentation detailing metrics and methodologies for evaluating LLM pipelines (e.g., RAGAS).

---

## Categories

Categories serve as the primary organizational taxonomy for Forge. While this list can expand in future versions, the V1 categories are:

- **LLM**: Large Language Models and their configurations.
- **Embeddings**: Text representation models and embedding strategies.
- **Retrieval**: Search algorithms, dense/sparse retrieval, and context fetching.
- **Reranking**: Cross-encoders and relevance optimization.
- **Vector Database**: Database architectures optimized for high-dimensional vectors.
- **Prompt Engineering**: Techniques for interacting optimally with language models.
- **Agents**: Autonomous AI agents, tools, and reasoning loops.
- **Evaluation**: Metrics, observability, and testing frameworks for AI systems.
- **Backend**: Traditional server-side architectures (APIs, databases).
- **Deployment**: MLOps, CI/CD, and production serving.

---

## Chunk Metadata

During ingestion, documents are broken into smaller, semantically meaningful "chunks" to optimize vector search. Every chunk must inherit specific metadata from its parent document while maintaining chunk-specific context to improve retrieval precision.

- **`parent_document_id`**: Foreign key linking the chunk back to its parent document.
- **`chunk_id`**: Unique identifier for the specific chunk.
- **`chunk_index`**: The sequential order of the chunk within the parent document (useful for windowed context retrieval).
- **`token_count`**: The number of tokens in the chunk, ensuring context window limits are respected during generation.
- **`section_title`**: The specific section or header under which the chunk was found.
- **`heading_path`**: The hierarchical path of headers (e.g., `["Introduction", "Usage", "Advanced Settings"]`) providing deep structural context.

Providing rich chunk-level metadata allows the reasoning engine to understand exactly *where* in a document a piece of information was found, dramatically improving synthesis quality.

---

## Design Principles

The Forge knowledge schema is guided by the following engineering principles:

- **One Canonical Schema**: Prevents fragmentation. All ingestion pipelines must map raw data to this exact structure.
- **Source Traceability**: Every piece of knowledge must be traceable back to a specific URL and version, ensuring transparent AI decisions.
- **Version Awareness**: AI moves fast. Tracking `version` and `last_updated` ensures architectures aren't built on deprecated practices.
- **Rich Metadata**: Embedding is only half the battle. Extensive metadata enables powerful hybrid search (vector + exact match).
- **Framework Agnostic**: The schema describes the *knowledge*, not how the underlying vector database implements it.
- **Extensible**: The nested `metadata` object provides flexibility for future, unforeseen data requirements.
- **AI-First Design**: Fields like `summary` and `heading_path` are specifically designed to aid LLM comprehension during the RAG generation phase.

---

## Future Extensions

To maintain scope and reliability in Version 1, the following advanced fields are intentionally excluded but planned for future integration:

- **Citations**: Explicit links to other documents referenced within the text.
- **Quality Score**: Automated scoring of document clarity and utility.
- **Popularity Score**: Github stars, citations, or community upvotes.
- **Confidence Score**: System-calculated trust level for the source.
- **Cross References**: Bidirectional links between related concepts across different documents.
- **Knowledge Graph Links**: Triples mapping relationships for graph-based RAG.
- **Document Relationships**: Explicit "supersedes", "depends_on", or "related_to" pointers.
- **Automatic Summaries**: LLM-generated summaries executed at ingestion time.
- **Embedding History**: Tracking which versions of embedding models were used over time.

---

## Conclusion

Designing a canonical, highly structured schema prior to initiating data collection is essential for building a production-grade AI Engineering system. It guarantees data uniformity, enables advanced hybrid retrieval techniques, and ensures that the AI reasoning engine operates on a foundation of clean, verifiable, and richly contextualized knowledge.
