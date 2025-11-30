"""
Bot Manager - Handles bot lifecycle and control from web interface
"""

import logging
import threading
import time
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

from bybit_client import BybitClient
from grid_strategy import GridTradingStrategy
from database import Database

logger = logging.getLogger(__name__)


class BotManager:
    """Manages bot lifecycle and provides control interface"""

    CONFIG_FILE = "bot_config.json"

    def __init__(self, db: Database):
        """
        Initialize bot manager

        Args:
            db: Database instance
        """
        self.db = db
        self.bot_thread: Optional[threading.Thread] = None
        self.running = False
        self.client: Optional[BybitClient] = None
        self.strategy: Optional[GridTradingStrategy] = None
        self.config: Dict[str, Any] = {}
        self.error_message: Optional[str] = None

        # Load saved configuration if exists
        self._load_config()

    def configure(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Configure the bot with new settings

        Args:
            config: Configuration dictionary

        Returns:
            Status dict with success/error message
        """
        try:
            # Validate required fields
            required = ['api_key', 'api_secret', 'symbol', 'grid_levels',
                       'grid_lower', 'grid_upper', 'order_amount']
            missing = [f for f in required if f not in config]
            if missing:
                return {
                    'status': 'error',
                    'message': f'Missing required fields: {", ".join(missing)}'
                }

            # Validate numeric fields
            try:
                config['grid_levels'] = int(config['grid_levels'])
                config['grid_lower'] = float(config['grid_lower'])
                config['grid_upper'] = float(config['grid_upper'])
                config['order_amount'] = float(config['order_amount'])
            except ValueError as e:
                return {
                    'status': 'error',
                    'message': f'Invalid numeric value: {e}'
                }

            # Validate ranges
            if config['grid_lower'] >= config['grid_upper']:
                return {
                    'status': 'error',
                    'message': 'Grid lower price must be less than upper price'
                }

            if config['grid_levels'] < 2:
                return {
                    'status': 'error',
                    'message': 'Grid levels must be at least 2'
                }

            if config['order_amount'] <= 0:
                return {
                    'status': 'error',
                    'message': 'Order amount must be greater than 0'
                }

            # Store configuration
            self.config = config

            # Save configuration to file
            self._save_config()

            # Save to database
            self.db.update_bot_status({
                'is_running': self.running,
                'symbol': config['symbol'],
                'market_type': config.get('market_type', 'spot'),
                'grid_levels': config['grid_levels'],
                'grid_lower': config['grid_lower'],
                'grid_upper': config['grid_upper'],
                'order_amount': config['order_amount'],
                'current_price': None
            })

            logger.info(f"Bot configured: {config['symbol']}, {config['grid_levels']} levels")
            return {'status': 'success', 'message': 'Configuration saved'}

        except Exception as e:
            logger.error(f"Error configuring bot: {e}")
            return {'status': 'error', 'message': str(e)}

    def start(self) -> Dict[str, str]:
        """
        Start the trading bot

        Returns:
            Status dict with success/error message
        """
        if self.running:
            return {'status': 'error', 'message': 'Bot is already running'}

        if not self.config:
            return {'status': 'error', 'message': 'Bot not configured. Please configure first.'}

        try:
            # Initialize client
            self.client = BybitClient(
                api_key=self.config['api_key'],
                api_secret=self.config['api_secret'],
                testnet=self.config.get('testnet', True)
            )

            # Test connection
            current_price = self.client.get_ticker_price(
                self.config['symbol'],
                self.config.get('market_type', 'spot')
            )

            if current_price is None:
                return {
                    'status': 'error',
                    'message': 'Failed to connect to Bybit. Check API credentials.'
                }

            # Auto-adjust grid range if current price is outside configured range
            grid_lower = self.config['grid_lower']
            grid_upper = self.config['grid_upper']
            auto_adjusted = False

            if current_price < grid_lower or current_price > grid_upper:
                # Calculate grid range as ±5% from current price
                range_percent = 0.05
                grid_lower = round(current_price * (1 - range_percent), 2)
                grid_upper = round(current_price * (1 + range_percent), 2)
                auto_adjusted = True

                # Update config with new range
                self.config['grid_lower'] = grid_lower
                self.config['grid_upper'] = grid_upper

                logger.info(
                    f"Auto-adjusted grid range from "
                    f"${self.config.get('grid_lower_original', 'N/A')}-${self.config.get('grid_upper_original', 'N/A')} "
                    f"to ${grid_lower}-${grid_upper} based on current price ${current_price}"
                )

            # Initialize strategy
            self.strategy = GridTradingStrategy(
                client=self.client,
                symbol=self.config['symbol'],
                grid_levels=self.config['grid_levels'],
                lower_price=grid_lower,
                upper_price=grid_upper,
                order_amount=self.config['order_amount'],
                category=self.config.get('market_type', 'spot'),
                db=self.db
            )

            # Initialize grid
            if not self.strategy.initialize_grid():
                return {
                    'status': 'error',
                    'message': 'Failed to initialize grid'
                }

            # Start bot thread
            self.running = True
            self.error_message = None
            self.bot_thread = threading.Thread(target=self._run_bot, daemon=True)
            self.bot_thread.start()

            # Update database
            self.db.update_bot_status({
                'is_running': True,
                'symbol': self.config['symbol'],
                'market_type': self.config.get('market_type', 'spot'),
                'grid_levels': self.config['grid_levels'],
                'grid_lower': grid_lower,
                'grid_upper': grid_upper,
                'order_amount': self.config['order_amount'],
                'current_price': current_price
            })

            logger.info("Bot started successfully")

            # Build success message
            message = 'Bot started successfully'
            if auto_adjusted:
                message += f'. Grid range auto-adjusted to ${grid_lower:,.2f}-${grid_upper:,.2f} (±5% of current price ${current_price:,.2f})'

            return {'status': 'success', 'message': message}

        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            self.running = False
            return {'status': 'error', 'message': str(e)}

    def stop(self) -> Dict[str, str]:
        """
        Stop the trading bot

        Returns:
            Status dict with success/error message
        """
        if not self.running:
            return {'status': 'error', 'message': 'Bot is not running'}

        try:
            self.running = False

            # Cancel all orders
            if self.strategy:
                self.strategy.stop()

            # Wait for thread to finish
            if self.bot_thread:
                self.bot_thread.join(timeout=5)

            # Update database
            self.db.update_bot_status({
                'is_running': False,
                'symbol': self.config.get('symbol'),
                'market_type': self.config.get('market_type', 'spot'),
                'grid_levels': self.config.get('grid_levels'),
                'grid_lower': self.config.get('grid_lower'),
                'grid_upper': self.config.get('grid_upper'),
                'order_amount': self.config.get('order_amount'),
                'current_price': None
            })

            logger.info("Bot stopped successfully")
            return {'status': 'success', 'message': 'Bot stopped successfully'}

        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return {'status': 'error', 'message': str(e)}

    def _run_bot(self):
        """Internal method to run bot loop"""
        logger.info("Bot loop started")
        check_interval = self.config.get('check_interval', 10)
        iteration = 0

        while self.running:
            try:
                iteration += 1

                # Check and rebalance grid
                if self.strategy:
                    self.strategy.check_and_rebalance()

                # Update status periodically
                if iteration % 6 == 0:
                    status = self.strategy.get_status()
                    logger.info(
                        f"Status: {status['active_buys']} buy orders, "
                        f"{status['active_sells']} sell orders, "
                        f"{status['filled_orders']} filled orders"
                    )

                    # Update current price in database
                    if self.client:
                        current_price = self.client.get_ticker_price(
                            self.config['symbol'],
                            self.config.get('market_type', 'spot')
                        )
                        if current_price:
                            self.db.update_bot_status({
                                'is_running': True,
                                'symbol': self.config['symbol'],
                                'market_type': self.config.get('market_type', 'spot'),
                                'grid_levels': self.config['grid_levels'],
                                'grid_lower': self.config['grid_lower'],
                                'grid_upper': self.config['grid_upper'],
                                'order_amount': self.config['order_amount'],
                                'current_price': current_price
                            })

                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error in bot loop: {e}", exc_info=True)
                self.error_message = str(e)
                time.sleep(check_interval)

        logger.info("Bot loop ended")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current bot status

        Returns:
            Status dictionary
        """
        return {
            'running': self.running,
            'configured': bool(self.config),
            'error': self.error_message,
            'config': {
                'symbol': self.config.get('symbol'),
                'market_type': self.config.get('market_type', 'spot'),
                'grid_levels': self.config.get('grid_levels'),
                'grid_lower': self.config.get('grid_lower'),
                'grid_upper': self.config.get('grid_upper'),
                'order_amount': self.config.get('order_amount'),
                'testnet': self.config.get('testnet', True)
            } if self.config else None
        }

    def _save_config(self) -> None:
        """Save configuration to file (encrypting sensitive data)"""
        try:
            # Create a copy without sensitive data for logging
            safe_config = {k: v for k, v in self.config.items() if k not in ['api_key', 'api_secret']}

            # Save full config to file
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)

            # Set restrictive permissions (owner read/write only)
            os.chmod(self.CONFIG_FILE, 0o600)

            logger.info(f"Configuration saved to {self.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)

                # Mask sensitive data in log
                safe_config = {k: '***' if k in ['api_key', 'api_secret'] else v
                              for k, v in self.config.items()}
                logger.info(f"Configuration loaded from {self.CONFIG_FILE}: {safe_config}")
            else:
                logger.info(f"No saved configuration found at {self.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = {}
