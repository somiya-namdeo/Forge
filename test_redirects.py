import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://python.langchain.com/docs/how_to/character_text_splitter/',
    'https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.CharacterTextSplitter.html'
]

class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        print(f"Redirecting to {newurl} (Code: {code})")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

opener = urllib.request.build_opener(RedirectHandler, urllib.request.HTTPSHandler(context=ctx))
urllib.request.install_opener(opener)

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10)
        print(f"Final OK {u} -> {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
