import type { AssistantReply, Brief, Design, Job, ProductType, RagResult, StudioMode } from './types'

const API = import.meta.env.VITE_FASHION_CAD_API ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  })
  if (!response.ok) throw new Error((await response.json().catch(() => ({ detail: response.statusText }))).detail)
  return response.status === 204 ? (undefined as T) : response.json() as Promise<T>
}

export const api = {
  listDesigns: () => request<Design[]>('/api/projects'),
  analyzeBrief: (payload: { description: string; product_type: ProductType }) =>
    request<Brief>('/api/briefs/local', { method: 'POST', body: JSON.stringify(payload) }),
  createDesign: (payload: { name: string; product_type: ProductType; mode: StudioMode; description: string; components?: string[]; materials?: string[]; measurements_mm?: Record<string, number> }) =>
    request<Design>('/api/projects', { method: 'POST', body: JSON.stringify(payload) }),
  operation: (id: string, kind: string, value: string | string[]) =>
    request<Design>(`/api/projects/${id}/operations`, { method: 'POST', body: JSON.stringify({ kind, value }) }),
  chat: (id: string, message: string) =>
    request<AssistantReply>(`/api/projects/${id}/assistant`, { method: 'POST', body: JSON.stringify({ message }) }),
  exportMockup: (id: string) => request<{ revision: number; artifacts: string[] }>(`/api/projects/${id}/exports/mockup`, { method: 'POST' }),
  exportPattern: (id: string) => request<{ revision: number; artifacts: string[] }>(`/api/projects/${id}/exports/pattern`, { method: 'POST' }),
  exportTechpack: (id: string) => request<{ revision: number; artifacts: string[] }>(`/api/projects/${id}/exports/techpack`, { method: 'POST' }),
  ragSearch: (query: string) => request<RagResult[]>(`/api/rag/search?query=${encodeURIComponent(query)}`),
  semanticSearch: (query: string) => request<RagResult[]>(`/api/rag/semantic/search?query=${encodeURIComponent(query)}`),
  startSemanticReindex: () => request<Job>('/api/rag/semantic/reindex', { method: 'POST' }),
  jobStatus: (jobId: string) => request<Job>(`/api/jobs/${jobId}`),
  cancelJob: (jobId: string) => request<Job>(`/api/jobs/${jobId}`, { method: 'DELETE' }),
  startOperator: () => request<{ session_id: string; expires_at: string }>('/api/operator/sessions', { method: 'POST', body: JSON.stringify({ requested_windows: ['Fashion CAD Studio'] }) }),
  stopOperator: (sessionId: string) => request<void>(`/api/operator/sessions/${sessionId}`, { method: 'DELETE' }),
}

export const artifactUrl = (relativePath: string) => `${API}/artifacts/${relativePath.split('/').map(encodeURIComponent).join('/')}`
