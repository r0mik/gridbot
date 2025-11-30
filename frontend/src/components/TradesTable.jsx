import React from 'react'

function TradesTable({ trades }) {
  if (!trades || trades.length === 0) {
    return <div className="loading">No trades yet</div>
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Profit</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade, index) => {
            const profit = trade.profit ? parseFloat(trade.profit) : 0
            const executedTime = trade.executed_at
              ? new Date(trade.executed_at).toLocaleTimeString()
              : 'N/A'

            return (
              <tr key={index}>
                <td>{executedTime}</td>
                <td>{trade.symbol}</td>
                <td>
                  <span className={`badge ${trade.side?.toLowerCase()}`}>
                    {trade.side}
                  </span>
                </td>
                <td>${parseFloat(trade.price).toFixed(2)}</td>
                <td>{parseFloat(trade.qty).toFixed(4)}</td>
                <td className={profit >= 0 ? 'metric-value positive' : 'metric-value negative'}>
                  ${profit.toFixed(4)}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default TradesTable
