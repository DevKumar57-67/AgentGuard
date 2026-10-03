import { useEffect, useRef } from 'react'
import {
  Activity, AlertCircle, AlertTriangle, ArrowUpRight, Check,
  CheckCircle2, ChevronDown, CircleHelp, Command, FileClock, Fingerprint,
  LayoutDashboard, LoaderCircle, Menu, PanelLeftClose, PanelLeftOpen,
  RefreshCw, Search, Shield, ShieldAlert, ShieldCheck, ShieldX, X,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { SecurityEvent } from './types'
import { formatRelative } from './utils'

export type ViewId = 'overview' | 'agents' | 'approvals' | 'policies' | 'audit' | 'playground'

const navigation: { id: ViewId; label: string; icon: LucideIcon; group: 'Monitor' | 'Operate' }[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard, group: 'Monitor' },
  { id: 'agents', label: 'Agents', icon: Fingerprint, group: 'Monitor' },
  { id: 'audit', label: 'Audit trail', icon: FileClock, group: 'Monitor' },
  { id: 'approvals', label: 'Approvals', icon: CheckCircle2, group: 'Operate' },
  { id: 'policies', label: 'Policy activity', icon: Shield, group: 'Operate' },
  { id: 'playground', label: 'Playground', icon: Command, group: 'Operate' },
]

