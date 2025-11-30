"""
Configuration management for Greed Bot
Loads settings from environment variables and .env file
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for bot settings"""

    # Bybit API Configuration
    BYBIT_API_KEY: str = os.getenv("BYBIT_API_KEY", "")
    BYBIT_API_SECRET: str = os.getenv("BYBIT_API_SECRET", "")
    BYBIT_TESTNET: bool = os.getenv("BYBIT_TESTNET", "true").lower() == "true"

    # Trading Configuration
    TRADING_SYMBOL: str = os.getenv("TRADING_SYMBOL", "BTCUSDT")
    MARKET_TYPE: str = os.getenv("MARKET_TYPE", "spot")  # 'spot' or 'linear' (futures)

    # Grid Trading Configuration
    GRID_LEVELS: int = int(os.getenv("GRID_LEVELS", "10"))
    GRID_LOWER_PRICE: float = float(os.getenv("GRID_LOWER_PRICE", "40000"))
    GRID_UPPER_PRICE: float = float(os.getenv("GRID_UPPER_PRICE", "50000"))
    ORDER_AMOUNT: float = float(os.getenv("ORDER_AMOUNT", "0.001"))

    # Bot Settings
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", "10"))  # seconds
    MAX_OPEN_ORDERS: int = int(os.getenv("MAX_OPEN_ORDERS", "20"))

    # Risk Management
    STOP_LOSS_PERCENT: float = float(os.getenv("STOP_LOSS_PERCENT", "0"))  # 0 = disabled
    TAKE_PROFIT_PERCENT: float = float(os.getenv("TAKE_PROFIT_PERCENT", "0"))  # 0 = disabled

    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration

        Returns:
            True if config is valid, False otherwise
        """
        errors = []

        if not cls.BYBIT_API_KEY:
            errors.append("BYBIT_API_KEY is not set")

        if not cls.BYBIT_API_SECRET:
            errors.append("BYBIT_API_SECRET is not set")

        if cls.GRID_LOWER_PRICE >= cls.GRID_UPPER_PRICE:
            errors.append("GRID_LOWER_PRICE must be less than GRID_UPPER_PRICE")

        if cls.GRID_LEVELS < 2:
            errors.append("GRID_LEVELS must be at least 2")

        if cls.ORDER_AMOUNT <= 0:
            errors.append("ORDER_AMOUNT must be greater than 0")

        if cls.MARKET_TYPE not in ["spot", "linear"]:
            errors.append("MARKET_TYPE must be 'spot' or 'linear'")

        if errors:
            for error in errors:
                print(f"Config Error: {error}")
            return False

        return True

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        Convert config to dictionary

        Returns:
            Dictionary of configuration values
        """
        return {
            "BYBIT_TESTNET": cls.BYBIT_TESTNET,
            "TRADING_SYMBOL": cls.TRADING_SYMBOL,
            "MARKET_TYPE": cls.MARKET_TYPE,
            "GRID_LEVELS": cls.GRID_LEVELS,
            "GRID_LOWER_PRICE": cls.GRID_LOWER_PRICE,
            "GRID_UPPER_PRICE": cls.GRID_UPPER_PRICE,
            "ORDER_AMOUNT": cls.ORDER_AMOUNT,
            "CHECK_INTERVAL": cls.CHECK_INTERVAL,
            "MAX_OPEN_ORDERS": cls.MAX_OPEN_ORDERS,
            "STOP_LOSS_PERCENT": cls.STOP_LOSS_PERCENT,
            "TAKE_PROFIT_PERCENT": cls.TAKE_PROFIT_PERCENT,
        }

    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)"""
        print("\n=== Greed Bot Configuration ===")
        for key, value in cls.to_dict().items():
            print(f"{key}: {value}")
        print("===============================\n")
