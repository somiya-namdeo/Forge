# Forge Knowledge Architecture

## Purpose

Forge is an AI Engineering Decision Support Platform that goes beyond suggesting isolated tools—it recommends complete, cohesive AI stacks. By leveraging a structured knowledge base, Retrieval-Augmented Generation (RAG), and a sophisticated reasoning engine, Forge evaluates project constraints to generate evidence-backed architectural recommendations. The platform is designed to be modular and extensible, ensuring it can rapidly adapt to the evolving AI ecosystem.

---

## Knowledge Domains

To effectively recommend comprehensive AI architectures, Forge organizes its knowledge base into four distinct domains:

### Technologies
The core building blocks of any AI system.
- **Large Language Models (LLMs)**: The reasoning engines (e.g., Llama 3, GPT-4).
- **Embedding Models**: Models that map text to vector space for semantic understanding (e.g., BGE-M3).
- **Vector Databases**: Specialized databases for storing and retrieving high-dimensional embeddings (e.g., Qdrant, Pinecone).
- **Frameworks**: The orchestration layers that tie components together (e.g., LangChain, LlamaIndex).
- **Rerankers**: Models that refine and re-order initial retrieval results for higher precision (e.g., Cohere Rerank).

### Techniques
The methodological approaches applied to technologies.
- **Retrieval Strategies**: Methods for finding relevant context (e.g., Dense, Sparse, Hybrid, Multi-query).
- **Chunking Strategies**: Rules for dividing documents into embeddable segments (e.g., Semantic, Recursive).
- **Prompting Techniques**: Strategies for eliciting optimal LLM behavior (e.g., Chain-of-Thought, ReAct).

### Architectures
High-level design patterns for autonomous and complex AI workflows.
- **Agent Architectures**: Blueprints for building autonomous agents (e.g., Plan-and-Execute, Tool Calling).

### Evaluation
Methodologies for measuring the success and reliability of the recommended stacks.
- **Evaluation Frameworks**: Tools for testing RAG and agent performance (e.g., Ragas, DeepEval).

---

## Entity Relationships

Forge models knowledge not as isolated records, but as an interconnected ecosystem. Understanding how technologies and techniques interact is critical for generating compatible stack recommendations.

**LLM**
- `works_with` → Framework
- `pairs_with` → Embedding Model
- `evaluated_by` → Evaluation Framework
- `supports` → Prompting Technique

**Embedding Model**
- `compatible_with` → Vector Database
- `recommended_for` → Use Cases

**Vector Database**
- `stores` → Embeddings
- `integrates_with` → Framework

**Framework**
- `supports` → Retrieval
- `supports` → Chunking
- `supports` → Prompting
- `supports` → Agents

**Agent**
- `uses` → LLM
- `uses` → Framework
- `evaluated_by` → Evaluation Framework

**Why these matter:** These edges allow the Decision Engine to validate compatibility. If a user requires a specific Vector Database, Forge navigates the graph to ensure the recommended Framework and Embedding Model natively support it.

---

## Knowledge Graph Design

Forge conceptually represents every technology, technique, and architecture as a node in a Knowledge Graph. 

```text
       +-------------------+
       |                   |
       |  Prompting Tech   |
       |                   |
       +--------+----------+
                ^
                | supports
                |
       +--------+----------+             +-------------------+
       |                   |             |                   |
       |       LLM         +------------>+ Evaluation Fwk    |
       |                   | evaluated_by|                   |
       +--------+----------+             +---------+---------+
                |                                  ^
     works_with |                                  |
                v                                  | evaluated_by
       +--------+----------+      uses   +---------+---------+
       |                   +<------------+                   |
       |    Framework      |             |       Agent       |
       |                   +------------>+                   |
       +--------+----------+  supports   +-------------------+
                |
integrates_with |
                v
       +--------+----------+             +-------------------+
       |                   |   stores    |                   |
       |  Vector Database  +<------------+  Embedding Model  |
       |                   |             |                   |
       +--------+----------+             +-------------------+
                |                                  ^
                |                                  |
                +----------------------------------+
                            compatible_with
```

**Enabling Complete Stack Recommendations:** By mapping the ecosystem as a graph, Forge's reasoning engine can perform path traversals to construct an entire architecture. It starts at a core requirement (e.g., a specific LLM), traverses to compatible Frameworks, finds Vector Databases supported by those Frameworks, and selects an Embedding Model suitable for the Vector Database.

---

## Schema Relationships

To ensure consistency, every entity in the Knowledge Graph adheres to a strict canonical schema.

**Technology Schemas**
- `llm_schema.json`
- `embedding_schema.json`
- `vectordb_schema.json`
- `framework_schema.json`
- `reranker_schema.json`

**Technique Schemas**
- `retrieval_schema.json`
- `chunking_schema.json`
- `prompting_schema.json`

**Architecture Schemas**
- `agent_schema.json`

**Evaluation Schemas**
- `evaluation_schema.json`

**Design Principles:**
- **Structured**: Strong typing and defined fields ensure reliable parsing.
- **Machine-readable**: Optimized for programmatic filtering and hybrid vector search.
- **Human-readable**: Maintained as clean JSON that engineers can easily audit and update.
- **Extensible**: Designed with nested metadata objects to accommodate future attributes.
- **Versionable**: Capable of tracking framework versions and model iterations.

