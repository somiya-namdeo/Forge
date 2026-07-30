class CorrectiveRetrieval:
    def __init__(self, retriever):
        self.retriever = retriever

    def retrieve(self, embedding, results, evaluation):
        if not evaluation["should_correct"]:
            return results

        return self.retriever.search(embedding, limit=10)