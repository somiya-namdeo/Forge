import urllib.request
import base64
import os

diagrams = {
    "architecture.png": """flowchart LR
    U[User] --> UI[Forge Web Interface]
    subgraph Frontend["Frontend"]
        UI
        EXPORT[JSON / PDF Export]
    end
    subgraph Backend["FastAPI Backend"]
        API[REST API]
        ANALYZER[Requirement Analyzer]
        RETRIEVAL[Retrieval Pipeline]
        SCORING[Decision Scoring Engine]
        REPORTING[Report Generator]
    end
    subgraph AI["AI Services"]
        EMB[Embedding Service]
        LLM[LLM Service / OpenAI]
    end
    subgraph Knowledge["Knowledge Infrastructure"]
        QDRANT[(Qdrant Vector Database)]
    end
    UI --> API
    API --> ANALYZER
    ANALYZER --> LLM
    LLM --> RETRIEVAL
    RETRIEVAL --> EMB
    EMB --> QDRANT
    QDRANT --> RETRIEVAL
    RETRIEVAL --> SCORING
    SCORING --> LLM
    LLM --> REPORTING
    REPORTING --> EXPORT
    EXPORT --> UI
""",
    "system-flow.png": """flowchart LR
    User([User Requirements]) --> Frontend[React Frontend]
    Frontend --> API[FastAPI Backend]
    API --> RA[Requirement Analysis]
    RA --> PP[Project Profile]
    PP --> ES[Query Embedding]
    ES --> QD[Semantic Retrieval]
    QD --> CT[Candidate Filtering]
    CT --> DS[Decision Scoring]
    DS --> Rec[Architecture Selection]
    Rec --> Rationale[Rationale Generation]
    Rationale --> AR[Architecture Report]
    AR --> Frontend
""",
    "sequence.png": """sequenceDiagram
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
    "data-model.png": """erDiagram
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
        float total_score
    }
    Rationale {
        string component_id
        string reason
        string trade_offs
    }
""",
    "deployment.png": """flowchart LR
    U[User] --> V[Vercel Frontend]
    V --> R[Render FastAPI Backend]
    R --> HF[Hugging Face Inference API]
    R --> OA[OpenAI API]
    R --> QD[(Local Qdrant Data)]
""",
    "decision-pipeline.png": """flowchart LR
    A[Requirement Input] --> B[Requirement Analysis]
    B --> C[Constraint Extraction]
    C --> D[Project Profile]
    D --> E[Semantic Retrieval]
    E --> F[Candidate Filtering]
    F --> G[Weighted Scoring]
    G --> H[Architecture Selection]
    H --> I[Rationale Generation]
    I --> J[Final Recommendation]
"""
}

os.makedirs("docs/diagrams", exist_ok=True)

# Generate high-res PNGs with white backgrounds
for filename, mmd in diagrams.items():
    b64 = base64.b64encode(mmd.encode('utf-8')).decode('utf-8')
    # bgColor=ffffff ensures solid white background instead of transparency
    url = f"https://mermaid.ink/img/{b64}?bgColor=ffffff"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            png_content = response.read()
            with open(f"docs/diagrams/{filename}", "wb") as out_file:
                out_file.write(png_content)
        print(f"Downloaded PNG {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")