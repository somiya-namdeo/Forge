import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://github.com/explodinggradients/ragas',
    'https://docs.ragas.io/en/stable/',
    'https://arxiv.org/abs/2309.15217',
    'https://github.com/confident-ai/deepeval',
    'https://docs.confident-ai.com/',
    'https://github.com/langchain-ai/langsmith-sdk',
    'https://docs.smith.langchain.com/',
    'https://github.com/openai/evals',
    'https://github.com/truera/trulens',
    'https://www.trulens.org/',
    'https://github.com/promptfoo/promptfoo',
    'https://www.promptfoo.dev/docs/intro/',
    'https://github.com/mlflow/mlflow',
    'https://mlflow.org/docs/latest/llms/llm-evaluate/index.html',
    'https://github.com/Arize-ai/phoenix',
    'https://docs.arize.com/phoenix/'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"OK {u} -> {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
