#!/bin/bash

echo "Starting Open WebUI Frontend..."

# Setup Node environment
unset npm_config_prefix
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 22

# Go to project root
cd /Users/guilhermevarela/Documents/Repositorios/open-webui

# Install dependencies if needed
if [ ! -d "node_modules/@sveltejs/kit" ]; then
    echo "Installing dependencies..."
    npm install --legacy-peer-deps
fi

# Start frontend dev server
echo "Starting frontend server on http://localhost:5173"
npm run dev:frontend