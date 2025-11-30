# Greed Bot - Bybit Grid Trading Bot

A Python-based automated grid trading bot for Bybit cryptocurrency exchange with **real-time web dashboard**. Supports both spot and futures trading with customizable grid parameters.

## 🌟 Features

### Trading
- **Grid Trading Strategy**: Automatically places buy and sell orders at predetermined price levels
- **Spot & Futures Support**: Trade on both spot and futures (perpetual) markets
- **Auto-Rebalancing**: Automatically rebalances grid when orders are filled
- **Risk Management**: Configurable grid levels and order sizes
- **Testnet Support**: Test your strategies safely on Bybit testnet
- **Detailed Logging**: Comprehensive logging to both console and file

### Web Dashboard (NEW!)
- **Real-Time Monitoring**: Live WebSocket updates every 2 seconds
- **Performance Charts**: Interactive charts showing cumulative profits
- **Grid Visualization**: Visual representation of all grid levels
- **Trade History**: Complete log of all executed trades
- **Order Tracking**: Real-time active order monitoring
- **Beautiful UI**: Modern dark-themed responsive interface

![Dashboard Preview](https://via.placeholder.com/800x400?text=Greed+Bot+Dashboard)

## How Grid Trading Works

Grid trading is a strategy that profits from market volatility:

1. The bot divides a price range into equal levels (grid)
2. Places buy orders below the current price
3. Places sell orders above the current price
4. When a buy order fills, it places a sell order at the next grid level above
5. When a sell order fills, it places a buy order at the next grid level below
6. Profits are made from the price spread between grid levels

## Installation

### Prerequisites

- Python 3.8 or higher
- Bybit account with API credentials
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create your configuration file**:
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` file with your settings**:
   ```bash
   # Bybit API Credentials (get from https://www.bybit.com/app/user/api-management)
   BYBIT_API_KEY=your_api_key_here
   BYBIT_API_SECRET=your_api_secret_here

   # Use testnet for testing (recommended for first time)
   BYBIT_TESTNET=true

   # Trading Configuration
   TRADING_SYMBOL=BTCUSDT
   GRID_LEVELS=10
   GRID_LOWER_PRICE=40000
   GRID_UPPER_PRICE=50000
   ORDER_AMOUNT=0.001
   MARKET_TYPE=spot  # 'spot' or 'linear' (futures)
   ```

## Configuration

### Required Settings

- **BYBIT_API_KEY**: Your Bybit API key
- **BYBIT_API_SECRET**: Your Bybit API secret
- **TRADING_SYMBOL**: Trading pair (e.g., BTCUSDT, ETHUSDT)
- **GRID_LEVELS**: Number of grid levels (min: 2, recommended: 10-20)
- **GRID_LOWER_PRICE**: Lower bound of the grid
- **GRID_UPPER_PRICE**: Upper bound of the grid
- **ORDER_AMOUNT**: Amount per order (in base currency)

### Optional Settings

- **BYBIT_TESTNET**: Use testnet (true) or mainnet (false)
- **MARKET_TYPE**: 'spot' for spot trading, 'linear' for futures
- **CHECK_INTERVAL**: How often to check for filled orders (seconds, default: 10)
- **MAX_OPEN_ORDERS**: Maximum number of open orders (default: 20)

## Getting Bybit API Credentials

1. Log in to your Bybit account
2. Go to API Management: https://www.bybit.com/app/user/api-management
3. Create a new API key
4. **Important**: Enable the following permissions:
   - For Spot trading: "Spot" read and write
   - For Futures trading: "Contract" read and write
5. **Security**: Use IP whitelist for added security
6. Save your API key and secret (you won't be able to see the secret again)

### Testnet Credentials

For testing, create testnet credentials:
1. Go to testnet: https://testnet.bybit.com/
2. Register/login to testnet account
3. Get testnet API credentials from API Management
4. Fund your testnet account with fake USDT

## Usage

### Option 1: Command Line Only

```bash
python main.py
```

The bot will run in your terminal with console logging.

### Option 2: With Web Dashboard (Recommended)

Run all three components:

**Terminal 1 - Trading Bot:**
```bash
python main.py
```

**Terminal 2 - API Server:**
```bash
python api_server.py
```

**Terminal 3 - Web Dashboard:**
```bash
cd frontend
npm install  # First time only
npm run dev
```

Then open http://localhost:3000 in your browser to see the live dashboard!

📚 **Detailed web setup guide**: See [WEB_SETUP.md](WEB_SETUP.md)

### Stopping the Bot

Press `Ctrl+C` in each terminal to stop. All open orders will be cancelled automatically.

### Monitoring

The bot will:
- Display configuration on startup
- Show current price and verify connection
- Log all order placements and fills
- Display periodic status updates
- Save detailed logs to timestamped log files

## Example Configuration

### Conservative Grid (Wide Range, More Levels)

```env
GRID_LEVELS=20
GRID_LOWER_PRICE=30000
GRID_UPPER_PRICE=70000
ORDER_AMOUNT=0.001
```

### Aggressive Grid (Narrow Range, Fewer Levels)

```env
GRID_LEVELS=5
GRID_LOWER_PRICE=45000
GRID_UPPER_PRICE=48000
ORDER_AMOUNT=0.01
```

## Risk Management

⚠️ **Important Warnings**:

1. **Start with Testnet**: Always test your configuration on testnet first
2. **Use Small Amounts**: Start with small order amounts
3. **Monitor Regularly**: Check the bot's performance regularly
4. **Price Range**: Ensure the grid range matches current market conditions
5. **Funding**: Ensure you have sufficient balance for all grid orders
6. **Market Volatility**: Grid trading works best in ranging markets
7. **API Security**: Keep your API keys secure, never share them

## Troubleshooting

### "Failed to connect to Bybit"
- Check your API credentials
- Verify API permissions (Spot/Contract read/write)
- Check if you're using the correct testnet/mainnet setting

### "Current price is outside grid range"
- Adjust GRID_LOWER_PRICE and GRID_UPPER_PRICE to include current price
- Or wait for price to return to grid range

### "Insufficient balance"
- Ensure you have enough USDT/base currency
- Calculate required balance: GRID_LEVELS × ORDER_AMOUNT × price

### Orders not filling
- Check if grid range is too wide
- Verify market has enough volatility
- Ensure order amounts meet minimum requirements

## Project Structure

```
greedbot/
├── main.py              # Main bot entry point
├── api_server.py        # FastAPI backend server
├── database.py          # SQLite database manager
├── bybit_client.py      # Bybit API wrapper
├── grid_strategy.py     # Grid trading logic
├── config.py            # Configuration management
├── logger.py            # Logging setup
├── check_balance.py     # Utility to check API connection
├── requirements.txt     # Python dependencies
├── .env                 # Your configuration (not in git)
├── .env.example         # Example configuration
├── README.md            # This file
├── WEB_SETUP.md         # Web interface setup guide
├── QUICKSTART.md        # 5-minute quick start
├── FEATURES.md          # Complete feature list
└── frontend/            # React web dashboard
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── Dashboard.jsx
    │   │   ├── TradesTable.jsx
    │   │   ├── OrdersTable.jsx
    │   │   ├── PerformanceChart.jsx
    │   │   └── GridVisualization.jsx
    │   └── App.css
    ├── package.json
    └── vite.config.js
```

## Advanced Features

### Multiple Bots

You can run multiple instances with different configurations:
```bash
# Terminal 1
python main.py

# Terminal 2 - edit .env with different symbol first
python main.py
```

### Custom Strategies

The code is modular - you can modify `grid_strategy.py` to implement:
- Different grid spacing (arithmetic vs geometric)
- Dynamic grid adjustment
- Custom rebalancing logic
- Integration with technical indicators

## Disclaimer

This bot is for educational purposes. Cryptocurrency trading carries risk of loss. Always:
- Test thoroughly on testnet
- Start with small amounts
- Never invest more than you can afford to lose
- Understand the strategy before using
- Monitor your bot regularly

The developers are not responsible for any financial losses incurred while using this software.

## License

MIT License - feel free to modify and use as you wish.

## Support

For issues or questions:
- Check the troubleshooting section above
- Review Bybit API documentation: https://bybit-exchange.github.io/docs/
- Test on testnet first

## Changelog

### Version 1.0.0
- Initial release
- Grid trading strategy for spot and futures
- Bybit API integration
- Configurable grid parameters
- Auto-rebalancing
- Testnet support
