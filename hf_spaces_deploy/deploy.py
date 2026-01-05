#!/usr/bin/env python3
"""
Deploy Software Effort Estimation API to Hugging Face Spaces
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder
import shutil

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN")  # Get token from environment variable
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set. Please set it with your Hugging Face token.")
REPO_NAME = "software-effort-estimation-api"
REPO_TYPE = "space"
SPACE_SDK = "gradio"

def deploy_to_hugging_face():
    """Deploy the application to Hugging Face Spaces"""
    
    # Initialize HF API
    api = HfApi(token=HF_TOKEN)
    
    # Current directory (hf_spaces_deploy)
    deploy_dir = Path(__file__).parent
    
    print(f"📁 Deploying from directory: {deploy_dir}")
    
    try:
        # Create repository if it doesn't exist
        print(f"🚀 Creating/updating repository: {REPO_NAME}")
        
        repo_url = create_repo(
            repo_id=REPO_NAME,
            repo_type=REPO_TYPE,
            space_sdk=SPACE_SDK,
            token=HF_TOKEN,
            exist_ok=True,  # Don't fail if repo already exists
            private=False
        )
        
        print(f"✅ Repository URL: {repo_url}")
        
        # Upload the entire folder
        print("📤 Uploading files...")
        
        api.upload_folder(
            folder_path=str(deploy_dir),
            repo_id=REPO_NAME,
            repo_type=REPO_TYPE,
            token=HF_TOKEN,
            commit_message="Deploy Software Effort Estimation API with priority analysis and COCOMO form",
            ignore_patterns=[
                "*.pyc",
                "__pycache__/*",
                ".git/*",
                "*.log",
                ".DS_Store",
                "deploy.py"  # Don't upload this script itself
            ]
        )
        
        print("🎉 Deployment successful!")
        print(f"🔗 Your Space will be available at: https://huggingface.co/spaces/{api.whoami(token=HF_TOKEN)['name']}/{REPO_NAME}")
        print("\n📋 Next steps:")
        print("1. Wait for the Space to build (2-5 minutes)")
        print("2. Visit your Space URL to test the interface")
        print("3. The API endpoints will be available for programmatic access")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

def check_deployment_files():
    """Check if all required files are present"""
    
    deploy_dir = Path(__file__).parent
    required_files = [
        "app.py",
        "requirements.txt", 
        "README.md",
        "requirement_analyzer/__init__.py",
        "requirement_analyzer/api.py",
        "requirement_analyzer/analyzer.py",
        "requirement_analyzer/estimator.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (deploy_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
        
    print("✅ All required files are present")
    return True

if __name__ == "__main__":
    print("🚀 Software Effort Estimation API - Hugging Face Deployment")
    print("=" * 60)
    
    # Check files
    if not check_deployment_files():
        sys.exit(1)
    
    # Deploy
    if deploy_to_hugging_face():
        print("\n🎉 Deployment completed successfully!")
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)