from ai_engine.retrieval.query_encoder import QueryEncoder
from ai_engine.retrieval.retriever import Retriever
from ai_engine.retrieval.retrieval_evaluator import RetrievalEvaluator
from ai_engine.retrieval.corrective_retrieval import CorrectiveRetrieval

encoder = QueryEncoder()
retriever = Retriever()
evaluator = RetrievalEvaluator()
corrector = CorrectiveRetrieval(retriever)

query = "Best open source vector database for RAG"

embedding = encoder.encode(query)

results = retriever.search(embedding)

evaluation = evaluator.evaluate(results)

final_results = corrector.retrieve(embedding, results, evaluation)

print(evaluation)
print()

for result in final_results:
    print(result["score"])
    print(result["payload"])
    print("-" * 50)