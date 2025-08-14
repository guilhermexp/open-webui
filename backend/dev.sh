#!/bin/bash

# NOTES APP PROTECTION CHECK
if [ ! -f "../.notes-app-only" ]; then
    echo "❌ ERRO: Esta aplicação deve funcionar APENAS como Notes App"
    echo "❌ Arquivo de proteção não encontrado"
    exit 1
fi

echo "✅ Proteção Notes App ativa - iniciando backend..."

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
export GLOBAL_LOG_LEVEL=WARNING
PORT="${PORT:-5001}"
python -m uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
