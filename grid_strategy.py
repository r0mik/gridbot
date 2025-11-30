"""
Grid Trading Strategy Implementation
Places buy and sell orders at predetermined price levels to profit from market volatility
"""

import logging
import time
from typing import List, Dict, Optional, Any, Tuple
from bybit_client import BybitClient
from database import Database

logger = logging.getLogger(__name__)


class GridTradingStrategy:
    """
    Grid trading strategy for both spot and futures markets

    The strategy works by:
    1. Dividing the price range into equal levels (grid)
    2. Placing buy orders below current price
    3. Placing sell orders above current price
    4. When a buy order fills, place a sell order above it
    5. When a sell order fills, place a buy order below it
    """

    def __init__(
        self,
        client: BybitClient,
        symbol: str,
        grid_levels: int,
        lower_price: float,
        upper_price: float,
        order_amount: float,
        category: str = "spot",
        db: Optional[Database] = None
    ):
        """
        Initialize grid trading strategy

        Args:
            client: Bybit client instance
            symbol: Trading pair (e.g., 'BTCUSDT')
            grid_levels: Number of grid levels
            lower_price: Lower bound of grid
            upper_price: Upper bound of grid
            order_amount: Amount per order
            category: 'spot' or 'linear' (futures)
            db: Database instance for logging
        """
        self.client = client
        self.symbol = symbol
        self.grid_levels = grid_levels
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.order_amount = order_amount
        self.category = category
        self.db = db

        # Calculate grid prices
        self.grid_prices = self._calculate_grid_prices()

        # Track active orders
        self.active_orders: Dict[str, Dict[str, Any]] = {}

        logger.info(
            f"Initialized grid strategy: {symbol} ({category}), "
            f"{grid_levels} levels from {lower_price} to {upper_price}"
        )

    def _calculate_grid_prices(self) -> List[float]:
        """
        Calculate grid price levels

        Returns:
            List of price levels for the grid
        """
        # Calculate evenly spaced prices (replaces np.linspace)
        step = (self.upper_price - self.lower_price) / (self.grid_levels - 1)
        prices = [self.lower_price + step * i for i in range(self.grid_levels)]
        grid_prices = [round(price, 2) for price in prices]
        logger.info(f"Grid prices: {grid_prices}")
        return grid_prices

    def initialize_grid(self) -> bool:
        """
        Initialize the grid by placing initial orders

        Returns:
            True if successful, False otherwise
        """
        logger.info("Initializing grid...")

        # Get current price
        current_price = self.client.get_ticker_price(self.symbol, self.category)
        if current_price is None:
            logger.error("Failed to get current price")
            return False

        logger.info(f"Current price: {current_price}")

        # Cancel any existing orders
        self.client.cancel_all_orders(self.symbol, self.category)
        time.sleep(1)

        # Place buy orders below current price and sell orders above
        buy_count = 0
        sell_count = 0

        for price in self.grid_prices:
            if price < current_price:
                # Place buy order
                order_link_id = f"grid_buy_{price}"
                result = self.client.place_order(
                    symbol=self.symbol,
                    side="Buy",
                    order_type="Limit",
                    qty=self.order_amount,
                    price=price,
                    category=self.category,
                    order_link_id=order_link_id
                )

                if result:
                    self.active_orders[order_link_id] = {
                        "price": price,
                        "side": "Buy",
                        "order_id": result.get("orderId"),
                        "status": "active"
                    }
                    buy_count += 1

                    # Log to database
                    if self.db:
                        self.db.add_order({
                            "order_id": result.get("orderId"),
                            "order_link_id": order_link_id,
                            "symbol": self.symbol,
                            "side": "Buy",
                            "order_type": "Limit",
                            "price": price,
                            "qty": self.order_amount,
                            "status": "active",
                            "category": self.category
                        })
                        self.db.update_grid_level(price, has_buy=True, buy_order_id=order_link_id)

                    time.sleep(0.2)  # Avoid rate limiting

            elif price > current_price:
                # Place sell order
                order_link_id = f"grid_sell_{price}"
                result = self.client.place_order(
                    symbol=self.symbol,
                    side="Sell",
                    order_type="Limit",
                    qty=self.order_amount,
                    price=price,
                    category=self.category,
                    order_link_id=order_link_id
                )

                if result:
                    self.active_orders[order_link_id] = {
                        "price": price,
                        "side": "Sell",
                        "order_id": result.get("orderId"),
                        "status": "active"
                    }
                    sell_count += 1

                    # Log to database
                    if self.db:
                        self.db.add_order({
                            "order_id": result.get("orderId"),
                            "order_link_id": order_link_id,
                            "symbol": self.symbol,
                            "side": "Sell",
                            "order_type": "Limit",
                            "price": price,
                            "qty": self.order_amount,
                            "status": "active",
                            "category": self.category
                        })
                        self.db.update_grid_level(price, has_sell=True, sell_order_id=order_link_id)

                    time.sleep(0.2)  # Avoid rate limiting

        logger.info(f"Grid initialized: {buy_count} buy orders, {sell_count} sell orders")
        return True

    def check_and_rebalance(self) -> None:
        """
        Check for filled orders and rebalance the grid
        """
        # Get current open orders from exchange
        open_orders = self.client.get_open_orders(self.symbol, self.category)
        open_order_ids = {order.get('orderLinkId') for order in open_orders}

        # Find filled orders
        filled_orders = []
        for order_link_id, order_info in list(self.active_orders.items()):
            if order_link_id not in open_order_ids and order_info['status'] == 'active':
                # Order was filled
                filled_orders.append((order_link_id, order_info))
                order_info['status'] = 'filled'
                logger.info(
                    f"Order filled: {order_info['side']} @ {order_info['price']}"
                )

                # Update database
                if self.db:
                    from datetime import datetime
                    self.db.update_order_status(
                        order_link_id,
                        'filled',
                        datetime.now().isoformat()
                    )
                    self.db.add_trade({
                        "order_id": order_info['order_id'],
                        "symbol": self.symbol,
                        "side": order_info['side'],
                        "price": order_info['price'],
                        "qty": self.order_amount,
                        "category": self.category
                    })

        # Rebalance: place opposite orders for filled ones
        for order_link_id, order_info in filled_orders:
            self._handle_filled_order(order_info)

    def _handle_filled_order(self, filled_order: Dict[str, Any]) -> None:
        """
        Handle a filled order by placing the opposite order at the next grid level

        Args:
            filled_order: Information about the filled order
        """
        filled_price = filled_order['price']
        filled_side = filled_order['side']

        # Find the next grid level
        next_price = self._find_next_grid_level(filled_price, filled_side)

        if next_price is None:
            logger.warning(
                f"No next grid level found for {filled_side} @ {filled_price}"
            )
            return

        # Place opposite order
        new_side = "Sell" if filled_side == "Buy" else "Buy"
        order_link_id = f"grid_{new_side.lower()}_{next_price}_{int(time.time())}"

        result = self.client.place_order(
            symbol=self.symbol,
            side=new_side,
            order_type="Limit",
            qty=self.order_amount,
            price=next_price,
            category=self.category,
            order_link_id=order_link_id
        )

        if result:
            self.active_orders[order_link_id] = {
                "price": next_price,
                "side": new_side,
                "order_id": result.get("orderId"),
                "status": "active"
            }
            logger.info(
                f"Rebalanced: Placed {new_side} order @ {next_price} "
                f"(filled {filled_side} @ {filled_price})"
            )

            # Log to database
            if self.db:
                self.db.add_order({
                    "order_id": result.get("orderId"),
                    "order_link_id": order_link_id,
                    "symbol": self.symbol,
                    "side": new_side,
                    "order_type": "Limit",
                    "price": next_price,
                    "qty": self.order_amount,
                    "status": "active",
                    "category": self.category
                })
                if new_side == "Buy":
                    self.db.update_grid_level(next_price, has_buy=True, buy_order_id=order_link_id)
                else:
                    self.db.update_grid_level(next_price, has_sell=True, sell_order_id=order_link_id)

    def _find_next_grid_level(
        self,
        current_price: float,
        side: str
    ) -> Optional[float]:
        """
        Find the next grid level for rebalancing

        Args:
            current_price: Price of filled order
            side: Side of filled order ('Buy' or 'Sell')

        Returns:
            Next grid price or None if at boundary
        """
        try:
            current_index = self.grid_prices.index(current_price)
        except ValueError:
            # Price not in grid, find nearest
            differences = [abs(p - current_price) for p in self.grid_prices]
            current_index = differences.index(min(differences))

        if side == "Buy":
            # Buy filled, place sell above
            if current_index < len(self.grid_prices) - 1:
                return self.grid_prices[current_index + 1]
        else:
            # Sell filled, place buy below
            if current_index > 0:
                return self.grid_prices[current_index - 1]

        return None

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the grid

        Returns:
            Dictionary with grid status information
        """
        active_buys = sum(
            1 for o in self.active_orders.values()
            if o['side'] == 'Buy' and o['status'] == 'active'
        )
        active_sells = sum(
            1 for o in self.active_orders.values()
            if o['side'] == 'Sell' and o['status'] == 'active'
        )
        filled_orders = sum(
            1 for o in self.active_orders.values()
            if o['status'] == 'filled'
        )

        return {
            "total_orders": len(self.active_orders),
            "active_buys": active_buys,
            "active_sells": active_sells,
            "filled_orders": filled_orders,
            "grid_range": f"{self.lower_price} - {self.upper_price}",
            "grid_levels": self.grid_levels
        }

    def stop(self) -> None:
        """Stop the strategy and cancel all orders"""
        logger.info("Stopping grid strategy...")
        self.client.cancel_all_orders(self.symbol, self.category)
        self.active_orders.clear()
        logger.info("Grid strategy stopped")
