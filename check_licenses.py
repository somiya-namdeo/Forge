import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

repos = [
    'vibrantlabsai/ragas',
    'confident-ai/deepeval',
    'langchain-ai/langsmith-sdk',
    'openai/evals',
    'truera/trulens',
    'promptfoo/promptfoo',
    'mlflow/mlflow',
    'Arize-ai/phoenix'
]

for repo in repos:
    try:
        req = urllib.request.Request(f'https://api.github.com/repos/{repo}/license', headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        data = json.loads(res.read())
        print(f"{repo} -> {data['license']['spdx_id']}")
    except Exception as e:
        print(f"ERR {repo} {str(e)}")
