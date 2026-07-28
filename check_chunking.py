import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://python.langchain.com/docs/how_to/character_text_splitter/',
    'https://python.langchain.com/docs/how_to/recursive_text_splitter/',
    'https://python.langchain.com/docs/how_to/split_by_token/',
    'https://python.langchain.com/docs/how_to/semantic_chunker/',
    'https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/',
    'https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/modules/',
    'https://docs.llamaindex.ai/en/stable/examples/node_parsers/hierarchical/',
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        print(f"OK {u} -> {res.geturl()}")
    except urllib.error.HTTPError as e:
        print(f"ERR {u} HTTPError: {e.code}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
