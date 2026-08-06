import { KnowledgeRegistryResponse, KnowledgeCategory } from '../types';

class KnowledgeService {
  async getRegistry(categoryFilter?: KnowledgeCategory | 'all', query?: string): Promise<KnowledgeRegistryResponse> {
    throw new Error('Backend Not Available');
  }
}

export const knowledgeService = new KnowledgeService();
