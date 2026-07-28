import urllib.request
urls = [
    'https://docs.trychroma.com/api',
    'https://docs.trychroma.com/cloud/sync/overview#reference',
    'https://faiss.ai/cpp_api/',
    'https://faiss.ai/api/',
    'https://milvus.io/api-reference/pymilvus/v2.4.x/About.md',
    'https://milvus.io/docs/api_reference.md',
    'https://milvus.io/api-reference/pymilvus/v2.4.x/'
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        print(u, res.getcode())
    except Exception as e:
        print(u, getattr(e, 'code', 'error'))
