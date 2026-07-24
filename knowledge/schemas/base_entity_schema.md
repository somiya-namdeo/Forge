# Base Entity Schema

## Purpose

As Forge's knowledge base expands, managing independent schemas for every technology (LLMs, Vector DBs, Frameworks) leads to field duplication and maintenance overhead. The conceptual **Base Entity** serves as a foundational blueprint that defines the common attributes shared across nearly all AI knowledge entities. 

By standardizing these universal fields—such as identity, licensing, and metadata—we ensure consistent ingestion, streamlined querying, and uniform evaluation logic. While Forge's JSON schemas remain standalone files to avoid the complexities of JSON inheritance parsing, they conceptually implement this Base Entity, ensuring a unified architectural language without sacrificing simplicity.

---

## Common Fields

The Base Entity defines the following fields that are expected to exist across the majority of Forge's domain-specific schemas.

### Identity
- **`id`** *(UUID)*: The unique identifier for the entity across the entire platform.
- **`name`** *(String)*: The human-readable name of the technology or technique.
- **`category`** *(String)*: The primary architectural domain (e.g., "Vector Database", "Large Language Model").
- **`description`** *(String)*: A concise summary of the entity and its primary function.

### Ownership
- **`developer`** *(String)*: The individual, community, or company that created the entity.
- **`organization`** *(String)*: The parent organization or legal entity backing the project.

### Licensing
- **`license`** *(String)*: The specific license type (e.g., "MIT", "Apache-2.0", "Proprietary").
- **`open_source`** *(Boolean)*: A quick-filter flag indicating if the technology is open source.

### Sources
The Base Entity replaces single-field references with a scalable array of multiple authoritative sources. Relying on diverse sources (like cross-referencing GitHub with Model Cards) dramatically improves recommendation quality and minimizes LLM hallucinations during generation.

Each source in the array should define:
- **`source_type`** *(Enum)*: Identifies the type (e.g., Official Documentation, GitHub Repository, Hugging Face, Research Paper, Technical Blog, Benchmark, API Documentation, Release Notes).
- **`url`** *(String/URL)*: The canonical link to the source.
- **`confidence`** *(Float)*: Assigned metric of the source's reliability and trust level.
- **`last_verified`** *(Timestamp)*: When this specific link was last validated or scraped.

### Recommendation
- **`advantages`** *(Array[String])*: Key strengths, used by the reasoning engine to justify recommendations.
- **`limitations`** *(Array[String])*: Known drawbacks or bottlenecks, used to evaluate trade-offs against constraints.

### Metadata
- **`schema_version`** *(String)*: The version of the schema structure this entity complies with.
- **`data_version`** *(String)*: The specific release version of the technology itself.
- **`created_at`** *(Timestamp)*: When this record was initially ingested.
- **`updated_at`** *(Timestamp)*: When this record was last refreshed from its sources.
- **`verified`** *(Boolean)*: Indicates if the data has passed manual or automated accuracy verification.
- **`confidence_score`** *(Float)*: System-calculated metric of the data's reliability and freshness.

---

## Naming Conventions

To guarantee precise entity resolution, every entity in Forge must strictly define:

- **`canonical_name`** *(String)*: The single, authoritative string representation of the technology (e.g., `LangChain`).
- **`aliases`** *(Array[String])* 
 An array of known variations, misspellings, or alternative casings (e.g., `["langchain", "Lang Chain", "lang-chain"]`).

Explicit alias management enables:
- **Search normalization**: User queries mapping reliably to the core entity.
- **Duplicate prevention**: Ingestion pipelines avoiding double-record creation.
- **Entity resolution**: Reasoning engines correctly merging disparate references.
- **Synonym matching**: Substantially higher retrieval quality during vector search.

---

## Design Principles

- **Single Source of Truth**: Core definitions like identity and metadata are defined once conceptually, preventing divergent naming conventions across files (e.g., using `license` vs `license_type`).
- **Minimal Duplication**: Ensures that developers don't have to reinvent the wheel when designing schemas for new AI ecosystem tools.
- **Extensibility**: The Base Entity provides the floor, not the ceiling. Specific schemas add whatever domain-specific fields they require.
- **Machine Readability**: Consistent typing and naming allow the Decision Engine to write generic filtering queries that apply to all entities.
- **Human Readability**: Schemas remain flat JSON files, easy for contributors to read, audit, and update manually.
- **Versionability**: Tracking both structural (`schema_version`) and content (`data_version`) changes allows Forge to maintain backward compatibility.
- **Forward Compatibility**: As new metrics become standard (e.g., carbon footprint), they can be added to the Base Entity and conceptually adopted by all specific schemas.
- **Source Traceability**: Every factual statement in the knowledge base should be traceable to one or more authoritative sources.
- **Entity Normalization**: Every technology should have exactly one canonical representation regardless of naming variations.

---

## Relationship to Other Schemas

The architecture models specific schemas as a composite of the Base Entity plus domain-specific properties.

```text
+-----------------------+
|                       |
|   Base Entity         |
|   (Identity, Meta)    |
|                       |
+-----------+-----------+
            ^
            | (Conceptually Extends)
            |
+-----------+-----------+
|                       |
|   Domain Schema       |
|   (Specific Fields)   |
|                       |
+-----------------------+
```

- **LLM Schema** = Base Entity + LLM-specific fields
- **Embedding Schema** = Base Entity + Embedding-specific fields
- **Vector Database Schema** = Base Entity + Vector Database-specific fields
- **Framework Schema** = Base Entity + Framework-specific fields
- **Reranker Schema** = Base Entity + Reranker-specific fields
- **Retrieval Schema** = Base Entity + Retrieval-specific fields
- **Chunking Schema** = Base Entity + Chunking-specific fields
- **Prompting Schema** = Base Entity + Prompting-specific fields
- **Agent Schema** = Base Entity + Agent-specific fields
- **Evaluation Schema** = Base Entity + Evaluation-specific fields

---

## Migration Strategy

Because Forge avoids strict JSON inheritance in favor of standalone, flat JSON files, adopting the Base Entity is a gradual, non-breaking process:

1. **Audit Existing Schemas**: Compare current JSON files (`llm_schema.json`, etc.) against the Base Entity definition.
2. **Standardize Naming**: Refactor fields in existing schemas to match the Base Entity exactly (e.g., changing `developer_name` to `developer`).
3. **Inject Missing Fields**: Run a migration script to add missing metadata fields (`created_at`, `confidence_score`) to existing records with safe default values.
4. **Validation Updates**: Update the ingestion pipeline to validate the Base Entity fields globally before checking domain-specific validation rules.

---

## Future Extensions

The Base Entity dramatically accelerates the integration of future technologies into Forge. When a novel AI paradigm emerges, architects can instantly generate a new schema by copying the Base Entity template and appending only the fields unique to that new domain. This ensures the new technology is immediately searchable, filterable, and compatible with the existing reasoning engine from day one.

Planned advanced features leveraging this foundation include:
- Automatic source verification
- Duplicate entity detection
- Knowledge graph synchronization
- Source confidence recalculation
- Alias generation
- Automated documentation updates
