# Forge: Engineering Implementation Roadmap

This document serves as the official execution plan for building Forge v2.0. It breaks the architecture down into 16 sequential milestones.

---

## High-Level Implementation Strategy

### Implementation Order
Implementation strictly follows a "Data First, API Last" approach:
1. **Phases 1-2**: Infrastructure scaffolding.
2. **Phases 3-7**: The Ingestion Pipeline (ETL, Chunking, Embedding, Qdrant).
3. **Phases 8-10**: The Inference Engine (Retrieval, Recommendation, Agents).
4. **Phases 11-12**: Presentation Layer (FastAPI, React UI).
5. **Phases 13-16**: Production Readiness (Eval, Observability, Deployment).

### Git Commit Recommendations
*   Use Conventional Commits (e.g., `feat:`, `fix:`, `chore:`, `test:`).
*   Prefix commits with the phase number (e.g., `feat(phase-4): implement github connector`).
*   Squash and merge PRs per milestone to maintain a clean history.

---

## Phase 1: Project Initialization
*   **Objective**: Scaffold the fundamental project structure and define environment configurations.
*   **Deliverables**: Empty folder tree matching `ARCHITECTURE.md`, `pyproject.toml`, `requirements.txt` (or Poetry setup), `.env.example`, and pre-commit hooks.
*   **Folder(s) involved**: Root `/`, `backend/`, `frontend/`
*   **Estimated complexity**: Low
*   **Dependencies**: None
*   **Success criteria**: Developer can run `pip install -r requirements.txt` and `npm install` without errors.
*   **Testing strategy**: Verify pre-commit hooks execute on dummy files.
*   **Definition of Done**: Project compiles empty; linting passes.

## Phase 2: Core Infrastructure
*   **Objective**: Setup foundational configuration, schemas, and utils.
*   **Deliverables**: `config/settings.py` (BaseSettings), `utils/` helpers, and base Pydantic models for responses and internal state.
*   **Folder(s) involved**: `backend/app/config/`, `backend/app/utils/`, `backend/app/schemas/`
*   **Estimated complexity**: Low
*   **Dependencies**: Phase 1
*   **Success criteria**: Configuration variables (like API keys) are successfully loaded from `.env` via Pydantic.
*   **Testing strategy**: Unit tests for config loading and utility pure functions.
*   **Definition of Done**: Base schemas validated; config handles missing variables gracefully.

## Phase 3: Document Discovery
*   **Objective**: Create the mechanism to discover official documentation URLs (sitemaps, RSS, GitHub releases).
*   **Deliverables**: URL crawler scripts and sitemap parsers.
*   **Folder(s) involved**: `backend/app/connectors/`
*   **Estimated complexity**: Medium
*   **Dependencies**: Phase 2
*   **Success criteria**: Given a domain (e.g., `qdrant.tech`), the system can return a list of valid documentation URLs.
*   **Testing strategy**: Mock HTTP requests and verify URL list extraction.
*   **Definition of Done**: Discovery logic successfully outputs arrays of target URLs.

## Phase 4: Connectors
*   **Objective**: Implement isolation layers to fetch raw data from specific sources.
*   **Deliverables**: `github_connector.py`, `markdown_connector.py`, `pdf_connector.py`, `crawl4ai_connector.py`.
*   **Folder(s) involved**: `backend/app/connectors/`
*   **Estimated complexity**: High
*   **Dependencies**: Phase 3
*   **Success criteria**: HTML, Markdown, and text can be successfully scraped and saved to `data/raw/`.
*   **Testing strategy**: End-to-end scrape of a test repository and a static webpage.
*   **Definition of Done**: Raw data reliably lands in the `data/raw/` directory.

## Phase 5: Processing Pipeline
*   **Objective**: Clean raw data, extract metadata, and split text into optimal chunks.
*   **Deliverables**: `cleaner.py`, `parser.py`, `deduplicator.py`, `chunker.py`.
*   **Folder(s) involved**: `backend/app/processing/`
*   **Estimated complexity**: High
*   **Dependencies**: Phase 4
*   **Success criteria**: Messy HTML is converted to clean Markdown, and then semantically chunked without breaking code blocks.
*   **Testing strategy**: Unit tests on edge-case markdown files to verify semantic chunk overlap.
*   **Definition of Done**: Processed chunks exist in `data/chunks/` with correct structural metadata.

## Phase 6: Embeddings
*   **Objective**: Convert processed text chunks into high-dimensional vectors.
*   **Deliverables**: API wrappers for OpenAI/BGE models, batching logic, rate-limit handling.
*   **Folder(s) involved**: `backend/app/processing/` (or dedicated embedder utility)
*   **Estimated complexity**: Medium
*   **Dependencies**: Phase 5
*   **Success criteria**: System can take 10,000 chunks and return vectors without hitting API rate limits.
*   **Testing strategy**: Mock LLM API and test retry/backoff logic.
*   **Definition of Done**: Chunks mapped to valid floating-point arrays.

## Phase 7: Vector Database
*   **Objective**: Configure Qdrant and upsert embedded chunks.
*   **Deliverables**: `db/qdrant.py` client wrapper, index creation scripts.
*   **Folder(s) involved**: `backend/app/db/`
*   **Estimated complexity**: Medium
*   **Dependencies**: Phase 6
*   **Success criteria**: Vectors and associated metadata are successfully searchable in a local Qdrant instance.
*   **Testing strategy**: Integration tests verifying successful upsert and count queries.
*   **Definition of Done**: Qdrant populated with test knowledge.

*(Testing Checkpoint: The complete Ingestion flow is now functional. Verify data exists in VectorDB.)*

