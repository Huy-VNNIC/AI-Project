"""
Tệp chạy chính cho service phân tích yêu cầu và ước lượng nỗ lực
"""

import os
import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

# Import API module
from requirement_analyzer.api import start_server

if __name__ == "__main__":
    # Hiển thị thông tin
    print("="*80)
    print("Software Effort Estimation Service")
    print("="*80)
    print(f"Project root: {PROJECT_ROOT}")
    print("Starting service...")
    
    # Khởi động server
    start_server(host="0.0.0.0", port=8001)
