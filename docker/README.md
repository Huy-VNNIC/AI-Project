# Docker Directory

Thư mục này chứa tất cả các file liên quan đến Docker configuration và deployment.

## Danh sách Files

### Dockerfiles
- `Dockerfile` - Docker image chính cho dự án
- `Dockerfile.api` - Docker image cho API service
- `Dockerfile.production` - Docker image cho production deployment
- `Dockerfile.api-production` - Docker image cho API production

### Docker Compose Files
- `docker-compose.yml` - Docker compose configuration chính
- `docker-compose.api.yml` - Docker compose cho API service
- `docker-compose.production.yml` - Docker compose cho production

### Configuration Files
- `.dockerignore` - Các file/folder được ignore khi build Docker image
- `nginx.conf` - Nginx configuration cho reverse proxy

## Sử dụng

### Build Docker Image
```bash
docker build -f docker/Dockerfile -t ai-project .
```

### Chạy với Docker Compose
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Production Deployment
```bash
docker-compose -f docker/docker-compose.production.yml up -d
```

## Lưu ý

- Đảm bảo đã cài đặt Docker và Docker Compose
- Kiểm tra file `.env` trước khi deploy
- Xem thêm chi tiết trong [DOCKER_README.md](../docs/DOCKER_README.md)
