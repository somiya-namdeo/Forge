import urllib.request
urls = [
    'https://docs.langchain.com/oss/python/langgraph/overview',
    'https://reference.langchain.com/python/langgraph/overview'
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        print(f"OK {u} {res.getcode()}")
    except Exception as e:
        print(f"ERR {u} {getattr(e, 'code', 'error')}")
