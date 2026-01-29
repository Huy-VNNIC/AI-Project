#!/usr/bin/env python3

import os
from huggingface_hub import HfApi

# Khởi tạo API client
api = HfApi()

# Thông tin không gian
username = "nhathuyyne"
space_name = "requirement-analyzer-api"
repo_id = f"{username}/{space_name}"

# Đường dẫn đến thư mục chứa các file cần tải lên
space_dir = "/workspaces/AI-Project/space_deployment"

# Tải lên các file
print(f"Đang tải lên các file từ {space_dir} đến {repo_id}...")
api.upload_folder(
    folder_path=space_dir,
    repo_id=repo_id,
    repo_type="space",
    ignore_patterns=["__pycache__", ".*"]
)

print("✅ Tải lên thành công!")
print(f"Space của bạn sẽ có sẵn tại: https://{username}-{space_name}.hf.space")
print(f"Tài liệu API có sẵn tại: https://{username}-{space_name}.hf.space/docs")
print("Lưu ý: Có thể mất vài phút để container Docker được xây dựng và khởi động.")