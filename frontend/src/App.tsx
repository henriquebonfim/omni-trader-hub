import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchStatus } from './lib/api'

import LiveStatus from './components/LiveStatus'
import TradeHistory from './components/TradeHistory'
import EquityCurve from './components/EquityCurve'
import StrategySelector from './components/StrategySelector'
import ConfigEditor from './components/ConfigEditor'
import BotControl from './components/BotControl'
import DiscordConfig from './components/DiscordConfig'

type Page = 'dashboard' | 'trades' | 'config' | 'notifications'

const NAV: { id: Page; label: string }[] = [
  { id: 'dashboard',     label: '📊 Dashboard' },
  { id: 'trades',        label: '📋 Trades' },
  { id: 'config',        label: '⚙️ Config' },
  { id: 'notifications', label: '🔔 Notifications' },
]

export default function App() {
  const [page, setPage] = useState<Page>('dashboard')
  const { data: status } = useQuery({ queryKey: ['status'], queryFn: fetchStatus })
  const running = status?.running ?? false

  return (
    <div className="layout">
      {/* Top bar */}
      <header className="topbar">
        <div className={`dot ${running ? 'running' : 'stopped'}`} />
        <h1>OmniTrader</h1>
        {status && (
          <span style={{ marginLeft: 8, fontSize: 12, color: 'var(--text-muted)' }}>
            {status.symbol} · {status.paper_mode ? 'Paper' : 'Live'} · {status.strategy}
          </span>
        )}
      </header>

      {/* Sidebar */}
      <nav className="sidebar">
        {NAV.map(n => (
          <button
            key={n.id}
            className={page === n.id ? 'active' : ''}
            onClick={() => setPage(n.id)}
          >
            {n.label}
          </button>
        ))}
      </nav>

      {/* Main content */}
      <main className="main">
        {page === 'dashboard' && (
          <>
            <LiveStatus />
            <div className="grid-2">
              <BotControl />
              <StrategySelector />
            </div>
            <EquityCurve />
          </>
        )}

        {page === 'trades' && (
          <>
            <EquityCurve />
            <TradeHistory />
          </>
        )}

        {page === 'config' && (
          <ConfigEditor />
        )}

        {page === 'notifications' && (
          <DiscordConfig />
        )}
      </main>
    </div>
  )
}
