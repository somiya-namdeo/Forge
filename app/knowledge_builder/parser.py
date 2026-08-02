from collections import Counter
import re


class MetadataParser:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks

    def all_text(self) -> str:
        return "\n".join(
            chunk.get("text", "")
            for chunk in self.chunks
        )

    def first_non_empty(self, key: str):
        for chunk in self.chunks:
            value = chunk.get(key)

            if value not in ("", None):
                return value

        return None

    def technology(self):
        return self.first_non_empty("technology")

    def category(self):
        return self.first_non_empty("category")

    def organization(self):
        return self.first_non_empty("organization")

    def license(self):
        return self.first_non_empty("license")

    def extract_tags(self):

        words = re.findall(r"[A-Za-z][A-Za-z0-9+\-]+", self.all_text())

        stopwords = {
            "the","and","for","with","from","that","this",
            "into","your","their","have","using","used",
            "about","which","when","where","there","also",
            "more","than","into","will","can","are","was",
            "been","being","its","our","you","they","them"
        }

        counter = Counter()

        for word in words:

            word = word.lower()

            if len(word) < 4:
                continue

            if word in stopwords:
                continue

            counter[word] += 1

        return [
            word
            for word, _ in counter.most_common(15)
        ]

    def extract_features(self):

        features = set()

        keywords = [
            "rag",
            "streaming",
            "agents",
            "tool calling",
            "embeddings",
            "vector search",
            "reranking",
            "multimodal",
            "function calling",
            "fine tuning",
            "quantization",
            "gpu",
            "cpu",
            "docker",
            "kubernetes",
            "rest api",
            "python",
            "javascript",
        ]

        text = self.all_text().lower()

        for keyword in keywords:

            if keyword in text:
                features.add(keyword)

        return sorted(features)