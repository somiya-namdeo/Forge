import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.schemas.knowledge import (
    KnowledgeComponent,
    KnowledgeRegistryResponse,
    KnowledgeCategoryCount,
)
from app.retriever.qdrant_retriever import get_qdrant_client
from app.core.config import COLLECTION_NAME

logger = logging.getLogger(__name__)

class KnowledgeService:
    def __init__(self):
        self._client = get_qdrant_client()

    def get_knowledge_registry(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 24,
    ) -> KnowledgeRegistryResponse:
        """Fetch deduplicated knowledge components from Qdrant with optional filtering."""
        
        # We need to scroll all items to deduplicate properly in-memory since 
        # Qdrant doesn't have a native "GROUP BY" without returning many points.
        # Given ~5000 chunks, scrolling them all (metadata only) takes very little time/memory.
        all_payloads: List[Dict[str, Any]] = []
        offset = None
        
        try:
            while True:
                response = self._client.scroll(
                    collection_name=COLLECTION_NAME,
                    limit=1000,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                points = response[0]
                next_offset = response[1]
                
                for point in points:
                    if point.payload:
                        all_payloads.append(point.payload)
                
                if next_offset is None:
                    break
                offset = next_offset
        except Exception as e:
            logger.error(f"Failed to scroll Qdrant collection {COLLECTION_NAME}: {e}")
            # If Qdrant is completely uninitialized or missing, return empty
            return KnowledgeRegistryResponse(
                totalComponents=0,
                lastSync=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                categories=[],
                components=[],
                page=page,
                page_size=page_size,
                total_pages=0
            )

        # Deduplicate by technology_id (or technology name)
        tech_map: Dict[str, Dict[str, Any]] = {}
        for p in all_payloads:
            tech_id = p.get("technology_id") or p.get("technology") or p.get("name")
            if not tech_id:
                continue
                
            tech_id_str = str(tech_id).strip()
            
            # Skip internal deepeval test chunks if existing logic does it
            if "deepeval" in tech_id_str.lower():
                continue
                
            if tech_id_str not in tech_map:
                tech_map[tech_id_str] = p

        # Extract deduplicated technologies
        unique_techs = list(tech_map.values())

        # Category counting (pre-filter)
        category_counts: Dict[str, int] = {}
        for p in unique_techs:
            cat = p.get("category", "general")
            cat_str = str(cat).strip().lower()
            category_counts[cat_str] = category_counts.get(cat_str, 0) + 1

        categories = [
            KnowledgeCategoryCount(name=k, count=v, label=k.replace("_", " ").title())
            for k, v in sorted(category_counts.items())
        ]

        # Apply filters
        filtered_techs = []
        search_lower = search.lower() if search else None
        cat_lower = category.lower() if category and category.lower() != "all" else None
        
        for p in unique_techs:
            p_cat = str(p.get("category", "general")).strip().lower()
            if cat_lower and p_cat != cat_lower:
                continue
                
            if search_lower:
                searchable_text = f"{p.get('technology', '')} {p.get('description', '')} {p.get('technology_id', '')}".lower()
                if search_lower not in searchable_text:
                    continue
                    
            filtered_techs.append(p)

        # Sort alphabetically by technology name for consistency
        filtered_techs.sort(key=lambda x: str(x.get("technology", x.get("technology_id", ""))).lower())

        total_filtered = len(filtered_techs)
        total_pages = max(1, (total_filtered + page_size - 1) // page_size)
        
        # Paginate
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_techs = filtered_techs[start_idx:end_idx]

        # Transform to KnowledgeComponent
        components = []
        for p in paginated_techs:
            tech_id = str(p.get("technology_id") or p.get("technology") or "unknown")
            cat = str(p.get("category", "general")).strip().lower()
            
            # Key features could be a list or a string in metadata. Ensure it's a list.
            features_raw = p.get("keyFeatures") or p.get("key_features") or []
            if isinstance(features_raw, str):
                features = [f.strip() for f in features_raw.split(",") if f.strip()]
            elif isinstance(features_raw, list):
                features = [str(f) for f in features_raw]
            else:
                features = []
                
            raw_desc = p.get("description")
            if not raw_desc:
                text_lines = p.get("text", "").split("\n")
                clean_lines = []
                for line in text_lines:
                    line = line.strip()
                    if len(line) < 45: continue
                    if line.startswith("-") or line.startswith("*"): continue
                    if line.count("|") > 2: continue
                    # Filter out common scraped UI navigation/artifacts
                    lower_line = line.lower()
                    if " spaces " in lower_line or "leaderboard" in lower_line or "fetching metadata" in lower_line: continue
                    clean_lines.append(line)
                
                if clean_lines:
                    raw_desc = clean_lines[0]
                    if len(raw_desc) > 250:
                        raw_desc = raw_desc[:247] + "..."
                else:
                    raw_desc = "Description unavailable"

            components.append(
                KnowledgeComponent(
                    id=tech_id,
                    category=cat,
                    name=str(p.get("technology") or p.get("name") or tech_id),
                    organization=p.get("organization"),
                    officialDocumentation=p.get("url") or p.get("officialDocumentation"),
                    githubRepository=p.get("github") or p.get("githubRepository"),
                    license=p.get("license"),
                    priority=None,
                    lastVerified=None,
                    description=raw_desc,
                    keyFeatures=features
                )
            )

        return KnowledgeRegistryResponse(
            totalComponents=len(unique_techs),
            lastSync=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            categories=categories,
            components=components,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
