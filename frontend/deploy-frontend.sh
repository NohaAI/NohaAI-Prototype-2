#!/bin/bash
#
## Default branch name
DEFAULT_BRANCH="main"

# Check if branch name is provided
if [ -z "$1" ]; then
  echo "Branch name not provided. Default branch '$DEFAULT_BRANCH' will be deployed. Are you sure? (y/Y to proceed)"
  read -r CONFIRM
  if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo -e "❌ Deployment aborted."
    exit 1
  fi
  BRANCH_NAME=$DEFAULT_BRANCH
else
  BRANCH_NAME=$1
fi

echo "ℹ️ Fetching latest changes from remote..."
git fetch && echo -e "✅ Fetch successful" || echo -e "❌ Fetch failed"

echo "ℹ️ Switching to branch: $BRANCH_NAME"
git checkout $BRANCH_NAME && echo -e "✅ Switched to $BRANCH_NAME" || echo -e "❌ Failed to switch branch"

echo "ℹ️ Pulling latest code from branch: $BRANCH_NAME"
git pull origin $BRANCH_NAME && echo -e "✅ Code pulled successfully" || echo -e "❌ Failed to pull code"
echo "ℹ️ Stopping all PM2 processes..."
pm2 stop all && echo -e "✅ PM2 stopped" || echo -e "❌ Failed to stop PM2"


echo "ℹ️ Installing dependencies..."
npm install && echo -e "✅ Dependencies installed" || echo -e "❌ Failed to install dependencies"

echo "ℹ️ Building the project..."
npm run build && echo -e "✅ Build successful" || echo -e "❌ Build failed"

echo "ℹ️ Restarting all PM2 processes..."
pm2 restart all && echo -e "✅ PM2 restarted" || echo -e "❌ Failed to restart PM2"
echo "ℹ️ Checking PM2 status..."
pm2 status && echo -e "✅ PM2 status displayed" || echo -e "❌ Failed to display PM2 status"

echo -e "✅ Deployment complete!"
