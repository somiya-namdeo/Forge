import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://arxiv.org/abs/2109.01652',
    'https://arxiv.org/abs/2005.14165',
    'https://arxiv.org/abs/2201.11903',
    'https://arxiv.org/abs/2203.11171',
    'https://arxiv.org/abs/2210.03629',
    'https://github.com/ysymyth/ReAct',
    'https://arxiv.org/abs/2305.10601',
    'https://github.com/princeton-nlp/tree-of-thought-llm',
    'https://arxiv.org/abs/2308.09687',
    'https://github.com/spcl/graph-of-thoughts',
    'https://arxiv.org/abs/2310.06117',
    'https://github.com/stanfordnlp/dspy',
    'https://github.com/stanfordnlp/dspy/blob/main/README.md',
    'https://github.com/guidance-ai/guidance',
    'https://github.com/guidance-ai/guidance/blob/main/README.md',
    'https://github.com/eth-sri/lmql',
    'https://lmql.ai/docs/'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"OK {u} -> {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
