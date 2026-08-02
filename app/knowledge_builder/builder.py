from pathlib import Path
import json

from app.knowledge_builder.extractor import MetadataExtractor


class KnowledgeBuilder:
    def __init__(self) -> None:
        self.extractor = MetadataExtractor()

        self.knowledge_dir = Path("knowledge_base")
        self.processed_dir = self.knowledge_dir / "processed"
        self.output_dir = self.knowledge_dir / "structured"

        self.output_dir.mkdir(parents=True, exist_ok=True)


    def _iter_technologies(self) -> list[Path]:
        if not self.processed_dir.exists():
            return []

        return sorted(
            folder
            for folder in self.processed_dir.iterdir()
            if folder.is_dir()
        )

    def _iter_technologies(self, category_dir: Path) -> list[Path]:
        return sorted(
            folder
            for folder in category_dir.iterdir()
            if folder.is_dir()
        )

    def _save_metadata(self, category: str, technology: str, metadata) -> None:
        category_dir = self.output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        output_file = category_dir / f"{technology}.json"

        with output_file.open("w", encoding="utf-8") as file:
            json.dump(
                metadata.model_dump(mode="json"),
                file,
                indent=2,
                ensure_ascii=False,
            )

    def build(self) -> None:
        for technology_dir in self._iter_technologies():
            metadata = self.extractor.extract(
                technology_dir=technology_dir,
                category="general",
            )

            if metadata is None:
                continue

            self._save_metadata(
                category="general",
                technology=technology_dir.name,
                metadata=metadata,
            )
if __name__ == "__main__":
    builder = KnowledgeBuilder()
    builder.build()