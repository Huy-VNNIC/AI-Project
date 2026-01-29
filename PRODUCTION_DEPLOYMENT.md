# Production Deployment Guide

## 🎯 Deployment Summary

API is successfully deployed and running in production on server **103.141.177.146:8000**

### Container Status
- **Container Name**: requirement-analyzer-api
- **Image**: requirement-analyzer:production
- **Status**: ✅ Running (healthy)
- **Port**: 8000 (mapped to host)
- **Network**: 0.0.0.0 (accessible from external network)

## 🌐 API Endpoints

### Base URL
- **Internal**: http://localhost:8000
- **External**: http://103.141.177.146:8000

### Available Endpoints

#### Health Checks
- `GET /health` - API health status
- `GET /api/health` - Legacy health endpoint

#### V1 Endpoints (Estimation)
- `POST /api/estimate` - Single estimation
- `POST /api/estimate-batch` - Batch estimation
- `POST /api/loc-estimate` - LOC estimation
- `POST /api/multi-model-estimate` - Multi-model estimation
- `GET /api/models` - List available models

#### V2 Endpoints (Requirements Engineering)
- `POST /api/v2/task-generation/generate` - Generate from text
- `POST /api/v2/task-generation/generate-from-file` - Generate from file upload
- `POST /api/v2/task-generation/refine` - Refine requirements
- `POST /api/v2/task-generation/detect-gaps` - Detect gaps
- `POST /api/v2/task-generation/slice` - Slice requirements

#### Frontend
- `GET /` - Web UI (static files served from `/app/requirement_analyzer/static`)

## 🔧 Container Management

Use the `manage-production.sh` script to manage the container:

```bash
# Show container status
./manage-production.sh status

# View logs (follow mode)
./manage-production.sh logs

# Check API health
./manage-production.sh health

# Restart container
./manage-production.sh restart

# Stop container
./manage-production.sh stop

# Start container
./manage-production.sh start

# Remove container
./manage-production.sh remove

# Rebuild image and restart
./manage-production.sh rebuild
```

## 🐳 Docker Details

### Image Configuration
- **Base Image**: python:3.10-slim
- **Working Directory**: /app
- **Dependencies**: requirements.txt + spaCy en_core_web_sm
- **Health Check**: HTTP GET to /health endpoint every 30s

### Volume Mounts
- `./logs:/app/logs` - API logs
- `./datasets/feedback:/app/datasets/feedback` - User feedback data
- `./processed_data:/app/processed_data` - Processed datasets

### Restart Policy
- **Policy**: unless-stopped
- Automatically restarts on failure or system reboot

## 🔐 Security Features

### Rate Limiting
- **Limit**: 100 requests per 60 seconds per IP
- **Response**: 429 Too Many Requests when exceeded

### File Upload Validation
- **Max Size**: 2MB per file
- **Allowed Types**: .txt, .md, .csv, .json, .pdf
- **Path Traversal**: Blocked

### Network Security
- API bound to 0.0.0.0 for external access
- Consider adding reverse proxy (nginx) for HTTPS in production
- Firewall rules recommended for port 8000

## 🔥 Firewall Configuration (Recommended)

```bash
# Allow port 8000 from specific IPs
sudo ufw allow from YOUR_IP_ADDRESS to any port 8000

# Or allow from anywhere (less secure)
sudo ufw allow 8000/tcp

# Check firewall status
sudo ufw status
```

## 📊 Monitoring

### View Logs
```bash
# Docker logs
docker logs -f requirement-analyzer-api

# Or use management script
./manage-production.sh logs
```

### Check Container Health
```bash
# Docker inspect
docker inspect --format='{{.State.Health.Status}}' requirement-analyzer-api

# Or use management script
./manage-production.sh health
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# External access
curl http://103.141.177.146:8000/health
```

## 🚀 Deployment Process

The deployment was automated using `deploy-api-production.sh`:

1. **Cleanup**: Stop existing containers and kill processes on port 8000
2. **Build**: Build Docker image from Dockerfile.api-production
3. **Deploy**: Run container with volume mounts and health checks
4. **Validate**: Health check with 10 retries
5. **Test**: Test V2 endpoints

## 📝 Configuration Files

### Dockerfile.api-production
- Multi-stage build with Python 3.10-slim
- Installs system dependencies (gcc, g++, wget)
- Installs Python dependencies from requirements.txt
- Downloads spaCy model (en_core_web_sm)
- Copies application code and models
- Configures health checks

### docker-compose.production.yml
- Service definition for requirement-analyzer-api
- Port mapping (8000:8000)
- Volume mounts for logs and data
- Health check configuration
- Restart policy

### deploy-api-production.sh
- Automated deployment script
- Handles container lifecycle
- Performs health validation
- Tests API endpoints

### manage-production.sh
- Container management utility
- Start/stop/restart operations
- Log viewing
- Health checks
- Rebuild functionality

## 🔄 Update Procedure

To update the API with new code:

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./manage-production.sh rebuild

# Verify deployment
./manage-production.sh health
```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs requirement-analyzer-api

# Check port availability
lsof -i :8000

# Remove and recreate
./manage-production.sh remove
./manage-production.sh start
```

### API not responding
```bash
# Check container status
docker ps -a | grep requirement-analyzer-api

# Check health
docker inspect --format='{{.State.Health.Status}}' requirement-analyzer-api

# Restart
./manage-production.sh restart
```

### Port 8000 already in use
```bash
# Kill process using port
lsof -ti:8000 | xargs kill -9

# Or use management script (rebuild command kills port automatically)
./manage-production.sh rebuild
```

## 📈 Performance

### Current Configuration
- **Models Loaded**: 
  - V1: LOC Linear, LOC RF, COCOMO II Extended (Linear, Decision Tree, RF, Gradient Boosting)
  - V2: Requirement detector, Type/Priority/Domain enrichers, spaCy NLP
- **Startup Time**: ~15 seconds
- **Memory Usage**: ~2GB (includes all ML models)
- **Health Check**: Every 30 seconds

## 🎉 Success Verification

✅ Docker image built successfully (150.3s)  
✅ Container started and running  
✅ Health check: **healthy**  
✅ API responding on port 8000  
✅ External access working from 172.144.0.206  
✅ All models loaded successfully  
✅ V1 and V2 endpoints available  
✅ Security middleware active  
✅ Files committed to GitHub  

## 📞 Support

For issues or questions:
1. Check logs: `./manage-production.sh logs`
2. Check health: `./manage-production.sh health`
3. Review container status: `./manage-production.sh status`
4. Rebuild if necessary: `./manage-production.sh rebuild`

---

**Deployment Date**: 2026-01-29  
**Server**: 103.141.177.146  
**Port**: 8000  
**Status**: ✅ Production Ready
