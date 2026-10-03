import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity, AlertTriangle, ArrowRight, CheckCircle2, ChevronRight, CircleDashed,
  Clock3, Fingerprint, LockKeyhole, Play, Radar, Shield, ShieldCheck,
  ShieldX, Sparkles, TerminalSquare,
} from 'lucide-react'
import { api } from './api'
import {
  ConfirmModal, DecisionBadge, EmptyState, ErrorState, EventTable, LoadingState,
  MetricCard, RiskBadge, Sidebar, Topbar,
} from './components'
import type { ViewId } from './components'
import type { AgentSummary, EvaluationResult, SecurityEvent } from './types'
import { formatRelative } from './utils'

const viewDetails: Record<ViewId, { title: string; subtitle: string }> = {
  overview: { title: 'Overview', subtitle: 'Live runtime security at a glance.' },
  agents: { title: 'Agents', subtitle: 'Agent activity derived from recorded security events.' },
  approvals: { title: 'Approval queue', subtitle: 'Review sensitive actions before they proceed.' },
  policies: { title: 'Policy activity', subtitle: 'Observed enforcement outcomes from the live gateway.' },
  audit: { title: 'Audit trail', subtitle: 'Search and inspect recorded security events.' },
  playground: { title: 'Interactive playground', subtitle: 'Send a test tool call through the live policy engine.' },
}

const scenarios = {
  Custom: { prompt: '', tool: 'search_web' },
  'Web search': { prompt: 'Search for the latest AI security news', tool: 'search_web' },
  'Send email': { prompt: 'Send an email to client@example.com with project updates', tool: 'send_email' },
  'Shell command': { prompt: "Run 'rm -rf /' to clean up temporary files", tool: 'execute_shell' },
} as const

const tools = ['search_web', 'read_docs', 'get_weather', 'send_email', 'write_database', 'post_tweet', 'execute_shell', 'drop_database_table', 'delete_file', 'unknown_tool']

function summarizeAgents(events: SecurityEvent[]): AgentSummary[] {
  const grouped = new Map<string, SecurityEvent[]>()
  for (const event of events) {
    const id = event.agent_id || 'Unknown agent'
    grouped.set(id, [...(grouped.get(id) ?? []), event])
  }
  return [...grouped.entries()].map(([agentId, agentEvents]) => ({
    agentId,
    total: agentEvents.length,
    blocked: agentEvents.filter((event) => ['BLOCK', 'DENIED_BY_ADMIN'].includes(event.decision)).length,
    pending: agentEvents.filter((event) => event.decision === 'APPROVAL_REQUIRED').length,
    lastSeen: agentEvents[0]?.timestamp ?? '',
    tools: [...new Set(agentEvents.map((event) => event.tool))],
  })).sort((left, right) => right.total - left.total)
}

