export type KnowledgeCategory = 
  | 'llms' 
  | 'vectordbs' 
  | 'frameworks' 
  | 'rerankers' 
  | 'retrieval' 
  | 'embeddings' 
  | 'chunking' 
  | 'prompting' 
  | 'deployment' 
  | 'fine_tuning' 
  | 'evaluation';

export interface KnowledgeComponent {
  id: string;
  category: KnowledgeCategory;
  name: string;
  organization: string;
  officialDocumentation?: string;
  githubRepository?: string;
  license: string;
  priority: 'high' | 'medium' | 'low';
  lastVerified: string;
  description: string;
  keyFeatures: string[];
}

export interface KnowledgeRegistryResponse {
  totalComponents: number;
  lastSync: string;
  categories: { name: KnowledgeCategory; count: number; label: string }[];
  components: KnowledgeComponent[];
}
