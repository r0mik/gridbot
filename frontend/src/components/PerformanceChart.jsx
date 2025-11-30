import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

function PerformanceChart({ trades }) {
  if (!trades || trades.length === 0) {
    return <div className="loading">No trade data for chart</div>
  }

  // Process trades to calculate cumulative profit
  const chartData = []
  let cumulativeProfit = 0

  trades
    .slice()
    .reverse()
    .forEach((trade, index) => {
      cumulativeProfit += parseFloat(trade.profit || 0)
      chartData.push({
        index: index + 1,
        profit: parseFloat(cumulativeProfit.toFixed(4)),
        price: parseFloat(trade.price),
        time: trade.executed_at ? new Date(trade.executed_at).toLocaleTimeString() : ''
      })
    })

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'rgba(26, 26, 46, 0.95)',
          border: '1px solid #3a3a5a',
          borderRadius: '8px',
          padding: '10px'
        }}>
          <p style={{ margin: '0 0 5px 0', color: '#9ca3af' }}>
            Trade #{payload[0].payload.index}
          </p>
          <p style={{ margin: '0', color: '#10b981' }}>
            Cumulative Profit: ${payload[0].value}
          </p>
          <p style={{ margin: '5px 0 0 0', color: '#e0e0e0', fontSize: '0.85rem' }}>
            {payload[0].payload.time}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
          <XAxis
            dataKey="index"
            stroke="#9ca3af"
            style={{ fontSize: '0.75rem' }}
          />
          <YAxis
            stroke="#9ca3af"
            style={{ fontSize: '0.75rem' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="profit"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ fill: '#10b981', r: 4 }}
            activeDot={{ r: 6 }}
            name="Cumulative Profit ($)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PerformanceChart
