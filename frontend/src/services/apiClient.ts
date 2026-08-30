/// <reference types="vite/client" />
/**
 * API Client Abstraction Layer
 * Handles network calls to backend REST API endpoints with robust
 * error handling, timeouts, auto-retries for GETs, and auth injection.
 */

const rawApiUrl = import.meta.env.VITE_API_URL || '';
export const API_BASE_URL = rawApiUrl
  ? (rawApiUrl.endsWith('/api/v1') ? rawApiUrl : `${rawApiUrl.replace(/\/$/, '')}/api/v1`)
  : '/api/v1';
const DEFAULT_TIMEOUT_MS = 30000;

export interface RequestOptions extends RequestInit {
  timeoutMs?: number;
  retries?: number;
}

export class ApiError extends Error {
  public status: number;
  public code: string;
  public details: any;
  public timestamp: string;

  constructor(status: number, message: string, code: string = 'HTTP_ERROR', details: any = null, timestamp: string = '') {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
    this.timestamp = timestamp;
  }
}

async function fetchWithRetry(url: string, options: RequestInit, retries: number): Promise<Response> {
  try {
    const res = await fetch(url, options);
    if (!res.ok && retries > 0 && options.method === 'GET') {
      // Only retry GETs for certain transient errors (500, 502, 503, 504)
      if ([500, 502, 503, 504].includes(res.status)) {
        await new Promise(r => setTimeout(r, 1000));
        return fetchWithRetry(url, options, retries - 1);
      }
    }
    return res;
  } catch (error: any) {
    if (error.name === 'AbortError') throw error;
    if (retries > 0 && options.method === 'GET') {
      await new Promise(r => setTimeout(r, 1000));
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
}

export async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, retries = 2, ...fetchOptions } = options;

  const controller = new AbortController();
  let externalSignal = fetchOptions.signal;
  
  if (externalSignal) {
    externalSignal.addEventListener('abort', () => controller.abort());
  }

  const timeoutId = setTimeout(() => {
    controller.abort(new Error('Request Timeout'));
  }, timeoutMs);

  const token = localStorage.getItem('forge_auth_token');
  const headers = new Headers(fetchOptions.headers || {});
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      ...fetchOptions,
      headers,
      signal: controller.signal,
    }, retries);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = {};
      }
      
      const payload = errorData.error || {};
      throw new ApiError(
        response.status,
        payload.message || `HTTP ${response.status}: ${response.statusText}`,
        payload.code || 'HTTP_ERROR',
        payload.details || null,
        payload.timestamp || new Date().toISOString()
      );
    }

    // Handle empty responses gracefully (e.g. 204 No Content)
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error: any) {
    if (error.name === 'AbortError' || error.message === 'Request Timeout') {
      console.warn(`[API Client] Request aborted or timed out for ${endpoint}`);
      throw new ApiError(408, 'Request timed out or was aborted', 'TIMEOUT');
    }
    if (!(error instanceof ApiError)) {
      console.warn(`[API Client] Network failure for ${endpoint}:`, error);
      throw new ApiError(0, 'Network connection failed', 'NETWORK_ERROR', error.message);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * @deprecated No-op stub kept for backward compatibility during service migration.
 */
export async function simulateLatency(_ms?: number): Promise<void> {
  // No-op — real network calls replace simulated delays.
}
