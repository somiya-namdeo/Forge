import urllib.request
import base64

diagrams = {
    "architecture.svg": """flowchart TB
    U[User]

    subgraph Frontend["Frontend"]
        UI[Forge Web Interface]
        INPUT[Requirement Input]
        REPORT[Architecture Report]
        EXPORT[JSON / PDF Export]
    end

    subgraph Backend["FastAPI Backend"]
        API[REST API]
        ANALYZER[Requirement Analyzer]
        PROFILE[Project Profile]
        RETRIEVAL[Retrieval Pipeline]
        SCORING[Decision Scoring]
        REPORTING[Report Generator]
    end

    subgraph AI["AI Services"]
        EMB[Embedding Service]
        LLM[LLM Service / OpenAI]
    end

    subgraph Knowledge["Knowledge Infrastructure"]
        QDRANT[(Qdrant Vector Database)]
        KB[Technology Knowledge Base]
    end

    U --> UI
    UI --> INPUT
    INPUT --> API
    API --> ANALYZER
    ANALYZER --> LLM
    LLM --> PROFILE
    PROFILE --> RETRIEVAL
    RETRIEVAL --> EMB
    EMB --> QDRANT
    KB --> QDRANT
    QDRANT --> RETRIEVAL
    RETRIEVAL --> SCORING
    SCORING --> LLM
    LLM --> REPORTING
    REPORTING --> REPORT
    REPORT --> EXPORT
    REPORT --> UI
""",
    "system-flow.svg": """flowchart TD
    User([User]) -->|enters project requirements| Frontend[React Frontend]
    Frontend -->|POST /decision/recommend| API[FastAPI]
    API --> RA[Requirement Analyzer]
    RA --> PP[Project Profile]
    PP --> ES[Embedding Generation]
    ES -->|Hugging Face API| Vec[768-dim Vector]
    Vec --> QD[Qdrant Semantic Retrieval]
    QD --> CT[Candidate Technologies]
    CT --> DS[Decision Scoring & Filtering]
    DS --> Rec[Architecture Recommendation]
    Rec --> AR[Architecture Report]
    AR -->|JSON Response| Frontend
    Frontend -->|Renders UI| User
""",
    "sequence.svg": """sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant API as FastAPI Backend
    participant REQ as Requirement Analyzer
    participant HF as Hugging Face API
    participant QD as Qdrant
    participant ENG as Decision Engine
    participant OAI as OpenAI API
    participant REP as Report Generator

    U->>UI: Submits constraints
    UI->>API: POST /api/v1/decision/recommend
    API->>REQ: Analyze text
    REQ->>OAI: Extract strict constraints
    OAI-->>REQ: Project Profile Schema
    API->>HF: embed_query(profile)
    HF-->>API: 768-dim Vector
    API->>QD: Search candidates (Cosine Similarity)
    QD-->>API: List[TechnologyComponent]
    API->>ENG: score_candidates()
    ENG-->>API: ArchitectureRecommendation
    API->>REP: generate_rationale()
    REP-->>API: ArchitectureReport
    API-->>UI: JSON Response
    UI-->>U: Renders Recommendation
""",
    "data-model.svg": """erDiagram
    ProjectProfile ||--o{ Constraint : extracts
    ProjectProfile {
        string project_name
        string domain
        string scale
        string deployment_target
        string optimization_priority
    }
    TechnologyComponent ||--o{ Metadata : contains
    TechnologyComponent {
        string component_id
        string name
        string category
        string license
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
""",
    "deployment.svg": """flowchart LR
    U[User] --> V[Vercel Frontend]
    V --> R[Render FastAPI Backend]
    R --> HF[Hugging Face Inference API]
    R --> OA[OpenAI API]
    R --> QD[(Local Qdrant Data)]
""",
    "decision-pipeline.svg": """flowchart LR
    A[Requirements] --> B[Requirement Analysis]
    B --> C[Project Profile]
    C --> D[Query Embedding]
    D --> E[Semantic Retrieval]
    E --> F[Candidate Filtering]
    F --> G[Scoring]
    G --> H[Architecture Selection]
    H --> I[Rationale]
    I --> J[Report]
"""
}

for filename, mmd in diagrams.items():
    b64 = base64.b64encode(mmd.encode('utf-8')).decode('utf-8')
    url = f"https://mermaid.ink/svg/{b64}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response, open(f"docs/diagrams/{filename}", "wb") as out_file:
            out_file.write(response.read())
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")