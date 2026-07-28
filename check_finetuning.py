import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://arxiv.org/abs/2106.09685',
    'https://github.com/microsoft/LoRA',
    'https://arxiv.org/abs/2305.14314',
    'https://github.com/artidoro/qlora',
    'https://github.com/huggingface/peft',
    'https://huggingface.co/docs/peft/index',
    'https://github.com/huggingface/trl',
    'https://huggingface.co/docs/trl/index',
    'https://github.com/unslothai/unsloth',
    'https://github.com/unslothai/unsloth/blob/main/README.md',
    'https://github.com/axolotl-ai-cloud/axolotl',
    'https://github.com/hiyouga/LLaMA-Factory',
    'https://github.com/Lightning-AI/litgpt'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"OK {u} -> {res.geturl()}")
    except Exception as e:
        print(f"ERR {u} {str(e)}")
