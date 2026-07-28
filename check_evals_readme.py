import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://github.com/confident-ai/deepeval/blob/main/README.md',
    'https://github.com/langchain-ai/langsmith-sdk/blob/main/README.md',
    'https://github.com/openai/evals/blob/main/README.md',
    'https://github.com/truera/trulens/blob/main/README.md',
    'https://github.com/Arize-ai/phoenix/blob/main/README.md'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"OK {u} -> {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
