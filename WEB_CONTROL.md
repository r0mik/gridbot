# Web Control Integration Guide

The Greed Bot now supports full web-based configuration and control! You can configure API keys, trading parameters, and start/stop the bot directly from the web interface.

## Features

### 1. Bot Configuration (Settings Page)
- Set Bybit API credentials
- Configure trading parameters
- Choose testnet/mainnet mode
- Set grid parameters
- All configuration stored securely

### 2. Bot Control (Dashboard)
- Start/Stop bot with one click
- Real-time bot status
- Error reporting
- Safety confirmations

## How It Works

### Architecture

```
Frontend (React)
    ↓ HTTP/WebSocket
Backend API (FastAPI)
    ↓ Python
Bot Manager
    ↓ Controls
Trading Bot (Grid Strategy)
    ↓ API Calls
Bybit Exchange
```

### Components

**Backend:**
- `bot_manager.py` - Manages bot lifecycle
- `api_server.py` - REST API endpoints
- `database.py` - Configuration storage

**Frontend:**
- `BotSettings.jsx` - Configuration form
- `BotControls.jsx` - Start/Stop buttons
- `App.jsx` - Main integration

## Usage Guide

### Step 1: Access the Dashboard

Open your browser:
```
http://localhost:30002
```

### Step 2: Configure the Bot

1. Click the **"Settings"** button in the header
2. Fill in the configuration form:

**API Credentials:**
- API Key: Your Bybit API key
- API Secret: Your Bybit API secret
- Testnet: Check for testnet, uncheck for mainnet

**Trading Parameters:**
- Symbol: BTCUSDT (or other pair)
- Market Type: Spot or Futures
- Grid Levels: Number of grid levels (e.g., 10)
- Grid Lower Price: Bottom of grid range (e.g., 40000)
- Grid Upper Price: Top of grid range (e.g., 50000)
- Order Amount: Size of each order (e.g., 0.001)

3. Click **"Save Configuration"**
4. Wait for success message

### Step 3: Start the Bot

1. Go back to **"Dashboard"**
2. Find the "Bot Controls" card
3. Click **"Start Bot"**
4. The bot will:
   - Connect to Bybit
   - Verify credentials
   - Initialize grid
   - Start trading

### Step 4: Monitor

Watch the dashboard for:
- Real-time order updates
- Trade executions
- Performance metrics
- Grid visualization

### Step 5: Stop the Bot

1. Click **"Stop Bot"** in Bot Controls
2. Confirm the action
3. All orders will be cancelled
4. Bot stops gracefully

## API Endpoints

### Configuration
```http
POST /api/bot/configure
Content-Type: application/json

{
  "api_key": "string",
  "api_secret": "string",
  "symbol": "BTCUSDT",
  "market_type": "spot",
  "grid_levels": 10,
  "grid_lower": 40000,
  "grid_upper": 50000,
  "order_amount": 0.001,
  "testnet": true
}

Response:
{
  "status": "success",
  "message": "Configuration saved"
}
```

### Start Bot
```http
POST /api/bot/start

Response:
{
  "status": "success",
  "message": "Bot started successfully"
}
```

### Stop Bot
```http
POST /api/bot/stop

Response:
{
  "status": "success",
  "message": "Bot stopped successfully"
}
```

### Get Bot Status
```http
GET /api/bot/status

Response:
{
  "running": true,
  "configured": true,
  "error": null,
  "config": {
    "symbol": "BTCUSDT",
    "market_type": "spot",
    "grid_levels": 10,
    "grid_lower": 40000,
    "grid_upper": 50000,
    "order_amount": 0.001,
    "testnet": true
  }
}
```

## Security Considerations

### API Credentials
- API keys are stored in bot manager memory (not persisted to disk)
- Never logged or displayed after initial entry
- Use password-type inputs with show/hide toggle

### Best Practices
1. **Use Testnet First**: Always test on testnet before mainnet
2. **Limited Permissions**: Give API keys only necessary permissions
3. **IP Whitelist**: Configure IP whitelist on Bybit
4. **Small Amounts**: Start with minimal order amounts
5. **Monitor Logs**: Check server logs for any issues

