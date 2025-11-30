import React, { useState } from 'react'

function BotControls({ botStatus, onStatusChange }) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)

  const handleStart = async () => {
    setLoading(true)
    setMessage(null)

    try {
      const response = await fetch('/api/bot/start', {
        method: 'POST'
      })

      const data = await response.json()

      if (data.status === 'success') {
        setMessage({ type: 'success', text: data.message })
        if (onStatusChange) onStatusChange()
      } else {
        setMessage({ type: 'error', text: data.message })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    if (!confirm('Are you sure you want to stop the bot? All open orders will be cancelled.')) {
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      const response = await fetch('/api/bot/stop', {
        method: 'POST'
      })

      const data = await response.json()

      if (data.status === 'success') {
        setMessage({ type: 'success', text: data.message })
        if (onStatusChange) onStatusChange()
      } else {
        setMessage({ type: 'error', text: data.message })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  const isRunning = botStatus?.running
  const isConfigured = botStatus?.configured

  return (
    <div>
      {message && (
        <div style={{
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          background: message.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          border: `1px solid ${message.type === 'success' ? '#10b981' : '#ef4444'}`,
          color: message.type === 'success' ? '#10b981' : '#ef4444',
          fontSize: '0.9rem'
        }}>
          {message.text}
        </div>
      )}

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button
          onClick={handleStart}
          disabled={loading || isRunning || !isConfigured}
          style={{
            flex: 1,
            minWidth: '150px',
            padding: '1rem 1.5rem',
            background: (loading || isRunning || !isConfigured)
              ? '#4b5563'
              : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            border: 'none',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: (loading || isRunning || !isConfigured) ? 'not-allowed' : 'pointer',
            opacity: (loading || isRunning || !isConfigured) ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem'
          }}
        >
          <span>▶</span>
          {loading ? 'Starting...' : 'Start Bot'}
        </button>

        <button
          onClick={handleStop}
          disabled={loading || !isRunning}
          style={{
            flex: 1,
            minWidth: '150px',
            padding: '1rem 1.5rem',
            background: (loading || !isRunning)
              ? '#4b5563'
              : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
            border: 'none',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: (loading || !isRunning) ? 'not-allowed' : 'pointer',
            opacity: (loading || !isRunning) ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem'
          }}
        >
          <span>■</span>
          {loading ? 'Stopping...' : 'Stop Bot'}
        </button>
      </div>

      {!isConfigured && (
        <div style={{
          marginTop: '1rem',
          padding: '0.75rem',
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid #3b82f6',
          borderRadius: '6px',
          color: '#3b82f6',
          fontSize: '0.9rem'
        }}>
          ℹ️ Please configure the bot first before starting
        </div>
      )}

      {botStatus?.error && (
        <div style={{
          marginTop: '1rem',
          padding: '0.75rem',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid #ef4444',
          borderRadius: '6px',
          color: '#ef4444',
          fontSize: '0.9rem'
        }}>
          ⚠️ Error: {botStatus.error}
        </div>
      )}
    </div>
  )
}

export default BotControls
