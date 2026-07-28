import urllib.request
import ssl
import json
import glob
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

files = glob.glob(r"c:\Users\namde\OneDrive\Desktop\forge\sources\deployment\*.json")

urls_to_check = []
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
        urls_to_check.extend(data.get("official_documentation", []))
        urls_to_check.extend(data.get("github_repository", []))

failed = 0
for u in urls_to_check:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req, timeout=5, context=ctx)
    except Exception as e:
        print(f"ERR {u} {str(e)}")
        failed += 1

if failed == 0:
    print("All URLs verified OK.")
else:
    print(f"Failed {failed} URLs.")
