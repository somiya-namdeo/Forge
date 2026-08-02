import json
import logging
from collections import defaultdict
from pathlib import Path

from app.knowledge_builder.extractor import MetadataExtractor

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class KnowledgeBuilder:

    def __init__(self):

        self.extractor = MetadataExtractor()

        self.base_dir = Path("knowledge_base")

        self.chunks_file = self.base_dir / "chunks.json"

        self.output_dir = self.base_dir / "structured"

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_chunks(self):

        with open(self.chunks_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def group_chunks(self, chunks):

        grouped = defaultdict(list)

        for chunk in chunks:

            technology = chunk.get("technology")

            if technology:

                grouped[technology].append(chunk)

        return grouped

    def build(self):

        logger.info("Loading chunks...")

        chunks = self.load_chunks()

        logger.info(f"Loaded {len(chunks)} chunks.")

        grouped = self.group_chunks(chunks)

        logger.info(f"Found {len(grouped)} technologies.\n")

        success = 0

        for technology, tech_chunks in grouped.items():

            category = tech_chunks[0].get("category", "general")

            logger.info(f"Processing {technology}")

            metadata = self.extractor.extract(
                technology_name=technology,
                category=category,
                chunks=tech_chunks,
            )

            category_dir = self.output_dir / category

            category_dir.mkdir(parents=True, exist_ok=True)

            output_file = category_dir / f"{technology.lower().replace(' ','-')}.json"

            with open(output_file, "w", encoding="utf-8") as f:

                json.dump(
                    metadata.model_dump(mode="json"),
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            success += 1

        logger.info("")
        logger.info("=" * 50)
        logger.info("Knowledge Builder Complete")
        logger.info("=" * 50)
        logger.info(f"Technologies Processed : {success}")
        logger.info(f"Output Directory       : {self.output_dir}")


if __name__ == "__main__":

    builder = KnowledgeBuilder()

    builder.build()