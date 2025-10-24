#!/bin/bash

# Script to push current code to GitHub
# For user: Huy-VNNIC
# Email: nguyennhathuy11@dtu.edu.vn
# Repository: https://github.com/Huy-VNNIC/AI-Project.git

# Exit on any error
set -e

echo "Setting up Git configuration..."
git config --global user.name "Huy-VNNIC"
git config --global user.email "nguyennhathuy11@dtu.edu.vn"

echo "Current working directory: $(pwd)"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git remote add origin https://github.com/Huy-VNNIC/AI-Project.git
else
    echo "Git repository already exists."
    # Check if origin remote exists
    if ! git remote | grep -q "^origin$"; then
        echo "Adding origin remote..."
        git remote add origin https://github.com/Huy-VNNIC/AI-Project.git
    else
        echo "Origin remote already exists. Updating URL..."
        git remote set-url origin https://github.com/Huy-VNNIC/AI-Project.git
    fi
fi

# Make sure we're on main branch
if ! git rev-parse --verify main > /dev/null 2>&1; then
    echo "Creating main branch..."
    git checkout -b main
else
    echo "Switching to main branch..."
    git checkout main
fi

# Add all files
echo "Adding all files to Git..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "Update features methodology and scoring algorithm"


# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo "Done! Code has been pushed to https://github.com/Huy-VNNIC/AI-Project.git"
