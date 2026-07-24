# Forge v2.0: AI Engineering Research Assistant

Forge is a production-grade AI Engineering Research Assistant powered by Retrieval-Augmented Generation (RAG) and multi-agent LLM reasoning. It automatically ingests official AI documentation, builds a searchable vector knowledge base, and generates evidence-backed AI stack recommendations with citations.

## Architecture & Implementation

For full details on the system architecture, Multi-Agent LLM reasoning pipelines, data models, and deployment strategy, please refer to the official design documents:

- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)

## Project Structure

- `backend/`: Python FastAPI Backend & RAG Engine (Agents, Workflows, Retrieval, Processing).
- `frontend/`: React-based web interface for AI stack recommendations.
- `evaluation/`: Golden datasets and scripts (e.g., Ragas/DeepEval) for CI/CD pipeline evaluation.
- `notebooks/`: Experimental scratchpad for benchmarking embedding and chunking models.
- `docs/`: Technical documentation and implementation roadmaps.

## Getting Started

*(Development setup instructions will be added during Phase 1 of the implementation roadmap).*
