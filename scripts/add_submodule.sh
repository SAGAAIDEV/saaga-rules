#!/bin/bash

# Check if a repository URL is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <repository_url>"
  exit 1
fi

REPO_URL=$1
# Extract the repository name from the URL
# e.g., https://github.com/SAGAAIDEV/mcp-atlassian.git -> mcp-atlassian
REPO_NAME=$(basename "$REPO_URL" .git)

# Add the submodule
git submodule add "$REPO_URL" "$REPO_NAME"

echo "Submodule $REPO_NAME added from $REPO_URL"