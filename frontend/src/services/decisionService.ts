import { request } from './apiClient';
import { DecisionRequest, DecisionResponse } from '../types';

/**
 * Service handling architecture recommendation and decision engine execution.
 */
class DecisionService {
  /**
   * Fetch session generated architectures. (Backend missing)
   */
  async getSessionArchitectures(): Promise<any[]> {
    throw new Error('Backend Not Available');
  }

  /**
   * Execute comprehensive Decision Engine reasoning matrix via FastAPI.
   */
  async runDecisionEngine(req: DecisionRequest): Promise<DecisionResponse> {
    return request<DecisionResponse>('/decision/recommend', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }
}

export const decisionService = new DecisionService();
