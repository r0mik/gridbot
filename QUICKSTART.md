# Quick Start Guide

Get your Greed Bot running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get Testnet API Credentials

1. Go to https://testnet.bybit.com/
2. Create an account or login
3. Navigate to API Management
4. Create a new API key with "Spot" permissions
5. Save your API Key and Secret

## Step 3: Configure the Bot

Copy the example config:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
BYBIT_API_KEY=your_testnet_api_key
BYBIT_API_SECRET=your_testnet_api_secret
BYBIT_TESTNET=true
```

## Step 4: Fund Your Testnet Account

1. Go to https://testnet.bybit.com/
2. Navigate to Assets
3. Use the testnet faucet to get free test USDT

## Step 5: Test Your Connection

```bash
python check_balance.py
```

You should see:
- Current BTC price
- Your testnet wallet balance
- Grid configuration check

## Step 6: Run the Bot

```bash
python main.py
```

The bot will:
1. Display your configuration
2. Show current price
3. Ask for confirmation if price is outside grid range
4. Initialize the grid by placing orders
5. Start monitoring and rebalancing

## Step 7: Monitor

Watch the console output for:
- Order placements
- Filled orders
- Rebalancing actions
- Periodic status updates

## Stopping the Bot

Press `Ctrl+C` to stop. The bot will:
- Cancel all open orders
- Exit gracefully

## Next Steps

Once comfortable with testnet:

1. **Switch to Mainnet**:
   - Get mainnet API credentials
   - Set `BYBIT_TESTNET=false`
   - Start with small amounts

2. **Optimize Configuration**:
   - Adjust grid range for current market
   - Tune number of grid levels
   - Set appropriate order amounts

3. **Monitor Performance**:
   - Check log files
   - Track filled orders
   - Calculate profits

## Common First-Time Issues

### "Failed to connect to Bybit"
- Double-check your API credentials
- Ensure you're using testnet credentials with BYBIT_TESTNET=true

### "Current price is outside grid range"
- Check current BTC price
- Adjust GRID_LOWER_PRICE and GRID_UPPER_PRICE in .env
- Make sure the range includes current price

### "Insufficient balance"
- Fund your testnet account using the faucet
- Reduce ORDER_AMOUNT or GRID_LEVELS

## Example Testnet Config

```env
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
BYBIT_TESTNET=true

TRADING_SYMBOL=BTCUSDT
GRID_LEVELS=5
GRID_LOWER_PRICE=40000
GRID_UPPER_PRICE=60000
ORDER_AMOUNT=0.001
MARKET_TYPE=spot
```

This creates a simple 5-level grid between $40k-$60k BTC.

## Tips for Success

1. **Always test on testnet first**
2. **Start with wide grid ranges** (less frequent rebalancing)
3. **Use small order amounts** initially
4. **Monitor for the first few hours**
5. **Keep logs** to track performance

Happy trading! 🚀
