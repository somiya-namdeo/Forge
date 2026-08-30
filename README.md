<p align="center">
  <img src="./frontend/public/forge-logo.png" alt="Forge Logo" width="120"/>
</p>

<h1 align="center">Forge</h1>

<p align="center">
  AI Engineering Decision Support Platform
</p>

<p align="center">
  Forge transforms natural-language AI project requirements into evidence-backed architecture recommendations by analyzing constraints, retrieving relevant technologies, scoring candidates, and generating structured decision reports.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.118-009688.svg?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB.svg?logo=react" alt="React">
  <img src="https://img.shields.io/badge/Qdrant-Vector_Store-FF5252.svg?logo=qdrant" alt="Qdrant">
  <img src="https://img.shields.io/badge/Hugging_Face-Inference_API-F9AB00.svg?logo=huggingface" alt="Hugging Face">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Tests-25_Passed-success.svg" alt="Tests">
</p>

<p align="center">
  <a href="#project-overview">Overview</a> •
  <a href="#system-architecture">Architecture</a> •
  <a href="#system-flow">System Flow</a> •
  <a href="#data-and-knowledge-architecture">Knowledge Base</a> •
  <a href="#evaluation">Evaluation</a> •
  <a href="#api-overview">API</a> •
  <a href="#local-development">Setup</a> •
  <a href="#testing">Testing</a> •
  <a href="#deployment">Deployment</a>
