import json
import urllib.request
import os

files = [
    "qdrant.json",
    "chroma.json",
    "milvus.json",
    "weaviate.json",
    "pinecone.json",
    "faiss.json"
]

def check_url(url):
    if "dl.acm.org" in url or "arxiv.org" in url: return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        return res.getcode() < 400
    except Exception as e:
        # print("Error checking", url, e)
        return False

for f in files:
    path = os.path.join(r"c:\Users\namde\OneDrive\Desktop\forge\sources\vectordbs", f)
    with open(path, "r", encoding="utf-8") as f_in:
        data = json.load(f_in)
    
    url_fields = [
        "official_documentation", "github_repository", "api_reference",
        "technical_blog", "release_notes", "research_papers", 
        "benchmark_pages", "community_resources"
    ]
    
    for field in url_fields:
        valid_urls = []
        for url in data.get(field, []):
            if check_url(url):
                valid_urls.append(url)
            else:
                print(f"Removed invalid URL: {url} from {f}")
        data[field] = valid_urls
    
    ordered = {}
    keys = ["id", "category", "name", "organization", "official_documentation", "github_repository", "api_reference", "technical_blog", "release_notes", "research_papers", "benchmark_pages", "license", "community_resources", "priority", "ingestion", "update_frequency", "last_verified"]
    
    for k in keys:
        if k == "last_verified":
            ordered[k] = "2026-07-28T12:30:00Z"
        else:
            ordered[k] = data.get(k)
            
    with open(path, "w", encoding="utf-8") as f_out:
        json.dump(ordered, f_out, indent=2)
print("Done checking and ordering.")
