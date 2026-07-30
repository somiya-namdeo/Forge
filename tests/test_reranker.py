from ai_engine.retrieval.query_encoder import QueryEncoder
from ai_engine.retrieval.retriever import Retriever
from ai_engine.retrieval.retrieval_evaluator import RetrievalEvaluator
from ai_engine.retrieval.corrective_retrieval import CorrectiveRetrieval
from ai_engine.retrieval.reranker import Reranker

query = "Best open source vector database for RAG"

encoder = QueryEncoder()
retriever = Retriever()
evaluator = RetrievalEvaluator()
corrector = CorrectiveRetrieval(retriever)
reranker = Reranker()

try:
    embedding = encoder.encode(query)

    results = retriever.search(embedding)

    evaluation = evaluator.evaluate(results)

    results = corrector.retrieve(embedding, results, evaluation)

    results = reranker.rerank(query, results)

    print("\nRetrieval Evaluation")
    print("=" * 80)
    print(evaluation)
    print()

    print("Top Retrieved Documents")
    print("=" * 80)

    for i, result in enumerate(results, start=1):
        print(f"Rank {i}")
        print(f"Rerank Score    : {result['rerank_score']:.4f}")
        print(f"Similarity Score: {result['score']:.4f}")
        print(f"Title           : {result['payload'].get('title', 'N/A')}")
        print(f"Source          : {result['payload'].get('source', 'N/A')}")
        print("Text:")
        print(result["payload"].get("text", "")[:250] + "...")
        print("-" * 80)

finally:
    retriever.close()