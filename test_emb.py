import urllib.request
urls = [
    'https://huggingface.co/BAAI',
    'https://github.com/FlagOpen/FlagEmbedding',
    'https://github.com/FlagOpen/FlagEmbedding/releases',
    'https://arxiv.org/abs/2309.07597',
    'https://huggingface.co/spaces/mteb/leaderboard',
    'https://huggingface.co/intfloat',
    'https://github.com/microsoft/unilm/tree/master/e5',
    'https://arxiv.org/abs/2212.03533',
    'https://arxiv.org/abs/2402.05672',
    'https://jina.ai/embeddings/',
    'https://github.com/jina-ai/jina',
    'https://jina.ai/news/',
    'https://github.com/jina-ai/jina/releases',
    'https://arxiv.org/abs/2310.19923',
    'https://docs.nomic.ai/',
    'https://github.com/nomic-ai/contrastors',
    'https://blog.nomic.ai/',
    'https://github.com/nomic-ai/contrastors/releases',
    'https://arxiv.org/abs/2402.01613',
    'https://sbert.net/',
    'https://github.com/UKPLab/sentence-transformers',
    'https://sbert.net/docs/package_reference/SentenceTransformer.html',
    'https://github.com/UKPLab/sentence-transformers/releases',
    'https://arxiv.org/abs/1908.10084'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=8)
        print(f"OK {u} {res.getcode()}")
    except Exception as e:
        print(f"ERR {u} {getattr(e, 'code', str(e))}")
