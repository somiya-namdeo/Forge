import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

class Follow308(urllib.request.HTTPRedirectHandler):
    def http_error_308(self, req, fp, code, msg, headers):
        return self.http_error_302(req, fp, code, msg, headers)

opener = urllib.request.build_opener(Follow308, urllib.request.HTTPSHandler(context=ctx))
urllib.request.install_opener(opener)

urls = [
    'https://python.langchain.com/docs/how_to/character_text_splitter/',
    'https://python.langchain.com/docs/how_to/recursive_text_splitter/',
    'https://python.langchain.com/docs/how_to/split_by_token/',
    'https://python.langchain.com/docs/how_to/MultiQueryRetriever/',
    'https://python.langchain.com/docs/how_to/self_query/',
    'https://python.langchain.com/docs/how_to/contextual_compression/',
    'https://python.langchain.com/docs/how_to/ensemble_retriever/',
    'https://python.langchain.com/docs/how_to/ParentDocumentRetriever/'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10)
        print(f"OK {u} -> {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
