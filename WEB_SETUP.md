# Web Interface Setup Guide

This guide will help you set up and run the Greed Bot web interface with real-time dashboard, charts, and trade monitoring.

## Architecture

The web interface consists of:
- **Backend**: FastAPI server with WebSocket support (Python)
- **Frontend**: React + Vite with real-time updates (JavaScript)
- **Database**: SQLite for storing trades, orders, and bot status

## Prerequisites

- Python 3.8+ with pip
- Node.js 18+ with npm
- All requirements from main README.md

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI - Web framework
- Uvicorn - ASGI server
- WebSockets - Real-time communication
- Pydantic - Data validation

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

This installs:
- React - UI framework
- Vite - Build tool
- Recharts - Charting library
- Axios - HTTP client

## Running the Application

You need to run **THREE** processes:

### Process 1: Trading Bot

```bash
python main.py
```

This runs the actual trading bot that:
- Connects to Bybit
- Places and manages orders
- Logs everything to the database

### Process 2: API Server

Open a new terminal:

```bash
python api_server.py
```

This runs the FastAPI backend on http://localhost:8000 that:
- Serves REST API endpoints
- Provides WebSocket for real-time updates
- Reads data from the database

### Process 3: Frontend Dev Server

Open another terminal:

```bash
cd frontend
npm run dev
```

This runs the React frontend on http://localhost:3000

## Accessing the Dashboard

Open your browser and go to:
```
http://localhost:3000
```

You should see:
- 🤖 **Bot Status** - Running/stopped, current price, grid config
- 💵 **Total Profit** - Cumulative profit from trades
- 📊 **Win Rate** - Percentage of profitable trades
- 🔄 **Total Trades** - Number of executed trades
- 📈 **Performance Chart** - Cumulative profit over time
- 🎯 **Grid Levels** - Visual representation of grid orders
- 📋 **Active Orders** - Real-time list of open orders
- 💰 **Recent Trades** - Latest executed trades

## Features

### Real-Time Updates

The dashboard updates automatically every 2 seconds via WebSocket:
- No need to refresh the page
- Live order status updates
- Instant trade notifications
- Current price updates

### Performance Chart

Interactive chart showing:
- Cumulative profit over time
- Trade-by-trade breakdown
- Hover to see details

### Grid Visualization

Shows all grid levels with:
- Current price indicator
- Active buy/sell orders at each level
- Color-coded orders (green=buy, red=sell)

### Trade History

Complete history of executed trades:
- Timestamp
- Symbol and side (buy/sell)
- Execution price
- Quantity
- Profit/loss per trade

## API Endpoints

The backend exposes these REST endpoints:

```
GET /api/status         - Get bot status
GET /api/orders         - Get orders (with optional filters)
GET /api/trades         - Get trade history
GET /api/performance    - Get performance metrics
GET /api/grid-levels    - Get grid level status
GET /api/dashboard      - Get all dashboard data
WS  /ws                 - WebSocket for real-time updates
```

### Example API Usage

```bash
# Get bot status
curl http://localhost:8000/api/status

# Get recent trades
curl http://localhost:8000/api/trades?limit=20

# Get active orders
curl http://localhost:8000/api/orders?status=active
```

## Production Deployment

### Build Frontend for Production

```bash
cd frontend
npm run build
```

This creates optimized production files in `frontend/dist/`

### Serve with Nginx (Optional)

1. Copy build files to web server:
```bash
cp -r frontend/dist/* /var/www/greedbot/
```

2. Configure Nginx to proxy API requests to FastAPI

3. Run API server with more workers:
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Process Manager (PM2)

Install PM2:
```bash
npm install -g pm2
```

Create `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'greedbot',
      script: 'main.py',
      interpreter: 'python3'
    },
    {
      name: 'greedbot-api',
      script: 'api_server.py',
      interpreter: 'python3'
    }
  ]
}
```

Start all processes:
```bash
pm2 start ecosystem.config.js
```

## Database

The SQLite database (`greedbot.db`) stores:

**Tables:**
- `bot_status` - Current bot configuration and status
- `orders` - All orders (active and filled)
- `trades` - Executed trades with profit tracking
- `grid_levels` - Grid level status
- `performance` - Performance metrics snapshots

**Location:** Root directory (`greedbot.db`)

**Backup:**
```bash
cp greedbot.db greedbot_backup_$(date +%Y%m%d).db
```

## Troubleshooting

### "Connection Failed" in UI

- Check if API server is running on port 8000
- Check if there are any CORS errors in browser console
- Verify backend is accessible: `curl http://localhost:8000/api/status`

### WebSocket Disconnecting

- Check API server logs for errors
- Ensure firewall allows WebSocket connections
- Try refreshing the browser page

### No Data Showing

- Make sure the trading bot (`main.py`) is running
- Check if database file exists (`greedbot.db`)
- Verify bot has made some trades/orders
- Check API server logs: `python api_server.py`

### Frontend Build Errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Port Already in Use

Change ports in:
- `api_server.py` - Line with `uvicorn.run(..., port=8000)`
- `frontend/vite.config.js` - `server.port: 3000`

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- Frontend: Changes auto-reload in browser
- Backend: Use `--reload` flag:
  ```bash
  uvicorn api_server:app --reload
  ```

### Debugging

Enable debug logging:
```python
# In api_server.py
logging.basicConfig(level=logging.DEBUG)
```

### Testing WebSocket

Use a WebSocket client:
```bash
npm install -g wscat
wscat -c ws://localhost:8000/ws
```

## Security Notes

For production:

1. **Enable Authentication**
   - Add API key authentication to endpoints
   - Use JWT tokens for WebSocket

2. **Use HTTPS**
   - Configure SSL/TLS certificates
   - Update CORS settings

3. **Restrict Access**
   - Firewall rules to limit API access
   - Use environment variables for secrets

4. **Database Security**
   - Set proper file permissions on `greedbot.db`
   - Regular backups
   - Consider PostgreSQL for production

## Next Steps

- Customize the UI colors/theme in `frontend/src/App.css`
- Add more charts and metrics
- Implement bot control buttons (start/stop/configure)
- Add notifications for important events
- Set up monitoring and alerts

Enjoy your new real-time trading dashboard! 🚀
