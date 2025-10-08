#!/usr/bin/env python3

import os
import sys
from huggingface_hub import create_repo, HfApi

# Set your Hugging Face username and space name
username = "nhathuyvne"
space_name = "requirement-analyzer-api"
space_type = "docker"

print("=== Creating Hugging Face Space ===")
print(f"Username: {username}")
print(f"Space name: {space_name}")
print(f"Space type: {space_type}")

try:
    # Attempt to create the space
    repo_id = f"{username}/{space_name}"
    create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker")
    print(f"✅ Successfully created space: {repo_id}")
    print(f"Your space will be available at: https://{username}-{space_name}.hf.space")
    
    # Get the current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Create HfApi instance
    api = HfApi()
    
    # Upload files to the space
    print("Uploading files to the space...")
    api.upload_folder(
        folder_path=current_dir,
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["__pycache__", ".git", ".gitignore", "create_space.py"]
    )
    print("✅ Files uploaded successfully!")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)