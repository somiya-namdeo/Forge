class PromptBuilder:
    def build(self, query, results):
        context = ""

        for i, result in enumerate(results, start=1):
            text = result["payload"].get("text", "")

            context += f"Document {i}:\n"
            context += text
            context += "\n\n"

        prompt = f"""You are an AI system design assistant.

Answer the user's question using only the provided context.

User Question:
{query}

Context:

{context}

Answer:
"""

        return prompt