import { simulateLatency } from './apiClient';
import { KnowledgeComponent, KnowledgeRegistryResponse, KnowledgeCategory } from '../types';

/**
 * Service simulating retrieval of dynamic verified component registries from backend JSON files.
 * Derived dynamically without hardcoding static marketing totals like "240+".
 */

const RAW_COMPONENTS: KnowledgeComponent[] = [
  // LLMs
  {
    id: 'src-llama-33-70b',
    category: 'llms',
    name: 'Meta Llama 3.3 70B Instruct',
    organization: 'Meta',
    officialDocumentation: 'https://llama.meta.com/docs',
    githubRepository: 'https://github.com/meta-llama/llama-models',
    license: 'Llama 3 Community License',
    priority: 'high',
    lastVerified: '2026-07-28',
    description: '70B parameter instruction-tuned open weights model with state-of-the-art multi-hop reasoning capabilities.',
    keyFeatures: ['128k Context Window', 'RoPE Scaling', 'Tool Calling Support', 'Multi-lingual']
  },
  {
    id: 'src-claude-35-sonnet',
    category: 'llms',
    name: 'Anthropic Claude 3.5 Sonnet',
    organization: 'Anthropic',
    officialDocumentation: 'https://docs.anthropic.com',
    license: 'Proprietary Commercial API',
    priority: 'high',
    lastVerified: '2026-07-29',
    description: 'Frontier AI system excels in coding, advanced reasoning, and structured data generation.',
    keyFeatures: ['200k Context', 'Vision Recognition', 'Computer Use capability', 'Low hallucination rates']
  },
  {
    id: 'src-openai-gpt4o',
    category: 'llms',
    name: 'OpenAI GPT-4o Omni',
    organization: 'OpenAI',
    officialDocumentation: 'https://platform.openai.com/docs',
    license: 'Proprietary Commercial API',
    priority: 'high',
    lastVerified: '2026-07-25',
    description: 'Multimodal flagship engine optimized for conversational latency and functional tool orchestration.',
    keyFeatures: ['128k Context', 'Native Audio & Vision', 'Structured Outputs', 'Function Calling']
  },
  {
    id: 'src-mistral-large-2',
    category: 'llms',
    name: 'Mistral Large 2 (123B)',
    organization: 'Mistral AI',
    officialDocumentation: 'https://docs.mistral.ai',
    githubRepository: 'https://github.com/mistralai/mistral-common',
    license: 'Mistral Research / Commercial License',
    priority: 'medium',
    lastVerified: '2026-07-22',
    description: 'High-density European foundation model designed for rigorous programming and logical deductive reasoning.',
    keyFeatures: ['128k Context', 'Multilingual proficiency', 'JSON mode enforcement']
  },
  
  // Vector DBs
  {
    id: 'src-qdrant',
    category: 'vectordbs',
    name: 'Qdrant Vector Database',
    organization: 'Qdrant',
    officialDocumentation: 'https://qdrant.tech/documentation',
    githubRepository: 'https://github.com/qdrant/qdrant',
    license: 'Apache-2.0',
    priority: 'high',
    lastVerified: '2026-07-30',
    description: 'High-performance vector search engine written in Rust featuring memory-mapped storage and exact payload filtering.',
    keyFeatures: ['Rust Engine', 'HNSW Indexing', 'Scalar & Product Quantization', 'Distributed RAFT Core']
  },
  {
    id: 'src-pinecone',
    category: 'vectordbs',
    name: 'Pinecone Serverless Index',
    organization: 'Pinecone',
    officialDocumentation: 'https://docs.pinecone.io',
    license: 'Cloud Managed Service',
    priority: 'high',
    lastVerified: '2026-07-26',
    description: 'Fully decoupled cloud vector storage infrastructure scaling dynamically without persistent cluster cost.',
    keyFeatures: ['Zero Server Maintenance', 'Namespace Isolation', 'Metadata Filtered Queries', 'AWS / GCP availability']
  },
  {
    id: 'src-milvus',
    category: 'vectordbs',
    name: 'Milvus Distributed Vector Store',
    organization: 'LF AI & Data Foundation (Zilliz)',
    officialDocumentation: 'https://milvus.io/docs',
    githubRepository: 'https://github.com/milvus-io/milvus',
    license: 'Apache-2.0',
    priority: 'medium',
    lastVerified: '2026-07-20',
    description: 'Cloud-native vector storage designed for massive enterprise scales exceeding 10 billion vector vectors.',
    keyFeatures: ['Decoupled Storage & Compute', 'Multiple Index Algorithms (IVF, HNSW, DiskANN)', 'GPU Acceleration']
  },

  // Frameworks
  {
    id: 'src-llamaindex',
    category: 'frameworks',
    name: 'LlamaIndex Enterprise Core',
    organization: 'LlamaIndex',
    officialDocumentation: 'https://docs.llamaindex.ai',
    githubRepository: 'https://github.com/run-llama/llama_index',
    license: 'MIT',
    priority: 'high',
    lastVerified: '2026-07-28',
    description: 'The premier data framework for connecting custom enterprise knowledge sources to LLMs and agentic pipelines.',
    keyFeatures: ['Advanced Data Connectors (800+)', 'Sub-question Query Engines', 'Agentic Workflows', 'Modular Retrievers']
  },
  {
    id: 'src-langchain',
    category: 'frameworks',
    name: 'LangChain & LangGraph Core',
    organization: 'LangChain',
    officialDocumentation: 'https://python.langchain.com',
    githubRepository: 'https://github.com/langchain-ai/langchain',
    license: 'MIT',
    priority: 'high',
    lastVerified: '2026-07-29',
    description: 'Orchestration framework specializing in cyclic multi-agent graph workflows and resilient prompt chains.',
    keyFeatures: ['LangGraph Stateful Agents', 'LangSmith Telemetry Integration', 'Unified Tool abstraction']
  },

  // Rerankers
  {
    id: 'src-bge-reranker-v2',
    category: 'rerankers',
    name: 'BGE-Reranker-v2-M3',
    organization: 'Beijing Academy of Artificial Intelligence (BAAI)',
    officialDocumentation: 'https://huggingface.co/BAAI/bge-reranker-v2-m3',
    githubRepository: 'https://github.com/FlagOpen/FlagEmbedding',
    license: 'MIT',
    priority: 'high',
    lastVerified: '2026-07-27',
    description: 'State-of-the-art cross-encoder reranker leveraging self-attention across prompt and document text pairs.',
    keyFeatures: ['Cross-Encoder attention', 'Multilingual support', 'High retrieval gain (+18% precision@5)']
  },

  // Embeddings
  {
    id: 'src-openai-embed-3-large',
    category: 'embeddings',
    name: 'text-embedding-3-large',
    organization: 'OpenAI',
    officialDocumentation: 'https://platform.openai.com/docs/guides/embeddings',
    license: 'Proprietary Commercial API',
    priority: 'high',
    lastVerified: '2026-07-29',
    description: 'High-capacity embedding model with up to 3,072 dimensions and flexible truncation capabilities.',
    keyFeatures: ['3072 Dimensions', 'Truncation without retraining', 'Ultra-high MTEB Benchmark scores']
  },
  {
    id: 'src-jina-embed-v3',
    category: 'embeddings',
    name: 'Jina Embeddings v3',
    organization: 'Jina AI',
    officialDocumentation: 'https://jina.ai/embeddings',
    githubRepository: 'https://github.com/jina-ai/jina',
    license: 'CC-BY-NC-4.0 / Commercial',
    priority: 'medium',
    lastVerified: '2026-07-25',
    description: 'Task-specific LoRA adapter embeddings supporting 8192 token lengths and multi-lingual representation.',
    keyFeatures: ['8192 Token Window', 'LoRA Task Modes (Query vs Document)', 'Open Weights']
  }
];

