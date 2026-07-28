import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        return res.getcode()
    except Exception as e:
        return getattr(e, 'code', str(e))

def check_license(repo_slug):
    url = f"https://api.github.com/repos/{repo_slug}/license"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        data = json.loads(res.read())
        return data.get("license", {}).get("spdx_id", "Unknown")
    except Exception as e:
        return str(e)

print("GraphRAG docs:", check_url("https://microsoft.github.io/graphrag/"))

repos = [
    "facebookresearch/DPR",
    "texttron/hyde",
    "AkariAsai/self-rag",
    "HuskyInSalt/CRAG",
    "microsoft/graphrag"
]

for r in repos:
    print(f"License {r}:", check_license(r))

