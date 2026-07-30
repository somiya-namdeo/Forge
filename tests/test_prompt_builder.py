from ai_engine.retrieval.query_encoder import QueryEncoder
from ai_engine.retrieval.retriever import Retriever
from ai_engine.retrieval.retrieval_evaluator import RetrievalEvaluator
from ai_engine.retrieval.corrective_retrieval import CorrectiveRetrieval
from ai_engine.retrieval.reranker import Reranker
from ai_engine.prompting.prompt_builder import PromptBuilder

query = "Best open source vector database for RAG"

encoder = QueryEncoder()
retriever = Retriever()
evaluator = RetrievalEvaluator()
corrector = CorrectiveRetrieval(retriever)
reranker = Reranker()
builder = PromptBuilder()

try:
    embedding = encoder.encode(query)

    results = retriever.search(embedding)

    evaluation = evaluator.evaluate(results)

    results = corrector.retrieve(embedding, results, evaluation)

    results = reranker.rerank(query, results)

    prompt = builder.build(query, results)

    print(prompt)

finally:
    retriever.close()