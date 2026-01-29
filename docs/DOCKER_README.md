# 🚀 AI Effort Estimation Service - Docker Deployment

Complete containerized solution for AI-powered software effort estimation with COCOMO II, Function Points, Use Case Points, and Machine Learning models.

## 🎯 Features

- **Multi-Model Estimation**: COCOMO II, Function Points, Use Case Points, LOC models, ML models
- **Interactive Web Interface**: User-friendly forms and real-time results
- **Document Processing**: Support for PDF, DOC, DOCX, TXT files
- **Requirements Analysis**: Advanced NLP-based requirement prioritization
- **Containerized Deployment**: Docker and Docker Compose ready
- **Production Ready**: Nginx reverse proxy included

## 🛠 Quick Start

### Prerequisites
- Docker (20.10+)
- Docker Compose (1.29+)
- At least 2GB RAM
- 5GB disk space

### 1. Simple Deployment

```bash
# Make scripts executable
chmod +x deploy.sh manage.sh

# Quick start
./deploy.sh
```

The service will be available at:
- **Main Application**: http://localhost:8000
- **COCOMO II Form**: http://localhost:8000/cocomo
- **Alternative Port**: http://localhost:8080

### 2. Production Deployment (with Nginx)

```bash
# Production deployment with reverse proxy
./deploy-production.sh
```

Access via:
- **Production URL**: http://localhost (port 80)
- **Direct API**: http://localhost:8000

## 🎮 Management Commands

Use the management script for easy operations:

```bash
# Start service
./manage.sh start

# Stop service
./manage.sh stop

# View logs
./manage.sh logs

# Check status
./manage.sh status

# Health check
./manage.sh health

# Backup data
./manage.sh backup

# Restore from backup
./manage.sh restore backup_20231024_143022.tar.gz

# Clean up
./manage.sh clean
```

## 📁 Directory Structure

```
AI-Project/
├── docker-compose.yml          # Main compose file
├── Dockerfile.production       # Production Dockerfile
├── nginx.conf                 # Nginx configuration
├── manage.sh                  # Management script
├── deploy.sh                  # Simple deployment
├── deploy-production.sh       # Production deployment
├── models/                    # ML models (mounted as volume)
├── datasets/                  # Training data and feedback
├── uploads/                   # File upload directory
├── logs/                      # Application logs
└── requirement_analyzer/      # Main application code
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
ENV=production

# Model Configuration
MODEL_PATH=/app/models
DATASET_PATH=/app/datasets

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

### Volume Mounts

The Docker setup uses the following volume mounts:

- `./models:/app/models:ro` - ML models (read-only)
- `./datasets:/app/datasets` - Training data and feedback
- `./uploads:/app/uploads` - File uploads
- `./logs:/app/logs` - Application logs

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/cocomo` | GET | COCOMO II parameter form |
| `/estimate` | POST | Text-based estimation |
| `/estimate-cocomo` | POST | COCOMO II parameter estimation |
| `/upload-requirements` | POST | File upload estimation |
| `/analyze` | POST | Requirements analysis |

## 📊 Usage Examples

### 1. COCOMO II Estimation

```bash
curl -X POST http://localhost:8000/estimate-cocomo \
  -H "Content-Type: application/json" \
  -d '{
    "software_size": 50.0,
    "cost_per_person_month": 8000,
    "method": "weighted_average",
    "precedentedness": "nominal",
    "development_flexibility": "high",
    "product_complexity": "high"
  }'
```

### 2. File Upload Estimation

```bash
curl -X POST http://localhost:8000/upload-requirements \
  -F "file=@requirements.pdf" \
  -F "method=weighted_average"
```

### 3. Text Analysis

```bash
curl -X POST http://localhost:8000/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Develop a web application with user authentication, database integration, and reporting features.",
    "method": "weighted_average"
  }'
```

## 🔍 Monitoring and Debugging

### View Real-time Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-estimation-app

# Nginx logs (if using production mode)
docker-compose logs -f nginx
```

### Health Checks
```bash
# Quick health check
curl http://localhost:8000/

# Detailed system check
./manage.sh health

# Container status
docker-compose ps
```

### Performance Monitoring
```bash
# Resource usage
docker stats

# Container inspection
docker-compose exec ai-estimation-app htop
```

## 🛡 Security Considerations

- Service runs as non-root user (`appuser`)
- File upload size limits configured
- CORS properly configured for production
- Nginx security headers (in production mode)
- Regular security updates via base image updates

## 🔄 Updates and Maintenance

### Update the Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
./manage.sh build
./manage.sh restart
```

### Backup Strategy
```bash
# Regular backup
./manage.sh backup

# Automated backup (add to crontab)
0 2 * * * cd /path/to/AI-Project && ./manage.sh backup
```

### Model Updates
```bash
# Stop service
./manage.sh stop

# Update models in ./models directory
# Copy new model files...

# Restart service
./manage.sh start
```

## 🚨 Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs
./manage.sh logs

# Verify Docker installation
docker --version
docker-compose --version

# Check port availability
netstat -tulpn | grep :8000
```

**High memory usage:**
```bash
# Monitor resources
docker stats

# Restart service
./manage.sh restart
```

**Model loading errors:**
```bash
# Check model files
ls -la models/

# Verify file permissions
chmod -R 755 models/
```

### Support

For issues and support:
1. Check logs: `./manage.sh logs`
2. Run health check: `./manage.sh health`
3. Review container status: `docker-compose ps`
4. Check system resources: `docker stats`

## 📝 License

This project is licensed under the MIT License.

---

**🎉 Ready to estimate software effort with AI precision!**
