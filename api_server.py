"""
FastAPI backend server for Greed Bot
Provides REST API and WebSocket endpoints for the frontend
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from database import Database
from config import Config
from bot_manager import BotManager

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Greed Bot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database("greedbot.db")

# Initialize bot manager
bot_manager = BotManager(db)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                dead_connections.append(connection)

        # Remove dead connections
        for connection in dead_connections:
            self.active_connections.remove(connection)

manager = ConnectionManager()


# Pydantic models for API requests/responses
class BotConfigRequest(BaseModel):
    api_key: str
    api_secret: str
    symbol: str
    market_type: str
    grid_levels: int
    grid_lower: float
    grid_upper: float
    order_amount: float
    testnet: bool = True
    check_interval: int = 10


class BotConfig(BaseModel):
    symbol: str
    market_type: str
    grid_levels: int
    grid_lower: float
    grid_upper: float
    order_amount: float


class BotStatusResponse(BaseModel):
    is_running: bool
    symbol: Optional[str] = None
    market_type: Optional[str] = None
    grid_levels: Optional[int] = None
    grid_lower: Optional[float] = None
    grid_upper: Optional[float] = None
    order_amount: Optional[float] = None
    current_price: Optional[float] = None
    last_update: Optional[str] = None


# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Greed Bot API", "version": "1.0.0"}


@app.get("/api/status", response_model=BotStatusResponse)
async def get_bot_status():
    """Get current bot status"""
    status = db.get_latest_bot_status()
    if status:
        return status
    return {
        "is_running": False,
        "symbol": None,
        "market_type": None,
        "grid_levels": None,
        "grid_lower": None,
        "grid_upper": None,
        "order_amount": None,
        "current_price": None,
        "last_update": None
    }


@app.get("/api/orders")
async def get_orders(limit: int = 100, status: Optional[str] = None):
    """Get orders from database"""
    orders = db.get_orders(limit=limit, status=status)
    return {"orders": orders}


@app.get("/api/trades")
async def get_trades(limit: int = 100):
    """Get trades from database"""
    trades = db.get_trades(limit=limit)
    return {"trades": trades}


@app.get("/api/performance")
async def get_performance():
    """Get performance metrics"""
    performance = db.get_performance()
    return performance or {
        "total_trades": 0,
        "total_profit": 0,
        "win_rate": 0,
        "avg_profit": 0
    }


@app.get("/api/grid-levels")
async def get_grid_levels():
    """Get grid levels status"""
    grid_levels = db.get_grid_levels()
    return {"grid_levels": grid_levels}


@app.get("/api/dashboard")
async def get_dashboard():
    """Get complete dashboard data"""
    status = db.get_latest_bot_status()
    performance = db.get_performance()
    recent_trades = db.get_trades(limit=10)
    active_orders = db.get_orders(limit=50, status="active")
    grid_levels = db.get_grid_levels()

    return {
        "status": status,
        "performance": performance,
        "recent_trades": recent_trades,
        "active_orders": active_orders,
        "grid_levels": grid_levels,
        "timestamp": datetime.now().isoformat()
    }


# Bot Control Endpoints

@app.post("/api/bot/configure")
async def configure_bot(config: BotConfigRequest):
    """
    Configure the bot with API credentials and trading parameters
    """
    try:
        result = bot_manager.configure(config.dict())
        return result
    except Exception as e:
        logger.error(f"Error configuring bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bot/start")
async def start_bot():
    """Start the trading bot"""
    try:
        result = bot_manager.start()
        # Broadcast status update
        await manager.broadcast({
            "type": "bot_status",
            "data": bot_manager.get_status()
        })
        return result
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bot/stop")
async def stop_bot():
    """Stop the trading bot"""
    try:
        result = bot_manager.stop()
        # Broadcast status update
        await manager.broadcast({
            "type": "bot_status",
            "data": bot_manager.get_status()
        })
        return result
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bot/status")
async def get_bot_manager_status():
    """Get current bot manager status"""
    try:
        return bot_manager.get_status()
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial data
        dashboard_data = {
            "type": "dashboard",
            "data": {
                "status": db.get_latest_bot_status(),
                "performance": db.get_performance(),
                "recent_trades": db.get_trades(limit=10),
                "active_orders": db.get_orders(limit=50, status="active"),
            }
        }
        await websocket.send_json(dashboard_data)

        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back or handle commands
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({"type": "keepalive"})
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_updates():
    """Background task to broadcast updates to all connected clients"""
    while True:
        try:
            if manager.active_connections:
                # Get latest data
                status = db.get_latest_bot_status()
                performance = db.get_performance()
                recent_trades = db.get_trades(limit=10)
                active_orders = db.get_orders(limit=50, status="active")

                # Broadcast to all clients
                await manager.broadcast({
                    "type": "update",
                    "data": {
                        "status": status,
                        "performance": performance,
                        "recent_trades": recent_trades,
                        "active_orders": active_orders,
                        "timestamp": datetime.now().isoformat()
                    }
                })

            await asyncio.sleep(2)  # Update every 2 seconds
        except Exception as e:
            logger.error(f"Error in broadcast_updates: {e}")
            await asyncio.sleep(5)


@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup"""
    logger.info("Starting API server...")
    asyncio.create_task(broadcast_updates())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    logger.info("Shutting down API server...")
    db.close()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
