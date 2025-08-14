#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    # Use Python 3.11 for compatibility
    if command -v python3.11 &> /dev/null; then
        python3.11 -m venv venv
    else
        python3 -m venv venv
    fi
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

export CORS_ALLOW_ORIGIN=http://localhost:4173
export PYTHONPATH="${PYTHONPATH}:/Users/guilhermevarela/Documents/Repositorios/open-webui/backend"
export ENABLE_WEB_SEARCH=true
export WEBUI_AUTH=True
PORT="${PORT:-8888}"
python -m uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
