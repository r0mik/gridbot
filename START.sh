#!/bin/bash
# Greed Bot Startup Script
# This script helps you start all components easily

echo "🤖 Greed Bot Startup Helper"
echo "============================"
echo ""
echo "This script will help you start the Greed Bot with web dashboard."
echo ""
echo "You need to run the following in SEPARATE terminals:"
echo ""
echo "Terminal 1 - Trading Bot:"
echo "  python main.py"
echo ""
echo "Terminal 2 - API Server:"
echo "  python api_server.py"
echo ""
echo "Terminal 3 - Web Dashboard:"
echo "  cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:30002"
echo ""
echo "Press Ctrl+C in each terminal to stop."
echo ""
echo "Choose what to start:"
echo "1) Trading Bot (main.py)"
echo "2) API Server (api_server.py)"
echo "3) Web Dashboard (frontend)"
echo "4) Show URLs and ports"
read -p "Enter choice (1-4): " choice

case $choice in
  1)
    echo "Starting Trading Bot..."
    python main.py
    ;;
  2)
    echo "Starting API Server..."
    python api_server.py
    ;;
  3)
    echo "Starting Web Dashboard..."
    cd frontend && npm run dev
    ;;
  4)
    echo ""
    echo "Service URLs:"
    echo "  Web Dashboard: http://localhost:30002"
    echo "  API Server:    http://localhost:8000"
    echo "  API Docs:      http://localhost:8000/docs"
    echo ""
    ;;
  *)
    echo "Invalid choice"
    ;;
esac
