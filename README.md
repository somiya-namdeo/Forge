<div align="center">
  <img src="./frontend/public/forge-logo.png" alt="Forge Logo" width="120"/>

# Forge

### AI Engineering Decision Support Platform

Evidence-backed architecture recommendations from natural-language AI system requirements.

[GitHub](https://github.com/somiya-namdeo/Forge) • [Live Demo](https://forge-beta-gilt-16.vercel.app) • [API Backend](https://forge-mmz3.onrender.com)

<br/>

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_Store-FF5252.svg?logo=qdrant)](https://qdrant.tech)
[![Hugging Face](https://img.shields.io/badge/Hugging_Face-Inference_API-F9AB00.svg?logo=huggingface)](https://huggingface.co)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991.svg?logo=openai)](https://openai.com)
[![Vercel](https://img.shields.io/badge/Vercel-Deployment-black.svg?logo=vercel)](https://vercel.com)
[![Render](https://img.shields.io/badge/Render-Backend-black.svg?logo=render)](https://render.com)
[![Tests](https://img.shields.io/badge/Tests-25_Passed-success.svg)](#testing)

</div>

---

## Table of Contents
- [Overview](#overview)
- [Key Capabilities](#key-capabilities)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [End-to-End System Flow](#end-to-end-system-flow)
- [Request Sequence](#request-sequence)
- [Decision Engine](#decision-engine)
- [Knowledge Base and Retrieval](#knowledge-base-and-retrieval)
- [Data Model](#data-model)
- [Evaluation](#evaluation)
- [Generated Architecture Report](#generated-architecture-report)
- [PDF Report Generation](#pdf-report-generation)
- [Deployment Architecture](#deployment-architecture)
- [API](#api)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Engineering Design Decisions](#engineering-design-decisions)
- [Security](#security)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [License](#license)

---

## Overview

Forge is an AI engineering decision-support platform designed to convert natural-language system requirements into structured, interoperable architecture recommendations.

When building a modern AI system, engineers must choose among many alternatives: LLMs, embedding models, vector databases, and retrieval strategies. The correct choice depends on strict constraints such as privacy, document volume, latency, and budget. Manually comparing these choices is difficult and time-consuming.

Forge automates this foundational architectural phase. Unlike a generic text-generation chatbot, Forge operates as a deterministic engineering co-pilot. It transforms natural language requirements into a Project Profile, uses Semantic Retrieval to fetch verified technology specifications from Qdrant, applies Constraint-Aware Scoring, and outputs a highly defensible Architecture Recommendation alongside explicit trade-off rationale in a structured JSON or exportable PDF report.

<p align="center">
  <img src="docs/screenshots/landing-page.png" alt="Forge Landing Page" width="900"/>
</p>
<p align="center"><i>Main Forge UI — Describe an AI system and its engineering constraints in plain language.</i></p>

## Key Capabilities

| Capability | Description |
|---|---|
| Natural-language requirement analysis | Parses unstructured user prompts into structured constraints using LLMs. |
| Constraint extraction | Identifies strict engineering blockers (e.g., privacy mandates, on-premise requirements). |
| Project profiling | Extracts scale, budget, and deployment targets deterministically. |
| Semantic technology retrieval | Queries a vector database for technically viable technology candidates. |
| Candidate filtering | Eliminates incompatible technologies before scoring begins. |
| Decision scoring | Analyzes trade-offs between competing LLMs, vector stores, and embedders using weighted matrices. |
| Architecture selection | Suggests a cohesive, interoperable AI stack prioritizing the user's constraints. |
| Rationale generation | Generates explicit "why" and "why not" justifications for every selected component. |
| Evaluation | Synthetically validates the retrieved rationale against the prompt using the RAGAS framework. |
| JSON export | Exposes the complete architecture recommendation payload via REST APIs. |
| PDF report generation | Programmatically synthesizes shareable PDF documents using ReportLab. |

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS | High-performance SPA rendering and strict type safety |
| Backend | FastAPI, Python 3.12 | High-throughput async REST API with rigid Pydantic schema validation |
| Embeddings | BAAI/bge-base-en-v1.5 | 768-dimensional semantic representation of requirements and profiles |
| Embedding Provider | Hugging Face Inference API | Remote embedding generation to maintain a lightweight API footprint |
| Vector Database | Qdrant | Fast semantic similarity search and local technology profile storage |
| LLM | OpenAI | Foundational intelligence for requirement parsing and rationale synthesis |
| Decision Engine | Python (Custom Deterministic Scoring) | Explicit mathematical scoring of architecture candidate trade-offs |
| Validation | RAGAS | Statistically robust generation validation against known ground truth |
| PDF Generation | ReportLab | Programmatic PDF document synthesis |
| Testing | Pytest | Comprehensive unit and integration test execution |
| Deployment | Vercel (Frontend), Render (Backend) | CI/CD enabled platforms for decoupled microservice hosting |

## System Architecture

The system utilizes a decoupled microservice architecture, separating the client application from the heavy decision-engine orchestration.

<p align="center">
  <img src="docs/diagrams/architecture.svg" alt="System Architecture Diagram" width="900"/>
</p>

| Layer | Component | Responsibility |
|---|---|---|
| Client | React SPA (Vercel) | Renders the web interface and handles user inputs/exports. |
| API | FastAPI Router (Render) | Exposes REST endpoints and orchestrates the backend pipeline. |
| Analysis | Requirement Analyzer | Parses user prompts into structured `ProjectProfile` objects via OpenAI. |
| Knowledge | Qdrant Vector Database | Stores technology schemas and semantic vectors locally. |
| Engine | Decision Scoring | Filters candidates and calculates weighted scores based on constraints. |
| Services | Hugging Face / OpenAI | External providers for embeddings and text generation. |

## End-to-End System Flow

The end-to-end request flow traces a user requirement through semantic translation, retrieval, and mathematical scoring.

<p align="center">
  <img src="docs/diagrams/system-flow.svg" alt="System Flow Diagram" width="900"/>
</p>

1. **User input**: The user enters natural-language requirements in the React frontend.
2. **API request**: The frontend sends a POST request to the FastAPI backend.
3. **Requirement analysis**: The backend analyzes the requirements using an LLM.
4. **Project profile**: A structured project profile (constraints, scale, budget) is created.
5. **Query embedding**: The requirement summary is embedded via the Hugging Face API (BAAI/bge-base-en-v1.5).
6. **Semantic retrieval**: Qdrant executes a cosine-similarity search against the knowledge base.
7. **Candidate filtering**: The backend filters out components that violate hard constraints.
8. **Decision scoring**: Remaining technologies are scored based on priorities (cost vs. latency vs. quality).
9. **Architecture selection**: The top-scoring components are selected to form a stack.
10. **Rationale generation**: An LLM synthesizes the engineering trade-offs into readable justifications.
11. **Report generation**: The structured architecture report is returned to the frontend.
12. **Export**: The user can export the result as JSON or PDF.

## Request Sequence

This sequence diagram illustrates the strict synchronous pipeline and external API boundaries during a recommendation request.

<p align="center">
  <img src="docs/diagrams/sequence.svg" alt="Request Sequence Diagram" width="900"/>
</p>

## Decision Engine

The core of Forge is the deterministic decision pipeline. Unlike LLM text generators, Forge does not rely on probability to guess an architecture. It uses retrieved facts.

<p align="center">
  <img src="docs/diagrams/decision-pipeline.svg" alt="Decision Pipeline Diagram" width="900"/>
</p>

- **Requirement Analysis**: Uses OpenAI to strictly format unstructured text into a Pydantic schema.
- **Constraint Detection**: Identifies binary flags (e.g., `is_open_source=True`).
- **Project Profile Creation**: Establishes weighting multipliers (e.g., if latency is prioritized, latency metrics receive a 1.5x score multiplier).
- **Candidate Retrieval**: Fetches top K related technologies from Qdrant based on vector similarity.
- **Candidate Filtering**: Drops candidates that fail the constraint check.
- **Scoring**: Applies the multipliers to the candidates' known `cost_indicator` and `performance_tier`.
- **Architecture Selection**: Selects the absolute highest numerical score for each category.
- **Rationale Generation**: Passes the winning component and the runner-up components to the LLM to explain the compromise.

<p align="center">
  <img src="docs/screenshots/decision-engine.png" alt="Decision Engine UI" width="900"/>
</p>
<p align="center"><i>Visualizing the synchronous filtering and scoring steps in the frontend.</i></p>

## Knowledge Base and Retrieval

Forge stores its engineering knowledge as structured JSON schemas embedded in Qdrant.

**Knowledge Domains:**
- **LLM**: Generative models, context windows, parameter sizes, licensing.
- **Embeddings**: Embedding models, dimensionality, maximum sequence lengths.
- **Vector Databases**: Storage engines, indexing support, deployment types.

**Retrieval Architecture:**
The application encodes incoming profiles into 768-dimensional vectors. Rather than executing a local PyTorch `SentenceTransformer` (which exceeds typical cloud free-tier memory limits), Forge routes text to the **Hugging Face Inference API** using `BAAI/bge-base-en-v1.5`. The returned vector is then used to perform a cosine-similarity search against the local Qdrant collections.

<p align="center">
  <img src="docs/screenshots/knowledge-base.png" alt="Knowledge Base UI" width="900"/>
</p>
<p align="center"><i>The Knowledge Base interface displaying retrieved components.</i></p>

## Data Model

Forge strictly avoids traditional relational databases (like PostgreSQL). All persistent data structures reside in Qdrant as semantic vectors with rich payload metadata, validated in memory via Pydantic.

<p align="center">
  <img src="docs/diagrams/data-model.svg" alt="Data Model ER Diagram" width="900"/>
</p>

| Entity / Schema | Purpose | Important Fields |
|---|---|---|
| `ProjectProfile` | Represents the user's analyzed requirement. | `project_name`, `scale`, `optimization_priority` |
| `Constraint` | Hard blockers extracted from the prompt. | `category`, `is_hard_constraint`, `description` |
| `TechnologyComponent`| The base schema for all technologies. | `component_id`, `name`, `license`, `cost_indicator` |
| `Metadata` | Component-specific technical facts. | `performance_tier`, `context_window` |
| `ArchitectureRecommendation` | The final synthesized output payload. | `id`, `total_confidence_score` |
| `Rationale` | The trade-off justification for a choice. | `component_id`, `reason`, `trade_offs` |

## Evaluation

Forge includes an explicit synthetic evaluation engine powered by the RAGAS framework. This system validates the quality of the architecture recommendation by statistically scoring the generated response against the retrieved context.

<p align="center">
  <img src="docs/screenshots/evaluation.png" alt="Evaluation Dashboard" width="900"/>
</p>
<p align="center"><i>The Evaluation interface comparing Evaluation Input, Retrieved Context, Ground Truth, and Generated Answer to calculate Faithfulness and Answer Relevancy metrics.</i></p>

## Generated Architecture Report

The backend aggregates all decision signals and technical rationales into a final structured `ArchitectureReport`.

<p align="center">
  <img src="docs/screenshots/architecture-report-1.png" alt="Architecture Report UI" width="900"/>
</p>
<p align="center"><i>The Architecture Decision Report displaying selected components, decision signals, and generated rationales.</i></p>

The report contains:
- **Decision Signals**: The constraints and priorities that drove the outcome.
- **Architecture Components**: The selected LLM, Vector DB, and Embedder.
- **Technical Rationale**: Explicit trade-off reasoning.

## PDF Report Generation

Recommendations can be natively exported as a structured engineering PDF artifact. The backend utilizes the Python `reportlab` library to programmatically draw the document based on the `ArchitectureReport` payload.

- **Request**: Frontend requests `/api/v1/reports/pdf`.
- **Generation**: Backend dynamically synthesizes the PDF buffer.
- **Response**: The file is returned as an `application/pdf` binary stream.
- **Download Flow**: Handled cleanly via the browser Blob API.

<p align="center">
  <img src="docs/screenshots/pdf-report.png" alt="PDF Report Export" width="900"/>
</p>
<p align="center"><i>A generated PDF architecture report output.</i></p>

## Deployment Architecture

The application utilizes a decoupled microservice deployment architecture.

<p align="center">
  <img src="docs/diagrams/deployment.svg" alt="Deployment Diagram" width="900"/>
</p>

- **Vercel Frontend**: Hosts the compiled React Vite SPA.
- **Render Backend**: Hosts the FastAPI Python runtime.
- **External Inference**: Offloaded to Hugging Face and OpenAI to maintain a lightweight compute footprint on Render.
- **Qdrant**: Runs locally within the Render instance utilizing local disk persistence.

## API

The FastAPI backend exposes the following core endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/decision/recommend` | Generates architecture recommendations and rationale from requirements. |
| `GET` | `/api/v1/knowledge` | Retrieves paginated specifications of registered AI technologies. |
| `POST` | `/api/v1/reports/generate` | Generates a structured JSON architecture decision report. |
| `POST` | `/api/v1/reports/pdf` | Generates the architecture report as a binary PDF download. |
| `POST` | `/api/v1/evaluation/evaluate` | Runs RAGAS metrics against a provided architecture recommendation. |

**Example Request Snippet:**
```json
// POST /api/v1/decision/recommend
{
  "description": "I need an open-source, highly secure RAG system for medical documents with low latency."
}
```

## Environment Variables

Create a `.env` file in the root directory based on `.env.example`.

| Variable | Required | Purpose | Example |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | Requirement extraction and rationale generation | `sk-your_openai_api_key` |
| `HUGGINGFACEHUB_API_TOKEN` | Yes | Remote embedding generation | `hf_your_huggingface_token` |
| `EMBEDDING_MODEL` | No | Overrides the default embedding model | `BAAI/bge-base-en-v1.5` |
| `FRONTEND_URL` | No | Configures CORS for the backend | `http://localhost:5173` |

*Never commit actual secrets to version control.*

## Local Development

### Clone Repository
```bash
git clone https://github.com/somiya-namdeo/Forge.git
cd Forge
```

### Backend Setup

Create and activate the virtual environment:

**Unix/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the backend:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Testing

The backend includes a comprehensive pytest suite covering decision scoring, API endpoints, and retrieval logic. The repository currently maintains 25 passing tests.

| Area | Coverage |
|---|---|
| Decision Engine | Scoring algorithms, filtering logic |
| API Routes | Request validation, payload structures |
| Retrieval | Mocked semantic similarity evaluation |

To run the test suite:
```bash
pytest tests/
```

## Project Structure

```text
Forge/
├── app/                     # FastAPI Backend Application
│   ├── api/                 # Route definitions and controllers
│   ├── core/                # Configuration and environment variables
│   ├── decision/            # Constraint extraction, scoring, and trade-offs
│   ├── embeddings/          # Hugging Face Inference API integrations
│   ├── evaluation/          # RAGAS evaluation engine integration
│   ├── reports/             # PDF export generation (ReportLab)
│   ├── retriever/           # Qdrant retrieval implementation
│   └── schemas/             # Pydantic validation models
├── docs/                    # Documentation assets
│   ├── diagrams/            # Architecture SVG files
│   └── screenshots/         # UI screenshots
├── frontend/                # React Single Page Application
│   ├── public/              # Static assets (including forge-logo.png)
│   └── src/
│       ├── components/      # Reusable UI elements
│       ├── pages/           # Main views (Decision Engine, Reports)
│       └── services/        # HTTP API client layer
├── knowledge_base/          # Local Qdrant SQLite vector storage
├── tests/                   # Pytest suite
├── .env.example             # Template for required environment variables
├── requirements.txt         # Backend Python dependencies
└── README.md                # Project documentation
```

## Engineering Design Decisions

- **Remote embeddings instead of local PyTorch inference**: Forge offloads the `BAAI/bge-base-en-v1.5` workload to Hugging Face rather than running local PyTorch `SentenceTransformer` binaries. This architectural decision significantly reduces CPU and RAM usage, enabling the backend to run reliably on resource-constrained platforms (like the Render free tier).
- **Qdrant semantic retrieval**: Bypassing a traditional relational database simplifies deployment and allows unstructured documentation to be seamlessly embedded alongside structured capability limits.
- **Structured Pydantic validation**: Enforces rigid boundaries between the LLM output and the deterministic scoring engine to prevent hallucination bleeding.
- **Explicit decision scoring**: The LLM is strictly used to parse requirements into schemas. The actual technology selection is handled by a deterministic mathematical scoring engine.

## Security

- **Environment-based secret management**: Tokens are managed via `.env` strictly isolated from source control.
- **API boundaries**: External inference services are only accessible via the backend proxy.
- **CORS validation**: Enforced at the FastAPI layer, restricting origins to the Vercel frontend.
- **Input validation**: Handled natively by Pydantic models preventing malformed payloads from executing in the scoring engine.

## Limitations and Future Improvements

**Limitations:**
- **Dependency on external inference APIs**: The system is bound to the availability and network latency of Hugging Face and OpenAI APIs.
- **Knowledge base freshness**: The recommendation quality is highly dependent on the breadth and freshness of the technology specifications stored locally in Qdrant.

**Future Improvements:**
- **Automated Knowledge Refreshing**: Implementing cron jobs to automatically scrape and embed new model specifications from the Hugging Face Model Hub.
- **Reranking**: Implementing Cohere or BGE-Reranker layers to refine candidate selection accuracy.
- **Expanded Observability**: Telemetry and trace logging for scoring evaluation transparency.

## License

MIT License