export function Sidebar({
  activeView, pendingCount, open, collapsed, onNavigate, onClose, onToggle,
}: {
  activeView: ViewId
  pendingCount: number
  open: boolean
  collapsed: boolean
  onNavigate: (view: ViewId) => void
  onClose: () => void
  onToggle: () => void
}) {
  const groups = ['Monitor', 'Operate'] as const
  return (
    <>
      {open && <button className="drawer-scrim" aria-label="Close navigation" onClick={onClose} />}
      <aside className={`sidebar ${open ? 'sidebar-open' : ''} ${collapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="brand-row">
          <div className="brand-mark"><Shield size={20} strokeWidth={2.4} /></div>
          {!collapsed && <div className="brand-copy"><strong>agent<span>guard</span></strong><small>SECURITY GATEWAY</small></div>}
          <button className="icon-button sidebar-collapse" onClick={onToggle} aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'} title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
            {collapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
          </button>
          <button className="icon-button drawer-close" onClick={onClose} aria-label="Close navigation"><X size={18} /></button>
        </div>
        <div className="workspace-switcher">
          <div className="workspace-avatar">AG</div>
          {!collapsed && <><div className="workspace-text"><strong>Security team</strong><span>Production workspace</span></div><ChevronDown size={15} /></>}
        </div>
        <nav aria-label="Primary navigation">
          {groups.map((group) => (
            <div className="nav-group" key={group}>
              {!collapsed && <span className="nav-label">{group}</span>}
              {navigation.filter((item) => item.group === group).map(({ id, label, icon: Icon }) => (
                <button key={id} className={`nav-item ${activeView === id ? 'nav-active' : ''}`} onClick={() => { onNavigate(id); onClose() }} aria-current={activeView === id ? 'page' : undefined} title={collapsed ? label : undefined}>
                  <Icon size={18} strokeWidth={1.8} /><span>{label}</span>
                  {id === 'approvals' && pendingCount > 0 && <b className="nav-count">{pendingCount}</b>}
                </button>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-status"><span className="status-dot" />{!collapsed && <><span>Gateway monitoring</span><span className="status-live">LIVE</span></>}</div>
          {!collapsed && <div className="user-profile"><div className="user-avatar">SA</div><div className="user-copy"><strong>Security admin</strong><span>Administrator</span></div><button className="icon-button" aria-label="Account menu"><ChevronDown size={15} /></button></div>}
        </div>
      </aside>
    </>
  )
}

export function Topbar({
  title, subtitle, apiOnline, lastUpdated, refreshing, query, onQueryChange, onRefresh, onMenu,
}: {
  title: string
  subtitle: string
  apiOnline: boolean | null
  lastUpdated: Date | null
  refreshing: boolean
  query: string
  onQueryChange: (value: string) => void
  onRefresh: () => void
  onMenu: () => void
}) {
  return (
    <header className="topbar">
      <div className="topbar-title">
        <button className="icon-button mobile-menu" onClick={onMenu} aria-label="Open navigation"><Menu size={20} /></button>
        <div><div className="breadcrumbs"><span>Workspace</span><span className="crumb-separator">/</span><strong>{title}</strong></div><p>{subtitle}</p></div>
      </div>
      <div className="topbar-actions">
        <label className="global-search"><Search size={16} /><span className="sr-only">Search events and agents</span><input value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Search events, agents..." /><kbd>⌘ K</kbd></label>
        <div className={`api-indicator ${apiOnline === false ? 'api-offline' : ''}`}><span className="status-dot" />{apiOnline === null ? 'Connecting' : apiOnline ? 'Gateway online' : 'Gateway offline'}</div>
        <button className="icon-button refresh-button" onClick={onRefresh} disabled={refreshing} aria-label="Refresh dashboard" title={lastUpdated ? `Last updated ${lastUpdated.toLocaleTimeString()}` : 'Refresh dashboard'}><RefreshCw size={17} className={refreshing ? 'spin' : ''} /></button>
      </div>
    </header>
  )
}

export function MetricCard({ label, value, detail, icon: Icon, tone = 'blue' }: {
  label: string
  value: number
  detail: string
  icon: LucideIcon
  tone?: 'blue' | 'green' | 'amber' | 'red'
}) {
  return (
    <article className={`metric-card metric-${tone}`}>
      <div className="metric-head"><span>{label}</span><span className="metric-icon"><Icon size={17} /></span></div>
      <strong className="metric-value">{value.toLocaleString()}</strong>
      <div className="metric-foot"><span>{detail}</span><span className="metric-trend"><Activity size={13} /> live</span></div>
      <span className="metric-accent" />
    </article>
  )
}

export function RiskBadge({ risk, decision }: { risk: string; decision?: string }) {
  const value = risk?.toUpperCase() ?? 'UNKNOWN'
  const tone = value === 'GREEN' ? 'green' : value === 'AMBER' ? 'amber' : value === 'RED' ? 'red' : 'neutral'
  const Icon = tone === 'green' ? ShieldCheck : tone === 'amber' ? AlertTriangle : tone === 'red' ? ShieldX : CircleHelp
  return <span className={`risk-badge risk-${tone}`}><Icon size={13} />{value}{decision?.includes('ADMIN') && <span className="risk-admin">· reviewed</span>}</span>
}

export function DecisionBadge({ decision }: { decision: string }) {
  const value = decision?.toUpperCase() ?? 'UNKNOWN'
  const tone = value === 'ALLOW' || value === 'APPROVED_BY_ADMIN' ? 'green' : value === 'APPROVAL_REQUIRED' ? 'amber' : value === 'BLOCK' || value === 'DENIED_BY_ADMIN' ? 'red' : 'neutral'
  return <span className={`decision-badge decision-${tone}`}><span className="decision-dot" />{value.replaceAll('_', ' ')}</span>
}

export function EventTable({ events, compact = false, onOpen }: { events: SecurityEvent[]; compact?: boolean; onOpen?: (event: SecurityEvent) => void }) {
  if (events.length === 0) return <EmptyState icon={FileClock} title="No events match" description="Try changing your search or wait for new security events." />
  return (
    <div className="table-scroll"><table className="event-table"><thead><tr><th>Event / agent</th><th>Tool</th><th>Risk</th><th>Decision</th><th>Time</th>{!compact && <th aria-label="Details" />}</tr></thead><tbody>
      {events.map((event) => <tr key={event.id} onClick={() => onOpen?.(event)} className={onOpen ? 'clickable-row' : undefined}>
        <td><div className="event-cell"><span className="event-id">#{event.id}</span><span className="event-agent">{event.agent_id || 'Unknown agent'}</span></div></td>
        <td><code className="tool-code">{event.tool || 'unknown'}</code></td>
        <td><RiskBadge risk={event.risk} decision={event.decision} /></td>
        <td><DecisionBadge decision={event.decision} /></td>
        <td><time className="event-time" dateTime={event.timestamp}>{formatRelative(event.timestamp)}</time></td>
        {!compact && <td className="row-arrow"><ArrowUpRight size={15} /></td>}
      </tr>)}
    </tbody></table></div>
  )
}

export function EmptyState({ icon: Icon, title, description, action }: { icon: LucideIcon; title: string; description: string; action?: React.ReactNode }) {
  return <div className="empty-state"><span className="empty-icon"><Icon size={20} /></span><strong>{title}</strong><p>{description}</p>{action}</div>
}

export function LoadingState({ label = 'Loading live security data' }: { label?: string }) {
  return <div className="loading-state" role="status"><LoaderCircle className="spin" size={20} /><span>{label}</span></div>
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <div className="error-state" role="alert"><AlertCircle size={19} /><div><strong>Could not load dashboard data</strong><p>{message}</p></div><button className="button button-secondary button-small" onClick={onRetry}><RefreshCw size={14} /> Retry</button></div>
}

export function ConfirmModal({
  event, action, busy, onClose, onConfirm,
}: {
  event: SecurityEvent | null
  action: 'APPROVE' | 'DENY' | null
  busy: boolean
  onClose: () => void
  onConfirm: () => void
}) {
  const cancelRef = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    if (!event || !action) return
    cancelRef.current?.focus()
    const onKeyDown = (keyboardEvent: KeyboardEvent) => { if (keyboardEvent.key === 'Escape' && !busy) onClose() }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [event, action, busy, onClose])
  if (!event || !action) return null
  const approving = action === 'APPROVE'
  return <div className="modal-backdrop" onMouseDown={(mouseEvent) => { if (mouseEvent.target === mouseEvent.currentTarget && !busy) onClose() }}>
    <section className="confirm-modal" role="dialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-description">
      <button className="icon-button modal-close" onClick={onClose} disabled={busy} aria-label="Close dialog"><X size={18} /></button>
      <span className={`modal-icon ${approving ? 'modal-approve' : 'modal-deny'}`}>{approving ? <Check size={21} /> : <ShieldAlert size={21} />}</span>
      <p className="eyebrow">HUMAN-IN-THE-LOOP REVIEW</p>
      <h2 id="confirm-title">{approving ? 'Approve this action?' : 'Deny this action?'}</h2>
      <p id="confirm-description">{approving ? 'This records your approval in the audit trail.' : 'This blocks the request and records your decision in the audit trail.'}</p>
      <div className="modal-event"><span>{event.agent_id}</span><code>{event.tool}</code><RiskBadge risk={event.risk} /></div>
      <div className="modal-actions"><button ref={cancelRef} className="button button-secondary" onClick={onClose} disabled={busy}>Cancel</button><button className={`button ${approving ? 'button-primary' : 'button-danger'}`} onClick={onConfirm} disabled={busy}>{busy ? <LoaderCircle className="spin" size={15} /> : approving ? <Check size={15} /> : <X size={15} />}{busy ? 'Saving...' : approving ? 'Confirm approval' : 'Confirm denial'}</button></div>
    </section>
  </div>
}