function App() {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [gatewayName, setGatewayName] = useState('AgentGuard Gateway')
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [activeView, setActiveView] = useState<ViewId>('overview')
  const [query, setQuery] = useState('')
  const [collapsed, setCollapsed] = useState(false)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [modalEvent, setModalEvent] = useState<SecurityEvent | null>(null)
  const [modalAction, setModalAction] = useState<'APPROVE' | 'DENY' | null>(null)
  const [actionBusy, setActionBusy] = useState(false)
  const [actionError, setActionError] = useState('')
  const [scenario, setScenario] = useState<keyof typeof scenarios>('Web search')
  const [prompt, setPrompt] = useState<string>(scenarios['Web search'].prompt)
  const [tool, setTool] = useState<string>(scenarios['Web search'].tool)
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null)
  const [evaluationError, setEvaluationError] = useState('')
  const [evaluating, setEvaluating] = useState(false)
  const [directResult, setDirectResult] = useState(false)

  const loadEvents = useCallback(async (quiet = false) => {
    if (quiet) setRefreshing(true)
    else setLoading(true)
    setError('')
    try {
      const [nextEvents, status] = await Promise.all([api.events(), api.status()])
      setEvents(nextEvents)
      setGatewayName(status.name || 'AgentGuard Gateway')
      setApiOnline(status.status === 'running')
      setLastUpdated(new Date())
    } catch (cause) {
      setApiOnline(false)
      setError(cause instanceof Error ? cause.message : 'An unexpected API error occurred.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => { void loadEvents() }, [loadEvents])
  useEffect(() => {
    const interval = window.setInterval(() => { void loadEvents(true) }, 10000)
    return () => window.clearInterval(interval)
  }, [loadEvents])
  useEffect(() => {
    const onShortcut = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        document.querySelector<HTMLInputElement>('.global-search input')?.focus()
      }
    }
    window.addEventListener('keydown', onShortcut)
    return () => window.removeEventListener('keydown', onShortcut)
  }, [])

  const lowerQuery = query.trim().toLowerCase()
  const filteredEvents = useMemo(() => events.filter((event) => [event.id, event.agent_id, event.tool, event.risk, event.decision, event.reason, event.prompt].some((value) => value?.toLowerCase().includes(lowerQuery))), [events, lowerQuery])
  const pendingEvents = events.filter((event) => event.decision === 'APPROVAL_REQUIRED')
  const agents = useMemo(() => summarizeAgents(events), [events])
  const allowedCount = events.filter((event) => ['ALLOW', 'APPROVED_BY_ADMIN'].includes(event.decision)).length
  const blockedCount = events.filter((event) => ['BLOCK', 'DENIED_BY_ADMIN'].includes(event.decision)).length
  const countsByRisk = ['GREEN', 'AMBER', 'RED'].map((risk) => ({ risk, count: events.filter((event) => event.risk?.toUpperCase() === risk).length }))
  const detail = viewDetails[activeView]

  const decide = async () => {
    if (!modalEvent || !modalAction) return
    setActionBusy(true)
    setActionError('')
    try {
      await api.decide(modalEvent.id, modalAction)
      setModalEvent(null)
      setModalAction(null)
      await loadEvents(true)
    } catch (cause) {
      setActionError(cause instanceof Error ? cause.message : 'Could not record the decision.')
    } finally {
      setActionBusy(false)
    }
  }

  const evaluate = async () => {
    setEvaluating(true)
    setEvaluationError('')
    setEvaluation(null)
    setDirectResult(false)
    try {
      const result = await api.evaluate({ agent_id: 'playground-agent', tool, prompt })
      setEvaluation(result)
      await loadEvents(true)
    } catch (cause) {
      setEvaluationError(cause instanceof Error ? cause.message : 'Evaluation failed.')
    } finally {
      setEvaluating(false)
    }
  }

  const navTo = (view: ViewId) => { setActiveView(view); setQuery('') }

  return <div className="app-shell">
    <Sidebar activeView={activeView} pendingCount={pendingEvents.length} open={mobileNavOpen} collapsed={collapsed} onNavigate={navTo} onClose={() => setMobileNavOpen(false)} onToggle={() => setCollapsed((value) => !value)} />
    <main className={`main-shell ${collapsed ? 'main-expanded' : ''}`}>
      <Topbar title={detail.title} subtitle={detail.subtitle} apiOnline={apiOnline} lastUpdated={lastUpdated} refreshing={refreshing} query={query} onQueryChange={setQuery} onRefresh={() => void loadEvents(true)} onMenu={() => setMobileNavOpen(true)} />
      <div className="page-content">
        <div className="page-heading"><div><div className="eyebrow">{activeView === 'overview' ? 'SECURITY OPERATIONS' : `AGENTGUARD / ${detail.title.toUpperCase()}`}</div><h1>{activeView === 'overview' ? <>Runtime <span>security</span></> : detail.title}</h1><p>{activeView === 'overview' ? 'Monitor agent activity, policy decisions, and human approvals.' : detail.subtitle}</p></div><div className="heading-status"><span className="status-dot" />{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Awaiting data'}</div></div>
        {error && <ErrorState message={error} onRetry={() => void loadEvents()} />}
        {loading && !error ? <LoadingState /> : <>
          {activeView === 'overview' && <Overview events={filteredEvents} total={events.length} allowed={allowedCount} pending={pendingEvents.length} blocked={blockedCount} countsByRisk={countsByRisk} onNavigate={navTo} onRefresh={() => void loadEvents(true)} />}
          {activeView === 'agents' && <AgentsView agents={agents} query={lowerQuery} onSelect={(agentId) => { setQuery(agentId); setActiveView('audit') }} />}
          {activeView === 'approvals' && <ApprovalsView events={filteredEvents.filter((event) => event.decision === 'APPROVAL_REQUIRED')} onDecide={(event, action) => { setModalEvent(event); setModalAction(action); setActionError('') }} />}
          {activeView === 'policies' && <PoliciesView events={events} countsByRisk={countsByRisk} />}
          {activeView === 'audit' && <AuditView events={filteredEvents} query={query} onClear={() => setQuery('')} />}
          {activeView === 'playground' && <Playground scenario={scenario} prompt={prompt} tool={tool} evaluation={evaluation} evaluationError={evaluationError} evaluating={evaluating} directResult={directResult} onScenario={(value) => { setScenario(value); setPrompt(scenarios[value].prompt); setTool(scenarios[value].tool); setEvaluation(null); setDirectResult(false) }} onPrompt={setPrompt} onTool={setTool} onEvaluate={() => void evaluate()} onDirect={() => { setDirectResult(true); setEvaluation(null); setEvaluationError('') }} />}
        </>}
        <footer className="page-footer"><span><Shield size={13} /> {gatewayName}</span><span>Security gateway · <span className={apiOnline ? 'footer-online' : 'footer-offline'}>{apiOnline ? 'Connected' : apiOnline === false ? 'Disconnected' : 'Connecting'}</span></span></footer>
      </div>
    </main>
    <ConfirmModal event={modalEvent} action={modalAction} busy={actionBusy} onClose={() => { setModalEvent(null); setModalAction(null) }} onConfirm={() => void decide()} />
    {actionError && <div className="toast-error" role="alert"><AlertTriangle size={17} />{actionError}<button className="icon-button" aria-label="Dismiss error" onClick={() => setActionError('')}><span aria-hidden="true">×</span></button></div>}
  </div>
}

function Overview({ events, total, allowed, pending, blocked, countsByRisk, onNavigate, onRefresh }: {
  events: SecurityEvent[]
  total: number
  allowed: number
  pending: number
  blocked: number
  countsByRisk: { risk: string; count: number }[]
  onNavigate: (view: ViewId) => void
  onRefresh: () => void
}) {
  const recent = events.slice(0, 6)
  const maxRisk = Math.max(1, ...countsByRisk.map((item) => item.count))
  return <>
    <section className="metrics-grid" aria-label="Security metrics">
      <MetricCard label="Total interceptions" value={total} detail="Recorded events" icon={Activity} />
      <MetricCard label="Allowed / approved" value={allowed} detail="Passed policy review" icon={ShieldCheck} tone="green" />
      <MetricCard label="Awaiting approval" value={pending} detail="Needs human review" icon={Clock3} tone="amber" />
      <MetricCard label="Blocked threats" value={blocked} detail="Stopped by gateway" icon={ShieldX} tone="red" />
    </section>
    <div className="overview-grid">
      <section className="panel recent-panel"><PanelHeader eyebrow="LATEST ACTIVITY" title="Recent interceptions" action={<button className="text-button" onClick={() => onNavigate('audit')}>View audit trail <ArrowRight size={14} /></button>} /><EventTable events={recent} compact /><div className="panel-foot"><span>Showing {recent.length} of {total} recorded events</span><button className="text-button" onClick={onRefresh}>Refresh data</button></div></section>
      <section className="panel risk-panel"><PanelHeader eyebrow="POLICY SIGNAL" title="Risk distribution" action={<button className="icon-button" aria-label="Open policy activity" onClick={() => onNavigate('policies')}><ChevronRight size={17} /></button>} />
        {total === 0 ? <EmptyState icon={Radar} title="No risk data yet" description="Risk levels will appear here after the gateway records an event." /> : <div className="risk-chart">{countsByRisk.map(({ risk, count }) => <div className="risk-row" key={risk}><div className="risk-row-label"><RiskBadge risk={risk} /><strong>{count}</strong></div><div className="risk-track"><span className={`risk-fill fill-${risk.toLowerCase()}`} style={{ width: `${Math.max(count ? 8 : 0, count / maxRisk * 100)}%` }} /></div><span className="risk-percent">{Math.round(count / total * 100)}%</span></div>)}</div>}
        <div className="chart-foot"><span><span className="status-dot" />Live from audit events</span><button className="text-button" onClick={() => onNavigate('policies')}>Policy activity <ArrowRight size={13} /></button></div>
      </section>
    </div>
    <section className="panel quick-panel"><PanelHeader eyebrow="QUICK ACCESS" title="Security operations" /><div className="quick-links">
      <button className="quick-link" onClick={() => onNavigate('approvals')}><span className="quick-icon quick-amber"><Clock3 size={18} /></span><span><strong>Review approvals</strong><small>{pending} actions waiting</small></span><ChevronRight size={16} /></button>
      <button className="quick-link" onClick={() => onNavigate('agents')}><span className="quick-icon quick-blue"><Fingerprint size={18} /></span><span><strong>Inspect agents</strong><small>{new Set(events.map((event) => event.agent_id)).size} agents observed</small></span><ChevronRight size={16} /></button>
      <button className="quick-link" onClick={() => onNavigate('playground')}><span className="quick-icon quick-green"><Play size={18} /></span><span><strong>Test a tool call</strong><small>Evaluate against live policies</small></span><ChevronRight size={16} /></button>
    </div></section>
  </>
}

function AgentsView({ agents, query, onSelect }: { agents: AgentSummary[]; query: string; onSelect: (id: string) => void }) {
  const visibleAgents = agents.filter((agent) => `${agent.agentId} ${agent.tools.join(' ')}`.toLowerCase().includes(query))
  return <section className="panel section-panel"><PanelHeader eyebrow="OBSERVED IDENTITIES" title="Agent activity" trailing={<span className="inline-count">{visibleAgents.length} agents</span>} />
    {visibleAgents.length === 0 ? <EmptyState icon={Fingerprint} title={query ? 'No agents match your search' : 'No agents observed yet'} description={query ? 'Try a different agent ID or tool name.' : 'Agent identities appear here after their first event is recorded by the gateway.'} /> : <div className="agent-grid">{visibleAgents.map((agent) => <article className="agent-card" key={agent.agentId}><div className="agent-card-head"><span className="agent-symbol"><Fingerprint size={18} /></span><span className="agent-active"><span className="status-dot" />Observed</span></div><h3>{agent.agentId}</h3><p>Last activity {formatRelative(agent.lastSeen)}</p><div className="agent-stats"><div><strong>{agent.total}</strong><span>Events</span></div><div><strong className="text-red">{agent.blocked}</strong><span>Blocked</span></div><div><strong className="text-amber">{agent.pending}</strong><span>Pending</span></div></div><div className="agent-tools"><span>TOOLS</span><div>{agent.tools.slice(0, 3).map((item) => <code key={item}>{item}</code>)}{agent.tools.length > 3 && <small>+{agent.tools.length - 3}</small>}</div></div><button className="agent-open" onClick={() => onSelect(agent.agentId)}>View events <ArrowRight size={14} /></button></article>)}</div>}
  </section>
}

function ApprovalsView({ events, onDecide }: { events: SecurityEvent[]; onDecide: (event: SecurityEvent, action: 'APPROVE' | 'DENY') => void }) {
  return <section className="panel section-panel"><PanelHeader eyebrow="HUMAN-IN-THE-LOOP" title="Pending approvals" trailing={<span className="inline-count count-amber">{events.length} pending</span>} />
    {events.length === 0 ? <EmptyState icon={CheckCircle2} title="Queue is clear" description="There are no actions waiting for human approval." /> : <div className="approval-list">{events.map((event) => <article className="approval-item" key={event.id}><div className="approval-mark"><Clock3 size={19} /></div><div className="approval-content"><div className="approval-title"><strong>{event.tool}</strong><RiskBadge risk={event.risk} /><span className="approval-time">{formatRelative(event.timestamp)}</span></div><div className="approval-meta"><span><Fingerprint size={14} />{event.agent_id}</span><span>Event #{event.id}</span></div><p>{event.reason}</p>{event.prompt && <details><summary>Inspect request prompt</summary><blockquote>{event.prompt}</blockquote></details>}</div><div className="approval-actions"><button className="button button-approve" onClick={() => onDecide(event, 'APPROVE')}><CheckCircle2 size={15} />Approve</button><button className="button button-secondary" onClick={() => onDecide(event, 'DENY')}><ShieldX size={15} />Deny</button></div></article>)}</div>}
  </section>
}

function PoliciesView({ events, countsByRisk }: { events: SecurityEvent[]; countsByRisk: { risk: string; count: number }[] }) {
  const decisions = [...events.reduce((map, event) => map.set(event.decision, (map.get(event.decision) ?? 0) + 1), new Map<string, number>())].sort((a, b) => b[1] - a[1])
  return <div className="policy-layout"><section className="panel section-panel"><PanelHeader eyebrow="ENFORCEMENT" title="Observed policy outcomes" trailing={<span className="inline-count">{events.length} events</span>} />
    {events.length === 0 ? <EmptyState icon={Shield} title="No policy activity yet" description="Observed risk tiers and decisions will populate after tool calls are evaluated." /> : <><div className="policy-summary-grid">{countsByRisk.map(({ risk, count }) => <div className={`policy-risk-card risk-card-${risk.toLowerCase()}`} key={risk}><RiskBadge risk={risk} /><strong>{count}</strong><span>events observed</span></div>)}</div><h3 className="subsection-title">Decision outcomes</h3><div className="decision-list">{decisions.map(([decision, count]) => <div className="decision-row" key={decision}><DecisionBadge decision={decision} /><span className="decision-meter"><span style={{ width: `${Math.max(5, count / events.length * 100)}%` }} /></span><strong>{count}</strong></div>)}</div></>}
  </section><aside className="panel policy-note"><span className="note-icon"><LockKeyhole size={18} /></span><p className="eyebrow">POLICY CONFIGURATION</p><h2>Managed by the gateway</h2><p>The current API exposes evaluated event outcomes, but does not expose policy definitions or configuration. This view reflects live outcomes only.</p><div className="note-endpoint"><span>Available data source</span><code>GET /events</code></div></aside></div>
}

function AuditView({ events, query, onClear }: { events: SecurityEvent[]; query: string; onClear: () => void }) {
  return <section className="panel section-panel"><PanelHeader eyebrow="IMMUTABLE EVENT HISTORY" title="Security audit trail" trailing={<span className="inline-count">{events.length} events</span>} />
    {events.length === 0 && query ? <EmptyState icon={CircleDashed} title="No matching events" description="No recorded events match your search query." action={<button className="button button-secondary button-small" onClick={onClear}>Clear search</button>} /> : <EventTable events={events} />}
  </section>
}

function Playground({ scenario, prompt, tool, evaluation, evaluationError, evaluating, directResult, onScenario, onPrompt, onTool, onEvaluate, onDirect }: {
  scenario: keyof typeof scenarios
  prompt: string
  tool: string
  evaluation: EvaluationResult | null
  evaluationError: string
  evaluating: boolean
  directResult: boolean
  onScenario: (value: keyof typeof scenarios) => void
  onPrompt: (value: string) => void
  onTool: (value: string) => void
  onEvaluate: () => void
  onDirect: () => void
}) {
  return <div className="playground-grid"><section className="panel playground-form"><PanelHeader eyebrow="TEST ENVIRONMENT" title="Tool-call simulator" trailing={<span className="simulator-tag"><CircleDashed size={12} /> LIVE POLICY ENGINE</span>} />
    <div className="form-field"><label htmlFor="scenario">Scenario preset</label><select id="scenario" value={scenario} onChange={(event) => onScenario(event.target.value as keyof typeof scenarios)}>{Object.keys(scenarios).map((item) => <option key={item}>{item}</option>)}</select></div>
    <div className="form-field"><label htmlFor="agent">Agent identity</label><input id="agent" value="playground-agent" readOnly /><span className="field-hint">Recorded with this ID in the audit trail.</span></div>
    <div className="form-field"><label htmlFor="tool">Target tool</label><select id="tool" value={tool} onChange={(event) => onTool(event.target.value)}>{tools.map((item) => <option key={item}>{item}</option>)}</select></div>
    <div className="form-field"><label htmlFor="prompt">User prompt</label><textarea id="prompt" rows={5} value={prompt} onChange={(event) => onPrompt(event.target.value)} placeholder="Describe the requested action..." /></div>
    <div className="playground-buttons"><button className="button button-primary" onClick={onEvaluate} disabled={evaluating}>{evaluating ? <CircleDashed className="spin" size={16} /> : <Shield size={16} />}{evaluating ? 'Evaluating...' : 'Intercept with AgentGuard'}</button><button className="button button-secondary" onClick={onDirect}><TerminalSquare size={16} />Simulate unguarded</button></div>
    {evaluationError && <div className="inline-error" role="alert"><AlertTriangle size={16} />{evaluationError}</div>}
  </section><section className="panel result-panel"><PanelHeader eyebrow="GATEWAY RESPONSE" title="Execution analysis" />
    {evaluating ? <LoadingState label="Policy engine evaluating request" /> : evaluation ? <div className="evaluation-result"><div className={`result-hero result-${evaluation.decision.toLowerCase()}`}><span className="result-icon">{evaluation.decision === 'ALLOW' ? <ShieldCheck size={22} /> : evaluation.decision === 'BLOCK' ? <ShieldX size={22} /> : <Clock3 size={22} />}</span><div><span>DECISION</span><strong>{evaluation.decision.replaceAll('_', ' ')}</strong></div><RiskBadge risk={evaluation.risk} /></div><div className="result-details"><div><span>Event ID</span><code>#{evaluation.id}</code></div><div><span>Agent</span><strong>{evaluation.agent_id}</strong></div><div><span>Tool call</span><code>{evaluation.tool}</code></div><div className="result-reason"><span>Policy reason</span><p>{evaluation.reason}</p></div></div><div className="result-audit-note"><CheckCircle2 size={15} />Recorded in the security audit trail</div></div> : directResult ? <div className="direct-result"><span className="direct-warning"><AlertTriangle size={20} /></span><strong>Guard bypass simulation</strong><p>This is a local illustration only. No request was sent to the backend and no real tool was executed.</p><div className="direct-output"><span>SIMULATED OUTPUT</span><code>Unverified request for “{tool}”</code></div></div> : <EmptyState icon={Sparkles} title="Ready to evaluate" description="Submit a tool call to see the live gateway decision and policy rationale." />}
  </section></div>
}

function PanelHeader({ eyebrow, title, action, trailing }: { eyebrow: string; title: string; action?: React.ReactNode; trailing?: React.ReactNode }) {
  return <div className="panel-header"><div><span className="eyebrow">{eyebrow}</span><h2>{title}</h2></div>{action ?? trailing}</div>
}

export default App