---

## Recommendation Pipeline

Forge processes natural language requirements through a multi-stage pipeline to generate a final architecture:

1. **User Requirements** → The user submits their project goals, constraints, and preferences in natural language.
2. **Constraint Extraction** → An LLM extracts hard constraints (e.g., "must be open source", "budget < $500/mo").
3. **Knowledge Retrieval** → The system performs hybrid search against the Knowledge Base to find candidate technologies.
4. **Technology Matching** → Candidates are scored against the extracted constraints.
5. **Compatibility Validation** → The system traverses the Knowledge Graph to ensure selected components can integrate seamlessly.
6. **Trade-off Analysis** → The engine evaluates alternative stacks, weighing pros and cons (e.g., Latency vs. Accuracy).
7. **Stack Generation** → A final, cohesive architecture is formulated.
8. **LLM Explanation** → The LLM generates a human-readable report detailing *why* the stack was chosen.
9. **Final Recommendation** → The user receives the evidence-backed architectural blueprint.

---

## Decision Engine Flow

The Decision Engine is the core logic that filters and scores candidate technologies before they are passed to the final LLM synthesis phase. It applies multi-dimensional scoring based on constraints:

- **Project Type**: (e.g., Chatbot, Semantic Search, Autonomous Agent)
- **Budget**: Filtering out enterprise solutions for low-budget projects.
- **Deployment**: Cloud vs. On-Premise vs. Edge.
- **Scale**: Number of users, QPS (Queries Per Second), and data volume.
- **Context Window**: Filtering LLMs based on required input length.
- **Open Source Preference**: Strictly limiting recommendations to permissive licenses if requested.
- **Licensing**: Ensuring compliance (e.g., avoiding AGPL for proprietary SaaS).
- **Latency**: Prioritizing speed for real-time applications.
- **Multilingual Support**: Filtering models based on supported languages.
- **Benchmarks**: Using MTEB or Open LLM Leaderboard scores to break ties.

**Compatibility Scoring:** Beyond individual scores, the engine applies a compatibility multiplier. A stack composed of highly rated individual tools that do not natively integrate will score lower than a stack of slightly less performant tools that offer seamless, out-of-the-box integration.

---

## Data Collection Pipeline

To maintain high reasoning quality, Forge relies on an authoritative, curated ingestion pipeline:

**Official Documentation** → **GitHub** → **Model Cards** → **Research Papers** → **Benchmarks**  
↓  
**Raw Knowledge** (HTML, Markdown, PDF)  
↓  
**Cleaning** (Removing boilerplate, fixing formatting)  
↓  
**Normalization** (Mapping entities to standard naming conventions)  
↓  
**Structured JSON** (Mapping content to the canonical Schemas)  
↓  
**Knowledge Base** (Storage for RAG)

**Why Official Sources are Prioritized:** Random blogs or social media often contain outdated or subjective opinions. By relying strictly on official documentation, model cards, and empirical benchmarks, Forge guarantees that its architectural recommendations are grounded in verified, objective reality, minimizing AI hallucination.

---

## Knowledge Base Storage

Every entity processed by the data collection pipeline is stored as structured JSON following its respective schema.

This dual-nature storage (structured data + unstructured text) supports:
- **Search**: Keyword search across titles, descriptions, and tags.
- **Filtering**: Hard filtering on metadata (e.g., `license == "MIT"`).
- **Comparison**: Side-by-side programmatic comparison of features (e.g., `max_input_tokens`).
- **RAG**: Embedding the `summary` and `content` fields to provide rich context to the generation LLM.
- **Reasoning**: Allowing the Decision Engine to execute programmatic rules before engaging the LLM.

---

## RAG Pipeline

When a user submits a query, Forge utilizes a sophisticated Retrieval-Augmented Generation pipeline:

1. **Knowledge Base**: The structured JSON corpus.
2. **Embedding Generation**: The user's query is converted into a vector.
3. **Vector Database**: A similarity search retrieves the top-$K$ most relevant documents.
4. **Retriever**: Executes hybrid search (Vector + Keyword) combined with hard metadata filters.
5. **Reranker**: A cross-encoder model re-evaluates the retrieved documents to ensure maximum relevance to the query.
6. **Context Builder**: The top documents are formatted and injected into the system prompt.
7. **LLM**: The generation model synthesizes the context, constraints, and relationships.
8. **Recommendation Report**: The final architecture document is presented to the user.

---

## Future Extensions

Forge is built for continuous evolution. Planned future improvements include:

- **Automatic benchmark synchronization**: Polling HuggingFace leaderboards to keep scores fresh.
- **Community knowledge contributions**: Allowing users to submit verified architectures.
- **Cost estimation**: Real-time API pricing calculation for recommended stacks.
- **Architecture diagram generation**: Automatically rendering Mermaid.js or Draw.io diagrams.
- **Deployment planning**: Generating Terraform or Docker Compose files for the recommended stack.
- **Fine-tuning recommendations**: Adapting suggestions based on user feedback loops.
- **Model evaluation dashboards**: UI components to visualize why a model was chosen.
- **MCP integration**: Implementing the Model Context Protocol to query external tools dynamically.
- **Multi-agent reasoning**: Utilizing separate agents for Retrieval, Scoring, and Writing to improve output quality.

---
