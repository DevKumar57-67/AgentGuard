import type { EvaluationPayload, EvaluationResult, GatewayStatus, SecurityEvent } from './types'

const API_URL = (import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new Error(`Cannot reach AgentGuard API at ${API_URL}. Check that the backend is running.`)
  }

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`API request failed (${response.status})${detail ? `: ${detail}` : ''}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  status: () => request<GatewayStatus>('/'),
  events: () => request<SecurityEvent[]>('/events'),
  evaluate: (payload: EvaluationPayload) =>
    request<EvaluationResult>('/evaluate', { method: 'POST', body: JSON.stringify(payload) }),
  decide: (eventId: string, action: 'APPROVE' | 'DENY') =>
    request<{ status: string; event: SecurityEvent }>('/action', {
      method: 'POST',
      body: JSON.stringify({ event_id: eventId, action }),
    }),
}