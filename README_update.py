content = '''# Forge

![Landing Page](frontend/public/screenshots/landing%20page.png)

Forge is an enterprise-grade AI architecture decision engine. It evaluates system constraints, automatically recommends robust RAG (Retrieval-Augmented Generation) architectures, and provides deterministic, evidence-based reasoning for its choices.

## 🚀 Live Deployment

- **Frontend (Vercel)**: [https://forge-beta-gilt-16.vercel.app](https://forge-beta-gilt-16.vercel.app)
- **Backend (Render)**: [https://forge-mmz3.onrender.com](https://forge-mmz3.onrender.com)
- **Repository**: [https://github.com/somiya-namdeo/Forge](https://github.com/somiya-namdeo/Forge)

## 📸 Platform Previews

### Decision Engine
Input strict project requirements, constraints, and budgets to receive statistically-backed architecture recommendations.

![Decision Engine](frontend/public/screenshots/decision-engine.png)

### Architecture Recommendations
Forge provides deep technical rationale, analyzing *why* a component was chosen and *why* alternatives were rejected.

![Architecture Report 1](frontend/public/screenshots/architecture1.png)
![Architecture Report 2](frontend/public/screenshots/architecture2.png)

### Quality Evaluation
Deep integration with RAGAS metrics to score and validate the proposed architecture against real-world QA contexts.

![Evaluation Engine](frontend/public/screenshots/evaluation1.png)
![Evaluation Results](frontend/public/screenshots/evaluation2.png)

### Unified Reports & Knowledge Base
Aggregate your decisions into portable engineering PDFs, while querying the underlying RAG knowledge base.

![Engineering Report](frontend/public/screenshots/report1.png)
![Report PDF Export](frontend/public/screenshots/report2.png)
![Knowledge Base Explorer](frontend/public/screenshots/knowledge-base.png)

## 🧠 Architecture & Data Flow

\\\mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant DecisionEngine
    participant KnowledgeRetriever
    participant Qdrant
    participant HuggingFaceAPI
    
    User->>Frontend: Submit constraints (e.g. latency, security)
    Frontend->>DecisionEngine: POST /api/v1/decision/recommend
    DecisionEngine->>HuggingFaceAPI: embed_query(constraints)
    HuggingFaceAPI-->>DecisionEngine: 768-dim Vector
    DecisionEngine->>KnowledgeRetriever: Retrieve component specs
    KnowledgeRetriever->>Qdrant: Query knowledge base
    Qdrant-->>KnowledgeRetriever: Return valid components
    KnowledgeRetriever-->>DecisionEngine: Component context
    DecisionEngine->>DecisionEngine: Score and extract constraints
    DecisionEngine-->>Frontend: Return DecisionResponse (Components + Reasoning)
    Frontend-->>User: Display Recommended Architecture
\\\

## 📁 Project Structure

\\\	ext
forge/
├── app/                     # FastAPI Backend
│   ├── api/                 # API route definitions
│   ├── core/                # Configuration and env variables
│   ├── decision/            # Constraint extraction and component scoring
│   ├── embeddings/          # Hugging Face Inference API integrations
│   ├── evaluation/          # Core Ragas evaluation engine
│   ├── reports/             # PDF export generation (ReportLab)
│   ├── retriever/           # Qdrant integration
│   ├── schemas/             # Pydantic validation models
│   └── services/            # Orchestration layer
├── frontend/                # React SPA
│   ├── public/screenshots/  # Application UI previews
│   └── src/
│       ├── components/      # Reusable UI elements
│       ├── context/         # React Context for global state
│       ├── pages/           # Main views (Decision Engine, Evaluation, Reports)
│       ├── services/        # HTTP API client layer
│       └── types/           # TypeScript interfaces matching backend Pydantic models
├── tests/                   # Pytest suite
├── .python-version          # Pinned to 3.12
└── requirements.txt         # Clean, Render-optimized Python dependencies
\\\

## 🛠️ Tech Stack

| Category | Technology | Purpose |
| --- | --- | --- |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS | High-performance, modular SPA rendering |
| **Backend Core** | FastAPI, Python 3.12, Pydantic | High-throughput REST API with strict schema validation |
| **Vector Database** | Qdrant | Structured application state and vector operations |
| **Model Interfaces** | OpenAI, LangChain | Foundational intelligence |
| **Evaluation** | RAGAS | Statistically robust RAG generation validation |
| **Embeddings** | Hugging Face Inference API | Serverless API-based embeddings (bge-base-en-v1.5) to maintain lightweight deployment |
| **Reports** | ReportLab | PDF architectural document generation |

## ⚙️ Engineering Workflow

1. **Requirements**: User inputs their constraints (e.g., latency, cost, security, domain).
2. **Architecture Recommendation**: Forge filters candidates and recommends a highly specific LLM, embedding model, and vector DB.
3. **Explanation**: Forge outputs exactly *why* components were chosen or rejected.
4. **Evaluation**: Proposed inputs and contexts can be validated against RAGAS metrics.
5. **Report Generation**: Data is exported as a unified engineering specification PDF.

## 💻 Local Development Setup

### 1. Clone the Repository
\\\ash
git clone https://github.com/somiya-namdeo/Forge.git
cd Forge
\\\

### 2. Backend Setup
The backend relies on Python 3.12 and is optimized for lightweight deployment, utilizing external APIs for ML workloads.

\\\ash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
\\\

### 3. Frontend Setup
\\\ash
cd frontend
npm install
\\\

### 4. Environment Variables
Create a \.env\ file in the root \orge/\ directory:
\\\env
OPENAI_API_KEY=your_openai_key
HUGGINGFACEHUB_API_TOKEN=your_hf_token
FRONTEND_URL=http://localhost:5173
\\\

### 5. Run the Backend
\\\ash
# From the repository root
uvicorn app.main:app --reload --port 8000
\\\

### 6. Run the Frontend
\\\ash
# In the frontend/ directory
npm run dev
\\\

## 🧪 Running Tests

The backend includes a comprehensive pytest suite testing all decision logic, retrievers, and API endpoints.

\\\ash
# From the repository root
pytest tests/
\\\

## 📐 Design Principles

- **Evidence-Driven Recommendations**: Avoids blindly guessing architectures; maps decisions directly to explicitly declared constraints.
- **Deterministic Scoring**: Utilizes rigid weighting mechanisms rather than pure LLM probabilistic completion.
- **Transparent Reasoning**: "Why" is treated as a first-class citizen alongside "What".
- **Explainability**: Focuses heavily on avoiding black-box decision systems.
- **Engineering-First Design**: Built to integrate directly into architectural design documents.

## 📄 License

Distributed under the MIT License. See LICENSE for more information.
'''

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
