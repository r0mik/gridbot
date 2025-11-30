# Port Configuration

## Current Port Setup

### Frontend (Web Dashboard)
- **Port:** 30002
- **URL:** http://localhost:30002
- **Config file:** `frontend/vite.config.js`

### Backend (API Server)
- **Port:** 8000
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Config file:** `api_server.py`

### WebSocket
- **URL:** ws://localhost:8000/ws
- Proxied through frontend for development

## How to Change Ports

### Change Frontend Port

Edit `frontend/vite.config.js`:
```javascript
server: {
  port: 30002,  // Change this number
  ...
}
```

### Change Backend Port

Edit `api_server.py` at the bottom:
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,  # Change this number
    log_level="info"
)
```

Also update the proxy in `frontend/vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',  // Update port here
    ...
  },
  '/ws': {
    target: 'ws://localhost:8000',  // Update port here
    ...
  }
}
```

## Firewall Rules

If running on a server, allow these ports:

```bash
# Ubuntu/Debian
sudo ufw allow 30002/tcp  # Frontend
sudo ufw allow 8000/tcp   # API (only if accessing externally)

# CentOS/RHEL
sudo firewall-cmd --add-port=30002/tcp --permanent
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

## Production Deployment

For production, typically:
- Frontend: Serve static build via Nginx (port 80/443)
- Backend: Keep on internal port (8000), proxy via Nginx
- WebSocket: Proxy via Nginx with upgrade headers

Example Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Serve frontend
    location / {
        root /var/www/greedbot/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Proxy WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
