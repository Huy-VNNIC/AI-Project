"""Deploy full API system to Hugging Face Spaces"""

import os
from huggingface_hub import HfApi

def deploy_to_hf_spaces():
    """Deploy the complete API system to Hugging Face Spaces"""
    
    # Get token from environment variable
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN environment variable is not set. Please set it with your Hugging Face token.")
    
    # Initialize API
    api = HfApi(token=token)
    
    # Repository for deployment (using personal namespace)
    repo_id = "nhathuyyne/software-effort-estimation-full-api"
    
    print("🚀 Deploying Full API System to Hugging Face Spaces...")
    
    try:
        # Create the repository if it doesn't exist
        try:
            api.create_repo(
                repo_id=repo_id, 
                repo_type="space", 
                space_sdk="docker",
                private=False
            )
            print("✅ Repository created")
        except Exception as e:
            print(f"ℹ️ Repository might already exist: {e}")
        
        # Upload all files except this script
        print("📁 Uploading application files...")
        
        # Upload main files
        files_to_upload = [
            "app.py", 
            "requirements.txt", 
            "README.md",
            "Dockerfile",
            "API_DOCUMENTATION.md"
        ]
        
        for file_name in files_to_upload:
            if os.path.exists(file_name):
                print(f"   📄 Uploading {file_name}...")
                api.upload_file(
                    path_or_fileobj=file_name,
                    path_in_repo=file_name,
                    repo_id=repo_id,
                    repo_type="space",
                    commit_message=f"Upload {file_name}"
                )
        
        # Upload the requirement_analyzer folder
        print("   📂 Uploading requirement_analyzer...")
        api.upload_folder(
            folder_path="requirement_analyzer",
            path_in_repo="requirement_analyzer",
            repo_id=repo_id,
            repo_type="space",
            commit_message="Upload requirement_analyzer module"
        )
        
        # Upload models folder if it exists (skip for now due to size)
        # if os.path.exists("models"):
        #     print("   🤖 Uploading models...")
        #     api.upload_folder(
        #         folder_path="models",
        #         path_in_repo="models", 
        #         repo_id=repo_id,
        #         repo_type="space",
        #         commit_message="Upload models directory"
        #     )
        
        print(f"✅ Successfully deployed to: https://huggingface.co/spaces/{repo_id}")
        print("📚 API Documentation: https://huggingface.co/spaces/{}/blob/main/API_DOCUMENTATION.md".format(repo_id))
        print("🔗 Interactive API Docs will be available at: https://{}.hf.space/docs".format(repo_id.replace("/", "-")))
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        print("💡 Make sure your token has write permissions to the repository")

if __name__ == "__main__":
    deploy_to_hf_spaces()