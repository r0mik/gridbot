import React from 'react'

function GridVisualization({ gridLevels, currentPrice }) {
  if (!gridLevels || gridLevels.length === 0) {
    return <div className="loading">No grid data available</div>
  }

  // Sort grid levels by price
  const sortedLevels = [...gridLevels].sort((a, b) => b.price - a.price)

  return (
    <div className="grid-visualization">
      {sortedLevels.map((level, index) => {
        const price = parseFloat(level.price)
        const hasBuy = level.has_buy_order
        const hasSell = level.has_sell_order
        const isCurrent = currentPrice && Math.abs(price - currentPrice) < 50

        let className = 'grid-level'
        if (hasBuy) className += ' has-buy'
        if (hasSell) className += ' has-sell'

        return (
          <div key={index} className={className} style={isCurrent ? { background: 'rgba(59, 130, 246, 0.2)' } : {}}>
            <div className="grid-price">
              ${price.toFixed(2)}
              {isCurrent && <span style={{ marginLeft: '0.5rem', fontSize: '0.85rem', color: '#3b82f6' }}>← Current</span>}
            </div>
            <div className="grid-orders">
              {hasBuy && <span className="badge buy">Buy</span>}
              {hasSell && <span className="badge sell">Sell</span>}
              {!hasBuy && !hasSell && <span style={{ color: '#6b7280', fontSize: '0.85rem' }}>No orders</span>}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default GridVisualization
