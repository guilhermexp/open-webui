#!/bin/bash

# Script para executar Open WebUI em portas aleatórias
set -e

# Função para gerar porta aleatória não ocupada
generate_random_port() {
    local port
    while true; do
        port=$(( RANDOM % 55535 + 10000 ))  # Portas entre 10000 e 65535
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo $port
            break
        fi
    done
}

# Gerar portas aleatórias
BACKEND_PORT=$(generate_random_port)
FRONTEND_PORT=$(generate_random_port)

# Garantir que as portas são diferentes
while [ "$BACKEND_PORT" = "$FRONTEND_PORT" ]; do
    FRONTEND_PORT=$(generate_random_port)
done

echo "🚀 Iniciando Open WebUI com portas aleatórias:"
echo "📡 Backend (API): http://localhost:$BACKEND_PORT"
echo "🌐 Frontend (UI): http://localhost:$FRONTEND_PORT"
echo ""

# Função para cleanup no final
cleanup() {
    echo ""
    echo "🛑 Encerrando serviços..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait
    echo "✅ Serviços encerrados"
}

# Configurar trap para cleanup
trap cleanup EXIT INT TERM

# Verificar se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python3 para continuar."
    exit 1
fi

# Verificar se o Node.js está disponível
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale o Node.js para continuar."
    exit 1
fi

# Verificar se o npm está disponível
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Instale o npm para continuar."
    exit 1
fi

echo "📦 Instalando dependências do frontend (ignorando versão do engine)..."
npm config set ignore-engines true
npm install --legacy-peer-deps
npm config delete ignore-engines

echo "📦 Verificando dependências do backend..."
cd backend
if [ ! -d ".venv" ]; then
    echo "🐍 Criando ambiente virtual Python..."
    python3 -m venv .venv
fi

echo "🔌 Ativando ambiente virtual..."
source .venv/bin/activate

echo "📦 Instalando dependências do Python..."
pip install -r requirements.txt

cd ..

echo ""
echo "🏁 Iniciando serviços..."

# Iniciar backend
echo "🔧 Iniciando backend na porta $BACKEND_PORT..."
cd backend
export CORS_ALLOW_ORIGIN="http://localhost:$FRONTEND_PORT"
export PORT="$BACKEND_PORT"
source .venv/bin/activate
uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload &
BACKEND_PID=$!
cd ..

# Aguardar um pouco para o backend inicializar
sleep 3

# Iniciar frontend
echo "🎨 Iniciando frontend na porta $FRONTEND_PORT..."
npm run pyodide:fetch
npx vite dev --host --port $FRONTEND_PORT &
FRONTEND_PID=$!

echo ""
echo "✅ Serviços iniciados com sucesso!"
echo ""
echo "🌍 Acesse a aplicação em: http://localhost:$FRONTEND_PORT"
echo "📊 API disponível em: http://localhost:$BACKEND_PORT"
echo ""
echo "Pressione Ctrl+C para encerrar os serviços"

# Aguardar os processos
wait