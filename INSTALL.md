# Complete Installation Guide

Follow these steps to get Greed Bot running with the full web dashboard.

## Prerequisites

- **Python 3.8+** - Check with: `python --version`
- **Node.js 18+** - Check with: `node --version`
- **npm** - Check with: `npm --version`
- **Git** (optional) - For cloning the repository

## Step 1: Install Python Dependencies

```bash
# Make sure you're in the greedbot directory
cd /path/to/greedbot

# Install Python packages
pip install -r requirements.txt
```

This installs:
- `pybit` - Bybit API client
- `python-dotenv` - Environment variable management
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support
- `pydantic` - Data validation
- `pandas` & `numpy` - Data processing

## Step 2: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js packages
npm install

# Go back to root
cd ..
```

This installs:
- `react` & `react-dom` - UI framework
- `vite` - Build tool
- `recharts` - Charting library
- `axios` - HTTP client

## Step 3: Configure the Bot

```bash
# Copy example configuration
cp .env.example .env

# Edit the configuration
# Use your favorite editor: nano, vim, code, etc.
nano .env
```

**Minimum required settings:**
```env
BYBIT_API_KEY=your_testnet_api_key
BYBIT_API_SECRET=your_testnet_api_secret
BYBIT_TESTNET=true
```

**Important:** Get testnet credentials from https://testnet.bybit.com/

## Step 4: Verify Installation

Test your API connection:
```bash
python check_balance.py
```

You should see:
- ✓ Current BTC price
- ✓ Your wallet balance
- ✓ Grid configuration check

If you see errors, check:
- API credentials are correct
- You're using testnet credentials with `BYBIT_TESTNET=true`
- API has "Spot" permissions enabled

## Step 5: Start the Bot

### Quick Start (Console Only)

```bash
python main.py
```

### Full Start (With Web Dashboard)

You need **3 separate terminals**:

#### Terminal 1: Trading Bot
```bash
python main.py
```
Wait for "Grid initialized successfully!" message.

#### Terminal 2: API Server
```bash
python api_server.py
```
Wait for "Application startup complete" message.
Server runs on http://localhost:8000

#### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```
Wait for "ready in XXms" message.
Frontend runs on http://localhost:3000

## Step 6: Access the Dashboard

Open your browser and go to:
```
http://localhost:3000
```

You should see:
- 🤖 Bot status banner (green = running)
- 💵 Total profit metric
- 📊 Win rate percentage
- 📈 Performance chart
- 🎯 Grid visualization
- 📋 Active orders table
- 💰 Recent trades table

## Verification Checklist

- [ ] Python dependencies installed
- [ ] Frontend dependencies installed
- [ ] `.env` file created and configured
- [ ] API connection test passed (`check_balance.py`)
- [ ] Trading bot starts without errors
- [ ] API server starts on port 8000
- [ ] Frontend starts on port 3000
- [ ] Dashboard loads in browser
- [ ] WebSocket shows "Connected" status

## Common Installation Issues

### "ModuleNotFoundError: No module named 'X'"
```bash
pip install -r requirements.txt
```

### "command not found: python"
Try `python3` instead:
```bash
python3 main.py
```

### "npm: command not found"
Install Node.js from https://nodejs.org/

### Port already in use
Change ports in:
- API server: Edit `api_server.py`, change `port=8000`
- Frontend: Edit `frontend/vite.config.js`, change `port: 3000`

### Database errors
Delete and recreate:
```bash
rm greedbot.db
python main.py
```

### Frontend won't connect to API
Check:
1. API server is running on port 8000
2. Check browser console for errors (F12)
3. Verify proxy settings in `frontend/vite.config.js`

## Directory Permissions

If you get permission errors:
```bash
chmod +x START.sh
chmod 644 *.py
chmod 644 frontend/src/**/*.jsx
```

## Next Steps

Once everything is running:

1. **Monitor the dashboard** - Watch orders being placed
2. **Check logs** - See `greedbot_*.log` files
3. **Verify trades** - Wait for price movements to see grid working
4. **Read documentation**:
   - `README.md` - Main documentation
   - `WEB_SETUP.md` - Web interface details
   - `QUICKSTART.md` - Quick start guide
   - `FEATURES.md` - Feature list

## Getting Help

If you encounter issues:

1. Check the troubleshooting section in `README.md`
2. Check the web setup guide in `WEB_SETUP.md`
3. Review API server logs
4. Check browser console (F12) for frontend errors
5. Verify your `.env` configuration

## Clean Reinstall

If nothing works, start fresh:

```bash
# Remove dependencies
rm -rf __pycache__
rm -rf frontend/node_modules
rm greedbot.db

# Reinstall
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Reconfigure
cp .env.example .env
# Edit .env with your settings

# Test
python check_balance.py
```

Good luck! 🚀
