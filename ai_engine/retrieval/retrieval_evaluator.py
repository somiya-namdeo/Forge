class RetrievalEvaluator:
    def __init__(self,high_threshold: float = 0.8, medium_threshold: float = 0.6):
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def evaluate(self, results):
        if not results:
            return {"confidence": "low","best_score": 0.0,"average_score": 0.0,"should_correct": True}

        scores = [result["score"] for result in results]

        best_score = max(scores)
        average_score = sum(scores) / len(scores)

        if average_score >= self.high_threshold:
            confidence = "high"
        elif average_score >= self.medium_threshold:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "confidence": confidence,
            "best_score": round(best_score, 3),
            "average_score": round(average_score, 3),
            "should_correct": confidence != "high"
        }