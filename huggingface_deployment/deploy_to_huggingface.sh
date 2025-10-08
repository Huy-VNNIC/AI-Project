#!/bin/bash

# Script triển khai lên Hugging Face Spaces
# Đảm bảo đã đăng nhập vào Hugging Face CLI và Docker trước khi chạy script

set -e

# Các biến cấu hình
HUGGINGFACE_USERNAME="nhathuyvne"  # Điền username Hugging Face của bạn
SPACE_NAME="requirement-analyzer-api"  # Tên không gian trên Hugging Face
SPACE_TYPE="docker"  # Loại không gian (docker hoặc space)

# Kiểm tra các biến cần thiết
if [ -z "$HUGGINGFACE_USERNAME" ]; then
  echo "ERROR: Vui lòng cung cấp username Hugging Face của bạn trong script"
  exit 1
fi

# Kiểm tra CLI Hugging Face
if ! command -v huggingface-cli &> /dev/null; then
  echo "Installing Hugging Face CLI..."
  pip install huggingface_hub
fi

# Đường dẫn đầy đủ đến thư mục làm việc
PROJECT_ROOT=$(pwd)
DEPLOYMENT_DIR="$PROJECT_ROOT/huggingface_deployment"

# Đảm bảo chúng ta ở thư mục gốc của dự án
cd "$PROJECT_ROOT"

echo "=== Preparing for deployment ==="
echo "Building Docker image locally for testing..."

# Tạo file README.md cho Hugging Face Space
cat > "$DEPLOYMENT_DIR/README.md" << EOL
---
title: Software Requirement Analyzer API
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Software Requirement Analyzer API

This API provides endpoints for analyzing software requirements and estimating development effort based on requirement specifications.

## API Endpoints

### POST /api/estimate
Estimate development effort based on requirement text.

Example:
\`\`\`bash
curl -X POST "https://your-domain/api/estimate" \\
     -H "Content-Type: application/json" \\
     -d '{"text": "Develop hospital management system", "method": "weighted_average"}'
\`\`\`

### POST /api/upload-requirements
Upload a requirements document file for analysis.

Supported file types:
- .txt, .md: Plain text files
- .pdf: PDF documents
- .doc, .docx: Microsoft Word documents

### GET /health
Check API status

## Online Demo
Visit the API documentation at: https://$HUGGINGFACE_USERNAME-$SPACE_NAME.hf.space/docs
EOL

# Tạo ra một docker-compose.yml phục vụ cho Hugging Face
cat > "$DEPLOYMENT_DIR/docker-compose.yml" << EOL
version: '3'
services:
  app:
    build:
      context: ..
      dockerfile: huggingface_deployment/Dockerfile
    ports:
      - "7860:7860"
    environment:
      - PORT=7860
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:7860/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOL

# Test build Docker image locally
echo "Building Docker image locally..."
docker build -t requirement-analyzer-api -f "$DEPLOYMENT_DIR/Dockerfile" .

# Kiểm tra nếu hình ảnh đã được xây dựng thành công
if [ $? -ne 0 ]; then
  echo "ERROR: Docker build failed. Please fix any issues before deploying."
  exit 1
fi

echo "=== Deployment to Hugging Face ==="
echo "This will deploy the API to: https://$HUGGINGFACE_USERNAME-$SPACE_NAME.hf.space"
read -p "Continue with deployment? (y/n): " confirm

if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
  echo "Deployment canceled."
  exit 0
fi

# Kiểm tra nếu không gian đã tồn tại
huggingface-cli space info $HUGGINGFACE_USERNAME/$SPACE_NAME &> /dev/null
SPACE_EXISTS=$?

if [ $SPACE_EXISTS -eq 0 ]; then
  echo "Updating existing Hugging Face Space..."
  huggingface-cli space upload "$DEPLOYMENT_DIR" $HUGGINGFACE_USERNAME/$SPACE_NAME --path-in-space="/" --repo-type="space"
else
  echo "Creating new Hugging Face Space..."
  huggingface-cli space create $HUGGINGFACE_USERNAME/$SPACE_NAME --type=$SPACE_TYPE --sdk=docker
  sleep 5  # Đợi không gian được tạo
  huggingface-cli space upload "$DEPLOYMENT_DIR" $HUGGINGFACE_USERNAME/$SPACE_NAME --path-in-space="/" --repo-type="space"
fi

echo "=== Deployment Complete ==="
echo "Your API should be available at: https://$HUGGINGFACE_USERNAME-$SPACE_NAME.hf.space"
echo "API documentation available at: https://$HUGGINGFACE_USERNAME-$SPACE_NAME.hf.space/docs"
echo ""
echo "Note: It may take a few minutes for the Docker container to build and start on Hugging Face."