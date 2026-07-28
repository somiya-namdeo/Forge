import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://sbert.net/examples/applications/cross-encoder/README.html',
    'https://github.com/UKPLab/sentence-transformers',
    'https://github.com/FlagOpen/FlagEmbedding',
    'https://arxiv.org/abs/2309.07597',
    'https://docs.cohere.com/docs/reranking',
    'https://docs.cohere.com/reference/rerank-1',
    'https://jina.ai/reranker/',
    'https://github.com/stanford-futuredata/ColBERT',
    'https://arxiv.org/abs/2004.12832',
    'https://github.com/castorini/pygaggle',
    'https://arxiv.org/abs/2003.06713',
    'https://arxiv.org/abs/2210.10634',
    'https://github.com/PrithivirajDamodaran/FlashRank',
    'https://arxiv.org/abs/2304.09542'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        print(f"OK {u} {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
