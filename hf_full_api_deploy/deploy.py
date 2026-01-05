"""Deploy full API to Hugging Face Spaces"""

import os
from huggingface_hub import HfApi

def deploy_full_api():
    """Deploy the complete API to Hugging Face Spaces"""
    
    # HF token from environment variable
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN environment variable is not set. Please set it with your Hugging Face token.")
    
    # Initialize API
    api = HfApi(token=token)
    
    repo_id = "nhathuyyne/software-effort-estimation-api"
    
    print("🚀 Deploying Full API to Hugging Face Spaces...")
    
    try:
        # Create the repository if it doesn't exist
        try:
            api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="gradio")
            print("✅ Repository created")
        except Exception as e:
            print(f"ℹ️ Repository already exists: {e}")
        
        # Upload essential files only (exclude deployment script)
        essential_files = [
            "app.py",
            "requirements.txt", 
            "README.md"
        ]
        
        for file_name in essential_files:
            print(f"📤 Uploading {file_name}...")
            api.upload_file(
                path_or_fileobj=file_name,
                path_in_repo=file_name,
                repo_id=repo_id,
                repo_type="space",
                commit_message=f"Update {file_name}"
            )
        
        # Upload the entire requirement_analyzer folder
        print("📤 Uploading requirement_analyzer...")
        api.upload_folder(
            folder_path="requirement_analyzer",
            path_in_repo="requirement_analyzer",
            repo_id=repo_id,
            repo_type="space",
            commit_message="Upload requirement analyzer modules"
        )
        
        print(f"✅ Full API deployed to: https://huggingface.co/spaces/{repo_id}")
        print("🎯 Available endpoints: /estimate, /upload-requirements, /estimate-from-tasks, /estimate-cocomo")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    deploy_full_api()