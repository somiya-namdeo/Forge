from ai_engine.reasoning.llm_engine import LLMEngine


def main():
    llm = LLMEngine()

    response = llm.generate(
        "What is Retrieval-Augmented Generation? Explain in exactly three sentences."
    )

    print(response)


if __name__ == "__main__":
    main()