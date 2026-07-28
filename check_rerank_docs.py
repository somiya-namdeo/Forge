import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://huggingface.co/BAAI/bge-reranker-v2-m3',
    'https://github.com/stanford-futuredata/ColBERT/blob/main/README.md',
    'https://github.com/castorini/pygaggle/blob/master/README.md',
    'https://github.com/PrithivirajDamodaran/FlashRank/blob/main/README.md',
    'https://developers.llamaindex.ai/python/framework-api-reference/postprocessors/llm_rerank/'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"OK {u} -> {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
