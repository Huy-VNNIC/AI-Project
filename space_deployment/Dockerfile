FROM python:3.9-slim

WORKDIR /app

# Tạo người dùng không phải root để chạy ứng dụng
RUN useradd -m -u 1000 appuser

# Cài đặt các công cụ cần thiết và phần mềm để hỗ trợ các định dạng tài liệu
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục cho NLTK data và cấp quyền
RUN mkdir -p /home/appuser/nltk_data && \
    chown -R appuser:appuser /home/appuser/

# Sao chép các file yêu cầu trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các phụ thuộc
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép code và script sửa lỗi
COPY app/ /app/app/
COPY static/ /app/static/
COPY templates/ /app/templates/
COPY patch_analyzer.py /app/

# Đảm bảo requirement_analyzer module được sao chép đúng
RUN if [ -d "/app/app/requirement_analyzer" ]; then \
        cp -r /app/app/requirement_analyzer /app/ ; \
    fi

# Sao chép script kiểm tra NLTK
COPY check_nltk.py /app/

# Chạy script sửa lỗi analyzer.py
RUN python /app/patch_analyzer.py

# Thiết lập các biến môi trường
ENV PORT=7860
ENV PYTHONPATH=/app
ENV MODEL_DIR=/app/app/models
ENV NLTK_DATA=/home/appuser/nltk_data
ENV MPLCONFIGDIR=/home/appuser/.config/matplotlib

# Sao chép packages.py và app.py
COPY packages.py app.py /app/

# Cài đặt mô hình spaCy và tải các gói NLTK
RUN pip install spacy && python -m spacy download en_core_web_sm

# Tạo thư mục Matplotlib
RUN mkdir -p /home/appuser/.config/matplotlib && chown -R appuser:appuser /home/appuser/.config

# Cài đặt sẵn các gói NLTK và lưu vào /home/appuser/nltk_data
RUN python -c "import nltk; nltk.download('punkt', download_dir='/home/appuser/nltk_data'); \
    nltk.download('stopwords', download_dir='/home/appuser/nltk_data'); \
    nltk.download('wordnet', download_dir='/home/appuser/nltk_data'); \
    nltk.download('averaged_perceptron_tagger', download_dir='/home/appuser/nltk_data'); \
    nltk.download('omw-1.4', download_dir='/home/appuser/nltk_data'); \
    nltk.download('vader_lexicon', download_dir='/home/appuser/nltk_data'); \
    nltk.download('maxent_ne_chunker', download_dir='/home/appuser/nltk_data'); \
    nltk.download('words', download_dir='/home/appuser/nltk_data');"

# Sửa quyền sở hữu trước khi chuyển đổi người dùng
RUN chown -R appuser:appuser /app

# Chuyển sang người dùng không phải root
USER appuser

# Thiết lập biến môi trường người dùng
ENV HOME=/home/appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Kiểm tra ứng dụng
HEALTHCHECK CMD curl --fail http://localhost:$PORT/health || exit 1

# Mở cổng 7860 (mặc định của Hugging Face)
EXPOSE 7860

# Khởi chạy ứng dụng với kiểm tra NLTK trước
CMD python check_nltk.py && python app.py