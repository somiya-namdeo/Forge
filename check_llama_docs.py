import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://developers.llamaindex.ai/python/framework-api-reference/node_parsers/semantic_splitter/',
    'https://developers.llamaindex.ai/python/framework-api-reference/node_parsers/sentence_window/',
    'https://github.com/langchain-ai/langchain/blob/master/README.md'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"OK {u} -> {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
