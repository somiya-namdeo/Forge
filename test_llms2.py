import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://platform.openai.com/docs/overview',
    'https://cdn.openai.com/papers/gpt-4-system-card.pdf',
    
    'https://docs.anthropic.com/en/home',
    'https://docs.anthropic.com/en/api/reference',
    'https://www-assets.anthropic.com/api/v1/model-card.pdf',
    
    'https://ai.google.dev/gemini-api/docs',
    'https://ai.google.dev/api/rest',
    
    'https://llama.meta.com/docs/overview',
    'https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md',
    
    'https://docs.mistral.ai/api',
    
    'https://api-docs.deepseek.com/',
    'https://deepseek.com/'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        print(f"OK {u} {res.getcode()}")
    except Exception as e:
        print(f"ERR {u} {getattr(e, 'code', str(e))}")
