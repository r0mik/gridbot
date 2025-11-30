import React from 'react'

function Dashboard({ status, performance }) {
  if (!status) {
    return (
      <div className="status-banner">
        <div className="loading">No bot status available</div>
      </div>
    )
  }

  const isRunning = status.is_running
  const currentPrice = status.current_price ? parseFloat(status.current_price).toFixed(2) : 'N/A'
  const totalProfit = performance?.total_profit ? parseFloat(performance.total_profit).toFixed(4) : '0.00'
  const winRate = performance?.win_rate ? parseFloat(performance.win_rate).toFixed(2) : '0.00'
  const totalTrades = performance?.total_trades || 0

  return (
    <>
      <div className={`status-banner ${isRunning ? 'running' : 'stopped'}`}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Bot Status</h2>
            <span className={`status-indicator ${isRunning ? 'running' : 'stopped'}`}>
              <div className={`status-dot ${isRunning ? 'running' : 'stopped'}`}></div>
              {isRunning ? 'Running' : 'Stopped'}
            </span>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="status-label">Current Price</div>
            <div className="status-value" style={{ fontSize: '2rem' }}>${currentPrice}</div>
          </div>
        </div>

        <div className="status-grid">
          <div className="status-item">
            <div className="status-label">Symbol</div>
            <div className="status-value">{status.symbol || 'N/A'}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Market Type</div>
            <div className="status-value">{status.market_type || 'N/A'}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Grid Levels</div>
            <div className="status-value">{status.grid_levels || 'N/A'}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Grid Range</div>
            <div className="status-value">
              {status.grid_lower && status.grid_upper
                ? `$${parseFloat(status.grid_lower).toFixed(0)} - $${parseFloat(status.grid_upper).toFixed(0)}`
                : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <h2>💵 Total Profit</h2>
          <div className="metric">
            <span className="metric-label">Profit</span>
            <span className={`metric-value ${totalProfit >= 0 ? 'positive' : 'negative'}`}>
              ${totalProfit}
            </span>
          </div>
        </div>

        <div className="card">
          <h2>📊 Win Rate</h2>
          <div className="metric">
            <span className="metric-label">Success Rate</span>
            <span className={`metric-value ${winRate >= 50 ? 'positive' : 'negative'}`}>
              {winRate}%
            </span>
          </div>
        </div>

        <div className="card">
          <h2>🔄 Total Trades</h2>
          <div className="metric">
            <span className="metric-label">Executed</span>
            <span className="metric-value">{totalTrades}</span>
          </div>
        </div>
      </div>
    </>
  )
}

export default Dashboard
