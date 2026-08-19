import { KnowledgeRegistryResponse } from '../types';
import { request } from './apiClient';

class KnowledgeService {
  async getRegistry(
    categoryFilter?: string, 
    query?: string,
    page: number = 1,
    pageSize: number = 24
  ): Promise<KnowledgeRegistryResponse> {
    const params = new URLSearchParams();
    if (categoryFilter && categoryFilter !== 'all') {
      params.append('category', categoryFilter);
    }
    if (query) {
      params.append('search', query);
    }
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());

    return request<KnowledgeRegistryResponse>(`/knowledge?${params.toString()}`);
  }
}

export const knowledgeService = new KnowledgeService();
