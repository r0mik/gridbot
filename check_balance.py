"""
Utility script to check API connection and wallet balance
Run this before starting the bot to verify everything is working
"""

from config import Config
from bybit_client import BybitClient
from logger import setup_logger


def main():
    """Check API connection and display wallet balance"""
    print("=" * 60)
    print("     Bybit API Connection & Balance Checker")
    print("=" * 60)

    # Setup logger
    logger = setup_logger("balance_checker", log_file=False)

    # Validate configuration
    if not Config.validate():
        logger.error("Invalid configuration. Please check your .env file")
        return

    # Display mode
    mode = "TESTNET" if Config.BYBIT_TESTNET else "MAINNET"
    print(f"\nMode: {mode}")
    print(f"Symbol: {Config.TRADING_SYMBOL}")
    print(f"Market: {Config.MARKET_TYPE}")

    # Initialize client
    print("\nConnecting to Bybit...")
    client = BybitClient(
        api_key=Config.BYBIT_API_KEY,
        api_secret=Config.BYBIT_API_SECRET,
        testnet=Config.BYBIT_TESTNET
    )

    # Test connection by getting ticker
    print(f"\nFetching {Config.TRADING_SYMBOL} price...")
    price = client.get_ticker_price(Config.TRADING_SYMBOL, Config.MARKET_TYPE)

    if price is None:
        print("❌ Failed to connect. Please check:")
        print("   - API credentials are correct")
        print("   - API has required permissions (Spot/Contract read)")
        print("   - You're using correct testnet/mainnet setting")
        return

    print(f"✓ Current price: {price}")

    # Get wallet balance
    print("\nFetching wallet balance...")
    balance = client.get_wallet_balance()

    if balance is None:
        print("❌ Failed to get wallet balance")
        return

    print("\n" + "=" * 60)
    print("Wallet Balance:")
    print("=" * 60)

    # Parse and display balance
    if 'list' in balance and len(balance['list']) > 0:
        for account in balance['list']:
            account_type = account.get('accountType', 'Unknown')
            print(f"\n{account_type} Account:")

            if 'coin' in account:
                for coin_balance in account['coin']:
                    coin = coin_balance.get('coin', 'Unknown')
                    wallet_balance = float(coin_balance.get('walletBalance', 0))
                    available = float(coin_balance.get('availableToWithdraw', 0))

                    if wallet_balance > 0:
                        print(f"  {coin}:")
                        print(f"    Total: {wallet_balance}")
                        print(f"    Available: {available}")
    else:
        print("No balance information available")

    # Calculate required balance for grid
    print("\n" + "=" * 60)
    print("Grid Configuration Check:")
    print("=" * 60)

    required_orders = Config.GRID_LEVELS
    order_amount = Config.ORDER_AMOUNT
    estimated_required = required_orders * order_amount * price / 2  # Rough estimate

    print(f"Grid Levels: {Config.GRID_LEVELS}")
    print(f"Price Range: {Config.GRID_LOWER_PRICE} - {Config.GRID_UPPER_PRICE}")
    print(f"Order Amount: {Config.ORDER_AMOUNT}")
    print(f"Estimated Required Balance: ~{estimated_required:.2f} USDT")

    # Check if current price is in range
    if Config.GRID_LOWER_PRICE <= price <= Config.GRID_UPPER_PRICE:
        print("✓ Current price is within grid range")
    else:
        print("⚠ WARNING: Current price is outside grid range!")

    print("\n" + "=" * 60)
    print("API connection successful! You can now run the bot.")
    print("=" * 60)


if __name__ == "__main__":
    main()
