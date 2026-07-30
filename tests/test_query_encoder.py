from ai_engine.retrieval.query_encoder import QueryEncoder
import numpy as np


def main():
    print("=" * 60)
    print("Testing Query Encoder")
    print("=" * 60)

    encoder = QueryEncoder()

    query = "Best open source vector database for RAG"

    print(f"\nQuery: {query}")

    embedding = encoder.encode(query)

    print("\nResults")
    print("-" * 60)
    print(f"Type           : {type(embedding)}")
    print(f"Shape          : {embedding.shape}")
    print(f"Dimensions     : {len(embedding)}")
    print(f"Data Type      : {embedding.dtype}")

    norm = np.linalg.norm(embedding)
    print(f"L2 Norm        : {norm:.6f}")

    print("\nFirst 10 Values")
    print("-" * 60)
    print(embedding[:10])

    # ---------------- Assertions ----------------

    assert embedding is not None
    assert isinstance(embedding, np.ndarray)
    assert embedding.ndim == 1
    assert embedding.shape[0] > 0

    # Since normalize_embeddings=True
    assert np.isclose(norm, 1.0, atol=1e-5)

    print("\n✓ Query encoding successful.")
    print("✓ Embedding generated correctly.")
    print("✓ Embedding normalization verified.")

    # ---------------- Empty Query Test ----------------

    print("\nTesting empty query...")

    try:
        encoder.encode("   ")
        raise AssertionError("Empty query should have raised ValueError.")
    except ValueError:
        print("✓ Empty query validation passed.")

    print("\nAll Query Encoder tests passed successfully!")


if __name__ == "__main__":
    main()