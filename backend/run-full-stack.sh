#!/bin/bash

# Kill existing processes
pkill -f "uvicorn open_webui.main:app" 2>/dev/null
pkill -f "vite dev" 2>/dev/null
sleep 1

# Find port
BACKEND_PORT=8082
echo "Using backend port: $BACKEND_PORT"

# Write env file
cat > ../.env << EOF
BACKEND_PORT=$BACKEND_PORT
VITE_API_BASE_URL=http://localhost:$BACKEND_PORT
EOF

# Start backend
echo "Starting backend..."
BACKEND_PORT=$BACKEND_PORT ./dev.sh &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Start frontend from parent directory
echo "Starting frontend..."
cd .. && BACKEND_PORT=$BACKEND_PORT npm run dev:frontend

# Cleanup
kill $BACKEND_PID 2>/dev/null