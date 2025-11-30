import React from 'react'

function OrdersTable({ orders }) {
  if (!orders || orders.length === 0) {
    return <div className="loading">No active orders</div>
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Type</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order, index) => {
            const createdTime = order.created_at
              ? new Date(order.created_at).toLocaleTimeString()
              : 'N/A'

            return (
              <tr key={index}>
                <td>{createdTime}</td>
                <td>{order.symbol}</td>
                <td>
                  <span className={`badge ${order.side?.toLowerCase()}`}>
                    {order.side}
                  </span>
                </td>
                <td>{order.order_type}</td>
                <td>${parseFloat(order.price).toFixed(2)}</td>
                <td>{parseFloat(order.qty).toFixed(4)}</td>
                <td>
                  <span className={`badge ${order.status?.toLowerCase()}`}>
                    {order.status}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default OrdersTable
