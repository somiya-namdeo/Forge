# Forge Source Registry v1.1

## Source Registry Philosophy
The Forge Source Registry is designed to be the foundational knowledge ingestion pipeline for the Forge Knowledge Base. It prioritizes **accuracy, maintainability, and trustworthiness over completeness**. The registry does not scrape arbitrary community resources; it explicitly mandates verified official origins to prevent hallucinations and supply chain attacks within the AI knowledge base.

## Canonical Implementation Principle
Techniques and patterns (such as ReAct, Multi-Query Retrieval, or QLoRA) should map directly to their widely accepted **Canonical Official Implementation** whenever one exists (e.g., mapping `Multi-Query Retrieval` to `LangChain`). This grounds abstract concepts in tangible, actionable code without altering the name of the technique itself. 

## Official Metadata Policy
We mandate a strict metadata hierarchy. If a field cannot be validated against an official resource, it is explicitly left as an empty array or empty string. The priority order for documentation is:
1. Official documentation site
2. Official GitHub README (if no dedicated docs site exists)
3. Official API/reference documentation
4. Official GitHub repository
5. Official research papers

We actively forbid Medium, Reddit, personal blogs, or unofficial tutorials. 

## Organization Policy
The `organization` field MUST represent the canonical implementation owner (e.g., `LangChain`, `LlamaIndex`, `Microsoft`, `CNCF`, `Hugging Face`). Individual author names are not used. In cases where an abstract concept has no formal framework owner (e.g., *Self-Consistency* or *Agentic Chunking*), the organization is strictly set to `Independent Research`.

## Update Policy
Updates occur on a strict, category-by-category basis (`update_frequency = "weekly"`). Modifications to existing schemas or IDs are not permitted without an architectural version bump. The registry is strictly append/update metadata only. 

## Validation Process
All entries undergo rigorous automated and manual validation. The validation process guarantees:
- 100% JSON schema adherence.
- Field presence and identical ordering across all files.
- Absolute HTTPS-only link enforcement.
- Strict mapping of licenses to open-source identifiers (MIT, Apache-2.0, etc.).
- Complete eradication of duplicate IDs and URLs. 
- Validation against WAF blocks (403/429) to verify endpoint existence before freezing.
