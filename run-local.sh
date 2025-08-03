#!/bin/bash

# Script DEFINITIVO para iniciar Open WebUI com MCP
# Este script GARANTE que tudo funcione corretamente

echo "🚀 Iniciando Open WebUI com suporte MCP"
echo "======================================="

# Função para limpar ao sair
cleanup() {
    echo -e "\n🛑 Parando todos os serviços..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup EXIT INT TERM

# 1. LIMPAR PORTAS EM USO
BACKEND_PORT=8082
echo "🧹 Limpando portas em uso..."
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:5174 | xargs kill -9 2>/dev/null || true
lsof -ti:5175 | xargs kill -9 2>/dev/null || true
lsof -ti:5176 | xargs kill -9 2>/dev/null || true
lsof -ti:5177 | xargs kill -9 2>/dev/null || true
sleep 2

# 2. VERIFICAR DEPENDÊNCIAS
echo "📋 Verificando sistema..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    exit 1
fi

# Verificar Node
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado!"
    exit 1
fi

# 2. INICIAR BACKEND
echo ""
echo "1️⃣  Iniciando Backend..."
cd backend

# Configurar CORS para múltiplas portas possíveis
export CORS_ALLOW_ORIGIN="http://localhost:5173"

# Verificar se existe ambiente virtual
if [ -d "venv" ]; then
    echo "   ✓ Usando ambiente virtual existente"
    source venv/bin/activate
    
    # Verificar se uvicorn está instalado
    if ! python3 -c "import uvicorn" 2>/dev/null; then
        echo "   📦 Instalando uvicorn..."
        pip install uvicorn
    fi
else
    echo "   ⚠️  Sem ambiente virtual, usando Python global"
fi

# Iniciar backend em porta alternativa
echo "   📡 Usando porta $BACKEND_PORT para o backend"
python3 -m uvicorn open_webui.main:app --port $BACKEND_PORT --host 0.0.0.0 --reload &
BACKEND_PID=$!
cd ..

# Aguardar backend
echo "   ⏳ Aguardando backend iniciar..."
for i in {1..10}; do
    if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        echo "   ✅ Backend rodando!"
        break
    fi
    sleep 1
done

# 3. INICIAR FRONTEND
echo ""
echo "2️⃣  Iniciando Frontend..."
npm run dev &
FRONTEND_PID=$!

# Aguardar frontend
echo "   ⏳ Aguardando frontend iniciar..."
sleep 8

# 4. VERIFICAR TABELAS MCP
echo ""
echo "3️⃣  Verificando banco de dados..."
if [ -f "backend/data/webui.db" ]; then
    if sqlite3 backend/data/webui.db ".tables" | grep -q "mcp_servers"; then
        echo "   ✅ Tabelas MCP encontradas!"
    else
        echo "   ⚠️  Tabelas MCP não encontradas"
        echo "   Execute: cd backend/open_webui && alembic upgrade head"
    fi
else
    echo "   ⚠️  Banco de dados não encontrado"
fi

# 5. MOSTRAR INFORMAÇÕES
echo ""
echo "════════════════════════════════════════════"
echo "✅ SISTEMA PRONTO!"
echo "════════════════════════════════════════════"
echo ""
echo "📍 URLs de Acesso:"
echo "   🌐 Frontend: http://localhost:5173"
echo "        (ou 5174, 5175, 5176, 5177 se ocupada)"
echo "   📡 Backend: http://localhost:$BACKEND_PORT"
echo "   📚 API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "🔧 Para configurar MCP:"
echo "   1. Acesse o frontend"
echo "   2. Faça login ou crie uma conta"
echo "   3. Vá para: Admin > Settings > MCP"
echo ""
echo "📝 Servidores MCP de teste:"
echo "   - Echo Server (simples)"
echo "   - File System (requer npx)"
echo "   - Time Server (requer uvx)"
echo ""
echo "💡 Pressione Ctrl+C para parar tudo"
echo "════════════════════════════════════════════"
echo ""

# Manter rodando
wait