## Configuration Validation

The backend validates all parameters:

- **API Keys**: Required, non-empty
- **Grid Levels**: Minimum 2
- **Price Range**: Lower must be < Upper
- **Order Amount**: Must be > 0
- **Market Type**: Must be 'spot' or 'linear'

Errors are displayed in the UI immediately.

## Real-Time Updates

The frontend receives real-time updates via WebSocket:
- Bot status changes
- Order fills
- Trade executions
- Performance updates

## Error Handling

### Common Errors

**"Bot not configured"**
- Go to Settings and save configuration first

**"Failed to connect to Bybit"**
- Check API credentials
- Verify API permissions
- Check testnet/mainnet setting
- Test connection with `check_balance.py`

**"Current price is outside grid range"**
- Adjust grid_lower and grid_upper
- Or wait for price to return to range

**"Insufficient balance"**
- Fund your account
- Reduce order amounts
- Reduce grid levels

**"Bot is already running"**
- Stop the bot first before reconfiguring

## Troubleshooting

### Bot won't start
1. Check configuration is saved
2. Verify API credentials
3. Check server logs: `python api_server.py`
4. Test manually: `python check_balance.py`

### Configuration not saving
1. Check browser console for errors (F12)
2. Verify API server is running
3. Check network tab for API responses
4. Restart API server

### Frontend not updating
1. Check WebSocket connection status (bottom right)
2. Refresh the page
3. Check browser console for WebSocket errors
4. Restart API server

## Development

### Run with Auto-Reload

**Backend (auto-reload):**
```bash
cd /Users/roman/projects/greedbot
source venv/bin/activate
uvicorn api_server:app --reload
```

**Frontend (hot reload):**
```bash
cd frontend
npm run dev
```

### Testing the Integration

1. Configure with testnet credentials
2. Start bot
3. Watch dashboard for orders
4. Verify orders appear in Bybit testnet
5. Stop bot
6. Verify all orders cancelled

## Migration from Manual Configuration

If you were using `.env` file:

1. Copy values from `.env`
2. Go to Settings page
3. Enter same values in the form
4. Save configuration
5. Start bot from dashboard

The bot manager replaces the need for `.env` when using web control.

## Comparison: CLI vs Web Control

| Feature | CLI (main.py) | Web Control |
|---------|--------------|-------------|
| Configuration | .env file | Web form |
| Start/Stop | Terminal | Buttons |
| Monitoring | Logs | Dashboard |
| Changes | Edit file + restart | Update form |
| Multiple configs | Multiple .env files | Save/load |
| Ease of use | Technical | User-friendly |

## Benefits of Web Control

1. **No File Editing**: Configure via intuitive form
2. **Real-Time Feedback**: Instant validation
3. **Visual Monitoring**: See everything in dashboard
4. **Easy Control**: One-click start/stop
5. **Error Visibility**: Clear error messages
6. **No Terminal Needed**: Works from browser
7. **Remote Access**: Access from anywhere (with proper security)

## Limitations

- Only one bot instance per API server
- Configuration not persisted (resets on server restart)
- No historical configuration versions
- No user authentication (single-user system)

## Future Enhancements

Planned features:
- Configuration profiles (save/load multiple configs)
- User authentication
- Multiple bot instances
- Scheduled start/stop
- Notification settings
- Advanced risk management
- Performance analytics

## Getting Started Quickly

**Fastest way to start trading:**

1. Start servers:
   ```bash
   python api_server.py  # Terminal 1
   cd frontend && npm run dev  # Terminal 2
   ```

2. Open http://localhost:30002

3. Click "Settings", enter:
   - Testnet API credentials
   - Symbol: BTCUSDT
   - Grid: 40000-50000, 10 levels
   - Amount: 0.001

4. Click "Save"

5. Click "Dashboard" → "Start Bot"

6. Done! Watch it trade.

---

**Questions?** Check the main README.md or WEB_SETUP.md for more details.
