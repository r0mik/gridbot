"""
Greed Bot - Grid Trading Bot for Bybit
Main entry point for running the trading bot
"""

import signal
import sys
import time
import logging
from typing import Optional

from config import Config
from bybit_client import BybitClient
from grid_strategy import GridTradingStrategy
from logger import setup_logger
from database import Database

# Global variables
bot_running = True
strategy: Optional[GridTradingStrategy] = None
db: Optional[Database] = None


def signal_handler(sig, frame):
    """Handle interrupt signal (Ctrl+C)"""
    global bot_running, strategy, db
    print("\n\nShutting down Greed Bot...")
    bot_running = False

    if strategy:
        strategy.stop()

    if db:
        db.close()

    sys.exit(0)


def main():
    """Main bot execution"""
    global bot_running, strategy, db

    # Setup logging
    logger = setup_logger("greedbot", level=logging.INFO)

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 60)
    print("     GREED BOT - Grid Trading Bot for Bybit")
    print("=" * 60)

    # Validate configuration
    if not Config.validate():
        logger.error("Invalid configuration. Please check your .env file")
        return

    # Print configuration
    Config.print_config()

    # Initialize database
    logger.info("Initializing database...")
    db = Database("greedbot.db")

    # Initialize Bybit client
    logger.info("Initializing Bybit client...")
    client = BybitClient(
        api_key=Config.BYBIT_API_KEY,
        api_secret=Config.BYBIT_API_SECRET,
        testnet=Config.BYBIT_TESTNET
    )

    # Get current price to verify connection
    current_price = client.get_ticker_price(Config.TRADING_SYMBOL, Config.MARKET_TYPE)
    if current_price is None:
        logger.error("Failed to connect to Bybit. Please check your API credentials")
        return

    logger.info(f"Current {Config.TRADING_SYMBOL} price: {current_price}")

    # Check if current price is within grid range
    if not (Config.GRID_LOWER_PRICE <= current_price <= Config.GRID_UPPER_PRICE):
        logger.warning(
            f"Current price ({current_price}) is outside grid range "
            f"({Config.GRID_LOWER_PRICE} - {Config.GRID_UPPER_PRICE})"
        )
        response = input("Do you want to continue anyway? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Exiting...")
            return

    # Initialize grid strategy
    logger.info("Initializing grid trading strategy...")
    strategy = GridTradingStrategy(
        client=client,
        symbol=Config.TRADING_SYMBOL,
        grid_levels=Config.GRID_LEVELS,
        lower_price=Config.GRID_LOWER_PRICE,
        upper_price=Config.GRID_UPPER_PRICE,
        order_amount=Config.ORDER_AMOUNT,
        category=Config.MARKET_TYPE,
        db=db
    )

    # Update bot status in database
    db.update_bot_status({
        'is_running': True,
        'symbol': Config.TRADING_SYMBOL,
        'market_type': Config.MARKET_TYPE,
        'grid_levels': Config.GRID_LEVELS,
        'grid_lower': Config.GRID_LOWER_PRICE,
        'grid_upper': Config.GRID_UPPER_PRICE,
        'order_amount': Config.ORDER_AMOUNT,
        'current_price': current_price
    })

    # Initialize the grid
    if not strategy.initialize_grid():
        logger.error("Failed to initialize grid. Exiting...")
        return

    logger.info("Grid initialized successfully!")
    logger.info("Bot is now running. Press Ctrl+C to stop.")

    # Main bot loop
    iteration = 0
    while bot_running:
        try:
            iteration += 1

            # Check and rebalance grid
            strategy.check_and_rebalance()

            # Get and display status periodically
            if iteration % 6 == 0:  # Every 6 iterations (every minute if interval is 10s)
                status = strategy.get_status()
                logger.info(
                    f"Status: {status['active_buys']} buy orders, "
                    f"{status['active_sells']} sell orders, "
                    f"{status['filled_orders']} filled orders"
                )

                # Update current price in database
                current_price = client.get_ticker_price(Config.TRADING_SYMBOL, Config.MARKET_TYPE)
                if current_price:
                    db.update_bot_status({
                        'is_running': True,
                        'symbol': Config.TRADING_SYMBOL,
                        'market_type': Config.MARKET_TYPE,
                        'grid_levels': Config.GRID_LEVELS,
                        'grid_lower': Config.GRID_LOWER_PRICE,
                        'grid_upper': Config.GRID_UPPER_PRICE,
                        'order_amount': Config.ORDER_AMOUNT,
                        'current_price': current_price
                    })

            # Sleep before next iteration
            time.sleep(Config.CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            time.sleep(Config.CHECK_INTERVAL)


if __name__ == "__main__":
    main()
