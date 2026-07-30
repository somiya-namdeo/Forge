from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch


class Reranker:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-reranker-base")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "BAAI/bge-reranker-base"
        )
        self.model.eval()

    def rerank(self, query, results, top_k=5):
        if not results:
            return []

        pairs = [
            [query, result["payload"].get("text", "")]
            for result in results
        ]

        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            scores = self.model(**inputs).logits.squeeze(-1)

        for result, score in zip(results, scores):
            result["rerank_score"] = float(score)

        results.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return results[:top_k]