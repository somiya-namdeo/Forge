import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://arxiv.org/abs/2004.04906',
    'https://github.com/facebookresearch/DPR',
    
    'https://python.langchain.com/docs/how_to/MultiQueryRetriever/',
    'https://python.langchain.com/docs/how_to/ParentDocumentRetriever/',
    'https://python.langchain.com/docs/how_to/self_query/',
    'https://python.langchain.com/docs/how_to/contextual_compression/',
    'https://python.langchain.com/docs/how_to/ensemble_retriever/',
    
    'https://arxiv.org/abs/2212.10496',
    'https://github.com/texttron/hyde',
    
    'https://arxiv.org/abs/2310.11511',
    'https://github.com/AkariAsai/self-rag',
    
    'https://arxiv.org/abs/2401.15884',
    'https://github.com/HuskyInSalt/CRAG',
    
    'https://arxiv.org/abs/2404.16130',
    'https://microsoft.github.io/graphrag/',
    'https://github.com/microsoft/graphrag'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        res = urllib.request.urlopen(req, timeout=8, context=ctx)
        print(f"OK {u} {res.getcode()}")
    except Exception as e:
        print(f"ERR {u} {getattr(e, 'code', str(e))}")
