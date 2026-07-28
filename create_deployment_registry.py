import json
import os

directory = r"c:\Users\namde\OneDrive\Desktop\forge\sources\deployment"
os.makedirs(directory, exist_ok=True)

entries = [
    {"id": "source-ollama", "name": "Ollama", "organization": "Ollama", "docs": "https://github.com/ollama/ollama/blob/main/README.md", "github": "https://github.com/ollama/ollama", "license": "MIT"},
    {"id": "source-lm-studio", "name": "LM Studio", "organization": "LM Studio", "docs": "https://lmstudio.ai/docs", "github": "", "license": ""},
    {"id": "source-docker", "name": "Docker", "organization": "Docker", "docs": "https://docs.docker.com/", "github": "https://github.com/docker/cli", "license": "Apache-2.0"},
    {"id": "source-docker-compose", "name": "Docker Compose", "organization": "Docker", "docs": "https://docs.docker.com/compose/", "github": "https://github.com/docker/compose", "license": "Apache-2.0"},
    
    {"id": "source-kubernetes", "name": "Kubernetes", "organization": "CNCF", "docs": "https://kubernetes.io/docs/home/", "github": "https://github.com/kubernetes/kubernetes", "license": "Apache-2.0"},
    {"id": "source-helm", "name": "Helm", "organization": "CNCF", "docs": "https://helm.sh/docs/", "github": "https://github.com/helm/helm", "license": "Apache-2.0"},
    {"id": "source-k3s", "name": "K3s", "organization": "Rancher", "docs": "https://docs.k3s.io/", "github": "https://github.com/k3s-io/k3s", "license": "Apache-2.0"},
    
    {"id": "source-vllm", "name": "vLLM", "organization": "vLLM", "docs": "https://docs.vllm.ai/en/latest/", "github": "https://github.com/vllm-project/vllm", "license": "Apache-2.0"},
    {"id": "source-nvidia-triton", "name": "NVIDIA Triton Inference Server", "organization": "NVIDIA", "docs": "https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html", "github": "https://github.com/triton-inference-server/server", "license": "BSD-3-Clause"},
    {"id": "source-hf-tgi", "name": "Hugging Face Text Generation Inference (TGI)", "organization": "Hugging Face", "docs": "https://huggingface.co/docs/text-generation-inference/index", "github": "https://github.com/huggingface/text-generation-inference", "license": ""},
    {"id": "source-sglang", "name": "SGLang", "organization": "LMSYS", "docs": "https://github.com/sgl-project/sglang/blob/main/README.md", "github": "https://github.com/sgl-project/sglang", "license": "Apache-2.0"},
    {"id": "source-llama-cpp", "name": "llama.cpp", "organization": "Georgi Gerganov", "docs": "https://github.com/ggerganov/llama.cpp/blob/master/README.md", "github": "https://github.com/ggerganov/llama.cpp", "license": "MIT"},
    
    {"id": "source-bentoml", "name": "BentoML", "organization": "BentoML", "docs": "https://docs.bentoml.org/en/latest/", "github": "https://github.com/bentoml/BentoML", "license": "Apache-2.0"},
    {"id": "source-ray-serve", "name": "Ray Serve", "organization": "Anyscale", "docs": "https://docs.ray.io/en/latest/serve/index.html", "github": "https://github.com/ray-project/ray", "license": "Apache-2.0"},
    {"id": "source-kserve", "name": "KServe", "organization": "Kubeflow", "docs": "https://kserve.github.io/website/latest/", "github": "https://github.com/kserve/kserve", "license": "Apache-2.0"},
    {"id": "source-mlserver", "name": "MLServer", "organization": "Seldon", "docs": "https://mlserver.readthedocs.io/en/latest/", "github": "https://github.com/SeldonIO/MLServer", "license": "Apache-2.0"},
    
    {"id": "source-render", "name": "Render", "organization": "Render", "docs": "https://render.com/docs", "github": "", "license": ""},
    {"id": "source-vercel", "name": "Vercel", "organization": "Vercel", "docs": "https://vercel.com/docs", "github": "", "license": ""},
    {"id": "source-railway", "name": "Railway", "organization": "Railway", "docs": "https://docs.railway.app/", "github": "", "license": ""},
    {"id": "source-fly-io", "name": "Fly.io", "organization": "Fly.io", "docs": "https://fly.io/docs/", "github": "", "license": ""},
    {"id": "source-hf-spaces", "name": "Hugging Face Spaces", "organization": "Hugging Face", "docs": "https://huggingface.co/docs/hub/spaces", "github": "", "license": ""},
    {"id": "source-hf-inference-endpoints", "name": "Hugging Face Inference Endpoints", "organization": "Hugging Face", "docs": "https://huggingface.co/docs/inference-endpoints/index", "github": "", "license": ""},
    {"id": "source-google-cloud-run", "name": "Google Cloud Run", "organization": "Google", "docs": "https://cloud.google.com/run/docs", "github": "", "license": ""},
    {"id": "source-aws-sagemaker", "name": "AWS SageMaker", "organization": "Amazon Web Services", "docs": "https://docs.aws.amazon.com/sagemaker/", "github": "", "license": ""},
    {"id": "source-azure-ai-foundry", "name": "Azure AI Foundry", "organization": "Microsoft", "docs": "https://learn.microsoft.com/en-us/azure/ai-studio/", "github": "", "license": ""},
    {"id": "source-vertex-ai", "name": "Vertex AI", "organization": "Google", "docs": "https://cloud.google.com/vertex-ai/docs", "github": "", "license": ""},
    
    {"id": "source-modal", "name": "Modal", "organization": "Modal Labs", "docs": "https://modal.com/docs", "github": "", "license": ""},
    {"id": "source-replicate", "name": "Replicate", "organization": "Replicate", "docs": "https://replicate.com/docs", "github": "", "license": ""},
    
    {"id": "source-cloudflare-workers-ai", "name": "Cloudflare Workers AI", "organization": "Cloudflare", "docs": "https://developers.cloudflare.com/workers-ai/", "github": "", "license": ""},
    {"id": "source-vercel-edge-functions", "name": "Vercel Edge Functions", "organization": "Vercel", "docs": "https://vercel.com/docs/functions", "github": "", "license": ""},
    
    {"id": "source-langfuse", "name": "Langfuse", "organization": "Langfuse", "docs": "https://langfuse.com/docs", "github": "https://github.com/langfuse/langfuse", "license": "MIT"},
    {"id": "source-weights-biases", "name": "Weights & Biases", "organization": "Weights & Biases", "docs": "https://docs.wandb.ai/", "github": "https://github.com/wandb/wandb", "license": "MIT"},
    {"id": "source-arize-ai", "name": "Arize AI", "organization": "Arize AI", "docs": "https://docs.arize.com/arize", "github": "", "license": ""},
    {"id": "source-prometheus", "name": "Prometheus", "organization": "CNCF", "docs": "https://prometheus.io/docs/introduction/overview/", "github": "https://github.com/prometheus/prometheus", "license": "Apache-2.0"},
    {"id": "source-grafana", "name": "Grafana", "organization": "Grafana Labs", "docs": "https://grafana.com/docs/grafana/latest/", "github": "https://github.com/grafana/grafana", "license": "AGPL-3.0"}
]

for entry in entries:
    file_name = entry["id"].replace("source-", "") + ".json"
    file_path = os.path.join(directory, file_name)
    
    data = {
        "id": entry["id"],
        "category": "deployment",
        "name": entry["name"],
        "organization": entry["organization"],
        "official_documentation": [entry["docs"]] if entry["docs"] else [],
        "github_repository": [entry["github"]] if entry["github"] else [],
        "api_reference": [],
        "technical_blog": [],
        "release_notes": [],
        "research_papers": [],
        "benchmark_pages": [],
        "license": entry["license"],
        "community_resources": [],
        "priority": "high",
        "ingestion": True,
        "update_frequency": "weekly",
        "last_verified": "2026-07-28T14:42:36Z"
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

print(f"Successfully created {len(entries)} registry entries in {directory}.")
