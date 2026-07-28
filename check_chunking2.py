import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://python.langchain.com/docs/',
    'https://developers.llamaindex.ai/',
    'https://github.com/langchain-ai/langchain',
    'https://github.com/run-llama/llama_index',
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        print(f"OK {u} -> {res.geturl()}")
    except urllib.error.HTTPError as e:
        print(f"ERR {u} HTTPError: {e.code}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
