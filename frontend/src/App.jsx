import { useState, useEffect } from 'react'
import './App.css'
import Dashboard from './components/Dashboard'
import TradesTable from './components/TradesTable'
import OrdersTable from './components/OrdersTable'
import PerformanceChart from './components/PerformanceChart'
import GridVisualization from './components/GridVisualization'
import BotSettings from './components/BotSettings'
import BotControls from './components/BotControls'

function App() {
  const [status, setStatus] = useState(null)
  const [performance, setPerformance] = useState(null)
  const [trades, setTrades] = useState([])
  const [orders, setOrders] = useState([])
  const [gridLevels, setGridLevels] = useState([])
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentView, setCurrentView] = useState('dashboard')
  const [botStatus, setBotStatus] = useState(null)

  useEffect(() => {
    // Initial data fetch
    fetchDashboardData()
    fetchBotStatus()

    // WebSocket connection for real-time updates
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws')

      ws.onopen = () => {
        console.log('WebSocket connected')
        setConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)

        if (message.type === 'dashboard' || message.type === 'update') {
          const data = message.data
          if (data.status) setStatus(data.status)
          if (data.performance) setPerformance(data.performance)
          if (data.recent_trades) setTrades(data.recent_trades)
          if (data.active_orders) setOrders(data.active_orders)
        } else if (message.type === 'bot_status') {
          setBotStatus(message.data)
        } else if (message.type === 'pong') {
          // Keepalive response
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnected(false)
        setError('WebSocket connection error')
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setConnected(false)
        // Attempt to reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000)
      }

      // Send keepalive ping every 25 seconds
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }))
        }
      }, 25000)

      return () => {
        clearInterval(pingInterval)
        ws.close()
      }
    }

    const cleanup = connectWebSocket()

    return () => {
      if (cleanup) cleanup()
    }
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/dashboard')
      const data = await response.json()

      setStatus(data.status)
      setPerformance(data.performance)
      setTrades(data.recent_trades || [])
      setOrders(data.active_orders || [])
      setGridLevels(data.grid_levels || [])
      setLoading(false)
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to fetch dashboard data')
      setLoading(false)
    }
  }

  const fetchBotStatus = async () => {
    try {
      const response = await fetch('/api/bot/status')
      const data = await response.json()
      setBotStatus(data)
    } catch (err) {
      console.error('Error fetching bot status:', err)
    }
  }

  if (loading && !status) {
    return (
      <div className="app">
        <div className="loading">
          <h2>Loading dashboard...</h2>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>🤖 Greed Bot</h1>
            <p className="header-subtitle">Grid Trading Bot for Bybit</p>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              onClick={() => setCurrentView('dashboard')}
              style={{
                padding: '0.75rem 1.5rem',
                background: currentView === 'dashboard' ? 'rgba(102, 126, 234, 0.3)' : 'rgba(42, 42, 74, 0.6)',
                border: currentView === 'dashboard' ? '1px solid #667eea' : '1px solid #3a3a5a',
                borderRadius: '8px',
                color: '#e0e0e0',
                cursor: 'pointer',
                fontWeight: currentView === 'dashboard' ? '600' : '400'
              }}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentView('settings')}
              style={{
                padding: '0.75rem 1.5rem',
                background: currentView === 'settings' ? 'rgba(102, 126, 234, 0.3)' : 'rgba(42, 42, 74, 0.6)',
                border: currentView === 'settings' ? '1px solid #667eea' : '1px solid #3a3a5a',
                borderRadius: '8px',
                color: '#e0e0e0',
                cursor: 'pointer',
                fontWeight: currentView === 'settings' ? '600' : '400'
              }}
            >
              Settings
            </button>
          </div>
        </div>
      </header>

      <div className="container">
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {currentView === 'dashboard' ? (
          <>
            <div className="card" style={{ marginBottom: '2rem' }}>
              <h2>🎮 Bot Controls</h2>
              <BotControls botStatus={botStatus} onStatusChange={fetchBotStatus} />
            </div>

            <Dashboard status={status} performance={performance} />

            <div className="dashboard-grid">
              <div className="card">
                <h2>📈 Performance Chart</h2>
                <PerformanceChart trades={trades} />
              </div>

              <div className="card">
                <h2>🎯 Grid Levels</h2>
                <GridVisualization
                  gridLevels={gridLevels}
                  currentPrice={status?.current_price}
                />
              </div>
            </div>

            <div className="card">
              <h2>📋 Active Orders</h2>
              <OrdersTable orders={orders} />
            </div>

            <div className="card">
              <h2>💰 Recent Trades</h2>
              <TradesTable trades={trades} />
            </div>
          </>
        ) : (
          <BotSettings onConfigSaved={fetchBotStatus} />
        )}
      </div>

      <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
        <div className={`status-dot ${connected ? 'running' : 'stopped'}`}></div>
        {connected ? 'Connected' : 'Disconnected'}
      </div>
    </div>
  )
}

export default App
