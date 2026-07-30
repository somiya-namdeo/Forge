from ai_engine.retrieval.query_encoder import QueryEncoder
from ai_engine.retrieval.retriever import Retriever


encoder = QueryEncoder()
retriever = Retriever()

query = "Best open source vector database for RAG"

embedding = encoder.encode(query)

results = retriever.search(embedding)

for result in results:
    print(result["score"])
    print(result["payload"])
    print("-" * 50)