</p>

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Capabilities](#key-capabilities)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [System Flow](#system-flow)
- [Recommendation Sequence](#recommendation-sequence)
- [Data and Knowledge Architecture](#data-and-knowledge-architecture)
- [Decision Engine Pipeline](#decision-engine-pipeline)
- [Report Generation](#report-generation)
- [Evaluation](#evaluation)
- [API Overview](#api-overview)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Engineering Design Decisions](#engineering-design-decisions)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Project Overview

Forge is an AI engineering decision-support platform designed to convert natural-language system requirements into structured, interoperable architecture recommendations.

Designing a modern Retrieval-Augmented Generation (RAG) or AI stack requires balancing complex engineering constraints: cost, latency, compliance, domain specificity, and scalability. Engineers often spend weeks reading documentation and benchmarking models before writing any code. Forge automates this foundational architectural phase.

Forge operates strictly as a deterministic engineering co-pilot, distinguishing it from generic LLM text-generation chatbots. Rather than relying on LLM probabilities to guess an architecture, Forge grounds its decisions in verified technology specifications retrieved via semantic search. It explicitly scores engineering trade-offs and outputs a highly defensible architecture draft.

**The Decision Pipeline:**
Natural Language Requirements &rarr; Requirement Analysis &rarr; Project Profile &rarr; Semantic Retrieval &rarr; Candidate Scoring &rarr; Architecture Recommendation &rarr; Structured Decision Report.

<p align="center">
  <img src="./docs/screenshots/landing-page.png" alt="Forge Landing Page" width="900">
</p>
<p align="center"><i>Natural-Language Requirements — Engineers describe their AI system and its constraints in plain language.</i></p>

## Key Capabilities

| Capability | Description |
|---|---|
| **Requirement Analysis** | Converts unstructured user prompts into structured constraints. |
| **Constraint Detection** | Identifies strict engineering blockers (e.g., privacy mandates or cloud-agnostic deployment). |
| **Semantic Retrieval** | Queries a Qdrant vector database for technically viable technology candidates. |
| **Technology Ranking** | Analyzes trade-offs between competing LLMs, vector stores, and embedders. |
| **Architecture Recommendation** | Suggests a cohesive, interoperable AI stack prioritizing the user's constraints. |
| **Evidence-backed Decisions** | Generates explicit "why" and "why not" rationales for every selected component. |
| **Evaluation** | Synthetically validates the retrieved rationale against the prompt using the RAGAS framework. |
| **Report Generation** | Compiles unified architecture decision documents outlining the selected stack. |
| **JSON Export** | Exposes the complete architecture recommendation payload via REST APIs. |
| **PDF Export** | Generates shareable ReportLab PDF files natively from the final architecture. |

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React / TypeScript / Vite | High-performance SPA rendering and strict type safety |
| **Backend** | FastAPI / Python 3.12 | High-throughput asynchronous REST API with rigid Pydantic schema validation |
| **AI / Orchestration**| OpenAI / LangChain | Foundational intelligence and semantic requirement parsing |
| **Embeddings** | BAAI/bge-base-en-v1.5 | Semantic representation of requirements and technology profiles |
| **Embedding Host** | Hugging Face Inference API | Serverless, remote embedding generation to maintain a lightweight API footprint |
| **Vector Database** | Qdrant | Fast semantic similarity search and local persistent technology profile storage |
| **Evaluation** | RAGAS | Statistically robust generation validation against known ground truth |
| **Reporting** | ReportLab | Programmatic PDF document synthesis for exportable reports |
| **Testing** | Pytest | Comprehensive unit and integration test execution |
| **Deployment** | Vercel / Render | CI/CD enabled platforms for decoupled frontend/backend hosting |

## System Architecture

The system utilizes a decoupled microservice architecture, separating the client application from the heavy decision-engine orchestration.

\\\mermaid
flowchart TB
    subgraph Client Layer
        Frontend[React SPA]
    end

    subgraph API Layer
        FastAPI[FastAPI Router]
    end

    subgraph Decision Engine
        RA[Requirement Analyzer]
        RE[Recommendation Engine]
        TR[Trade-off Analyzer]
    end

    subgraph AI and Retrieval Layer
        ES[Embedding Service]
        RET[Qdrant Retriever]
    end

    subgraph Knowledge Store
        QD[(Qdrant Vector DB)]
    end

    subgraph External Providers
        HF[Hugging Face Inference API]
        OAI[OpenAI / LLM API]
    end

    subgraph Presentation Layer
        RG[Report Generator]
        PDF[PDF Export Service]
    end

    Frontend -->|HTTP Requests| FastAPI
    FastAPI --> RA
    FastAPI --> RE
    FastAPI --> RG

    RA --> OAI
    RE --> TR
    RE --> RET

    RET --> ES
    ES --> HF
    RET --> QD

    RG --> PDF
\\\

## System Flow

The end-to-end flow traces a requirement through semantic translation, retrieval, and mathematical scoring.

\\\mermaid
flowchart TD
    User([User]) -->|Enters project requirements| Frontend[React Frontend]
    Frontend -->|POST /decision/recommend| API[FastAPI]
    API --> RA[Requirement Analyzer]
    RA --> PP[Project Profile]
    PP --> ES[Embedding Generation]
    ES -->|Hugging Face API| Vec[768-dim Vector]
    Vec --> QD[Qdrant Semantic Retrieval]
    QD --> CT[Candidate Technologies]
    CT --> DS[Decision Scoring]
    DS --> Rec[Architecture Recommendation]
    Rec --> AR[Architecture Report]
    AR -->|JSON Response| Frontend
    Frontend -->|Renders UI| User
\\\

## Recommendation Sequence

This sequence diagram details the strict synchronous processing pipeline and external API boundaries during a recommendation request.

\\\mermaid
sequenceDiagram
    participant Frontend
    participant FastAPI
    participant Analyzer as Requirement Analyzer
    participant Embedder as Embedding Service
    participant HuggingFace as Hugging Face API
    participant Retriever as Qdrant Retriever
    participant Engine as Decision Engine

    Frontend->>FastAPI: POST /api/v1/decision/recommend
    FastAPI->>Analyzer: extract_profile(prompt)
    Analyzer-->>FastAPI: ProjectProfile (Constraints)
    FastAPI->>Embedder: embed_query(profile_summary)
    Embedder->>HuggingFace: feature_extraction(text)
    HuggingFace-->>Embedder: 768-dim Vector
    Embedder-->>FastAPI: Vector
    FastAPI->>Retriever: query_candidates(Vector)
    Retriever-->>FastAPI: List[TechnologyComponent]
    FastAPI->>Engine: score_candidates(Components, Profile)
    Engine-->>FastAPI: ArchitectureRecommendation
    FastAPI-->>Frontend: DecisionResponse
\\\

<p align="center">
  <img src="./docs/screenshots/decision-engine.png" alt="Decision Engine Interface" width="900">
</p>
<p align="center"><i>The Decision Engine synchronously processes the pipeline stages, visualizing each deterministic step to the user.</i></p>

## Data and Knowledge Architecture

Forge avoids traditional relational databases (e.g., PostgreSQL or MySQL). All persistent data structures reside directly in Qdrant as semantic vectors with rich payload metadata. These payloads are validated strictly in-memory using Pydantic schemas.

\\\mermaid
erDiagram
    ProjectProfile ||--o{ Constraint : extracts
    ProjectProfile {
        string project_name
        string domain
        string scale
        string deployment_target
        string optimization_priority
    }
    Constraint {
        string category
        boolean is_hard_constraint
        string description
    }
    TechnologyComponent ||--o{ Metadata : contains
    TechnologyComponent {
        string component_id
        string name
        string category
        string license
        float cost_indicator
    }
    Metadata {
        string performance_tier
        int context_window
        string deployment_options
    }
    ArchitectureRecommendation ||--o{ TechnologyComponent : selects
    ArchitectureRecommendation ||--o{ Rationale : includes
    ArchitectureRecommendation {
        string id
        float total_confidence_score
    }
    Rationale {
        string component_id
        string reason
        string trade_offs
    }
\\\

## Decision Engine Pipeline

Forge converts retrieved candidates into structured recommendations using a deterministic, multi-stage pipeline:

1. **Filtering**: The scoring engine applies hard filters based on the parsed ProjectProfile. If a user requires an open-source model, proprietary APIs (e.g., GPT-4) are immediately eliminated.
2. **Prioritization**: The engine applies weights derived from the user's optimization_priority (latency, cost, or quality).
3. **Scoring**: Remaining candidates are scored mathematically. A model with high throughput scores highly on latency-optimized configurations.
4. **Recommendation Generation**: The highest-scoring combination of LLM, vector database, and embedding model is designated the winner.
5. **Trade-off Analysis**: The engine compares the winning stack against runner-up components to generate explicit readable rationales explaining the necessary engineering compromises.

<p align="center">
  <img src="./docs/screenshots/architecture-report-1.png" alt="Architecture Decision Report - Overview" width="900">
</p>
<br/>
<p align="center">
  <img src="./docs/screenshots/architecture-report-2.png" alt="Architecture Decision Report - Rationale" width="900">
</p>
<p align="center"><i>Architecture Decision Report — Forge transforms project requirements into structured, evidence-backed architecture decisions containing explicit trade-off reasoning.</i></p>

## Report Generation

The backend aggregates all decision signals and technical rationales into a final ArchitectureReport schema.

- **JSON Export**: The structured data is returned to the frontend for interactive rendering.
- **PDF Generation**: When requested, the FastAPI backend invokes ReportLab to programmatically format the JSON data into a styled engineering document.

**Frontend PDF Download Flow:**
Frontend &rarr; API request &rarr; FastAPI PDF endpoint &rarr; ReportLab generation &rarr; binary PDF response &rarr; Browser handles the download blob.

<p align="center">
  <img src="./docs/screenshots/pdf-report.png" alt="Exportable Architecture Report" width="900">
</p>
<p align="center"><i>Exportable Architecture Report — Recommendations can be natively exported as a structured engineering PDF artifact.</i></p>

## Evaluation

Forge includes an explicit synthetic evaluation engine powered by the **RAGAS** framework. This system validates the quality of the architecture recommendation by statistically scoring the generated response against the retrieved context and known ground truth.

- **Evaluation Input**: The initial user query constraint.
- **Retrieved Context**: The technology specifications provided by Qdrant.
- **Generated Answer**: The rationale produced by the decision engine.
- **Metrics**:
  - **Faithfulness**: Measures whether the rationale is factually supported by the retrieved technology specifications.
  - **Answer Relevancy**: Measures whether the generated architecture directly addresses the user's explicit prompt.

<p align="center">
  <img src="./docs/screenshots/evaluation.png" alt="Evaluation Pipeline" width="900">
</p>
<p align="center"><i>Evaluation Pipeline — Forge statistically evaluates retrieved context and generated responses against known ground truth.</i></p>

## API Overview

The FastAPI backend exposes the following core capabilities:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/v1/decision/recommend | Generates architecture recommendations and rationale from project requirements. |
| GET | /api/v1/knowledge | Retrieves paginated specifications of registered AI technologies from the Qdrant store. |
| POST | /api/v1/reports/generate | Generates a structured JSON architecture decision report from decision data. |
| POST | /api/v1/reports/pdf | Generates the architecture report as a binary PDF download. |
| POST | /api/v1/evaluation/evaluate | Runs Ragas metrics against a provided architecture recommendation and context payload. |

## Project Structure

`	ext
Forge/
├── app/                     # FastAPI Backend Application
│   ├── api/                 # Route definitions and controllers
│   ├── core/                # Configuration and environment variables
│   ├── decision/            # Constraint extraction, scoring, and trade-off analysis
│   ├── embeddings/          # Hugging Face Inference API integrations
│   ├── evaluation/          # RAGAS evaluation engine integration
│   ├── reports/             # PDF export generation (ReportLab)
│   ├── retriever/           # Qdrant retrieval implementation
│   ├── schemas/             # Pydantic validation models
│   └── services/            # Request orchestration layer
├── docs/                    # Documentation assets
│   └── screenshots/         # Professional UI screenshots
├── frontend/                # React Single Page Application
│   ├── public/              # Static assets (including forge-logo.png)
│   └── src/
│       ├── components/      # Reusable UI elements
│       ├── context/         # React Context for global state
│       ├── pages/           # Main views (Decision Engine, Evaluation, Reports)
│       └── services/        # HTTP API client layer
├── knowledge_base/          # Local Qdrant SQLite vector storage
├── tests/                   # Pytest suite
├── .env.example             # Template for required environment variables
├── requirements.txt         # Backend Python dependencies
└── README.md                # Project documentation
`

## Local Development

### Prerequisites

- Python 3.12
- Node.js 18+
- Git

### Clone Repository

`ash
git clone https://github.com/somiya-namdeo/Forge.git
cd Forge
`

### Backend Setup

`ash
# Create and activate virtual environment
python -m venv .venv

# On Unix/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
`

### Frontend Setup

`ash
cd frontend
npm install
`

### Environment Variables

Create a .env file in the root directory based on .env.example:

| Variable | Required | Purpose | Example |
|---|---|---|---|
| OPENAI_API_KEY | Yes | Requirement extraction and rationale generation | sk-... |
| HUGGINGFACEHUB_API_TOKEN | Yes | Remote embedding generation | hf_... |
| EMBEDDING_MODEL | No | Overrides the default embedding model | BAAI/bge-base-en-v1.5 |
| FRONTEND_URL | No | Configures CORS for the backend | http://localhost:5173 |

### Run Application

Start the backend (from the repository root):

`ash
uvicorn app.main:app --reload --port 8000
`

Start the frontend (from the rontend/ directory):

`ash
npm run dev
`

## Testing

The backend includes a comprehensive pytest suite covering decision scoring, API endpoints, and retrieval logic. The repository currently maintains 25 passing tests.

To run the test suite:

`ash
pytest tests/
`

## Deployment

The application utilizes a decoupled deployment architecture:

`mermaid
flowchart LR
    User([User]) --> Vercel[Frontend - Vercel]
    Vercel --> Render[Backend - Render]
    Render --> HF[Hugging Face API]
    Render --> OAI[OpenAI API]
`

- **Frontend**: Deployed on Vercel as a static SPA. Requires VITE_API_URL pointing to the backend.
- **Backend**: Deployed on Render as a Python Web Service. Requires OPENAI_API_KEY and HUGGINGFACEHUB_API_TOKEN configured in the Render dashboard.
- **Data**: Qdrant runs locally within the Render instance utilizing local disk persistence.

## Engineering Design Decisions

- **Semantic Retrieval over Hardcoding**: Instead of hardcoding model limits in standard conditional statements, Forge dynamically queries Qdrant. This allows the knowledge base to be updated rapidly without altering application logic.
- **Schema-less Vector Storage**: By avoiding a relational database, Forge streamlines deployment and allows unstructured documentation to be seamlessly embedded alongside structured capability limits.
- **Remote Embedding Inference**: Forge offloads the BAAI/bge-base-en-v1.5 workload to Hugging Face rather than running local PyTorch SentenceTransformer binaries. This architectural decision significantly reduces CPU and RAM usage, enabling the backend to run reliably on resource-constrained platforms (like the Render free tier).
- **Separation of Analysis and Scoring**: The LLM is only used to parse requirements into structured schemas. The actual technology selection is handled by a deterministic mathematical scoring engine. This rigidly prevents LLM hallucinations from recommending incompatible architectures.

## Limitations

- **Knowledge Freshness**: The accuracy of recommendations is strictly bound to the freshness of the Qdrant knowledge base. If new models are released, the database must be manually updated.
- **External API Dependency**: The system relies heavily on the availability of the Hugging Face Inference API and OpenAI APIs. Network degradation heavily impacts recommendation latency.
- **Domain Coverage**: Currently limited to standard RAG architectures, missing deep coverage for multi-agent systems or edge-deployment specific constraints.

## Future Improvements

- **Automated Knowledge Refresh**: Implementing pipelines to automatically scrape and embed new model specifications from the Hugging Face Model Hub.
- **Expanded Inference Providers**: Adding fallback logic to Anthropic or Groq if primary APIs are rate-limited.
- **Cost Estimation**: Providing estimated monthly infrastructure costs based on the recommended architecture and projected request scale.
- **Expanded Evaluation Coverage**: Adding multi-turn context evaluations and retrieval precision metrics.

## License

Distributed under the MIT License.