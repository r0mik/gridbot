# Greed Bot Frontend

React dashboard for monitoring and controlling the Greed Bot trading system.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Features

- Real-time bot status monitoring
- Live performance metrics
- Interactive profit chart
- Grid level visualization
- Active orders table
- Trade history
- WebSocket live updates

## Tech Stack

- React 18
- Vite 5
- Recharts for charts
- WebSocket for real-time updates

## Development

The dev server runs on `http://localhost:3000` and proxies API requests to `http://localhost:8000`.

Make sure the API server is running before starting the frontend:
```bash
# In root directory
python api_server.py
```

## Components

- `Dashboard.jsx` - Main status and metrics
- `TradesTable.jsx` - Recent trades list
- `OrdersTable.jsx` - Active orders list
- `PerformanceChart.jsx` - Cumulative profit chart
- `GridVisualization.jsx` - Grid levels display

## Configuration

Edit `vite.config.js` to change:
- Development port (default: 3000)
- API proxy settings
- Build options
