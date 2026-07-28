import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://docs.cohere.com/reference/rerank',
    'https://docs.cohere.com/docs/reranking-overview',
    'https://docs.cohere.com/'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"OK {u} {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
