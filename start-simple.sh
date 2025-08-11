#!/bin/bash

# Script SIMPLES para iniciar Open WebUI
# Apenas frontend + backend, sem complicações

echo "🚀 Iniciando Open WebUI (Versão Simples)"
echo "========================================="

# Parar ao primeiro erro
set -e

# Função para limpar ao sair
cleanup() {
    echo -e "\n🛑 Parando serviços..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup EXIT INT TERM

# 1. BACKEND
echo "1️⃣  Iniciando Backend..."
cd backend
export CORS_ALLOW_ORIGIN="http://localhost:5175,http://localhost:5173,http://localhost:5177"
# Usar ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 -m uvicorn open_webui.main:app --port 8082 --host 0.0.0.0 --reload &
BACKEND_PID=$!
cd ..

# Esperar backend iniciar
echo "   Aguardando backend..."
sleep 5

# 2. FRONTEND
echo "2️⃣  Iniciando Frontend..."
npm run dev &
FRONTEND_PID=$!

# Esperar frontend iniciar
echo "   Aguardando frontend..."
sleep 8

# 3. MOSTRAR URLs
echo ""
echo "✅ PRONTO! Acesse:"
echo "===================="
echo "🌐 Frontend: http://localhost:5173 (ou 5175/5177 se a porta estiver em uso)"
echo "📡 Backend API: http://localhost:8082"
echo "📚 API Docs: http://localhost:8082/docs"
echo ""
echo "🔧 Para acessar MCP:"
echo "1. Faça login em http://localhost:5173"
echo "2. Vá para Admin > Settings > MCP"
echo ""
echo "💡 Pressione Ctrl+C para parar"
echo ""

# Manter rodando
wait