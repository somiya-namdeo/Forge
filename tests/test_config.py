from app.core.config import GROQ_API_KEY, LLM_MODEL

print("API Key Loaded:", bool(GROQ_API_KEY))
print("Model:", LLM_MODEL)

if GROQ_API_KEY:
    print("Key Prefix:", GROQ_API_KEY[:10] + "...")