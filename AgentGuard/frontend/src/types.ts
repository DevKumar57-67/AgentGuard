export type Decision =
  | 'ALLOW'
  | 'BLOCK'
  | 'APPROVAL_REQUIRED'
  | 'APPROVED_BY_ADMIN'
  | 'DENIED_BY_ADMIN'
  | string

export type Risk = 'GREEN' | 'AMBER' | 'RED' | string

export interface SecurityEvent {
  id: string
  timestamp: string
  agent_id: string
  tool: string
  prompt?: string
  risk: Risk
  decision: Decision
  reason: string
}

export interface EvaluationPayload {
  agent_id: string
  tool: string
  prompt: string
}

export type EvaluationResult = SecurityEvent

export interface GatewayStatus {
  name: string
  status: string
  version?: string
}

export interface AgentSummary {
  agentId: string
  total: number
  blocked: number
  pending: number
  lastSeen: string
  tools: string[]
}