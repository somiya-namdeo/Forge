import urllib.request
urls = [
    'https://python.langchain.com/docs/introduction/',
    'https://github.com/langchain-ai/langchain',
    'https://api.python.langchain.com/',
    'https://blog.langchain.dev/',
    'https://github.com/langchain-ai/langchain/releases',
    'https://langchain-ai.github.io/langgraph/',
    'https://github.com/langchain-ai/langgraph',
    'https://langchain-ai.github.io/langgraph/reference/',
    'https://github.com/langchain-ai/langgraph/releases',
    'https://docs.llamaindex.ai/',
    'https://github.com/run-llama/llama_index',
    'https://docs.llamaindex.ai/en/stable/api_reference/',
    'https://www.llamaindex.ai/blog',
    'https://github.com/run-llama/llama_index/releases',
    'https://haystack.deepset.ai/',
    'https://github.com/deepset-ai/haystack',
    'https://docs.haystack.deepset.ai/reference',
    'https://www.deepset.ai/blog',
    'https://github.com/deepset-ai/haystack/releases'
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        print(f"OK {u}")
    except Exception as e:
        print(f"ERR {u} {getattr(e, 'code', 'error')}")
