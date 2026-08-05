/// <reference types="vite/client" />
/**
 * API Client Abstraction Layer
 * Handles network calls to backend REST API endpoints.
 * Currently configured to support realistic frontend execution via simulation mode
 * when live FastAPI servers are disconnected, without hardcoded initial production pollution.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.warn(`[API Client] Network call failed for ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Utility to simulate latency when testing UI loading skeletons and animations
 * prior to backend integration.
 */
export async function simulateLatency(ms: number = 800): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
