export interface KnowledgeCategoryCount {
  name: string;
  count: number;
  label: string;
}

export interface KnowledgeComponent {
  id: string;
  category: string;
  name: string;
  organization?: string;
  officialDocumentation?: string;
  githubRepository?: string;
  license?: string;
  priority?: string;
  lastVerified?: string;
  description?: string;
  keyFeatures: string[];
}

export interface KnowledgeRegistryResponse {
  totalComponents: number;
  lastSync: string;
  categories: KnowledgeCategoryCount[];
  components: KnowledgeComponent[];
  page: number;
  page_size: number;
  total_pages: number;
}
