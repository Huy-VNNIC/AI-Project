#!/bin/bash
# Script to initialize Git repository and prepare for GitHub

# Initialize Git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
else
    echo "Git repository already initialized."
fi

# Create .gitignore file
echo "Creating .gitignore file..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
venv_new/
ENV/

# Logs
*.log
logs/

# Jupyter Notebook
.ipynb_checkpoints

# VS Code
.vscode/

# PyCharm
.idea/

# OS specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Large files and datasets
*.csv
*.arff
!requirements.txt
!comparison_metrics.csv
!comparison_results.csv

# Temporary files
*.tmp
*.bak
*.swp
EOF

# Add files to git
echo "Adding files to Git..."
git add .

# Instructions for GitHub
echo "
---------------------------------------------------------
GitHub Repository Setup Instructions:

1. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Enter a repository name (e.g., 'software-effort-estimation')
   - Add a description: 'Requirement Analysis and Effort Estimation System'
   - Choose public or private visibility
   - Click 'Create repository'

2. Link your local repository to GitHub:
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

3. Commit your changes:
   git commit -m 'Initial commit: Requirement Analyzer and Effort Estimation System'

4. Push to GitHub:
   git push -u origin main (or master, depending on your default branch)

Note: Make sure you have a GitHub account and are logged in.
---------------------------------------------------------
"

# Make the script executable
chmod +x setup_github.sh

echo "GitHub setup script created and executed successfully!"
