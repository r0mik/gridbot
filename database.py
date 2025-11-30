"""
Database models and operations for Greed Bot
Using SQLite for storing trades, orders, and bot status
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database manager for Greed Bot"""

    def __init__(self, db_path: str = "greedbot.db"):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Bot status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_running BOOLEAN DEFAULT 0,
                symbol TEXT,
                market_type TEXT,
                grid_levels INTEGER,
                grid_lower REAL,
                grid_upper REAL,
                order_amount REAL,
                current_price REAL,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE,
                order_link_id TEXT,
                symbol TEXT,
                side TEXT,
                order_type TEXT,
                price REAL,
                qty REAL,
                status TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                filled_at TIMESTAMP
            )
        """)

        # Trades table (filled orders with profit tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                symbol TEXT,
                side TEXT,
                price REAL,
                qty REAL,
                commission REAL DEFAULT 0,
                profit REAL DEFAULT 0,
                category TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Grid status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grid_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                price REAL,
                has_buy_order BOOLEAN DEFAULT 0,
                has_sell_order BOOLEAN DEFAULT 0,
                buy_order_id TEXT,
                sell_order_id TEXT,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_trades INTEGER DEFAULT 0,
                total_profit REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_profit REAL DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")

    def update_bot_status(self, status: Dict[str, Any]) -> bool:
        """
        Update bot status

        Args:
            status: Dictionary with bot status information

        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO bot_status (
                    is_running, symbol, market_type, grid_levels,
                    grid_lower, grid_upper, order_amount, current_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                status.get('is_running', False),
                status.get('symbol'),
                status.get('market_type'),
                status.get('grid_levels'),
                status.get('grid_lower'),
                status.get('grid_upper'),
                status.get('order_amount'),
                status.get('current_price')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating bot status: {e}")
            return False

    def get_latest_bot_status(self) -> Optional[Dict[str, Any]]:
        """
        Get latest bot status

        Returns:
            Dictionary with bot status or None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM bot_status
                ORDER BY last_update DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return None

    def add_order(self, order: Dict[str, Any]) -> bool:
        """
        Add or update order

        Args:
            order: Order information

        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO orders (
                    order_id, order_link_id, symbol, side, order_type,
                    price, qty, status, category, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                order.get('order_id'),
                order.get('order_link_id'),
                order.get('symbol'),
                order.get('side'),
                order.get('order_type'),
                order.get('price'),
                order.get('qty'),
                order.get('status', 'active'),
                order.get('category')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding order: {e}")
            return False

    def update_order_status(self, order_id: str, status: str, filled_at: Optional[str] = None) -> bool:
        """
        Update order status

        Args:
            order_id: Order ID or order link ID
            status: New status
            filled_at: Timestamp when order was filled

        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            if filled_at:
                cursor.execute("""
                    UPDATE orders
                    SET status = ?, filled_at = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE order_id = ? OR order_link_id = ?
                """, (status, filled_at, order_id, order_id))
            else:
                cursor.execute("""
                    UPDATE orders
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE order_id = ? OR order_link_id = ?
                """, (status, order_id, order_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False

    def add_trade(self, trade: Dict[str, Any]) -> bool:
        """
        Add executed trade

        Args:
            trade: Trade information

        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO trades (
                    order_id, symbol, side, price, qty,
                    commission, profit, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.get('order_id'),
                trade.get('symbol'),
                trade.get('side'),
                trade.get('price'),
                trade.get('qty'),
                trade.get('commission', 0),
                trade.get('profit', 0),
                trade.get('category')
            ))
            self.conn.commit()

            # Update performance metrics
            self._update_performance()
            return True
        except Exception as e:
            logger.error(f"Error adding trade: {e}")
            return False

    def get_orders(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders from database

        Args:
            limit: Maximum number of orders to return
            status: Filter by status (optional)

        Returns:
            List of orders
        """
        try:
            cursor = self.conn.cursor()
            if status:
                cursor.execute("""
                    SELECT * FROM orders
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (status, limit))
            else:
                cursor.execute("""
                    SELECT * FROM orders
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []

    def get_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get trades from database

        Args:
            limit: Maximum number of trades to return

        Returns:
            List of trades
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM trades
                ORDER BY executed_at DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []

    def _update_performance(self):
        """Update performance metrics based on trades"""
        try:
            cursor = self.conn.cursor()

            # Calculate metrics
            cursor.execute("""
                SELECT
                    COUNT(*) as total_trades,
                    SUM(profit) as total_profit,
                    AVG(profit) as avg_profit,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
                FROM trades
            """)

            metrics = cursor.fetchone()

            cursor.execute("""
                INSERT INTO performance (
                    total_trades, total_profit, win_rate, avg_profit
                ) VALUES (?, ?, ?, ?)
            """, (
                metrics['total_trades'] or 0,
                metrics['total_profit'] or 0,
                metrics['win_rate'] or 0,
                metrics['avg_profit'] or 0
            ))

            self.conn.commit()
        except Exception as e:
            logger.error(f"Error updating performance: {e}")

    def get_performance(self) -> Optional[Dict[str, Any]]:
        """
        Get latest performance metrics

        Returns:
            Dictionary with performance metrics
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM performance
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {
                'total_trades': 0,
                'total_profit': 0,
                'win_rate': 0,
                'avg_profit': 0
            }
        except Exception as e:
            logger.error(f"Error getting performance: {e}")
            return None

    def get_grid_levels(self) -> List[Dict[str, Any]]:
        """Get current grid levels status"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM grid_levels ORDER BY price ASC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting grid levels: {e}")
            return []

    def update_grid_level(self, price: float, has_buy: bool = False, has_sell: bool = False,
                          buy_order_id: Optional[str] = None, sell_order_id: Optional[str] = None):
        """Update grid level status"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO grid_levels (
                    price, has_buy_order, has_sell_order,
                    buy_order_id, sell_order_id, last_update
                ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (price, has_buy, has_sell, buy_order_id, sell_order_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error updating grid level: {e}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
