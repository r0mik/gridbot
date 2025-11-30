"""
Bybit API Client Wrapper
Handles all interactions with Bybit's API for spot and futures trading
"""

from pybit.unified_trading import HTTP
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class BybitClient:
    """Wrapper for Bybit API using pybit library"""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Bybit client

        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            testnet: Use testnet if True, mainnet if False
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet

        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )
        logger.info(f"Initialized Bybit client ({'testnet' if testnet else 'mainnet'})")

    def get_ticker_price(self, symbol: str, category: str = "spot") -> Optional[float]:
        """
        Get current ticker price

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            category: 'spot' or 'linear' (futures)

        Returns:
            Current price or None if error
        """
        try:
            response = self.session.get_tickers(
                category=category,
                symbol=symbol
            )

            if response['retCode'] == 0:
                price = float(response['result']['list'][0]['lastPrice'])
                logger.debug(f"Got ticker price for {symbol}: {price}")
                return price
            else:
                logger.error(f"Error getting ticker: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"Exception getting ticker price: {e}")
            return None

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        qty: float,
        price: Optional[float] = None,
        category: str = "spot",
        time_in_force: str = "GTC",
        order_link_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Place an order on Bybit

        Args:
            symbol: Trading pair
            side: 'Buy' or 'Sell'
            order_type: 'Limit' or 'Market'
            qty: Order quantity
            price: Limit price (required for limit orders)
            category: 'spot' or 'linear'
            time_in_force: 'GTC', 'IOC', 'FOK'
            order_link_id: Custom order ID

        Returns:
            Order response or None if error
        """
        try:
            params = {
                "category": category,
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(qty),
                "timeInForce": time_in_force
            }

            if price is not None:
                params["price"] = str(price)

            if order_link_id:
                params["orderLinkId"] = order_link_id

            response = self.session.place_order(**params)

            if response['retCode'] == 0:
                logger.info(f"Order placed: {side} {qty} {symbol} @ {price if price else 'market'}")
                return response['result']
            else:
                logger.error(f"Error placing order: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"Exception placing order: {e}")
            return None

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        order_link_id: Optional[str] = None,
        category: str = "spot"
    ) -> bool:
        """
        Cancel an order

        Args:
            symbol: Trading pair
            order_id: Exchange order ID
            order_link_id: Custom order ID
            category: 'spot' or 'linear'

        Returns:
            True if successful, False otherwise
        """
        try:
            params = {
                "category": category,
                "symbol": symbol
            }

            if order_id:
                params["orderId"] = order_id
            elif order_link_id:
                params["orderLinkId"] = order_link_id
            else:
                logger.error("Must provide either order_id or order_link_id")
                return False

            response = self.session.cancel_order(**params)

            if response['retCode'] == 0:
                logger.info(f"Order cancelled: {order_id or order_link_id}")
                return True
            else:
                logger.error(f"Error cancelling order: {response['retMsg']}")
                return False
        except Exception as e:
            logger.error(f"Exception cancelling order: {e}")
            return False

    def get_open_orders(self, symbol: str, category: str = "spot") -> List[Dict[str, Any]]:
        """
        Get all open orders for a symbol

        Args:
            symbol: Trading pair
            category: 'spot' or 'linear'

        Returns:
            List of open orders
        """
        try:
            response = self.session.get_open_orders(
                category=category,
                symbol=symbol
            )

            if response['retCode'] == 0:
                orders = response['result']['list']
                logger.debug(f"Got {len(orders)} open orders for {symbol}")
                return orders
            else:
                logger.error(f"Error getting open orders: {response['retMsg']}")
                return []
        except Exception as e:
            logger.error(f"Exception getting open orders: {e}")
            return []

    def cancel_all_orders(self, symbol: str, category: str = "spot") -> bool:
        """
        Cancel all open orders for a symbol

        Args:
            symbol: Trading pair
            category: 'spot' or 'linear'

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.cancel_all_orders(
                category=category,
                symbol=symbol
            )

            if response['retCode'] == 0:
                logger.info(f"All orders cancelled for {symbol}")
                return True
            else:
                logger.error(f"Error cancelling all orders: {response['retMsg']}")
                return False
        except Exception as e:
            logger.error(f"Exception cancelling all orders: {e}")
            return False

    def get_wallet_balance(self, account_type: str = "UNIFIED") -> Optional[Dict[str, Any]]:
        """
        Get wallet balance

        Args:
            account_type: 'UNIFIED', 'SPOT', or 'CONTRACT'

        Returns:
            Wallet balance info or None if error
        """
        try:
            response = self.session.get_wallet_balance(accountType=account_type)

            if response['retCode'] == 0:
                logger.debug("Retrieved wallet balance")
                return response['result']
            else:
                logger.error(f"Error getting wallet balance: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"Exception getting wallet balance: {e}")
            return None

    def get_position(self, symbol: str, category: str = "linear") -> Optional[Dict[str, Any]]:
        """
        Get position info for futures trading

        Args:
            symbol: Trading pair
            category: 'linear' (futures)

        Returns:
            Position info or None if error
        """
        try:
            response = self.session.get_positions(
                category=category,
                symbol=symbol
            )

            if response['retCode'] == 0:
                positions = response['result']['list']
                if positions:
                    logger.debug(f"Retrieved position for {symbol}")
                    return positions[0]
                return None
            else:
                logger.error(f"Error getting position: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"Exception getting position: {e}")
            return None
