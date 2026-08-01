"""Standalone debugging utility to inspect knowledge_base metadata schema fields."""

import json
from pathlib import Path
from typing import Any

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge_base"

# Fields to inspect for each technology entity
INSPECT_FIELDS: dict[str, tuple[str, ...]] = {
    "quality_score": ("quality_score", "performance.quality_score", "benchmark.score"),
    "performance": ("performance", "performance_score"),
    "benchmark": ("benchmark", "benchmark_score"),
    "recommendation": ("recommendation", "recommendation.score"),
    "latency": ("latency", "latency_ms", "performance.latency_ms", "capabilities.latency_ms"),
    "pricing": ("pricing", "cost", "min_monthly_cost_usd", "pricing.monthly_cost"),
    "open_source": ("open_source", "is_open_source", "pricing.open_source"),
    "free_tier": ("free_tier", "has_free_tier", "pricing.free_tier"),
    "adoption": ("adoption", "community_score", "adoption.community_score"),
    "github_stars": ("stars", "github_stars", "adoption.github_stars"),
    "downloads": ("downloads", "monthly_downloads", "adoption.downloads"),
    "active_users": ("active_users", "adoption.active_users"),
    "organizations": ("organizations", "enterprise_users", "adoption.organizations"),
    "capabilities": ("capabilities", "features"),
    "supported_deployments": ("supported_deployments", "deployments", "supported_platforms"),
}


def get_nested_val(entry: dict[str, Any], path: str) -> Any:
    """Retrieve value from dictionary using dot-separated path."""
    if not isinstance(entry, dict):
        return None
    keys = path.split(".")
    curr: Any = entry
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return None
    return curr


def check_field_presence(entry: dict[str, Any], paths: tuple[str, ...]) -> tuple[bool, Any]:
    """Check if any path exists in entity and return presence flag + sample value."""
    for path in paths:
        val = get_nested_val(entry, path)
        if val is not None:
            return True, val
    return False, None


def parse_json_file(file_path: Path) -> list[dict[str, Any]]:
    """Safely parse a JSON file returning list of dictionary items."""
    if not file_path.exists() or not file_path.is_file():
        return []

    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]

        if isinstance(data, dict):
            entries = (
                data.get("entries")
                or data.get("items")
                or data.get("data")
                or data.get("candidates")
            )
            if isinstance(entries, list):
                return [item for item in entries if isinstance(item, dict)]
            return [data]
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return []

    return []


def infer_category(file_path: Path, kb_root: Path) -> str:
    """Infer category string from relative file path."""
    try:
        rel_parts = [p.lower() for p in file_path.relative_to(kb_root).parts]
    except ValueError:
        rel_parts = [p.lower() for p in file_path.parts]

    if len(rel_parts) > 1 and rel_parts[0] != "processed":
        return rel_parts[0]

    if len(rel_parts) > 2 and rel_parts[0] == "processed":
        return rel_parts[1]

    return file_path.stem.lower()


def main() -> None:
    """Scan knowledge_base directory and output metadata inspection report."""
    if not KNOWLEDGE_DIR.exists():
        print(f"Error: Knowledge directory '{KNOWLEDGE_DIR}' does not exist.")
        return

    json_files = sorted(KNOWLEDGE_DIR.rglob("*.json"))

    total_files = len(json_files)
    total_entities = 0

    quality_count = 0
    latency_count = 0
    pricing_count = 0
    adoption_count = 0
    capabilities_count = 0

    print(f"Scanning {total_files} JSON files in '{KNOWLEDGE_DIR}'...\n")

    for json_file in json_files:
        # Skip raw text chunk collections
        if json_file.name in ("chunks.json", "embedding_metadata.json"):
            continue

        entities = parse_json_file(json_file)
        if not entities:
            continue

        category = infer_category(json_file, KNOWLEDGE_DIR)
        first_entity = entities[0]
        total_entities += 1

        tech_name = (
            first_entity.get("technology")
            or first_entity.get("name")
            or first_entity.get("id")
            or json_file.stem
        )

        top_keys = list(first_entity.keys())[:10]

        rel_path = json_file.relative_to(KNOWLEDGE_DIR) if json_file.is_relative_to(KNOWLEDGE_DIR) else json_file

        print("-" * 60)
        print(f"File:       knowledge_base/{rel_path}")
        print(f"Category:   {category}")
        print(f"Technology: {tech_name}")
        print(f"Top Keys:   {top_keys}")
        print()

        file_has_quality = False
        file_has_latency = False
        file_has_pricing = False
        file_has_adoption = False
        file_has_capabilities = False

        for field_name, paths in INSPECT_FIELDS.items():
            present, val = check_field_presence(first_entity, paths)

            if present:
                display_val = str(val)
                if len(display_val) > 40:
                    display_val = display_val[:37] + "..."
                print(f"  {field_name:<25} YES ({display_val})")

                if field_name in ("quality_score", "performance", "benchmark", "recommendation"):
                    file_has_quality = True
                if field_name in ("latency",):
                    file_has_latency = True
                if field_name in ("pricing", "open_source", "free_tier"):
                    file_has_pricing = True
                if field_name in ("adoption", "github_stars", "downloads", "active_users", "organizations"):
                    file_has_adoption = True
                if field_name in ("capabilities", "supported_deployments"):
                    file_has_capabilities = True
            else:
                print(f"  {field_name:<25} NO")

        if file_has_quality:
            quality_count += 1
        if file_has_latency:
            latency_count += 1
        if file_has_pricing:
            pricing_count += 1
        if file_has_adoption:
            adoption_count += 1
        if file_has_capabilities:
            capabilities_count += 1

        print()

    print("=" * 60)
    print("KNOWLEDGE BASE METADATA SUMMARY REPORT")
    print("=" * 60)
    print(f"Files Scanned:              {total_files}")
    print(f"Entities Analyzed:          {total_entities}")
    print()
    print(f"Quality Metadata Found:     {quality_count} files")
    print(f"Latency Metadata Found:     {latency_count} files")
    print(f"Pricing Metadata Found:     {pricing_count} files")
    print(f"Adoption Metadata Found:    {adoption_count} files")
    print(f"Capabilities Metadata Found: {capabilities_count} files")
    print("=" * 60)


if __name__ == "__main__":
    main()
