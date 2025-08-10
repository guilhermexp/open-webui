#!/bin/bash

echo "Starting Open WebUI Application..."

# Kill any existing processes on ports 8082 and 5173
echo "Cleaning up existing processes..."
pkill -f "uvicorn.*8082" 2>/dev/null
pkill -f "vite.*5173" 2>/dev/null
sleep 2

# Start backend
echo "Starting backend server on port 8082..."
cd /Users/guilhermevarela/Documents/Repositorios/open-webui/backend
./dev.sh &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start frontend
echo "Starting frontend server on port 5173..."
cd /Users/guilhermevarela/Documents/Repositorios/open-webui

# Setup Node environment
unset npm_config_prefix
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 22

# Install dependencies if needed
if [ ! -d "node_modules/@sveltejs/kit" ]; then
    echo "Installing dependencies..."
    npm install --legacy-peer-deps
fi

# Run pyodide fetch
npm run pyodide:fetch

# Start frontend
npm run dev:frontend &
FRONTEND_PID=$!

echo ""
echo "======================================="
echo "Open WebUI is starting..."
echo "Backend: http://localhost:8082"
echo "Frontend: http://localhost:5173"
echo "======================================="
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID