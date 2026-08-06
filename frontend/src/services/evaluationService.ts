import { request } from './apiClient';

import { EvaluationResult } from '../types';

class EvaluationService {
  /**
   * Returns current evaluation status. (Backend missing)
   */
  async getCurrentEvaluation(): Promise<EvaluationResult | null> {
    throw new Error('Backend Not Available');
  }

  /**
   * Execute evaluation suite against targeted architecture pipeline via real backend.
   */
  async runEvaluation(
    question: string,
    retrievedContext: string,
    groundTruth: string,
    generatedAnswer: string
  ): Promise<any> {
    const payload = {
      question: question,
      answer: generatedAnswer,
      contexts: [retrievedContext],
      ground_truth: groundTruth,
      provider: "ragas"
    };

    return request<any>('/evaluation/run', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }
}

export const evaluationService = new EvaluationService();
