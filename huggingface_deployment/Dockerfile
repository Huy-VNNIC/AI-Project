FROM python:3.9-slim

WORKDIR /app

# Cài đặt các công cụ cần thiết và phần mềm để hỗ trợ các định dạng tài liệu
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Sao chép các file yêu cầu trước để tận dụng cache của Docker
COPY huggingface_deployment/requirements.txt .

# Cài đặt các phụ thuộc
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép code của project
COPY requirement_analyzer/ /app/requirement_analyzer/
COPY huggingface_deployment/ /app/
COPY models/ /app/app/models/

# Tạo thư mục static và templates nếu chưa tồn tại
RUN mkdir -p /app/static /app/templates

# Thiết lập các biến môi trường
ENV PORT=7860
ENV PYTHONPATH=/app
ENV MODEL_DIR=/app/app/models

# Tải các gói NLTK cần thiết
RUN python /app/packages.py

# Kiểm tra ứng dụng
HEALTHCHECK CMD curl --fail http://localhost:$PORT/health || exit 1

# Mở cổng 7860 (mặc định của Hugging Face)
EXPOSE 7860

# Khởi chạy ứng dụng
CMD ["python", "app.py"]