class KnowledgeService {
  async getRegistry(categoryFilter?: KnowledgeCategory | 'all', query?: string): Promise<KnowledgeRegistryResponse> {
    await simulateLatency(350);

    let items = [...RAW_COMPONENTS];
    
    if (categoryFilter && categoryFilter !== 'all') {
      items = items.filter(c => c.category === categoryFilter);
    }
    
    if (query) {
      const q = query.toLowerCase();
      items = items.filter(c => c.name.toLowerCase().includes(q) || c.description.toLowerCase().includes(q) || c.organization.toLowerCase().includes(q));
    }

    // Automatically derive statistics dynamically from the current dataset
    const categories: { name: KnowledgeCategory; count: number; label: string }[] = [
      { name: 'llms', count: RAW_COMPONENTS.filter(c => c.category === 'llms').length, label: 'LLMs & Reasoning' },
      { name: 'vectordbs', count: RAW_COMPONENTS.filter(c => c.category === 'vectordbs').length, label: 'Vector Databases' },
      { name: 'frameworks', count: RAW_COMPONENTS.filter(c => c.category === 'frameworks').length, label: 'Orchestration' },
      { name: 'rerankers', count: RAW_COMPONENTS.filter(c => c.category === 'rerankers').length, label: 'Cross-Rerankers' },
      { name: 'embeddings', count: RAW_COMPONENTS.filter(c => c.category === 'embeddings').length, label: 'Dense Embeddings' }
    ];

    return {
      totalComponents: RAW_COMPONENTS.length,
      lastSync: new Date().toISOString().split('T')[0],
      categories,
      components: items
    };
  }
}

export const knowledgeService = new KnowledgeService();
