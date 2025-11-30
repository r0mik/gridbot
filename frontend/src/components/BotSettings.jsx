import React, { useState, useEffect } from 'react'

function BotSettings({ onConfigSaved }) {
  const [config, setConfig] = useState({
    api_key: '',
    api_secret: '',
    symbol: 'BTCUSDT',
    market_type: 'spot',
    grid_levels: 10,
    grid_lower: 40000,
    grid_upper: 50000,
    order_amount: 0.001,
    testnet: true,
    check_interval: 10
  })

  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [showApiKey, setShowApiKey] = useState(false)
  const [showApiSecret, setShowApiSecret] = useState(false)

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    try {
      const response = await fetch('/api/bot/configure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...config,
          grid_levels: parseInt(config.grid_levels),
          grid_lower: parseFloat(config.grid_lower),
          grid_upper: parseFloat(config.grid_upper),
          order_amount: parseFloat(config.order_amount),
          check_interval: parseInt(config.check_interval)
        })
      })

      const data = await response.json()

      if (data.status === 'success') {
        setMessage({ type: 'success', text: data.message })
        if (onConfigSaved) onConfigSaved()
      } else {
        setMessage({ type: 'error', text: data.message })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h2>⚙️ Bot Configuration</h2>

      {message && (
        <div style={{
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          background: message.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          border: `1px solid ${message.type === 'success' ? '#10b981' : '#ef4444'}`,
          color: message.type === 'success' ? '#10b981' : '#ef4444'
        }}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* API Credentials */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: '#9ca3af' }}>
            API Credentials
          </h3>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#9ca3af' }}>
              API Key *
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showApiKey ? 'text' : 'password'}
                name="api_key"
                value={config.api_key}
                onChange={handleChange}
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(26, 26, 46, 0.6)',
                  border: '1px solid #3a3a5a',
                  borderRadius: '6px',
                  color: '#e0e0e0',
                  fontSize: '0.9rem'
                }}
                placeholder="Enter your Bybit API key"
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#9ca3af',
                  cursor: 'pointer',
                  fontSize: '0.85rem'
                }}
              >
                {showApiKey ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#9ca3af' }}>
              API Secret *
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showApiSecret ? 'text' : 'password'}
                name="api_secret"
                value={config.api_secret}
                onChange={handleChange}
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(26, 26, 46, 0.6)',
                  border: '1px solid #3a3a5a',
                  borderRadius: '6px',
                  color: '#e0e0e0',
                  fontSize: '0.9rem'
                }}
                placeholder="Enter your Bybit API secret"
              />
              <button
                type="button"
                onClick={() => setShowApiSecret(!showApiSecret)}
                style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#9ca3af',
                  cursor: 'pointer',
                  fontSize: '0.85rem'
                }}
              >
                {showApiSecret ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#9ca3af' }}>
              <input
                type="checkbox"
                name="testnet"
                checked={config.testnet}
                onChange={handleChange}
                style={{ width: '18px', height: '18px' }}
              />
              Use Testnet (recommended for testing)
            </label>
          </div>
        </div>

        {/* Trading Parameters */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: '#9ca3af' }}>
            Trading Parameters
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#9ca3af', fontSize: '0.9rem' }}>
                Symbol *
              </label>
              <input
                type="text"
                name="symbol"
                value={config.symbol}
                onChange={handleChange}
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(26, 26, 46, 0.6)',
                  border: '1px solid #3a3a5a',
                  borderRadius: '6px',
                  color: '#e0e0e0'
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#9ca3af', fontSize: '0.9rem' }}>
                Market Type *
              </label>
              <select
                name="market_type"
                value={config.market_type}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(26, 26, 46, 0.6)',
                  border: '1px solid #3a3a5a',
                  borderRadius: '6px',
                  color: '#e0e0e0'
                }}
              >
                <option value="spot">Spot</option>
                <option value="linear">Futures (Linear)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#9ca3af', fontSize: '0.9rem' }}>
                Grid Levels *
              </label>
              <input
                type="number"
                name="grid_levels"
                value={config.grid_levels}
                onChange={handleChange}
                min="2"
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(26, 26, 46, 0.6)',
                  border: '1px solid #3a3a5a',
                  borderRadius: '6px',
                  color: '#e0e0e0'
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#9ca3af', fontSize: '0.9rem' }}>
                Grid Lower Price *
              </label>
              <input
                type="number"
                name="grid_lower"
                value={config.grid_lower}
                onChange={handleChange}
                step="0.01"
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(26, 26, 46, 0.6)',
                  border: '1px solid #3a3a5a',
                  borderRadius: '6px',
                  color: '#e0e0e0'
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#9ca3af', fontSize: '0.9rem' }}>
                Grid Upper Price *
              </label>
              <input
                type="number"
                name="grid_upper"
                value={config.grid_upper}
                onChange={handleChange}
                step="0.01"
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(26, 26, 46, 0.6)',
                  border: '1px solid #3a3a5a',
                  borderRadius: '6px',
                  color: '#e0e0e0'
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#9ca3af', fontSize: '0.9rem' }}>
                Order Amount *
              </label>
              <input
                type="number"
                name="order_amount"
                value={config.order_amount}
                onChange={handleChange}
                step="0.0001"
                min="0.0001"
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(26, 26, 46, 0.6)',
                  border: '1px solid #3a3a5a',
                  borderRadius: '6px',
                  color: '#e0e0e0'
                }}
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '1rem',
            background: loading ? '#4b5563' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? 'Saving Configuration...' : 'Save Configuration'}
        </button>
      </form>
    </div>
  )
}

export default BotSettings
