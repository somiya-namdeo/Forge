import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.CharacterTextSplitter.html',
    'https://python.langchain.com/docs/how_to/#text-splitters',
    'https://docs.llamaindex.ai/en/stable/api_reference/node_parsers/hierarchical/',
    'https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/modules/#hierarchicalnodeparser'
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
