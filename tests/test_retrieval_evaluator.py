from ai_engine.retrieval.query_encoder import QueryEncoder
from ai_engine.retrieval.retriever import Retriever
from ai_engine.retrieval.retrieval_evaluator import RetrievalEvaluator


encoder = QueryEncoder()
retriever = Retriever()
evaluator = RetrievalEvaluator()

query = "Best open source vector database for RAG"

embedding = encoder.encode(query)
results = retriever.search(embedding)

evaluation = evaluator.evaluate(results)

print(evaluation)