import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://platform.openai.com/docs/',
    'https://github.com/openai/openai-python',
    'https://platform.openai.com/docs/api-reference',
    'https://openai.com/news/',
    'https://platform.openai.com/docs/changelog',
    'https://arxiv.org/abs/2303.08774',
    
    'https://docs.anthropic.com/en/docs',
    'https://github.com/anthropics/anthropic-sdk-python',
    'https://docs.anthropic.com/en/api/getting-started',
    'https://www.anthropic.com/news',
    'https://docs.anthropic.com/en/release-notes/overview',
    
    'https://ai.google.dev/docs',
    'https://github.com/google/generative-ai-python',
    'https://ai.google.dev/api',
    'https://blog.google/technology/ai/',
    'https://ai.google.dev/gemini-api/docs/changelog',
    'https://arxiv.org/abs/2312.11805',
    
    'https://llama.meta.com/docs/getting-started/',
    'https://github.com/meta-llama/llama-models',
    'https://ai.meta.com/blog/',
    'https://arxiv.org/abs/2407.21783',
    
    'https://docs.mistral.ai/',
    'https://github.com/mistralai/mistral-src',
    'https://docs.mistral.ai/api/',
    'https://mistral.ai/news/',
    'https://arxiv.org/abs/2310.06825',
    
    'https://qwen.readthedocs.io/en/latest/',
    'https://github.com/QwenLM/Qwen2.5',
    'https://qwenlm.github.io/blog/',
    'https://github.com/QwenLM/Qwen2.5/releases',
    'https://arxiv.org/abs/2407.10671',
    
    'https://api-docs.deepseek.com/',
    'https://github.com/deepseek-ai/DeepSeek-V3',
    'https://github.com/deepseek-ai/DeepSeek-V3/releases',
    'https://arxiv.org/abs/2412.19437'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        print(f"OK {u} {res.getcode()}")
    except Exception as e:
        print(f"ERR {u} {getattr(e, 'code', str(e))}")
