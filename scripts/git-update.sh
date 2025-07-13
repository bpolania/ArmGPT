#!/bin/bash

# Git update script - add, commit, and push changes
echo "🔄 Adding all changes to git..."
git add .

echo "📝 Committing changes..."
git commit -m "updated logs"

echo "📤 Pushing to remote repository..."
git push

echo "✅ Git update completed!"