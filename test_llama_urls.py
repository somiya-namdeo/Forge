import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://developers.llamaindex.ai/python/framework-api-reference/node_parsers/hierarchical/',
    'https://developers.llamaindex.ai/python/framework-api-reference/node_parsers/sentence_splitter/'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"OK {u} {res.getcode()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