## Phase 8: Retrieval Engine
*   **Objective**: Implement dense, sparse, and hybrid search alongside cross-encoder reranking.
*   **Deliverables**: `dense.py`, `sparse.py`, `hybrid.py`, `reranker.py`, `context_builder.py`.
*   **Folder(s) involved**: `backend/app/retrieval/`
*   **Estimated complexity**: High
*   **Dependencies**: Phase 7
*   **Success criteria**: System can accept a natural language query and return the top 10 highly relevant text chunks.
*   **Testing strategy**: Manual query testing and precision verification.
*   **Definition of Done**: High-quality context strings generated dynamically from Qdrant.

## Phase 9: Recommendation Engine
*   **Objective**: Build the core trade-off analysis and tech selection logic.
*   **Deliverables**: `tradeoff_analyzer.py`, `technology_selector.py`, `architecture_generator.py`.
*   **Folder(s) involved**: `backend/app/recommendation/`
*   **Estimated complexity**: Very High (Core IP)
*   **Dependencies**: Phase 8
*   **Success criteria**: Engine can successfully pair compatible frameworks/databases based on retrieved context constraints.
*   **Testing strategy**: Unit testing logic rules (e.g., if constraint=low_latency, Qdrant > local chroma).
*   **Definition of Done**: Raw textual recommendations correctly generated based on context.

## Phase 10: Multi-Agent Workflows
*   **Objective**: Orchestrate Retrieval, Prompts, Memory, and Recommendation into autonomous loops.
*   **Deliverables**: `agents/` (Query, Architecture, Citation), `prompts/`, `memory/`, `workflows/`.
*   **Folder(s) involved**: `backend/app/agents/`, `backend/app/workflows/`, `backend/app/prompts/`, `backend/app/memory/`
*   **Estimated complexity**: Very High
*   **Dependencies**: Phase 9
*   **Success criteria**: An intent flows from Query Agent -> Retrieval -> Architecture Agent -> Citation Agent automatically.
*   **Testing strategy**: End-to-end integration tests simulating user queries.
*   **Definition of Done**: `recommendation_workflow.py` produces a finalized markdown report with citations.

## Phase 11: Backend APIs
*   **Objective**: Expose the multi-agent workflows as REST endpoints via FastAPI.
*   **Deliverables**: `/chat` streaming endpoint, `/ingest` trigger endpoint.
*   **Folder(s) involved**: `backend/app/api/`
*   **Estimated complexity**: Medium
*   **Dependencies**: Phase 10
*   **Success criteria**: Frontend can send a POST request and receive a Server-Sent Events (SSE) stream of markdown.
*   **Testing strategy**: FastAPI `TestClient` endpoint validation.
*   **Definition of Done**: OpenAPI Swagger documentation available at `/docs` and endpoints responding correctly.

## Phase 12: Frontend
*   **Objective**: Build the React UI for users to interact with Forge.
*   **Deliverables**: Chat interface, streaming markdown renderer, Mermaid.js integration.
*   **Folder(s) involved**: `frontend/src/`
*   **Estimated complexity**: High
*   **Dependencies**: Phase 11
*   **Success criteria**: Users can type queries and watch the architecture recommendation stream in real-time.
*   **Testing strategy**: Cypress E2E tests / React Testing Library.
*   **Definition of Done**: UI matches premium design requirements and correctly renders backend data.

## Phase 13: Evaluation
*   **Objective**: Establish automated metrics to guarantee RAG output quality.
*   **Deliverables**: Golden Datasets, Ragas/DeepEval integration scripts.
*   **Folder(s) involved**: `evaluation/`
*   **Estimated complexity**: Medium
*   **Dependencies**: Phase 10
*   **Success criteria**: Pipeline can be mathematically scored for `answer_correctness` and `context_precision`.
*   **Testing strategy**: Execute evaluation script against a known set of 50 complex engineering queries.
*   **Definition of Done**: CI pipeline fails if evaluation score drops below defined threshold.

## Phase 14: Observability
*   **Objective**: Add distributed tracing, metrics, and application logging.
*   **Deliverables**: `observability/` integration (Langfuse/OpenTelemetry), custom loggers.
*   **Folder(s) involved**: `backend/app/observability/`
*   **Estimated complexity**: Low
*   **Dependencies**: Phase 11
*   **Success criteria**: Every LLM call, retrieval time, and API request is tracked in a central dashboard.
*   **Testing strategy**: Verify traces appear in local Langfuse instance.
*   **Definition of Done**: No missing telemetry data for critical paths.

## Phase 15: Deployment
*   **Objective**: Containerize and deploy the application.
*   **Deliverables**: `docker-compose.yml`, Dockerfiles, production environment variables.
*   **Folder(s) involved**: Root `/`, `backend/`, `frontend/`
*   **Estimated complexity**: Medium
*   **Dependencies**: Phase 12, Phase 14
*   **Success criteria**: Application successfully spins up via `docker-compose up --build`.
*   **Testing strategy**: Post-deployment smoke tests.
*   **Definition of Done**: Forge is accessible on a local or public network port.

*(Deployment Checkpoint: The system is now containerized and ready for staging/production hosting).*

## Phase 16: Final Polish
*   **Objective**: Address technical debt, edge cases, and documentation.
*   **Deliverables**: Updated `README.md`, developer onboarding guide, security audit.
*   **Folder(s) involved**: `docs/`, `notebooks/`
*   **Estimated complexity**: Low
*   **Dependencies**: Phase 15
*   **Success criteria**: A new developer can clone, build, and run the project in under 15 minutes.
*   **Testing strategy**: Peer review and manual QA.
*   **Definition of Done**: Repository is tagged as `v1.0.0` release.
