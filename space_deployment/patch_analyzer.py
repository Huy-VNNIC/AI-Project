"""
Patch for requirement_analyzer's analyzer.py to prevent permission errors
"""
import os
import sys

def patch_analyzer():
    """
    Create a patched version of analyzer.py that doesn't try to download NLTK data
    if the file exists
    """
    analyzer_path = "/app/app/requirement_analyzer/analyzer.py"
    backup_path = "/app/app/requirement_analyzer/analyzer.py.bak"
    
    if os.path.exists(analyzer_path):
        # Create backup
        os.system(f"cp {analyzer_path} {backup_path}")
        
        with open(analyzer_path, 'r') as file:
            content = file.read()
        
        # Replace problematic lines that try to download NLTK data
        if "nltk.download('punkt')" in content:
            modified = content.replace(
                "nltk.download('punkt')",
                "print('NLTK punkt package should be pre-installed. Check NLTK_DATA environment variable.')"
            )
            
            with open(analyzer_path, 'w') as file:
                file.write(modified)
            
            print("Successfully patched analyzer.py to prevent NLTK download attempts")
        else:
            print("No need to patch analyzer.py")
    else:
        print(f"analyzer.py not found at {analyzer_path}")

if __name__ == "__main__":
    patch_analyzer()